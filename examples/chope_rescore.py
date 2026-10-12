"""Offline audit and re-scoring for completed Chope experiments.

This script never calls an API. It preserves the raw experiment artifacts and
writes detector-v2 outputs to an ``analysis_v2`` subdirectory, plus one combined
comparison report beside the experiment directories.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
from statistics import fmean
from typing import Iterable, Mapping, Sequence

# Allow direct execution from a source checkout.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tinytroupe.examples.chope_metrics import (
    OUTCOMES,
    boundary_events,
    compute_convergence,
    detect_practical_resolution,
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: Sequence[Mapping]) -> None:
    fieldnames = sorted({key for row in rows for key in row}) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_audit(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_true(value) -> bool:
    return str(value).strip().lower() == "true"


def manual_label(note: str) -> tuple[bool | None, str | None]:
    lower = note.lower()
    if "manual: unresolved" in lower:
        return False, "unresolved"
    if "manual: resolved/" in lower:
        outcome = lower.split("manual: resolved/", 1)[1].split(".", 1)[0]
        return True, outcome.strip()
    return None, None


def rescore_experiment(experiment: Path) -> dict:
    manifest = read_json(experiment / "manifest.json")
    original_rows = read_jsonl(experiment / "runs.jsonl")
    embedding_rows = read_jsonl(experiment / "embeddings.jsonl")
    embeddings = {row["run_id"]: row["embedding"] for row in embedding_rows}
    output_dir = experiment / "analysis_v2"
    output_dir.mkdir(exist_ok=True)

    rescored = []
    for original in original_rows:
        row = dict(original)
        transcript_path = experiment / "transcripts" / f"{row['run_id']}.json"
        transcript = read_json(transcript_path)
        events = transcript.get("events", transcript) if isinstance(transcript, dict) else transcript
        signal = detect_practical_resolution(events)
        detected = signal is not None
        turn = signal["turn"] if signal else None
        censored = turn if turn is not None else int(row.get("completed_agent_turn_slots") or 0) + 1
        projected_rounds = (
            min(int(row.get("completed_rounds") or manifest["rounds"]), math.ceil(turn / 4))
            if turn
            else int(row.get("completed_rounds") or manifest["rounds"])
        )

        row.update(
            {
                "detector_version": "v2_audit_calibrated",
                "deterministic_resolution_achieved": detected,
                "deterministic_stop_detected": detected,
                "deterministic_resolution_signal": signal,
                "stop_signal": signal,
                "deterministic_outcome": signal["outcome"] if signal else "unresolved",
                "deterministic_resolution_turn": turn,
                "deterministic_resolution_turn_censored": censored,
                "projected_stop_round_v2": projected_rounds,
                "projected_rounds_saved_v2": max(
                    0, int(row.get("completed_rounds") or 0) - projected_rounds
                ),
            }
        )
        completed_rounds = int(row.get("completed_rounds") or 0)
        if completed_rounds:
            resources = row.get("total_resources") or {}
            simulation = row.get("simulation_resources") or {}
            fixed_cost = sum(
                float((row.get(key) or {}).get("cost_usd") or 0)
                for key in ("evaluation_resources", "embedding_resources")
            )
            row["projected_total_cost_usd_v2"] = round(
                fixed_cost
                + float(simulation.get("cost_usd") or 0)
                * projected_rounds
                / completed_rounds,
                10,
            )
            row["projected_cost_saved_usd_v2"] = round(
                float(resources.get("cost_usd") or 0)
                - row["projected_total_cost_usd_v2"],
                10,
            )
        rescored.append(row)

    thresholds = manifest["thresholds"]
    convergence_rows = []
    for model in manifest["models"]:
        model_rows = [
            row
            for row in rescored
            if row.get("model") == model and row.get("status") == "completed"
        ]
        records = compute_convergence(
            model_rows,
            embeddings,
            min_runs=manifest["min_runs"],
            batch_size=manifest["batch_size"],
            max_runs=manifest["max_runs"],
            outcome_tvd_threshold=thresholds["outcome_tvd"],
            binary_change_threshold=thresholds["binary_rate_change"],
            continuous_smd_threshold=thresholds["continuous_smd"],
            semantic_distance_threshold=thresholds["semantic_centroid_distance"],
        )
        for record in records:
            convergence_rows.append({"model": model, **record})

    audit_rows = read_audit(experiment / "manual_review.csv")
    rescored_by_id = {row["run_id"]: row for row in rescored}
    detector_resolution_matches = []
    detector_outcome_matches = []
    for audit in audit_rows:
        expected_resolved, expected_outcome = manual_label(audit.get("notes", ""))
        rescored_row = rescored_by_id.get(audit.get("run_id"))
        if expected_resolved is not None and rescored_row:
            detector_resolution_matches.append(
                bool(rescored_row["deterministic_resolution_achieved"])
                == expected_resolved
            )
            detector_outcome_matches.append(
                rescored_row["deterministic_outcome"] == expected_outcome
            )

    model_summaries = {}
    for model in manifest["models"]:
        rows = [row for row in rescored if row.get("model") == model]
        checkpoints = [row for row in convergence_rows if row["model"] == model]
        outcomes = Counter(row["deterministic_outcome"] for row in rows)
        converged_at = next((row["n"] for row in checkpoints if row["converged"]), None)
        actual_cost = sum(float(row["total_resources"]["cost_usd"]) for row in rows)
        projected_cost = sum(float(row["projected_total_cost_usd_v2"]) for row in rows)
        model_summaries[model] = {
            "runs": len(rows),
            "deterministic_resolution_rate": fmean(
                bool(row["deterministic_resolution_achieved"]) for row in rows
            ),
            "deterministic_outcome_counts": {
                outcome: outcomes[outcome] for outcome in OUTCOMES
            },
            "judge_resolution_rate": fmean(bool(row.get("resolution_achieved")) for row in rows),
            "detector_judge_resolution_disagreements": sum(
                bool(row["deterministic_resolution_achieved"])
                != bool(row.get("resolution_achieved"))
                for row in rows
            ),
            "detector_judge_outcome_disagreements": sum(
                row["deterministic_outcome"] != row.get("outcome") for row in rows
            ),
            "mean_actual_rounds": fmean(float(row["completed_rounds"]) for row in rows),
            "mean_projected_stop_round_v2": fmean(float(row["projected_stop_round_v2"]) for row in rows),
            "actual_cost_usd": round(actual_cost, 10),
            "projected_cost_usd_v2": round(projected_cost, 10),
            "projected_cost_saved_usd_v2": round(actual_cost - projected_cost, 10),
            "converged": bool(checkpoints and checkpoints[-1]["converged"]),
            "convergence_checkpoint": converged_at,
        }

    summary = {
        "experiment_id": manifest["experiment_id"],
        "execution_mode": manifest.get("execution_mode", "stress"),
        "detector_version": "v2_audit_calibrated",
        "models": model_summaries,
        "manual_audit": {
            "reviewed_runs": len(audit_rows),
            "judge_resolution_agreement": fmean(
                is_true(row.get("resolution_agrees")) for row in audit_rows
            )
            if audit_rows
            else None,
            "judge_outcome_agreement": fmean(
                is_true(row.get("outcome_agrees")) for row in audit_rows
            )
            if audit_rows
            else None,
            "judge_boundary_agreement": fmean(
                is_true(row.get("boundary_violations_agree")) for row in audit_rows
            )
            if audit_rows
            else None,
            "detector_v2_resolution_agreement": fmean(detector_resolution_matches)
            if detector_resolution_matches
            else None,
            "detector_v2_outcome_agreement": fmean(detector_outcome_matches)
            if detector_outcome_matches
            else None,
        },
    }

    expanded_boundary_events = [event for row in rescored for event in boundary_events(row)]
    write_jsonl(output_dir / "rescored_runs.jsonl", rescored)
    write_csv(output_dir / "convergence.csv", convergence_rows)
    write_jsonl(output_dir / "boundary_events.jsonl", expanded_boundary_events)
    write_json(output_dir / "summary.json", summary)
    (output_dir / "report.md").write_text(render_experiment_report(summary), encoding="utf-8")
    return summary


def percent(value) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def render_experiment_report(summary: Mapping) -> str:
    audit = summary["manual_audit"]
    lines = [
        "# Chope audit and offline re-score (detector v2)",
        "",
        f"Experiment: `{summary['experiment_id']}`  ",
        f"Execution mode: `{summary['execution_mode']}`  ",
        "",
        "## Re-scored cohort",
        "",
        "| Model | Runs | Detector resolution | Compromise | Unresolved | Actual mean rounds | Projected mean stop round | Actual cost | Projected cost* | Recomputed convergence |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for model, values in summary["models"].items():
        counts = values["deterministic_outcome_counts"]
        checkpoint = values["convergence_checkpoint"] or "—"
        lines.append(
            f"| {model} | {values['runs']} | {percent(values['deterministic_resolution_rate'])} | "
            f"{counts['compromise']} | {counts['unresolved']} | {values['mean_actual_rounds']:.2f} | "
            f"{values['mean_projected_stop_round_v2']:.2f} | ${values['actual_cost_usd']:.6f} | "
            f"${values['projected_cost_usd_v2']:.6f} | "
            f"{'yes' if values['converged'] else 'no'} ({checkpoint}) |"
        )
    lines.extend(
        [
            "",
            "## Manual audit (20% stratified sample)",
            "",
            f"- Reviewed: {audit['reviewed_runs']} runs.",
            f"- Judge resolution agreement: {percent(audit['judge_resolution_agreement'])}.",
            f"- Judge outcome agreement: {percent(audit['judge_outcome_agreement'])}.",
            f"- Judge boundary-event agreement: {percent(audit['judge_boundary_agreement'])}.",
            f"- Detector-v2 resolution agreement: {percent(audit['detector_v2_resolution_agreement'])}.",
            f"- Detector-v2 outcome agreement: {percent(audit['detector_v2_outcome_agreement'])}.",
            "",
            "## Interpretation notes",
            "",
            "- The original files are unchanged; all derived artifacts are under `analysis_v2`.",
            "- *Projected cost is a counterfactual estimate: simulation cost is prorated by projected rounds, while evaluation and embedding costs remain fixed. It is not an observed bill.",
            "- Recomputed semantic convergence reuses embeddings of the saved full transcripts. It does not represent embeddings of counterfactually truncated stress transcripts.",
            "- Convergence is numerical stability under the declared thresholds, not external validity or proof that the scenario is realistic.",
            "",
        ]
    )
    return "\n".join(lines)


def render_combined_report(summaries: Sequence[Mapping]) -> str:
    audit_totals = {
        key: sum(
            summary["manual_audit"][key] * summary["manual_audit"]["reviewed_runs"]
            for summary in summaries
            if summary["manual_audit"][key] is not None
        )
        / sum(
            summary["manual_audit"]["reviewed_runs"]
            for summary in summaries
            if summary["manual_audit"][key] is not None
        )
        for key in (
            "judge_resolution_agreement",
            "judge_outcome_agreement",
            "judge_boundary_agreement",
            "detector_v2_resolution_agreement",
            "detector_v2_outcome_agreement",
        )
    }
    lines = [
        "# Chope combined audit report",
        "",
        "This report compares the saved outcome-mode and fixed-horizon stress cohorts after the same audited detector-v2 rules were applied offline.",
        "",
        "## Dashboard",
        "",
        "![Chope convergence, findings, and limitations](chope_audit_dashboard.png)",
        "",
        "## Main results",
        "",
        "| Mode | Model | Runs | Detector resolution | Mean actual rounds | Mean projected stop round | Actual cost | Projected cost* | Converged |",
        "|---|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for summary in summaries:
        for model, values in summary["models"].items():
            checkpoint = values["convergence_checkpoint"] or "—"
            lines.append(
                f"| {summary['execution_mode']} | {model} | {values['runs']} | "
                f"{percent(values['deterministic_resolution_rate'])} | "
                f"{values['mean_actual_rounds']:.2f} | {values['mean_projected_stop_round_v2']:.2f} | "
                f"${values['actual_cost_usd']:.6f} | ${values['projected_cost_usd_v2']:.6f} | "
                f"{'yes' if values['converged'] else 'no'} ({checkpoint}) |"
            )
    lines.extend(
        [
            "",
            "Main completed runs only; pilot costs are excluded from this table.",
            "",
            "## Manual audit",
            "",
            "| Sample | Reviewed | Judge resolution | Judge outcome | Judge boundary events | Detector-v2 resolution | Detector-v2 outcome |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for summary in summaries:
        audit = summary["manual_audit"]
        lines.append(
            f"| {summary['execution_mode']} | {audit['reviewed_runs']} | "
            f"{percent(audit['judge_resolution_agreement'])} | "
            f"{percent(audit['judge_outcome_agreement'])} | "
            f"{percent(audit['judge_boundary_agreement'])} | "
            f"{percent(audit['detector_v2_resolution_agreement'])} | "
            f"{percent(audit['detector_v2_outcome_agreement'])} |"
        )
    lines.extend(
        [
            f"| combined | {sum(s['manual_audit']['reviewed_runs'] for s in summaries)} | "
            f"{percent(audit_totals['judge_resolution_agreement'])} | "
            f"{percent(audit_totals['judge_outcome_agreement'])} | "
            f"{percent(audit_totals['judge_boundary_agreement'])} | "
            f"{percent(audit_totals['detector_v2_resolution_agreement'])} | "
            f"{percent(audit_totals['detector_v2_outcome_agreement'])} |",
            "",
            "## What the audit supports",
            "",
            "- In the audited sample, 19 of 20 runs resolved through concession/accommodation (`compromise`), not consensus; one stress run remained unresolved.",
            "- Fixed-horizon runs often continue with generic agreement after the practical issue is already settled; those extra turns add cost and repetition, not much new scenario evidence.",
            "- The structured judge is strong on whether resolution occurred, but less reliable on outcome taxonomy and especially weak at flagging repetitive or corrupted dialogue as boundary failures.",
            "- Use outcome stopping for the showcase. Keep a smaller fixed-horizon cohort as a boundary test demonstrating post-resolution repetition.",
            "",
            "## Guardrails",
            "",
            "- The two cohorts are independent samples, not paired runs with matched random seeds.",
            "- *Projected cost is estimated by prorating simulation cost by rounds; it is not an observed OpenRouter charge.",
            "- Recomputed convergence still uses the original saved transcript embeddings.",
            "- A 20% audit sample is diagnostic rather than a definitive error-rate estimate.",
            "- Detector v2 was calibrated from this audit sample, so its 100% sample agreement is in-sample fit, not independent validation. Validate it on fresh held-out runs before making a general accuracy claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiments", nargs="+", type=Path)
    parser.add_argument(
        "--combined-output",
        type=Path,
        default=Path("data/chope_experiments/chope-combined-analysis-v2/report.md"),
    )
    args = parser.parse_args()
    summaries = [rescore_experiment(path.resolve()) for path in args.experiments]
    args.combined_output.parent.mkdir(parents=True, exist_ok=True)
    args.combined_output.write_text(render_combined_report(summaries), encoding="utf-8")
    print(f"Wrote combined report: {args.combined_output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
