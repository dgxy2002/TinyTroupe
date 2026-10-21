"""Offline resolution and repetition analysis for the isolated scenarios.

This module never calls an LLM. It can be rerun from the saved transcripts and
round embeddings after either a completed or interrupted experiment.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from statistics import fmean, median
from typing import Iterable, Mapping

import matplotlib.pyplot as plt


AGENT_REPEAT_THRESHOLD = 0.80
MEAN_SIMILARITY_THRESHOLD = 0.70
REPEATED_AGENT_FRACTION_THRESHOLD = 0.50
SEMANTIC_SIMILARITY_THRESHOLD = 0.90
SEMANTIC_LEXICAL_FLOOR = 0.15
REQUIRED_CONSECUTIVE_REPEATED_ROUNDS = 2
CONTROL_FRAGMENT = re.compile(r"u[0-9a-fA-F]{4,6}")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[Mapping]) -> None:
    fields = sorted({key for row in rows for key in row}) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalized_text(text: str) -> str:
    text = CONTROL_FRAGMENT.sub(" ", text.lower())
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return " ".join(text.split())


def sequence_similarity(left: str, right: str) -> float:
    left = normalized_text(left)
    right = normalized_text(right)
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def cosine_vector_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def public_talks(events: Iterable[Mapping]) -> list[dict]:
    return [
        dict(event)
        for event in events
        if event.get("type") == "TALK" and str(event.get("content") or "").strip()
    ]


def first_consecutive_candidate(rows: list[dict]) -> int | None:
    streak = 0
    start = None
    for row in rows:
        if row["repeated_round_candidate"]:
            if streak == 0:
                start = row["round"]
            streak += 1
            if streak >= REQUIRED_CONSECUTIVE_REPEATED_ROUNDS:
                return start
        else:
            streak = 0
            start = None
    return None


def analyze_run(
    run: Mapping,
    events: list[Mapping],
    round_embeddings: Mapping[str, list[float]] | None = None,
) -> tuple[dict, list[dict]]:
    """Return one run classification and its per-round repetition measures."""

    round_embeddings = round_embeddings or {}
    max_round = int(run["completed_rounds"])
    talks_by_round_agent: dict[int, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for event in public_talks(events):
        talks_by_round_agent[int(event["round"])][str(event["agent"])].append(
            str(event["content"])
        )

    previous_by_agent: dict[str, str] = {}
    round_rows = []
    for round_number in range(1, max_round + 1):
        current_by_agent = {
            agent: " ".join(parts)
            for agent, parts in talks_by_round_agent.get(round_number, {}).items()
        }
        similarities = [
            sequence_similarity(text, previous_by_agent[agent])
            for agent, text in current_by_agent.items()
            if agent in previous_by_agent
        ]
        mean_similarity = fmean(similarities) if similarities else 0.0
        repeated_fraction = (
            fmean(value >= AGENT_REPEAT_THRESHOLD for value in similarities)
            if similarities
            else 0.0
        )
        current_embedding = round_embeddings.get(str(round_number))
        previous_embedding = round_embeddings.get(str(round_number - 1))
        semantic_similarity = (
            cosine_vector_similarity(current_embedding, previous_embedding)
            if current_embedding and previous_embedding
            else None
        )
        lexical_repeat = bool(
            similarities
            and mean_similarity >= MEAN_SIMILARITY_THRESHOLD
            and repeated_fraction >= REPEATED_AGENT_FRACTION_THRESHOLD
        )
        semantic_repeat = bool(
            semantic_similarity is not None
            and semantic_similarity >= SEMANTIC_SIMILARITY_THRESHOLD
            and mean_similarity >= SEMANTIC_LEXICAL_FLOOR
        )
        round_rows.append(
            {
                "run_id": run["run_id"],
                "scenario": run["scenario"],
                "model": run["model"],
                "round": round_number,
                "mean_same_agent_similarity": round(mean_similarity, 6),
                "same_agent_repeated_fraction": round(repeated_fraction, 6),
                "semantic_similarity_to_previous_round": (
                    round(semantic_similarity, 6)
                    if semantic_similarity is not None
                    else None
                ),
                "lexical_repeat_candidate": lexical_repeat,
                "semantic_repeat_candidate": semantic_repeat,
                "repeated_round_candidate": lexical_repeat or semantic_repeat,
            }
        )
        previous_by_agent = current_by_agent

    repetition_round = first_consecutive_candidate(round_rows)
    resolution_round = (
        int(run["resolution_round"])
        if run.get("resolution_achieved") and run.get("resolution_round") is not None
        else None
    )
    for row in round_rows:
        row["resolved_by_round"] = bool(
            resolution_round is not None and row["round"] >= resolution_round
        )
        row["repetition_onset_round"] = repetition_round

    resolved = resolution_round is not None
    repetitive = repetition_round is not None
    category = (
        f"{'Resolved' if resolved else 'Unresolved'} + "
        f"{'repetitive' if repetitive else 'not repetitive'}"
    )
    resources = run.get("total_resources") or {}
    run_result = {
        "run_id": run["run_id"],
        "scenario": run["scenario"],
        "model": run["model"],
        "completed_rounds": max_round,
        "outcome": run.get("outcome", "unresolved"),
        "resolved": resolved,
        "resolution_round": resolution_round,
        "repetitive": repetitive,
        "repetition_onset_round": repetition_round,
        "category": category,
        "total_tokens": int(resources.get("total_tokens") or 0),
        "cost_usd": float(resources.get("cost_usd") or 0),
        "exact_cost_complete": bool(run.get("exact_cost_complete", False)),
        "transcript": f"../transcripts/{run['run_id']}.md",
    }
    return run_result, round_rows


def optional_median(values: list[int]) -> float | None:
    return median(values) if values else None


def build_summary(run_rows: list[dict], manifest: Mapping) -> dict:
    resolved = [row for row in run_rows if row["resolved"]]
    repeated = [row for row in run_rows if row["repetitive"]]
    definitions = (
        ("Resolved + repetitive", True, True),
        ("Resolved + not repetitive", True, False),
        ("Unresolved + repetitive", False, True),
        ("Unresolved + not repetitive", False, False),
    )
    category_summary = [
        {
            "category": label,
            "count": sum(
                row["resolved"] is is_resolved
                and row["repetitive"] is is_repetitive
                for row in run_rows
            ),
            "share": (
                sum(
                    row["resolved"] is is_resolved
                    and row["repetitive"] is is_repetitive
                    for row in run_rows
                )
                / len(run_rows)
                if run_rows
                else 0.0
            ),
        }
        for label, is_resolved, is_repetitive in definitions
    ]
    outcomes = Counter(row["outcome"] for row in run_rows)
    return {
        "experiment_id": manifest["experiment_id"],
        "scenario": manifest["scenario"],
        "model": manifest["model"],
        "fixed_horizon_rounds": int(manifest["rounds"]),
        "completed_runs": len(run_rows),
        "planned_runs": int(manifest["runs"]),
        "resolved_count": len(resolved),
        "unresolved_count": len(run_rows) - len(resolved),
        "resolution_rate": len(resolved) / len(run_rows) if run_rows else 0.0,
        "median_resolution_round": optional_median(
            [row["resolution_round"] for row in resolved]
        ),
        "repetitive_count": len(repeated),
        "not_repetitive_count": len(run_rows) - len(repeated),
        "repetition_rate": len(repeated) / len(run_rows) if run_rows else 0.0,
        "median_repetition_onset_round": optional_median(
            [row["repetition_onset_round"] for row in repeated]
        ),
        "total_tokens": sum(row["total_tokens"] for row in run_rows),
        "total_cost_usd": round(sum(row["cost_usd"] for row in run_rows), 10),
        "exact_cost_complete": all(row["exact_cost_complete"] for row in run_rows),
        "outcomes": dict(sorted(outcomes.items())),
        "category_summary": category_summary,
        "definitions": {
            "resolution": (
                "The scenario-specific structured evaluator finds mutually accepted "
                "consensus or compromise; the first accepted turn is converted to a round."
            ),
            "agent_repeat_threshold": AGENT_REPEAT_THRESHOLD,
            "mean_similarity_threshold": MEAN_SIMILARITY_THRESHOLD,
            "repeated_agent_fraction_threshold": REPEATED_AGENT_FRACTION_THRESHOLD,
            "semantic_similarity_threshold": SEMANTIC_SIMILARITY_THRESHOLD,
            "semantic_lexical_floor": SEMANTIC_LEXICAL_FLOOR,
            "consecutive_rounds": REQUIRED_CONSECUTIVE_REPEATED_ROUNDS,
        },
    }


def value_or_na(value) -> str:
    return "n/a" if value is None else f"{value:g}"


def render_report(summary: Mapping) -> str:
    category_rows = "\n".join(
        f"| {row['category']} | {row['count']} | {row['share']:.1%} |"
        for row in summary["category_summary"]
    )
    outcome_rows = "\n".join(
        f"| {outcome} | {count} |" for outcome, count in summary["outcomes"].items()
    ) or "| No completed runs | 0 |"
    definitions = summary["definitions"]
    return f"""# {summary['scenario']} resolution and repetition report

Experiment: `{summary['experiment_id']}`  
Model: `{summary['model']}`  
Fixed horizon: {summary['fixed_horizon_rounds']} rounds  
Completed runs: {summary['completed_runs']}/{summary['planned_runs']}  

## Main results

- Resolved: {summary['resolved_count']}/{summary['completed_runs']} ({summary['resolution_rate']:.1%}); median first-resolution round: {value_or_na(summary['median_resolution_round'])}.
- Repetitive: {summary['repetitive_count']}/{summary['completed_runs']} ({summary['repetition_rate']:.1%}); median repetition-onset round: {value_or_na(summary['median_repetition_onset_round'])}.
- Total tokens (simulation, evaluation, and embeddings): {summary['total_tokens']:,}.
- Total recorded cost: ${summary['total_cost_usd']:.6f}; exact cost metadata complete: {str(summary['exact_cost_complete']).lower()}.

## Category summary

| Final category | Runs | Share |
|---|---:|---:|
{category_rows}

## Scenario outcomes

| Outcome | Runs |
|---|---:|
{outcome_rows}

## Operational definitions

- Resolution: {definitions['resolution']}
- Lexical repetition: mean same-agent similarity >= {definitions['mean_similarity_threshold']:.2f}, with at least {definitions['repeated_agent_fraction_threshold']:.0%} of comparable agents individually >= {definitions['agent_repeat_threshold']:.2f}.
- Semantic repetition: adjacent-round embedding similarity >= {definitions['semantic_similarity_threshold']:.2f}, plus mean lexical similarity >= {definitions['semantic_lexical_floor']:.2f}. This can detect the same broad topic expressed using different words.
- Repetition onset: the first of {definitions['consecutive_rounds']} consecutive rounds meeting either repetition rule.
- A run can resolve and later repeat; these are separate measurements. Manual transcript review remains necessary for ambiguous cases.
"""


def plot_first_event_counts(
    run_rows: list[Mapping],
    *,
    round_field: str,
    title: str,
    color: str,
    output: Path,
    max_round: int,
) -> None:
    counts = Counter(
        int(row[round_field])
        for row in run_rows
        if row.get(round_field) is not None
    )
    rounds = list(range(1, max_round + 1))
    values = [counts.get(round_number, 0) for round_number in rounds]
    fig, axis = plt.subplots(figsize=(15, 6), facecolor="#F7F5F0")
    axis.set_facecolor("white")
    bars = axis.bar(rounds, values, width=0.82, color=color)
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", alpha=0.25)
    axis.set_axisbelow(True)
    axis.set_title(title, loc="left", fontsize=16, fontweight="bold")
    axis.set_xlabel("Round (first detection)")
    axis.set_ylabel("Number of runs")
    tick_step = 1 if max_round <= 20 else 5
    axis.set_xticks(sorted(set([1, max_round, *range(tick_step, max_round + 1, tick_step)])))
    axis.set_xlim(0.25, max_round + 0.75)
    axis.set_ylim(0, max(1, max(values, default=0)) * 1.18)
    axis.yaxis.get_major_locator().set_params(integer=True)
    for bar, value in zip(bars, values):
        if value:
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                str(value),
                ha="center",
                va="bottom",
                fontweight="bold",
            )
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def create_manual_review(path: Path, run_rows: list[dict]) -> None:
    if path.exists() or not run_rows:
        return
    sample_size = max(1, math.ceil(len(run_rows) * 0.20))
    ranked = sorted(run_rows, key=lambda row: row["run_id"])
    if sample_size == 1:
        sampled = ranked[:1]
    else:
        indexes = [
            round(index * (len(ranked) - 1) / (sample_size - 1))
            for index in range(sample_size)
        ]
        sampled = [ranked[index] for index in indexes]
    write_csv(
        path,
        [
            {
                "run_id": row["run_id"],
                "transcript": row["transcript"],
                "detected_outcome": row["outcome"],
                "detected_resolution_round": row["resolution_round"],
                "detected_repetition_onset_round": row["repetition_onset_round"],
                "outcome_agrees": "",
                "resolution_round_agrees": "",
                "repetition_round_agrees": "",
                "notes": "",
            }
            for row in sampled
        ],
    )


def analyze_experiment(experiment: Path) -> dict:
    manifest = read_json(experiment / "manifest.json")
    runs = [
        row
        for row in read_jsonl(experiment / "runs.jsonl")
        if row.get("status") == "completed"
    ]
    run_results = []
    round_results = []
    for run in runs:
        transcript = read_json(experiment / "transcripts" / f"{run['run_id']}.json")
        result, per_round = analyze_run(
            run, transcript["events"], transcript.get("round_embeddings")
        )
        run_results.append(result)
        round_results.extend(per_round)

    output = experiment / "analysis"
    output.mkdir(exist_ok=True)
    summary = build_summary(run_results, manifest)
    write_csv(output / "runs.csv", run_results)
    write_csv(output / "round_metrics.csv", round_results)
    write_csv(output / "category_summary.csv", summary["category_summary"])
    write_json(output / "summary.json", summary)
    (output / "report.md").write_text(render_report(summary), encoding="utf-8")
    create_manual_review(output / "manual_review.csv", run_results)
    plot_first_event_counts(
        run_results,
        round_field="resolution_round",
        title="Runs first resolved at each round",
        color="#176B87",
        output=output / "resolution_by_round.png",
        max_round=int(manifest["rounds"]),
    )
    plot_first_event_counts(
        run_results,
        round_field="repetition_onset_round",
        title="Runs first becoming repetitive at each round",
        color="#C84B31",
        output=output / "repetition_by_round.png",
        max_round=int(manifest["rounds"]),
    )
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", type=Path)
    args = parser.parse_args(argv)
    summary = analyze_experiment(args.experiment.resolve())
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
