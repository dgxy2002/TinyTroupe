"""Fixed-horizon runner shared only by the isolated research scenarios."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Mapping, Optional, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tinytroupe import config_manager, control
from tinytroupe.agent import TinyPerson
from tinytroupe.clients import client, force_api_cache, force_api_type
from tinytroupe.clients.openrouter_client import OpenRouterClient
from tinytroupe.environment import TinyWorld


SCENARIOS = {
    "hdb-space": "research_scenarios.hdb_space",
    "mrt-audio": "research_scenarios.mrt_loud_audio",
}
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_JUDGE_MODEL = "openai/gpt-5-mini"
DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
CHECKPOINT_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def write_json(path: Path, value) -> None:
    atomic_write_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str),
    )


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_jsonl(path: Path, rows: Sequence[Mapping]) -> None:
    atomic_write_text(
        path,
        "".join(json.dumps(row, ensure_ascii=False, default=str) + "\n" for row in rows),
    )


def write_csv(path: Path, rows: Sequence[Mapping]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        atomic_write_text(path, "")
        return
    fields = sorted({key for row in rows for key in row})
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def git_commit() -> Optional[str]:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reset_simulation_state() -> None:
    control.reset()
    TinyPerson.clear_agents()
    TinyWorld.clear_environments()


def flatten_actions(actions_over_time: Sequence[Mapping]) -> list[dict]:
    events = []
    turn = 0
    for round_number, round_actions in enumerate(actions_over_time, start=1):
        if not isinstance(round_actions, Mapping):
            continue
        for agent_name, agent_actions in round_actions.items():
            turn += 1
            for action_index, action_record in enumerate(agent_actions or [], start=1):
                action = action_record.get("action", action_record)
                if not isinstance(action, Mapping):
                    continue
                events.append(
                    {
                        "round": round_number,
                        "turn": turn,
                        "agent": agent_name,
                        "action_index": action_index,
                        "type": str(action.get("type", "UNKNOWN")).upper(),
                        "content": str(action.get("content") or ""),
                        "target": action.get("target"),
                    }
                )
    return events


def transcript_markdown(events: Sequence[Mapping]) -> str:
    lines = ["# Public transcript", ""]
    current_round = None
    for event in events:
        if event.get("type") != "TALK" or not str(event.get("content") or "").strip():
            continue
        if event["round"] != current_round:
            current_round = event["round"]
            lines.extend([f"## Round {current_round}", ""])
        lines.append(
            f"- **Turn {event['turn']} — {event['agent']}:** "
            f"{str(event['content']).strip()}"
        )
    return "\n".join(lines) + "\n"


def aggregate_resources(records: Sequence[Mapping]) -> dict:
    costs = [record.get("cost_usd") for record in records]
    failed = [record for record in records if record.get("request_status") == "failed"]
    return {
        "calls": len(records),
        "successful_calls": len(records) - len(failed),
        "failed_calls": len(failed),
        "input_tokens": sum(int(record.get("input_tokens") or 0) for record in records),
        "output_tokens": sum(int(record.get("output_tokens") or 0) for record in records),
        "reasoning_tokens": sum(
            int(record.get("reasoning_tokens") or 0) for record in records
        ),
        "total_tokens": sum(int(record.get("total_tokens") or 0) for record in records),
        "cost_usd": round(sum(float(cost or 0) for cost in costs), 10),
        "exact_cost_complete": all(cost is not None for cost in costs) if records else True,
        "local_latency_ms": round(
            sum(float(record.get("local_latency_ms") or 0) for record in records), 3
        ),
        "providers": sorted(
            {record["provider_name"] for record in records if record.get("provider_name")}
        ),
    }


def load_package(scenario_key: str):
    package = SCENARIOS[scenario_key]
    return import_module(f"{package}.scenario"), import_module(f"{package}.evaluation")


def checkpoint_path(output_dir: Path, run_id: str) -> Path:
    return output_dir / "checkpoints" / f"{run_id}.json"


def save_checkpoint(
    path: Path,
    *,
    scenario_key: str,
    run_id: str,
    model: str,
    planned_rounds: int,
    started_at: str,
    elapsed_wall_time_ms: float,
    scenario,
    actions_over_time: Sequence,
    round_slices: Sequence[Mapping],
    call_records: Sequence[Mapping],
) -> None:
    write_json(
        path,
        {
            "version": CHECKPOINT_VERSION,
            "scenario": scenario_key,
            "run_id": run_id,
            "model": model,
            "planned_rounds": planned_rounds,
            "started_at": started_at,
            "checkpointed_at": utc_now(),
            "elapsed_wall_time_ms": round(elapsed_wall_time_ms, 3),
            "actions_over_time": actions_over_time,
            "round_slices": round_slices,
            "call_records": call_records,
            "world_state": scenario.world.encode_complete_state(),
        },
    )


def load_checkpoint(
    path: Path, *, scenario_key: str, run_id: str, model: str, planned_rounds: int
) -> Optional[dict]:
    if not path.exists():
        return None
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "version": CHECKPOINT_VERSION,
        "scenario": scenario_key,
        "run_id": run_id,
        "model": model,
        "planned_rounds": planned_rounds,
    }
    mismatches = {
        key: (checkpoint.get(key), value)
        for key, value in expected.items()
        if checkpoint.get(key) != value
    }
    if mismatches:
        raise ValueError(f"Checkpoint does not match this run: {mismatches}")
    return checkpoint


def execute_run(
    *,
    scenario_key: str,
    run_id: str,
    model: str,
    judge_model: str,
    embedding_model: str,
    rounds: int,
    output_dir: Path,
) -> tuple[dict, list[dict]]:
    scenario_module, evaluation_module = load_package(scenario_key)
    reset_simulation_state()
    config_manager.update("model", model)
    llm_client = client()
    if not isinstance(llm_client, OpenRouterClient):
        raise RuntimeError("Research scenarios require API_TYPE=openrouter.")
    llm_client.reset_usage_tracking()

    saved = load_checkpoint(
        checkpoint_path(output_dir, run_id),
        scenario_key=scenario_key,
        run_id=run_id,
        model=model,
        planned_rounds=rounds,
    )
    if saved:
        llm_client.restore_call_records(saved.get("call_records", []))
    started_at = saved.get("started_at", utc_now()) if saved else utc_now()
    prior_wall_time_ms = float(saved.get("elapsed_wall_time_ms") or 0) if saved else 0
    wall_start = time.perf_counter()
    actions_over_time = list(saved.get("actions_over_time", [])) if saved else []
    round_slices = list(saved.get("round_slices", [])) if saved else []
    resumed_after = len(round_slices)

    scenario = scenario_module.create_scenario()
    event_state = scenario.trigger()
    if saved:
        scenario.world.decode_complete_state(saved["world_state"])
        print(f"[{run_id}] resumed after round {resumed_after}/{rounds}", flush=True)

    for round_number in range(resumed_after + 1, rounds + 1):
        print(f"[{run_id}] round {round_number}/{rounds} starting", flush=True)
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
        save_checkpoint(
            checkpoint_path(output_dir, run_id),
            scenario_key=scenario_key,
            run_id=run_id,
            model=model,
            planned_rounds=rounds,
            started_at=started_at,
            elapsed_wall_time_ms=prior_wall_time_ms
            + (time.perf_counter() - wall_start) * 1000,
            scenario=scenario,
            actions_over_time=actions_over_time,
            round_slices=round_slices,
            call_records=llm_client.get_call_records(),
        )
        print(
            f"[{run_id}] round {round_number}/{rounds} complete "
            f"({round_slices[-1]['wall_time_ms'] / 1000:.1f}s)",
            flush=True,
        )

    simulation_end = len(llm_client.get_call_records())
    events = flatten_actions(actions_over_time)
    print(f"[{run_id}] structured outcome evaluation starting", flush=True)
    evaluation_start = simulation_end
    evaluation = evaluation_module.evaluate(events, judge_model)
    evaluation_end = len(llm_client.get_call_records())
    print(f"[{run_id}] structured outcome evaluation complete", flush=True)

    embedding_start = evaluation_end
    round_embedding_vectors = {}
    print(f"[{run_id}] generating {rounds} round embeddings", flush=True)
    for round_number in range(1, rounds + 1):
        round_events = [event for event in events if event.get("round") == round_number]
        round_text = evaluation_module.transcript_text(round_events)
        round_embedding_vectors[str(round_number)] = llm_client.get_embedding(
            round_text or "[No public speech in this round]", model=embedding_model
        )
        if round_number == rounds or round_number % 5 == 0:
            print(
                f"[{run_id}] round embeddings {round_number}/{rounds} complete",
                flush=True,
            )
    embedding_end = len(llm_client.get_call_records())

    try:
        llm_client.enrich_call_records()
    except Exception as exc:
        print(f"Warning: cost metadata enrichment failed: {exc}", file=sys.stderr)
    call_records = llm_client.get_call_records()
    total_resources = aggregate_resources(call_records)
    evaluation_data = evaluation.model_dump(mode="json")
    participant_count = len(scenario.participants)
    resolution_turn = evaluation_data.get("resolution_turn")
    record = {
        "run_id": run_id,
        "scenario": scenario_key,
        "status": "completed",
        "model": model,
        "judge_model": judge_model,
        "embedding_model": embedding_model,
        "planned_rounds": rounds,
        "completed_rounds": len(round_slices),
        "participants_per_round": participant_count,
        "participant_keys": list(scenario.participants),
        "participant_names": [
            participant.name for participant in scenario.participants.values()
        ],
        "principal_participant_keys": list(
            scenario_module.PRINCIPAL_PARTICIPANTS
        ),
        "started_at": started_at,
        "finished_at": utc_now(),
        "wall_time_ms": round(
            prior_wall_time_ms + (time.perf_counter() - wall_start) * 1000, 3
        ),
        "resumed_from_checkpoint": saved is not None,
        "resumed_after_round": resumed_after if saved else None,
        "event": {
            "key": event_state.key,
            "summary": event_state.summary,
            "started_at": event_state.started_at.isoformat(),
        },
        "resolution_round": (
            (int(resolution_turn) - 1) // participant_count + 1
            if resolution_turn is not None
            else None
        ),
        "simulation_resources": aggregate_resources(call_records[:simulation_end]),
        "evaluation_resources": aggregate_resources(
            call_records[evaluation_start:evaluation_end]
        ),
        "embedding_resources": aggregate_resources(
            call_records[embedding_start:embedding_end]
        ),
        "total_resources": total_resources,
        "exact_cost_complete": total_resources["exact_cost_complete"],
        **evaluation_data,
    }
    transcript = {
        "run": record,
        "events": events,
        "private_and_public_actions": actions_over_time,
        "evaluation": evaluation_data,
        "api_calls": call_records,
        "round_embeddings": round_embedding_vectors,
    }
    write_json(output_dir / "transcripts" / f"{run_id}.json", transcript)
    atomic_write_text(
        output_dir / "transcripts" / f"{run_id}.md",
        transcript_markdown(events),
    )
    round_rows = []
    for round_slice in round_slices:
        round_rows.append(
            {
                "run_id": run_id,
                "scenario": scenario_key,
                "model": model,
                "round": round_slice["round"],
                "wall_time_ms": round_slice["wall_time_ms"],
                **aggregate_resources(
                    call_records[round_slice["call_start"] : round_slice["call_end"]]
                ),
            }
        )
    return record, round_rows


def create_manifest(args, output_dir: Path) -> dict:
    scenario_module, _ = load_package(args.scenario)
    package_dir = Path(scenario_module.__file__).resolve().parent
    persona_hashes = {
        key: file_sha256(package_dir / "personas" / filename)
        for key, filename in scenario_module.PERSONA_FILES.items()
    }
    return {
        "experiment_id": output_dir.name,
        "created_at": utc_now(),
        "git_commit": git_commit(),
        "scenario": args.scenario,
        "model": args.model,
        "judge_model": args.judge_model,
        "embedding_model": args.embedding_model,
        "runs": args.runs,
        "rounds": args.rounds,
        "fixed_horizon": True,
        "full_run_embedding": False,
        "round_embeddings": True,
        "participant_keys": list(scenario_module.PERSONA_FILES),
        "principal_participant_keys": list(
            scenario_module.PRINCIPAL_PARTICIPANTS
        ),
        "scenario_sha256": file_sha256(package_dir / "scenario.py"),
        "evaluation_sha256": file_sha256(package_dir / "evaluation.py"),
        "persona_sha256": persona_hashes,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=50)
    parser.add_argument("--experiment-id")
    parser.add_argument("--output-root", type=Path, default=Path("research_scenarios/results"))
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args(argv)
    if args.runs < 1 or args.rounds < 1:
        parser.error("runs and rounds must be positive")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    force_api_type("openrouter")
    force_api_cache(False)
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
            "max_completion_tokens": 4096,
        }
    )

    if args.resume:
        output_dir = args.resume.resolve()
        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        if args.scenario != manifest["scenario"]:
            raise ValueError("--scenario must match the resumed experiment")
        args.model = manifest["model"]
        args.judge_model = manifest["judge_model"]
        args.embedding_model = manifest["embedding_model"]
        args.runs = int(manifest["runs"])
        args.rounds = int(manifest["rounds"])
    else:
        experiment_id = args.experiment_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = (args.output_root / args.scenario / experiment_id).resolve()
        output_dir.mkdir(parents=True, exist_ok=False)
        manifest = create_manifest(args, output_dir)
        write_json(output_dir / "manifest.json", manifest)

    runs_path = output_dir / "runs.jsonl"
    rows = read_jsonl(runs_path)
    committed_ids = {row["run_id"] for row in rows}
    round_rows = [
        row
        for row in read_csv(output_dir / "round_metrics.csv")
        if row.get("run_id") in committed_ids
    ]
    for run_id in committed_ids:
        checkpoint_path(output_dir, run_id).unlink(missing_ok=True)

    print(f"Experiment output: {output_dir}", flush=True)
    while len(rows) < args.runs:
        run_number = len(rows) + 1
        run_id = f"run-{run_number:03d}"
        print(f"Starting run {run_number}/{args.runs} ({run_id})", flush=True)
        record, new_round_rows = execute_run(
            scenario_key=args.scenario,
            run_id=run_id,
            model=args.model,
            judge_model=args.judge_model,
            embedding_model=args.embedding_model,
            rounds=args.rounds,
            output_dir=output_dir,
        )
        rows.append(record)
        round_rows.extend(new_round_rows)
        write_csv(output_dir / "round_metrics.csv", round_rows)
        write_jsonl(runs_path, rows)
        checkpoint_path(output_dir, run_id).unlink(missing_ok=True)
        print(
            f"Finished run {run_number}/{args.runs}: "
            f"${record['total_resources']['cost_usd']:.6f}",
            flush=True,
        )

    from research_scenarios.analysis import analyze_experiment

    analyze_experiment(output_dir)
    print(f"Complete. Report: {output_dir / 'analysis' / 'report.md'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

