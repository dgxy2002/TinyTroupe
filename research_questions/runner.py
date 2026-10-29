"""CLI and fixed-horizon runtime for the 10 × 5 conflict pilot."""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from tinytroupe import config_manager
from tinytroupe.agent import TinyPerson
from tinytroupe.clients import client, force_api_cache, force_api_type
from tinytroupe.environment import TinyWorld

from .evaluator import (
    EVALUATOR_PROMPT_VERSION,
    evaluate_transcript,
    evaluator_prompt_sha256,
)
from .experiment_presets import (
    EXPERIMENT_PRESETS,
    ExperimentPreset,
    RunSpec,
    get_experiment_preset,
    iter_run_specs,
)
from .scenario_presets import BACKGROUND_CONFIGURATIONS, SCENARIOS
from .simulation import (
    AGENT_PROMPT_PATH,
    create_scenario_instance,
    flatten_actions,
    inject_round_observation,
    reset_simulation_state,
    run_one_round,
)
from .storage import (
    aggregate_resources,
    file_sha256,
    git_commit,
    read_json,
    transcript_markdown,
    utc_now,
    write_json_once,
    write_json_replace,
    write_round_scores_csv,
    write_text_once,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parent / "outputs"
CHECKPOINT_VERSION = 1
TRANSCRIPT_SCHEMA_VERSION = 2
EVALUATION_SCHEMA_VERSION = 2


def _call_records() -> list[dict]:
    llm_client = client()
    if hasattr(llm_client, "get_call_records"):
        return llm_client.get_call_records()
    return []


def _reset_client_usage() -> None:
    llm_client = client()
    if hasattr(llm_client, "reset_usage_tracking"):
        llm_client.reset_usage_tracking()
    elif hasattr(llm_client, "reset_cost_stats"):
        llm_client.reset_cost_stats()


def _restore_call_records(records: list[dict]) -> None:
    llm_client = client()
    if records and hasattr(llm_client, "restore_call_records"):
        llm_client.restore_call_records(records)


def _scenario_configuration_sha256(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    import hashlib

    return hashlib.sha256(encoded).hexdigest()


def _checkpoint_path(output_dir: Path, run_id: str) -> Path:
    return output_dir / "checkpoints" / f"{run_id}.json"


def _load_checkpoint(
    path: Path,
    *,
    run_spec: RunSpec,
    simulation_model: str,
    scenario_sha256: str,
) -> dict[str, Any] | None:
    if not path.exists():
        return None
    checkpoint = read_json(path)
    expected = {
        "version": CHECKPOINT_VERSION,
        "run_id": run_spec.run_id,
        "scenario_id": run_spec.scenario_id,
        "configuration_id": run_spec.configuration_id,
        "planned_rounds": run_spec.rounds,
        "simulation_model": simulation_model,
        "scenario_configuration_sha256": scenario_sha256,
        "agent_prompt_sha256": file_sha256(AGENT_PROMPT_PATH),
        "conversation_mode": run_spec.conversation_mode,
    }
    mismatches = {
        key: (
            checkpoint.get(
                key,
                "fixed_round_robin" if key == "conversation_mode" else None,
            ),
            expected_value,
        )
        for key, expected_value in expected.items()
        if checkpoint.get(
            key,
            "fixed_round_robin" if key == "conversation_mode" else None,
        )
        != expected_value
    }
    if mismatches:
        raise ValueError(f"Checkpoint does not match the requested run: {mismatches}")
    return checkpoint


def _save_checkpoint(
    path: Path,
    *,
    run_spec: RunSpec,
    simulation_model: str,
    scenario_sha256: str,
    started_at: str,
    elapsed_wall_time_ms: float,
    instance,
    actions_over_time: list,
    round_records: list[dict],
) -> None:
    write_json_replace(
        path,
        {
            "version": CHECKPOINT_VERSION,
            "run_id": run_spec.run_id,
            "scenario_id": run_spec.scenario_id,
            "configuration_id": run_spec.configuration_id,
            "planned_rounds": run_spec.rounds,
            "simulation_model": simulation_model,
            "scenario_configuration_sha256": scenario_sha256,
            "agent_prompt_sha256": file_sha256(AGENT_PROMPT_PATH),
            "conversation_mode": run_spec.conversation_mode,
            "started_at": started_at,
            "checkpointed_at": utc_now(),
            "elapsed_wall_time_ms": round(elapsed_wall_time_ms, 3),
            "actions_over_time": actions_over_time,
            "round_records": round_records,
            "api_calls": _call_records(),
            "world_state": instance.world.encode_complete_state(),
        },
    )


def execute_simulation_run(
    *,
    run_spec: RunSpec,
    simulation_model: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Complete and immutably save one simulation before evaluation starts."""

    transcript_path = output_dir / "transcripts" / f"{run_spec.run_id}.json"
    if transcript_path.exists():
        return read_json(transcript_path)

    reset_simulation_state()
    config_manager.update("model", simulation_model)
    _reset_client_usage()

    scenario = SCENARIOS[run_spec.scenario_id]
    instance = create_scenario_instance(scenario, run_spec.configuration_id)
    scenario_sha256 = _scenario_configuration_sha256(instance.preset)
    checkpoint_path = _checkpoint_path(output_dir, run_spec.run_id)
    saved = _load_checkpoint(
        checkpoint_path,
        run_spec=run_spec,
        simulation_model=simulation_model,
        scenario_sha256=scenario_sha256,
    )

    if saved:
        _restore_call_records(saved.get("api_calls", []))
        instance.world.decode_complete_state(saved["world_state"])
    actions_over_time = list(saved.get("actions_over_time", [])) if saved else []
    round_records = list(saved.get("round_records", [])) if saved else []
    completed_before = len(round_records)
    started_at = saved.get("started_at", utc_now()) if saved else utc_now()
    prior_wall_time_ms = float(saved.get("elapsed_wall_time_ms") or 0) if saved else 0
    wall_start = time.perf_counter()

    for round_number in range(completed_before + 1, run_spec.rounds + 1):
        print(
            f"[{run_spec.run_id}] simulation round {round_number}/{run_spec.rounds}",
            flush=True,
        )
        call_start = len(_call_records())
        round_start = time.perf_counter()
        public_observation = inject_round_observation(instance, round_number)
        generated = run_one_round(
            instance, conversation_mode=run_spec.conversation_mode
        )
        actions_over_time.extend(generated)
        call_end = len(_call_records())
        round_records.append(
            {
                "round": round_number,
                "wall_time_ms": round((time.perf_counter() - round_start) * 1000, 3),
                "call_start": call_start,
                "call_end": call_end,
                "public_observation": public_observation,
            }
        )
        _save_checkpoint(
            checkpoint_path,
            run_spec=run_spec,
            simulation_model=simulation_model,
            scenario_sha256=scenario_sha256,
            started_at=started_at,
            elapsed_wall_time_ms=prior_wall_time_ms
            + (time.perf_counter() - wall_start) * 1000,
            instance=instance,
            actions_over_time=actions_over_time,
            round_records=round_records,
        )

    events = flatten_actions(actions_over_time)
    for record in round_records:
        if record.get("public_observation"):
            events.append(
                {
                    "round": record["round"],
                    "turn": 0,
                    "agent": "Environment",
                    "action_index": 0,
                    "type": "OBSERVE",
                    "content": record["public_observation"],
                    "target": None,
                }
            )
    events.extend(getattr(instance.world, "public_state_events", []))
    events.sort(key=lambda event: (event["round"], event["turn"], event["action_index"]))
    call_records = _call_records()
    transcript = {
        "schema_version": TRANSCRIPT_SCHEMA_VERSION,
        "run": {
            **asdict(run_spec),
            "simulation_model": simulation_model,
            "started_at": started_at,
            "finished_at": utc_now(),
            "completed_rounds": len(round_records),
            "resumed_from_checkpoint": saved is not None,
            "simulation_resources": aggregate_resources(call_records),
        },
        "provenance": {
            "git_commit": git_commit(),
            "scenario_configuration_sha256": scenario_sha256,
            "agent_prompt_sha256": file_sha256(AGENT_PROMPT_PATH),
        },
        "scenario": instance.preset,
        "events": events,
        "private_and_public_actions": actions_over_time,
        "round_records": round_records,
        "scheduler_events": getattr(instance.world, "scheduler_events", []),
    }
    transcript_markdown_path = (
        output_dir / "transcripts" / f"{run_spec.run_id}.md"
    )
    if not transcript_markdown_path.exists():
        write_text_once(
            transcript_markdown_path,
            transcript_markdown(events, len(round_records)),
        )
    write_json_replace(
        output_dir / "resources" / f"{run_spec.run_id}.json",
        {
            "run_id": run_spec.run_id,
            "simulation_api_calls": call_records,
            "simulation_resources": aggregate_resources(call_records),
        },
    )
    # The immutable JSON is the completion marker. Write it only after all
    # simulation sidecars are durable, and always before evaluation begins.
    write_json_once(transcript_path, transcript)
    checkpoint_path.unlink(missing_ok=True)
    return transcript


def execute_evaluation(
    *,
    transcript: dict[str, Any],
    evaluator_model: str,
    output_dir: Path,
    evaluator_max_completion_tokens: int,
) -> dict[str, Any]:
    run = transcript["run"]
    run_id = run["run_id"]
    evaluation_path = output_dir / "evaluations" / f"{run_id}.json"
    if evaluation_path.exists():
        return read_json(evaluation_path)

    before = len(_call_records())
    evaluator_setting = (
        f"{transcript['scenario']['shared_setting']}\n\n"
        f"Opening situation: {transcript['scenario']['shared_trigger']}"
    )
    evaluation = evaluate_transcript(
        events=transcript["events"],
        shared_setting=evaluator_setting,
        completed_rounds=run["completed_rounds"],
        evaluator_model=evaluator_model,
        max_completion_tokens=evaluator_max_completion_tokens,
    )
    evaluator_calls = _call_records()[before:]
    artifact = {
        "schema_version": EVALUATION_SCHEMA_VERSION,
        "run": {
            "run_id": run_id,
            "scenario_id": run["scenario_id"],
            "configuration_id": run["configuration_id"],
            "repetition": run["repetition"],
            "completed_rounds": run["completed_rounds"],
            "evaluator_model": evaluator_model,
        },
        "evaluator": {
            "prompt_version": EVALUATOR_PROMPT_VERSION,
            "prompt_sha256": evaluator_prompt_sha256(),
            "evaluated_at": utc_now(),
            "normalizations": list(evaluation.normalization_notes),
            "resources": aggregate_resources(evaluator_calls),
        },
        "evaluation": evaluation.model_dump(mode="json"),
    }
    resources_path = output_dir / "resources" / f"{run_id}.json"
    resources = read_json(resources_path) if resources_path.exists() else {"run_id": run_id}
    resources["evaluator_api_calls"] = evaluator_calls
    resources["evaluator_resources"] = aggregate_resources(evaluator_calls)
    write_json_replace(resources_path, resources)
    # As with transcripts, the immutable evaluation is written last and acts
    # as the marker that this stage completed successfully.
    write_json_once(evaluation_path, artifact)
    return artifact


def _manifest(
    *,
    experiment_id: str,
    preset: ExperimentPreset,
    run_specs: list[RunSpec],
    api_type: str,
    simulation_model: str,
    evaluator_model: str,
    agent_max_completion_tokens: int,
    evaluator_max_completion_tokens: int,
) -> dict[str, Any]:
    scenario_hashes = {
        scenario_id: _scenario_configuration_sha256(asdict(SCENARIOS[scenario_id]))
        for scenario_id in preset.scenario_ids
    }
    return {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "created_at": utc_now(),
        "git_commit": git_commit(),
        "api_type": api_type,
        "simulation_model": simulation_model,
        "evaluator_model": evaluator_model,
        "models_are_distinct": simulation_model != evaluator_model,
        "experiment_preset": asdict(preset),
        "run_specs": [asdict(run_spec) for run_spec in run_specs],
        "fixed_horizon": True,
        "stop_on_resolution": False,
        "evaluation_timing": "after_complete_run",
        "agent_max_completion_tokens": agent_max_completion_tokens,
        "evaluator_max_completion_tokens": evaluator_max_completion_tokens,
        "agent_prompt_sha256": file_sha256(AGENT_PROMPT_PATH),
        "evaluator_prompt_version": EVALUATOR_PROMPT_VERSION,
        "evaluator_prompt_sha256": evaluator_prompt_sha256(),
        "protocol_sha256": file_sha256(
            REPOSITORY_ROOT
            / "reference folders"
            / "tinytroupe_conflict_scenarios_10x5.md"
        ),
        "scenario_module_sha256": scenario_hashes,
    }


def _preset_from_args(args) -> ExperimentPreset:
    preset = get_experiment_preset(args.preset)
    if args.scenario:
        preset = replace(preset, scenario_ids=(args.scenario.upper(),))
    if args.configuration:
        preset = replace(
            preset, configuration_ids=(args.configuration.upper(),)
        )
    if args.repetitions is not None:
        preset = replace(preset, repetitions_per_configuration=args.repetitions)
    if args.rounds is not None:
        preset = replace(preset, rounds_per_run=args.rounds)
    return preset


def _dry_run_payload(
    preset: ExperimentPreset,
    run_specs: list[RunSpec],
    simulation_model: str,
    evaluator_model: str,
) -> dict[str, Any]:
    return {
        "preset": asdict(preset),
        "simulation_model": simulation_model,
        "evaluator_model": evaluator_model,
        "models_are_distinct": simulation_model != evaluator_model,
        "total_runs": len(run_specs),
        "total_rounds": sum(run.rounds for run in run_specs),
        "run_ids": [run.run_id for run in run_specs],
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=tuple(EXPERIMENT_PRESETS), default="smoke")
    parser.add_argument("--scenario", choices=tuple(SCENARIOS))
    parser.add_argument("--configuration", choices=tuple(BACKGROUND_CONFIGURATIONS))
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--rounds", type=int)
    parser.add_argument("--max-runs", type=int)
    parser.add_argument("--simulation-model")
    parser.add_argument("--evaluator-model")
    parser.add_argument(
        "--api-type",
        choices=("openai", "azure", "openrouter", "ollama"),
        default=config_manager.get("api_type"),
    )
    parser.add_argument("--agent-max-completion-tokens", type=int, default=4096)
    parser.add_argument("--evaluator-max-completion-tokens", type=int, default=4096)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--experiment-id")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    for name in (
        "repetitions",
        "rounds",
        "max_runs",
        "agent_max_completion_tokens",
        "evaluator_max_completion_tokens",
    ):
        value = getattr(args, name)
        if value is not None and value < 1:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.resume and any(
        value is not None
        for value in (
            args.scenario,
            args.configuration,
            args.repetitions,
            args.rounds,
            args.max_runs,
            args.experiment_id,
        )
    ):
        parser.error("Selection overrides cannot be combined with --resume.")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.resume:
        output_dir = args.resume.resolve()
        manifest = read_json(output_dir / "manifest.json")
        compatibility_mismatches = {}
        if manifest.get("agent_prompt_sha256") != file_sha256(AGENT_PROMPT_PATH):
            compatibility_mismatches["agent_prompt_sha256"] = (
                manifest.get("agent_prompt_sha256"),
                file_sha256(AGENT_PROMPT_PATH),
            )
        if manifest.get("evaluator_prompt_sha256") != evaluator_prompt_sha256():
            compatibility_mismatches["evaluator_prompt_sha256"] = (
                manifest.get("evaluator_prompt_sha256"),
                evaluator_prompt_sha256(),
            )
        if compatibility_mismatches:
            raise ValueError(
                "This experiment was created with a different prompt version and "
                f"cannot be mixed with the current V2 pipeline: {compatibility_mismatches}"
            )
        api_type = manifest["api_type"]
        simulation_model = manifest["simulation_model"]
        evaluator_model = manifest["evaluator_model"]
        run_specs = [RunSpec(**value) for value in manifest["run_specs"]]
        preset_data = manifest["experiment_preset"]
        preset = ExperimentPreset(
            **{
                **preset_data,
                "scenario_ids": tuple(preset_data["scenario_ids"]),
                "configuration_ids": tuple(preset_data["configuration_ids"]),
            }
        )
        args.agent_max_completion_tokens = manifest["agent_max_completion_tokens"]
        args.evaluator_max_completion_tokens = manifest[
            "evaluator_max_completion_tokens"
        ]
    else:
        api_type = args.api_type
        simulation_model = args.simulation_model or config_manager.get("model")
        evaluator_model = args.evaluator_model or os.getenv(
            "TINY_TROUPE_EVALUATOR_MODEL", "openai/gpt-5-mini"
        )
        preset = _preset_from_args(args)
        run_specs = list(iter_run_specs(preset))
        if args.max_runs is not None:
            run_specs = run_specs[: args.max_runs]

    if args.dry_run:
        print(
            json.dumps(
                _dry_run_payload(
                    preset, run_specs, simulation_model, evaluator_model
                ),
                indent=2,
            )
        )
        return 0

    force_api_type(api_type)
    force_api_cache(False)
    TinyPerson.communication_display = False
    TinyWorld.communication_display = False
    config_manager.update_multiple(
        {
            "model": simulation_model,
            "enable_memory_consolidation": False,
            "enable_continuous_contextual_semantic_memory_retrieval": False,
            "parallel_agent_generation": False,
            "parallel_agent_actions": False,
            "action_generator_enable_quality_checks": False,
            "action_generator_enable_regeneration": False,
            "max_completion_tokens": args.agent_max_completion_tokens,
        }
    )

    if args.resume:
        if not output_dir.exists():
            raise FileNotFoundError(output_dir)
    else:
        timestamp = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y%m%d-%H%M%S")
        experiment_id = args.experiment_id or f"{preset.name}-{timestamp}"
        output_dir = (args.output_root / experiment_id).resolve()
        output_dir.mkdir(parents=True, exist_ok=False)
        manifest = _manifest(
            experiment_id=experiment_id,
            preset=preset,
            run_specs=run_specs,
            api_type=api_type,
            simulation_model=simulation_model,
            evaluator_model=evaluator_model,
            agent_max_completion_tokens=args.agent_max_completion_tokens,
            evaluator_max_completion_tokens=args.evaluator_max_completion_tokens,
        )
        write_json_once(output_dir / "manifest.json", manifest)

    print(f"Experiment output: {output_dir}", flush=True)
    for index, run_spec in enumerate(run_specs, start=1):
        print(f"Run {index}/{len(run_specs)}: {run_spec.run_id}", flush=True)
        transcript = execute_simulation_run(
            run_spec=run_spec,
            simulation_model=simulation_model,
            output_dir=output_dir,
        )
        execute_evaluation(
            transcript=transcript,
            evaluator_model=evaluator_model,
            output_dir=output_dir,
            evaluator_max_completion_tokens=args.evaluator_max_completion_tokens,
        )
        write_round_scores_csv(
            output_dir / "evaluations", output_dir / "round_scores.csv"
        )
        write_json_replace(
            output_dir / "status.json",
            {
                "updated_at": utc_now(),
                "completed_evaluations": len(
                    list((output_dir / "evaluations").glob("*.json"))
                ),
                "planned_runs": len(run_specs),
            },
        )

    print(f"Complete: {output_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
