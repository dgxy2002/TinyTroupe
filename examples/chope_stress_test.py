"""Run the Chope scenario as a resumable, convergence-aware experiment.

This is intentionally a command-line experiment rather than an import-time
demo. Running it incurs model and embedding charges. Use ``--help`` to inspect
the settings before starting a cohort.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean
from typing import Iterable, Mapping, Optional, Sequence

# Allow direct execution from a source checkout without requiring an editable
# package install first.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tinytroupe import config_manager, control
from tinytroupe.agent import TinyPerson
from tinytroupe.clients import client, force_api_cache, force_api_type
from tinytroupe.clients.openrouter_client import OpenRouterClient
from tinytroupe.environment import TinyWorld
from tinytroupe.examples.chope import PARTICIPANT_SPECIFICATIONS, create_chope_scenario
from tinytroupe.examples.chope_metrics import (
    EXECUTION_MODES,
    OUTCOMES,
    boundary_events,
    compute_convergence,
    compute_observable_metrics,
    detect_practical_resolution,
    evaluate_chope_run,
    evaluation_metrics,
    flatten_actions,
    json_dumps,
    public_transcript_text,
    transcript_markdown,
)


DEFAULT_MODELS = ("openai/gpt-4o-mini", "openai/gpt-5-mini")
DEFAULT_JUDGE_MODEL = "openai/gpt-5-mini"
DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"

THRESHOLDS = {
    "outcome_tvd": 0.10,
    "binary_rate_change": 0.10,
    "continuous_smd": 0.20,
    "semantic_centroid_distance": 0.05,
    "required_consecutive_passes": 2,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def model_slug(model: str) -> str:
    return model.replace("/", "--").replace(":", "-")


def git_commit() -> Optional[str]:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, value: Mapping):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json_dumps(value) + "\n")


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def write_csv(path: Path, rows: Sequence[Mapping]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json_dumps(value)
                    if isinstance(value, (dict, list, tuple))
                    else value
                    for key, value in row.items()
                }
            )


def read_csv(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def aggregate_resources(records: Sequence[Mapping]) -> dict:
    costs = [record.get("cost_usd") for record in records]
    exact = bool(records) and all(value is not None for value in costs)
    failed_records = [
        record for record in records if record.get("request_status") == "failed"
    ]
    return {
        "calls": len(records),
        "successful_calls": len(records) - len(failed_records),
        "failed_calls": len(failed_records),
        "call_error_types": sorted(
            {
                str(record.get("call_error") or "unknown").split(":", 1)[0]
                for record in failed_records
            }
        ),
        "input_tokens": sum(int(record.get("input_tokens") or 0) for record in records),
        "output_tokens": sum(int(record.get("output_tokens") or 0) for record in records),
        "reasoning_tokens": sum(
            int(record.get("reasoning_tokens") or 0) for record in records
        ),
        "total_tokens": sum(int(record.get("total_tokens") or 0) for record in records),
        "local_latency_ms": round(
            sum(float(record.get("local_latency_ms") or 0) for record in records), 3
        ),
        "cost_usd": round(sum(float(value or 0) for value in costs), 10),
        "exact_cost_complete": exact,
        "providers": sorted(
            {record["provider_name"] for record in records if record.get("provider_name")}
        ),
    }


def reset_simulation_state():
    control.reset()
    TinyPerson.clear_agents()
    TinyWorld.clear_environments()


def execute_run(
    *,
    run_id: str,
    model: str,
    judge_model: str,
    embedding_model: Optional[str],
    round_embeddings: bool,
    rounds: int,
    execution_mode: str,
    output_dir: Path,
    cohort: str = "main",
) -> tuple[dict, Optional[list[float]], list[dict]]:
    """Execute one fresh scenario and persist its complete audit trail."""

    if execution_mode not in EXECUTION_MODES:
        raise ValueError(
            f"Unknown execution mode {execution_mode!r}; expected one of "
            f"{', '.join(EXECUTION_MODES)}."
        )

    reset_simulation_state()
    config_manager.update("model", model)
    llm_client = client()
    if not isinstance(llm_client, OpenRouterClient):
        raise RuntimeError("The Chope experiment requires API_TYPE=openrouter.")
    llm_client.reset_usage_tracking()

    started_at = utc_now()
    wall_start = time.perf_counter()
    actions_over_time = []
    round_slices = []
    evaluation = None
    embedding = None
    round_embedding_vectors = {}
    error = None
    status = "completed"
    stop_signal = None

    try:
        scenario = create_chope_scenario()
        event_state = scenario.trigger()
        for round_number in range(1, rounds + 1):
            call_start = len(llm_client.get_call_records())
            round_start = time.perf_counter()
            actions = scenario.world.run(
                1,
                return_actions=True,
                parallelize=False,
                randomize_agents_order=False,
            )
            actions_over_time.extend(actions)
            call_end = len(llm_client.get_call_records())
            round_slices.append(
                {
                    "round": round_number,
                    "call_start": call_start,
                    "call_end": call_end,
                    "wall_time_ms": round((time.perf_counter() - round_start) * 1000, 3),
                }
            )
            if execution_mode == "outcome":
                stop_signal = detect_practical_resolution(
                    flatten_actions(actions_over_time)
                )
                if stop_signal:
                    break

        simulation_end = len(llm_client.get_call_records())
        events = flatten_actions(actions_over_time)
        deterministic_resolution_signal = stop_signal or detect_practical_resolution(
            events
        )

        evaluation_start = simulation_end
        evaluation = evaluate_chope_run(events, judge_model)
        evaluation_end = len(llm_client.get_call_records())

        embedding_start = evaluation_end
        if embedding_model:
            embedding = llm_client.get_embedding(
                public_transcript_text(events), model=embedding_model
            )
            if round_embeddings:
                for round_slice in round_slices:
                    round_number = round_slice["round"]
                    round_events = [
                        event for event in events if event.get("round") == round_number
                    ]
                    round_embedding_vectors[str(round_number)] = llm_client.get_embedding(
                        public_transcript_text(round_events), model=embedding_model
                    )
        embedding_end = len(llm_client.get_call_records())

    except Exception as exc:
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"
        events = flatten_actions(actions_over_time)
        event_state = getattr(locals().get("scenario"), "event_state", None)
        simulation_end = min(
            locals().get("simulation_end", len(llm_client.get_call_records())),
            len(llm_client.get_call_records()),
        )
        evaluation_start = locals().get("evaluation_start", simulation_end)
        evaluation_end = locals().get(
            "evaluation_end", len(llm_client.get_call_records())
        )
        embedding_start = locals().get("embedding_start", evaluation_end)
        embedding_end = len(llm_client.get_call_records())
        deterministic_resolution_signal = stop_signal or detect_practical_resolution(
            events
        )
        traceback.print_exc()

    # Metadata lookup is best effort: the run remains usable if billing details
    # are temporarily unavailable, and the gap becomes a boundary event.
    try:
        llm_client.enrich_call_records()
    except Exception as exc:
        print(f"Warning: could not enrich OpenRouter call metadata: {exc}", file=sys.stderr)

    call_records = llm_client.get_call_records()
    simulation_resources = aggregate_resources(call_records[:simulation_end])
    evaluation_resources = aggregate_resources(
        call_records[evaluation_start:evaluation_end]
    )
    embedding_resources = aggregate_resources(call_records[embedding_start:embedding_end])
    total_resources = aggregate_resources(call_records)

    record = {
        "run_id": run_id,
        "cohort": cohort,
        "status": status,
        "error": error,
        "model": model,
        "judge_model": judge_model,
        "embedding_model": embedding_model,
        "execution_mode": execution_mode,
        "rounds": rounds,
        "completed_rounds": len(round_slices),
        "stopped_early": bool(stop_signal and len(round_slices) < rounds),
        "deterministic_stop_detected": bool(stop_signal),
        "stop_signal": stop_signal,
        "deterministic_resolution_achieved": bool(
            deterministic_resolution_signal
        ),
        "deterministic_resolution_signal": deterministic_resolution_signal,
        "deterministic_outcome": (
            deterministic_resolution_signal["outcome"]
            if deterministic_resolution_signal
            else "unresolved"
        ),
        "deterministic_resolution_turn": (
            deterministic_resolution_signal["turn"]
            if deterministic_resolution_signal
            else None
        ),
        "deterministic_resolution_turn_censored": (
            deterministic_resolution_signal["turn"]
            if deterministic_resolution_signal
            else len(round_slices) * len(PARTICIPANT_SPECIFICATIONS) + 1
        ),
        "planned_agent_turns": rounds * len(PARTICIPANT_SPECIFICATIONS),
        "completed_agent_turn_slots": len(round_slices)
        * len(PARTICIPANT_SPECIFICATIONS),
        "event": {
            "key": event_state.key,
            "summary": event_state.summary,
            "started_at": event_state.started_at.isoformat(),
        }
        if event_state
        else None,
        "started_at": started_at,
        "finished_at": utc_now(),
        "wall_time_ms": round((time.perf_counter() - wall_start) * 1000, 3),
        "simulation_resources": simulation_resources,
        "evaluation_resources": evaluation_resources,
        "embedding_resources": embedding_resources,
        "total_resources": total_resources,
        "exact_cost_complete": total_resources["exact_cost_complete"],
        **compute_observable_metrics(events),
    }
    if evaluation is not None:
        record.update(
            evaluation_metrics(
                evaluation,
                max(1, len(round_slices) * len(PARTICIPANT_SPECIFICATIONS)),
            )
        )
        record["post_resolution_talk_count"] = sum(
            event.get("type") == "TALK"
            and event.get("turn", 0) > evaluation.resolution_turn
            for event in events
        ) if evaluation.resolution_turn is not None else 0

    transcript_dir = output_dir / ("pilots" if cohort == "pilot" else "transcripts")
    write_json(
        transcript_dir / f"{run_id}.json",
        {
            "run": record,
            "events": events,
            "private_and_public_actions": actions_over_time,
            "evaluation": evaluation.model_dump(mode="json") if evaluation else None,
            "api_calls": call_records,
            "round_embeddings": round_embedding_vectors,
        },
    )
    (transcript_dir / f"{run_id}.md").write_text(
        transcript_markdown(events), encoding="utf-8"
    )

    round_rows = []
    for round_slice in round_slices:
        resources = aggregate_resources(
            call_records[round_slice["call_start"] : round_slice["call_end"]]
        )
        round_rows.append(
            {
                "run_id": run_id,
                "cohort": cohort,
                "model": model,
                "round": round_slice["round"],
                "wall_time_ms": round_slice["wall_time_ms"],
                **resources,
            }
        )
    return record, embedding, round_rows


def convergence_for_model(
    rows: Sequence[Mapping], embeddings: Mapping[str, Sequence[float]], args
) -> list[dict]:
    completed = [row for row in rows if row.get("status") == "completed"]
    records = compute_convergence(
        completed,
        embeddings if args.embedding_model else None,
        min_runs=args.min_runs,
        batch_size=args.batch_size,
        max_runs=args.max_runs,
        outcome_tvd_threshold=THRESHOLDS["outcome_tvd"],
        binary_change_threshold=THRESHOLDS["binary_rate_change"],
        continuous_smd_threshold=THRESHOLDS["continuous_smd"],
        semantic_distance_threshold=THRESHOLDS["semantic_centroid_distance"],
    )
    for record in records:
        record["model"] = completed[0]["model"] if completed else None
    return records


def target_reached(rows: Sequence[Mapping], convergence: Sequence[Mapping], args) -> bool:
    completed = sum(row.get("status") == "completed" for row in rows)
    if completed < args.min_runs:
        return False
    if not args.adaptive:
        return True
    return bool(convergence and convergence[-1].get("converged")) or completed >= args.max_runs


def create_manifest(args, output_dir: Path) -> dict:
    package_root = Path(__file__).resolve().parents[1]
    agent_dir = package_root / "tinytroupe" / "examples" / "agents"
    agent_hashes = {
        key: file_sha256(agent_dir / f"{filename}.agent.json")
        for key, filename in PARTICIPANT_SPECIFICATIONS.items()
    }
    return {
        "experiment_id": output_dir.name,
        "created_at": utc_now(),
        "git_commit": git_commit(),
        "models": list(args.models),
        "judge_model": args.judge_model,
        "embedding_model": args.embedding_model,
        "round_embeddings": args.round_embeddings,
        "agent_max_completion_tokens": args.agent_max_completion_tokens,
        "execution_mode": args.execution_mode,
        "pilot_runs_per_model": args.pilot_runs,
        "rounds": args.rounds,
        "agent_turns_per_run": args.rounds * len(PARTICIPANT_SPECIFICATIONS),
        "max_agent_turns_per_run": args.rounds * len(PARTICIPANT_SPECIFICATIONS),
        "min_runs": args.min_runs,
        "max_runs": args.max_runs,
        "batch_size": args.batch_size,
        "adaptive": args.adaptive,
        "thresholds": THRESHOLDS,
        "agent_spec_sha256": agent_hashes,
        "generation_config": {
            "temperature": config_manager.get("temperature"),
            "max_completion_tokens": config_manager.get("max_completion_tokens"),
            "reasoning_effort": config_manager.get("reasoning_effort"),
            "timeout": config_manager.get("timeout"),
            "max_attempts": config_manager.get("max_attempts"),
        },
        "controls": {
            "fresh_world_and_agents_per_run": True,
            "one_injected_event": True,
            "fixed_sequential_agent_order": True,
            "live_communication_display": False,
            "api_cache": False,
            "memory_consolidation": False,
            "continuous_semantic_memory_retrieval": False,
            "action_quality_checks": False,
            "action_regeneration": False,
            "resolution_stop_policy": (
                "deterministic_explicit_practical_commitment_after_each_round"
                if args.execution_mode == "outcome"
                else "none_fixed_horizon"
            ),
        },
        "measurement": {
            "structured_evaluator_calls_per_completed_run": 1,
            "round_embeddings_per_completed_run": (
                args.rounds if args.embedding_model and args.round_embeddings else 0
            ),
            "primary_convergence_outcome_source": "deterministic_explicit_practical_commitment",
            "llm_judge_role": "secondary_qualitative_coding_and_audit",
            "manual_audit_fraction": 0.20,
            "pilot_excluded_from_convergence": True,
            "cost_phases": ["simulation", "evaluation", "embedding", "total"],
        },
    }


def build_summary(rows: Sequence[Mapping], convergence_rows: Sequence[Mapping]) -> dict:
    summary = {"generated_at": utc_now(), "models": {}}
    for model in sorted({row["model"] for row in rows}):
        model_rows = [row for row in rows if row["model"] == model]
        completed = [row for row in model_rows if row.get("status") == "completed"]
        outcomes = Counter(row.get("outcome") for row in completed)
        deterministic_outcomes = Counter(
            row.get("deterministic_outcome", "unresolved") for row in completed
        )
        model_convergence = [row for row in convergence_rows if row.get("model") == model]
        attempt_costs = [row["total_resources"]["cost_usd"] for row in model_rows]
        completed_costs = [
            row["total_resources"]["cost_usd"] for row in completed
        ]
        resolved = [row for row in completed if row.get("resolution_achieved")]
        convergence_checkpoint = next(
            (row["n"] for row in model_convergence if row.get("converged")), None
        )
        rows_through_convergence = []
        if convergence_checkpoint:
            completed_seen = 0
            for row in model_rows:
                rows_through_convergence.append(row)
                if row.get("status") == "completed":
                    completed_seen += 1
                if completed_seen == convergence_checkpoint:
                    break

        def rate(key):
            return (
                fmean(1.0 if row.get(key) else 0.0 for row in completed)
                if completed
                else None
            )

        def mean(key):
            values = [row.get(key) for row in completed if row.get(key) is not None]
            return fmean(values) if values else None

        def optional_rate(key):
            values = [row.get(key) for row in completed if key in row]
            return (
                fmean(1.0 if value else 0.0 for value in values)
                if values
                else None
            )

        outcome_mode_rows = [
            row for row in completed if row.get("execution_mode") == "outcome"
        ]

        def outcome_mode_rate(key):
            return (
                fmean(1.0 if row.get(key) else 0.0 for row in outcome_mode_rows)
                if outcome_mode_rows
                else None
            )

        summary["models"][model] = {
            "attempted_runs": len(model_rows),
            "completed_runs": len(completed),
            "failed_runs": len(model_rows) - len(completed),
            "failed_api_calls": sum(
                row["total_resources"].get("failed_calls", 0) for row in model_rows
            ),
            "runs_with_failed_api_calls": sum(
                row["total_resources"].get("failed_calls", 0) > 0
                for row in model_rows
            ),
            "outcome_counts": {outcome: outcomes[outcome] for outcome in OUTCOMES},
            "deterministic_outcome_counts": {
                outcome: deterministic_outcomes[outcome] for outcome in OUTCOMES
            },
            "resolution_rate": rate("resolution_achieved"),
            "deterministic_resolution_rate": optional_rate(
                "deterministic_resolution_achieved"
            ),
            "deterministic_resolution_coverage": sum(
                "deterministic_resolution_achieved" in row for row in completed
            ),
            "conflict_rate": rate("conflict_emerged"),
            "norm_recognition_rate": rate("norm_recognized"),
            "rachel_norm_acknowledgement_rate": rate("rachel_acknowledged_norm"),
            "mediation_rate": rate("mediator_emerged"),
            "immediate_capitulation_rate": rate("immediate_capitulation"),
            "premature_yield_rate": rate("premature_yield"),
            "age_deference_rate": rate("age_deference"),
            "mean_resolution_turn_censored": mean("resolution_turn_censored"),
            "mean_deterministic_resolution_turn_censored": mean(
                "deterministic_resolution_turn_censored"
            ),
            "mean_post_resolution_talk_count": mean("post_resolution_talk_count"),
            "mean_completed_rounds": mean("completed_rounds"),
            "early_stop_rate": outcome_mode_rate("stopped_early"),
            "deterministic_stop_rate": outcome_mode_rate(
                "deterministic_stop_detected"
            ),
            "mean_persona_adherence": mean("persona_adherence_mean"),
            "mean_perspective_diversity": mean("perspective_diversity"),
            "mean_total_tokens_per_run": fmean(
                row["total_resources"].get("total_tokens", 0) for row in completed
            )
            if completed
            else None,
            "mean_total_tokens_per_attempt": fmean(
                row["total_resources"].get("total_tokens", 0) for row in model_rows
            )
            if model_rows
            else None,
            "mean_wall_time_ms_per_run": mean("wall_time_ms"),
            "total_cost_usd": round(sum(attempt_costs), 10),
            "completed_runs_cost_usd": round(sum(completed_costs), 10),
            "failed_runs_cost_usd": round(
                sum(
                    row["total_resources"]["cost_usd"]
                    for row in model_rows
                    if row.get("status") != "completed"
                ),
                10,
            ),
            "simulation_cost_usd": round(
                sum(row["simulation_resources"]["cost_usd"] for row in model_rows), 10
            ),
            "evaluation_cost_usd": round(
                sum(row["evaluation_resources"]["cost_usd"] for row in model_rows), 10
            ),
            "embedding_cost_usd": round(
                sum(row["embedding_resources"]["cost_usd"] for row in model_rows), 10
            ),
            "cost_per_completed_run_usd": round(
                sum(attempt_costs) / len(completed), 10
            )
            if completed
            else None,
            "cost_per_resolved_run_usd": round(
                sum(attempt_costs) / len(resolved), 10
            )
            if resolved
            else None,
            "exact_cost_complete": all(
                row.get("exact_cost_complete") for row in model_rows
            )
            if model_rows
            else False,
            "converged": bool(
                model_convergence and model_convergence[-1].get("converged")
            ),
            "convergence_checkpoint": convergence_checkpoint,
            "cost_to_convergence_usd": round(
                sum(
                    row["total_resources"]["cost_usd"]
                    for row in rows_through_convergence
                ),
                10,
            )
            if convergence_checkpoint
            else None,
        }
    return summary


def render_report(manifest: Mapping, summary: Mapping) -> str:
    lines = [
        "# Chope experiment report",
        "",
        f"Experiment: `{manifest['experiment_id']}`  ",
        f"Git commit: `{manifest.get('git_commit') or 'unavailable'}`  ",
        f"Execution mode: `{manifest.get('execution_mode', 'stress')}`  ",
        f"Maximum rounds per run: {manifest['rounds']}  ",
        "",
        "## Cohort results",
        "",
        "| Model | Attempts | Completed | Deterministic resolution | Judge resolution | Mean rounds | Early stop | Actual cost (USD) | Converged | Checkpoint |",
        "|---|---:|---:|---:|---:|---:|---:|---:|:---:|---:|",
    ]
    for model, values in summary["models"].items():
        resolution = values["resolution_rate"]
        resolution_text = f"{resolution:.1%}" if resolution is not None else "n/a"
        deterministic_resolution = values.get("deterministic_resolution_rate")
        deterministic_resolution_text = (
            f"{deterministic_resolution:.1%}"
            if deterministic_resolution is not None
            else "n/a"
        )
        mean_rounds = values.get("mean_completed_rounds")
        mean_rounds_text = f"{mean_rounds:.2f}" if mean_rounds is not None else "n/a"
        early_stop = values.get("early_stop_rate")
        early_stop_text = f"{early_stop:.1%}" if early_stop is not None else "n/a"
        lines.append(
            f"| {model} | {values['attempted_runs']} | {values['completed_runs']} | "
            f"{deterministic_resolution_text} | {resolution_text} | "
            f"{mean_rounds_text} | {early_stop_text} | "
            f"{values['total_cost_usd']:.6f} | "
            f"{'yes' if values['converged'] else 'no'} | "
            f"{values['convergence_checkpoint'] or '—'} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- Convergence means the predeclared numerical stability criteria passed at two consecutive checkpoints; it does not prove external validity.",
            "- Qualitative findings should be supported by evaluator evidence and the saved transcript, then checked in the manual-audit sheet.",
            "- Boundary events and incomplete exact-cost metadata are retained rather than silently dropped.",
            "",
        ]
    )
    return "\n".join(lines)


def update_manual_review(path: Path, rows: Sequence[Mapping]):
    completed = [row for row in rows if row.get("status") == "completed"]
    previous = {row["run_id"]: row for row in read_csv(path)}
    selected_ids = list(previous)
    for model in sorted({row["model"] for row in completed}):
        model_rows = [row for row in completed if row["model"] == model]
        sample_size = math.ceil(len(model_rows) * 0.20)
        already_selected = sum(
            previous_row.get("model") == model for previous_row in previous.values()
        )
        ranked = sorted(
            model_rows,
            key=lambda row: hashlib.sha256(row["run_id"].encode()).hexdigest(),
        )
        for row in ranked:
            if already_selected >= sample_size:
                break
            if row["run_id"] not in selected_ids:
                selected_ids.append(row["run_id"])
                already_selected += 1
    completed_by_id = {row["run_id"]: row for row in completed}
    review_rows = []
    for run_id in selected_ids:
        if run_id not in completed_by_id:
            continue
        row = completed_by_id[run_id]
        template = {
            "run_id": row["run_id"],
            "model": row["model"],
            "transcript": f"transcripts/{row['run_id']}.md",
            "reviewer": "",
            "reviewed_at": "",
            "outcome_agrees": "",
            "resolution_agrees": "",
            "boundary_violations_agree": "",
            "notes": "",
        }
        template.update(previous.get(run_id, {}))
        review_rows.append(template)
    write_csv(path, review_rows)


def persist_analysis_outputs(
    output_dir: Path,
    rows: Sequence[Mapping],
    embeddings: Mapping[str, Sequence[float]],
    round_rows: Sequence[Mapping],
    args,
    manifest: Mapping,
) -> list[dict]:
    """Materialize current checkpoints after every batch for safe resumption."""

    all_convergence = []
    for model in args.models:
        all_convergence.extend(
            convergence_for_model(
                [row for row in rows if row.get("model") == model], embeddings, args
            )
        )
    write_csv(output_dir / "round_metrics.csv", round_rows)
    write_csv(output_dir / "convergence.csv", all_convergence)
    update_manual_review(output_dir / "manual_review.csv", rows)
    summary = build_summary(rows, all_convergence)
    write_json(output_dir / "summary.json", summary)
    (output_dir / "report.md").write_text(
        render_report(manifest, summary), encoding="utf-8"
    )
    return all_convergence


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--no-embeddings", action="store_true")
    parser.add_argument(
        "--round-embeddings",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Embed each completed round for within-run semantic-boundary analysis.",
    )
    parser.add_argument("--agent-max-completion-tokens", type=int, default=4096)
    parser.add_argument(
        "--execution-mode",
        choices=EXECUTION_MODES,
        default="outcome",
        help=(
            "outcome stops after a deterministic explicit settlement signal; "
            "stress always runs the fixed round horizon"
        ),
    )
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--pilot-runs", type=int, default=1)
    parser.add_argument("--min-runs", type=int, default=10)
    parser.add_argument("--max-runs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument(
        "--adaptive", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument("--output-root", type=Path, default=Path("data/chope_experiments"))
    parser.add_argument("--experiment-id")
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args(argv)
    if args.no_embeddings:
        args.embedding_model = None
    if args.rounds < 1 or args.pilot_runs < 0:
        parser.error("rounds must be positive and pilot-runs cannot be negative")
    if args.agent_max_completion_tokens < 512:
        parser.error("agent-max-completion-tokens must be at least 512")
    if args.batch_size < 1 or args.min_runs < args.batch_size:
        parser.error("min-runs must be >= batch-size >= 1")
    if args.max_runs < args.min_runs:
        parser.error("max-runs must be >= min-runs")
    return args


def main(argv=None):
    args = parse_args(argv)
    force_api_type("openrouter")
    force_api_cache(False)
    # Full transcripts are persisted. Live Rich rendering is unnecessary in a
    # batch and can crash Windows CP1252 consoles on otherwise valid Unicode.
    TinyPerson.communication_display = False
    TinyWorld.communication_display = False
    config_manager.update_multiple(
        {
            "enable_memory_consolidation": False,
            "enable_continuous_contextual_semantic_memory_retrieval": False,
            "parallel_agent_generation": False,
            "parallel_agent_actions": False,
            "action_generator_enable_quality_checks": False,
            "action_generator_enable_regeneration": False,
        }
    )

    if args.resume:
        output_dir = args.resume.resolve()
        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        if list(args.models) != manifest["models"]:
            raise ValueError("--models must match the manifest when resuming.")
        args.judge_model = manifest["judge_model"]
        args.embedding_model = manifest["embedding_model"]
        args.round_embeddings = manifest.get("round_embeddings", False)
        # Historical manifests predate early stopping and therefore represent
        # fixed-horizon stress runs.
        args.execution_mode = manifest.get("execution_mode", "stress")
        args.agent_max_completion_tokens = manifest.get(
            "agent_max_completion_tokens",
            manifest.get("generation_config", {}).get("max_completion_tokens", 4096),
        )
        args.pilot_runs = manifest["pilot_runs_per_model"]
        args.rounds = manifest["rounds"]
        args.min_runs = manifest["min_runs"]
        args.max_runs = manifest["max_runs"]
        args.batch_size = manifest["batch_size"]
        args.adaptive = manifest["adaptive"]
        config_manager.update(
            "max_completion_tokens", args.agent_max_completion_tokens
        )
    else:
        config_manager.update(
            "max_completion_tokens", args.agent_max_completion_tokens
        )
        experiment_id = args.experiment_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = (args.output_root / experiment_id).resolve()
        output_dir.mkdir(parents=True, exist_ok=False)
        manifest = create_manifest(args, output_dir)
        write_json(output_dir / "manifest.json", manifest)

    runs_path = output_dir / "runs.jsonl"
    embeddings_path = output_dir / "embeddings.jsonl"
    boundary_path = output_dir / "boundary_events.jsonl"
    rows = read_jsonl(runs_path)
    embeddings = {
        row["run_id"]: row["embedding"] for row in read_jsonl(embeddings_path)
    }
    round_rows = read_csv(output_dir / "round_metrics.csv")

    print(f"Experiment output: {output_dir}")
    for model in args.models:
        pilot_dir = output_dir / "pilots"
        existing_pilot_files = sorted(
            pilot_dir.glob(f"{model_slug(model)}-pilot-*.json")
        )
        for pilot_path in existing_pilot_files:
            pilot_data = json.loads(pilot_path.read_text(encoding="utf-8"))
            if pilot_data.get("run", {}).get("status") != "completed":
                raise RuntimeError(
                    f"Existing pilot {pilot_path.name} failed; inspect or start a new "
                    "experiment before paid main runs."
                )
        existing_pilots = len(existing_pilot_files)
        for number in range(existing_pilots + 1, args.pilot_runs + 1):
            run_id = f"{model_slug(model)}-pilot-{number:03d}"
            print(f"Pilot {run_id}")
            pilot_record, _, _ = execute_run(
                run_id=run_id,
                model=model,
                judge_model=args.judge_model,
                embedding_model=args.embedding_model,
                round_embeddings=args.round_embeddings,
                rounds=args.rounds,
                execution_mode=args.execution_mode,
                output_dir=output_dir,
                cohort="pilot",
            )
            if pilot_record["status"] != "completed":
                raise RuntimeError(
                    f"Pilot {run_id} failed; inspect pilots/{run_id}.json before "
                    "starting paid main runs."
                )

        model_rows = [row for row in rows if row.get("model") == model]
        attempt_limit = args.max_runs * 2
        while True:
            convergence = convergence_for_model(model_rows, embeddings, args)
            if target_reached(model_rows, convergence, args):
                break
            if len(model_rows) >= attempt_limit:
                print(f"Stopping {model}: failure-attempt limit reached.", file=sys.stderr)
                break

            completed_count = sum(row.get("status") == "completed" for row in model_rows)
            next_checkpoint = (
                args.min_runs
                if completed_count < args.min_runs
                else min(args.max_runs, completed_count + args.batch_size)
            )
            needed = max(1, next_checkpoint - completed_count)
            for _ in range(needed):
                sequence = len(model_rows) + 1
                run_id = f"{model_slug(model)}-{sequence:03d}"
                print(f"Run {run_id}")
                record, embedding, new_round_rows = execute_run(
                    run_id=run_id,
                    model=model,
                    judge_model=args.judge_model,
                    embedding_model=args.embedding_model,
                    round_embeddings=args.round_embeddings,
                    rounds=args.rounds,
                    execution_mode=args.execution_mode,
                    output_dir=output_dir,
                )
                append_jsonl(runs_path, record)
                rows.append(record)
                model_rows.append(record)
                round_rows.extend(new_round_rows)
                if embedding is not None:
                    embeddings[run_id] = embedding
                    append_jsonl(
                        embeddings_path,
                        {"run_id": run_id, "model": model, "embedding": embedding},
                    )
                for event in boundary_events(record):
                    append_jsonl(boundary_path, event)

            persist_analysis_outputs(
                output_dir, rows, embeddings, round_rows, args, manifest
            )

    persist_analysis_outputs(
        output_dir, rows, embeddings, round_rows, args, manifest
    )
    print(f"Complete. Report: {output_dir / 'report.md'}")


if __name__ == "__main__":
    main()

