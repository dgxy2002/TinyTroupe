"""Offline within-run boundary analysis for long-horizon Chope experiments.

The analysis separates practical resolution from dialogue repetition and
saturation. It does not call an API and can be rerun from saved transcripts.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from statistics import fmean, median
from typing import Iterable, Mapping

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tinytroupe.examples.chope_metrics import detect_practical_resolution


AGENT_REPEAT_THRESHOLD = 0.80
MEAN_SIMILARITY_THRESHOLD = 0.70
REPEATED_AGENT_FRACTION_THRESHOLD = 0.50
REQUIRED_CONSECUTIVE_REPEATED_ROUNDS = 2
SEMANTIC_SIMILARITY_THRESHOLD = 0.90
SEMANTIC_LEXICAL_FLOOR = 0.15
INITIAL_RELEVANCE_THRESHOLD = 0.75
CONTROL_FRAGMENT = re.compile(r"u[0-9a-fA-F]{4,6}")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


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
    fieldnames = sorted({key for row in rows for key in row}) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalized_text(text: str) -> str:
    text = CONTROL_FRAGMENT.sub(" ", text.lower())
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return " ".join(text.split())


def sequence_similarity(left: str, right: str) -> float:
    left_normalized = normalized_text(left)
    right_normalized = normalized_text(right)
    if not left_normalized or not right_normalized:
        return 0.0
    return SequenceMatcher(None, left_normalized, right_normalized).ratio()


def cosine_token_similarity(left: str, right: str) -> float:
    left_counts = Counter(normalized_text(left).split())
    right_counts = Counter(normalized_text(right).split())
    if not left_counts or not right_counts:
        return 0.0
    numerator = sum(
        left_counts[token] * right_counts[token]
        for token in left_counts.keys() & right_counts.keys()
    )
    left_norm = math.sqrt(sum(value * value for value in left_counts.values()))
    right_norm = math.sqrt(sum(value * value for value in right_counts.values()))
    return numerator / (left_norm * right_norm)


def cosine_vector_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def public_talks(events: Iterable[Mapping]) -> list[dict]:
    return [
        dict(event)
        for event in events
        if event.get("type") == "TALK" and str(event.get("content") or "").strip()
    ]


def _first_consecutive_round(
    round_rows: list[dict],
    field: str,
    *,
    after_round: int | None = None,
) -> int | None:
    streak = 0
    streak_start = None
    for row in round_rows:
        eligible = row[field] and (
            after_round is None or row["round"] > after_round
        )
        if eligible:
            if streak == 0:
                streak_start = row["round"]
            streak += 1
            if streak >= REQUIRED_CONSECUTIVE_REPEATED_ROUNDS:
                return streak_start
        else:
            streak = 0
            streak_start = None
    return None


def analyze_run(
    run: Mapping,
    events: list[Mapping],
    resource_rows: Mapping[int, Mapping] | None = None,
    round_embeddings: Mapping[str, list[float]] | None = None,
) -> tuple[dict, list[dict]]:
    """Compute resolution, repetition onset, and saturation for one run."""

    resource_rows = resource_rows or {}
    round_embeddings = round_embeddings or {}
    talks = public_talks(events)
    max_round = int(run.get("completed_rounds") or max(event["round"] for event in talks))
    talks_by_round_agent: dict[int, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    events_by_round: dict[int, list[dict]] = defaultdict(list)
    for event in events:
        round_number = int(event.get("round") or 0)
        if round_number:
            events_by_round[round_number].append(dict(event))
    for event in talks:
        talks_by_round_agent[int(event["round"])][str(event["agent"])].append(
            str(event.get("content") or "")
        )

    round_rows = []
    cumulative_events = []
    resolution_round = None
    resolution_signal = None
    previous_by_agent: dict[str, str] = {}
    previous_round_text = ""
    initial_embedding = round_embeddings.get("1")

    for round_number in range(1, max_round + 1):
        cumulative_events.extend(events_by_round.get(round_number, []))
        current_signal = detect_practical_resolution(cumulative_events)
        if current_signal and resolution_round is None:
            resolution_round = round_number
            resolution_signal = current_signal

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
        current_round_text = " ".join(current_by_agent.values())
        aggregate_similarity = (
            cosine_token_similarity(current_round_text, previous_round_text)
            if previous_round_text
            else 0.0
        )
        current_embedding = round_embeddings.get(str(round_number))
        previous_embedding = round_embeddings.get(str(round_number - 1))
        semantic_similarity = (
            cosine_vector_similarity(current_embedding, previous_embedding)
            if current_embedding and previous_embedding
            else None
        )
        initial_relevance = (
            cosine_vector_similarity(current_embedding, initial_embedding)
            if current_embedding and initial_embedding
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
        repeated_candidate = lexical_repeat or semantic_repeat
        drift_candidate = bool(
            round_number > 1
            and initial_relevance is not None
            and initial_relevance < INITIAL_RELEVANCE_THRESHOLD
        )
        artifact_count = sum(
            len(CONTROL_FRAGMENT.findall(str(event.get("content") or "")))
            for event in events_by_round.get(round_number, [])
        )
        resources = resource_rows.get(round_number, {})
        round_rows.append(
            {
                "run_id": run["run_id"],
                "model": run["model"],
                "round": round_number,
                "resolution_detected_by_round": current_signal is not None,
                "first_resolution_round": resolution_round,
                "after_resolution": bool(
                    resolution_round is not None and round_number > resolution_round
                ),
                "mean_same_agent_similarity": round(mean_similarity, 6),
                "same_agent_repeated_fraction": round(repeated_fraction, 6),
                "aggregate_round_similarity": round(aggregate_similarity, 6),
                "semantic_similarity_to_previous_round": (
                    round(semantic_similarity, 6)
                    if semantic_similarity is not None
                    else None
                ),
                "semantic_relevance_to_initial_round": (
                    round(initial_relevance, 6)
                    if initial_relevance is not None
                    else None
                ),
                "dialogue_novelty": round(
                    1.0
                    - (
                        semantic_similarity
                        if semantic_similarity is not None
                        else mean_similarity
                    ),
                    6,
                ),
                "repeated_round_candidate": repeated_candidate,
                "topic_drift_candidate": drift_candidate,
                "control_fragment_count": artifact_count,
                "simulation_tokens": int(float(resources.get("total_tokens") or 0)),
                "simulation_cost_usd": float(resources.get("cost_usd") or 0),
            }
        )
        previous_by_agent = current_by_agent
        previous_round_text = current_round_text

    deterministic_resolution_round = resolution_round
    if "resolution_achieved" in run:
        resolution_source = "structured_evaluator"
        resolution_turn = run.get("resolution_turn")
        turns_per_round = max(
            1,
            int(run.get("planned_agent_turns") or max_round * 4) // max_round,
        )
        resolution_round = (
            min(max_round, math.ceil(int(resolution_turn) / turns_per_round))
            if run.get("resolution_achieved") and resolution_turn is not None
            else None
        )
    else:
        resolution_source = "deterministic_fallback"

    # The structured evaluator is the primary resolution measure. Refresh fields
    # populated during the deterministic pass so every exported row is consistent.
    for row in round_rows:
        row["resolution_detected_by_round"] = bool(
            resolution_round is not None and row["round"] >= resolution_round
        )
        row["first_resolution_round"] = resolution_round
        row["after_resolution"] = bool(
            resolution_round is not None and row["round"] > resolution_round
        )

    repetition_onset = _first_consecutive_round(
        round_rows, "repeated_round_candidate"
    )
    drift_onset = (
        _first_consecutive_round(
            round_rows, "topic_drift_candidate", after_round=resolution_round
        )
        if resolution_round is not None
        else None
    )
    saturation_round = (
        _first_consecutive_round(
            round_rows, "repeated_round_candidate", after_round=resolution_round
        )
        if resolution_round is not None
        else None
    )
    boundary_onset = min(
        value for value in (drift_onset, saturation_round) if value is not None
    ) if drift_onset is not None or saturation_round is not None else None
    for row in round_rows:
        row["repetition_onset_round"] = repetition_onset
        row["topic_drift_onset_round"] = drift_onset
        row["saturation_round"] = saturation_round
        row["boundary_onset_round"] = boundary_onset

    simulation_tokens = sum(row["simulation_tokens"] for row in round_rows)
    simulation_cost = sum(row["simulation_cost_usd"] for row in round_rows)
    post_saturation = [
        row
        for row in round_rows
        if saturation_round is not None and row["round"] > saturation_round
    ]
    post_boundary = [
        row
        for row in round_rows
        if boundary_onset is not None and row["round"] > boundary_onset
    ]
    run_result = {
        "run_id": run["run_id"],
        "model": run["model"],
        "completed_rounds": max_round,
        "resolution_detected": resolution_round is not None,
        "resolution_round": resolution_round,
        "resolution_source": resolution_source,
        "deterministic_resolution_round": deterministic_resolution_round,
        "deterministic_outcome": (
            resolution_signal["outcome"] if resolution_signal else "unresolved"
        ),
        "repetition_onset_detected": repetition_onset is not None,
        "repetition_onset_round": repetition_onset,
        "topic_drift_detected": drift_onset is not None,
        "topic_drift_onset_round": drift_onset,
        "saturation_detected": saturation_round is not None,
        "saturation_round": saturation_round,
        "boundary_detected": boundary_onset is not None,
        "boundary_onset_round": boundary_onset,
        "post_resolution_rounds": (
            max_round - resolution_round if resolution_round is not None else 0
        ),
        "post_saturation_rounds": (
            max_round - saturation_round if saturation_round is not None else 0
        ),
        "post_boundary_rounds": (
            max_round - boundary_onset if boundary_onset is not None else 0
        ),
        "simulation_tokens": simulation_tokens,
        "simulation_cost_usd": round(simulation_cost, 10),
        "post_saturation_tokens": sum(
            row["simulation_tokens"] for row in post_saturation
        ),
        "post_saturation_cost_usd": round(
            sum(row["simulation_cost_usd"] for row in post_saturation), 10
        ),
        "post_boundary_tokens": sum(
            row["simulation_tokens"] for row in post_boundary
        ),
        "post_boundary_cost_usd": round(
            sum(row["simulation_cost_usd"] for row in post_boundary), 10
        ),
        "control_fragment_count": sum(
            row["control_fragment_count"] for row in round_rows
        ),
    }
    return run_result, round_rows


def _optional_median(values: list[int]) -> float | None:
    return median(values) if values else None


def build_summary(run_rows: list[dict], round_rows: list[dict], manifest: Mapping) -> dict:
    completed_rounds = int(manifest["rounds"])
    resolved = [row for row in run_rows if row["resolution_detected"]]
    repeated = [row for row in run_rows if row["repetition_onset_detected"]]
    drifted = [row for row in run_rows if row["topic_drift_detected"]]
    saturated = [row for row in run_rows if row["saturation_detected"]]
    bounded = [row for row in run_rows if row["boundary_detected"]]
    total_tokens = sum(row["simulation_tokens"] for row in run_rows)
    total_cost = sum(row["simulation_cost_usd"] for row in run_rows)
    waste_tokens = sum(row["post_saturation_tokens"] for row in run_rows)
    waste_cost = sum(row["post_saturation_cost_usd"] for row in run_rows)
    boundary_tokens = sum(row["post_boundary_tokens"] for row in run_rows)
    boundary_cost = sum(row["post_boundary_cost_usd"] for row in run_rows)
    category_definitions = (
        ("Resolved + repetitive", True, True),
        ("Resolved + not repetitive", True, False),
        ("Unresolved + repetitive", False, True),
        ("Unresolved + not repetitive", False, False),
    )
    category_summary = []
    for label, is_resolved, is_repetitive in category_definitions:
        count = sum(
            bool(row["resolution_detected"]) is is_resolved
            and bool(row["repetition_onset_detected"]) is is_repetitive
            for row in run_rows
        )
        category_summary.append(
            {
                "category": label,
                "count": count,
                "share": count / len(run_rows) if run_rows else 0.0,
            }
        )

    by_round = []
    for round_number in range(1, completed_rounds + 1):
        available = [row for row in round_rows if row["round"] == round_number]
        by_round.append(
            {
                "round": round_number,
                "resolved_cumulative_rate": fmean(
                    bool(row["resolution_round"] and row["resolution_round"] <= round_number)
                    for row in run_rows
                ),
                "repetition_onset_cumulative_rate": fmean(
                    bool(
                        row["repetition_onset_round"]
                        and row["repetition_onset_round"] <= round_number
                    )
                    for row in run_rows
                ),
                "topic_drift_cumulative_rate": fmean(
                    bool(
                        row["topic_drift_onset_round"]
                        and row["topic_drift_onset_round"] <= round_number
                    )
                    for row in run_rows
                ),
                "saturation_cumulative_rate": fmean(
                    bool(
                        row["saturation_round"]
                        and row["saturation_round"] <= round_number
                    )
                    for row in run_rows
                ),
                "boundary_cumulative_rate": fmean(
                    bool(
                        row["boundary_onset_round"]
                        and row["boundary_onset_round"] <= round_number
                    )
                    for row in run_rows
                ),
                "repeated_round_rate": fmean(
                    bool(row["repeated_round_candidate"]) for row in available
                )
                if available
                else 0.0,
                "mean_dialogue_novelty": fmean(
                    float(row["dialogue_novelty"]) for row in available
                )
                if available
                else 0.0,
                "mean_initial_relevance": fmean(
                    float(row["semantic_relevance_to_initial_round"])
                    for row in available
                    if row["semantic_relevance_to_initial_round"] is not None
                )
                if any(
                    row["semantic_relevance_to_initial_round"] is not None
                    for row in available
                )
                else None,
                "topic_drift_round_rate": fmean(
                    bool(row["topic_drift_candidate"]) for row in available
                )
                if available
                else 0.0,
            }
        )

    return {
        "experiment_id": manifest["experiment_id"],
        "model": manifest["models"][0],
        "fixed_horizon_rounds": completed_rounds,
        "runs": len(run_rows),
        "definitions": {
            "resolution": (
                "The structured evaluator's first accepted practical-resolution "
                "turn, converted to its simulation round."
            ),
            "agent_repeat_threshold": AGENT_REPEAT_THRESHOLD,
            "mean_similarity_threshold": MEAN_SIMILARITY_THRESHOLD,
            "repeated_agent_fraction_threshold": REPEATED_AGENT_FRACTION_THRESHOLD,
            "required_consecutive_repeated_rounds": REQUIRED_CONSECUTIVE_REPEATED_ROUNDS,
            "semantic_similarity_threshold": SEMANTIC_SIMILARITY_THRESHOLD,
            "semantic_lexical_floor": SEMANTIC_LEXICAL_FLOOR,
            "initial_relevance_threshold": INITIAL_RELEVANCE_THRESHOLD,
            "saturation": (
                "First of two consecutive repeated-round candidates strictly after "
                "practical resolution."
            ),
        },
        "resolution_rate": len(resolved) / len(run_rows) if run_rows else 0.0,
        "resolved_count": len(resolved),
        "unresolved_count": len(run_rows) - len(resolved),
        "median_resolution_round": _optional_median(
            [row["resolution_round"] for row in resolved]
        ),
        "repetition_onset_rate": len(repeated) / len(run_rows) if run_rows else 0.0,
        "repetitive_count": len(repeated),
        "not_repetitive_count": len(run_rows) - len(repeated),
        "median_repetition_onset_round": _optional_median(
            [row["repetition_onset_round"] for row in repeated]
        ),
        "topic_drift_rate": len(drifted) / len(run_rows) if run_rows else 0.0,
        "median_topic_drift_round": _optional_median(
            [row["topic_drift_onset_round"] for row in drifted]
        ),
        "saturation_rate": len(saturated) / len(run_rows) if run_rows else 0.0,
        "median_saturation_round": _optional_median(
            [row["saturation_round"] for row in saturated]
        ),
        "boundary_rate": len(bounded) / len(run_rows) if run_rows else 0.0,
        "median_boundary_round": _optional_median(
            [row["boundary_onset_round"] for row in bounded]
        ),
        "mean_post_resolution_rounds": fmean(
            row["post_resolution_rounds"] for row in run_rows
        )
        if run_rows
        else 0.0,
        "mean_post_saturation_rounds": fmean(
            row["post_saturation_rounds"] for row in run_rows
        )
        if run_rows
        else 0.0,
        "mean_post_boundary_rounds": fmean(
            row["post_boundary_rounds"] for row in run_rows
        )
        if run_rows
        else 0.0,
        "simulation_tokens": total_tokens,
        "post_saturation_tokens": waste_tokens,
        "post_saturation_token_share": waste_tokens / total_tokens if total_tokens else 0.0,
        "simulation_cost_usd": round(total_cost, 10),
        "post_saturation_cost_usd": round(waste_cost, 10),
        "post_saturation_cost_share": waste_cost / total_cost if total_cost else 0.0,
        "post_boundary_tokens": boundary_tokens,
        "post_boundary_token_share": boundary_tokens / total_tokens if total_tokens else 0.0,
        "post_boundary_cost_usd": round(boundary_cost, 10),
        "post_boundary_cost_share": boundary_cost / total_cost if total_cost else 0.0,
        "runs_with_control_fragments": sum(
            row["control_fragment_count"] > 0 for row in run_rows
        ),
        "category_summary": category_summary,
        "by_round": by_round,
    }


def render_report(summary: Mapping) -> str:
    def value_or_na(value, suffix=""):
        return "n/a" if value is None else f"{value:g}{suffix}"

    category_lines = [
        "## Category summary",
        "",
        "| Final category | Runs | Share |",
        "|---|---:|---:|",
        *[
            f"| {row['category']} | {row['count']} | {row['share']:.1%} |"
            for row in summary["category_summary"]
        ],
        "",
        (
            f"Unresolved by round {summary['fixed_horizon_rounds']}: "
            f"{summary['unresolved_count']}/{summary['runs']}.  "
        ),
        (
            f"No repetition detected by round {summary['fixed_horizon_rounds']}: "
            f"{summary['not_repetitive_count']}/{summary['runs']}."
        ),
        "",
    ]
    return "\n".join(
        [
            "# Chope resolution and repetition report",
            "",
            f"Experiment: `{summary['experiment_id']}`  ",
            f"Model: `{summary['model']}`  ",
            f"Fixed horizon: {summary['fixed_horizon_rounds']} rounds  ",
            f"Completed runs: {summary['runs']}  ",
            "",
            "## Main results",
            "",
            f"- Resolved: {summary['resolved_count']}/{summary['runs']} ({summary['resolution_rate']:.1%}); median first-resolution round: {value_or_na(summary['median_resolution_round'])}.",
            f"- Repetitive: {summary['repetitive_count']}/{summary['runs']} ({summary['repetition_onset_rate']:.1%}); median first-repetition round: {value_or_na(summary['median_repetition_onset_round'])}.",
            f"- Simulation tokens: {summary['simulation_tokens']:,}.",
            f"- Simulation cost: ${summary['simulation_cost_usd']:.6f}.",
            "",
            *category_lines,
            "## Operational definitions",
            "",
            f"- Resolution: {summary['definitions']['resolution']}",
            f"- An agent utterance repeats when normalized sequence similarity is at least {summary['definitions']['agent_repeat_threshold']:.2f} relative to the same agent's preceding-round utterance.",
            f"- A repeated-round candidate requires mean same-agent similarity of at least {summary['definitions']['mean_similarity_threshold']:.2f} and at least {summary['definitions']['repeated_agent_fraction_threshold']:.0%} of comparable agents to repeat.",
            f"- With round embeddings, semantic similarity of at least {summary['definitions']['semantic_similarity_threshold']:.2f} plus a lexical floor of {summary['definitions']['semantic_lexical_floor']:.2f} also qualifies.",
            f"- Repetition onset is the first of {summary['definitions']['required_consecutive_repeated_rounds']} consecutive repeated-round candidates.",
            "- Manual transcript review remains necessary for ambiguous cases.",
            "",
        ]
    )


def plot_first_event_counts(
    run_rows: list[Mapping],
    *,
    round_field: str,
    title: str,
    color: str,
    output: Path,
    max_round: int,
) -> None:
    """Plot how many runs first met an event condition in each exact round."""

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
    ticks = sorted(set([1, max_round, *range(tick_step, max_round + 1, tick_step)]))
    axis.set_xticks(ticks)
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


def plot_dashboard(summary: Mapping, output: Path) -> None:
    by_round = summary["by_round"]
    rounds = [row["round"] for row in by_round]
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), facecolor="#F7F5F0")
    for axis in axes.flat:
        axis.set_facecolor("white")
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", alpha=0.25)
        axis.set_axisbelow(True)

    axes[0, 0].plot(
        rounds,
        [row["resolved_cumulative_rate"] for row in by_round],
        marker="o",
        label="Resolved",
        color="#176B87",
        linewidth=2.4,
    )
    axes[0, 0].plot(
        rounds,
        [row["topic_drift_cumulative_rate"] for row in by_round],
        marker="o",
        label="Topic drift",
        color="#E9B824",
        linewidth=2.4,
    )
    axes[0, 0].plot(
        rounds,
        [row["repetition_onset_cumulative_rate"] for row in by_round],
        marker="o",
        label="Repetition onset",
        color="#C84B31",
        linewidth=2.4,
    )
    axes[0, 0].plot(
        rounds,
        [row["saturation_cumulative_rate"] for row in by_round],
        marker="o",
        label="Convergence (after resolution)",
        color="#6B5B95",
        linewidth=2.4,
    )
    axes[0, 0].set_title(
        "A. Cumulative convergence and boundary events",
        loc="left",
        fontweight="bold",
    )
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Share of runs")
    axes[0, 0].set_ylim(0, 1.05)
    axes[0, 0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[0, 0].legend(frameon=False)

    axes[0, 1].plot(
        rounds,
        [row["mean_dialogue_novelty"] for row in by_round],
        marker="o",
        color="#176B87",
        linewidth=2.4,
        label="Novelty vs previous round",
    )
    axes[0, 1].plot(
        rounds,
        [
            row["mean_initial_relevance"]
            if row["mean_initial_relevance"] is not None
            else 1.0
            for row in by_round
        ],
        marker="s",
        color="#E9B824",
        linewidth=2.1,
        label="Relevance to conflict round",
    )
    axes[0, 1].axhline(
        summary["definitions"]["initial_relevance_threshold"],
        color="#8C6D1F",
        linestyle="--",
        linewidth=1,
    )
    axes[0, 1].set_title("B. Novelty and scenario relevance", loc="left", fontweight="bold")
    axes[0, 1].set_xlabel("Round")
    axes[0, 1].set_ylabel("Mean dialogue novelty (1 − similarity)")
    axes[0, 1].set_ylim(0, 1.05)
    axes[0, 1].legend(frameon=False, fontsize=8)

    repeated_rates = [row["repeated_round_rate"] for row in by_round]
    drift_rates = [row["topic_drift_round_rate"] for row in by_round]
    width = 0.38
    axes[1, 0].bar(
        np.array(rounds) - width / 2,
        repeated_rates,
        width,
        color="#C84B31",
        label="Repetition",
    )
    axes[1, 0].bar(
        np.array(rounds) + width / 2,
        drift_rates,
        width,
        color="#E9B824",
        label="Topic drift",
    )
    axes[1, 0].set_title("C. Boundary frequency by round", loc="left", fontweight="bold")
    axes[1, 0].set_xlabel("Round")
    axes[1, 0].set_ylabel("Runs meeting repetition rule")
    axes[1, 0].set_ylim(0, 1.05)
    axes[1, 0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[1, 0].legend(frameon=False)

    labels = ["All simulation", "After first boundary"]
    token_values = [summary["simulation_tokens"], summary["post_boundary_tokens"]]
    bars = axes[1, 1].bar(labels, token_values, color=["#4B8B8B", "#E9B824"])
    axes[1, 1].set_title("D. Token boundary cost", loc="left", fontweight="bold")
    axes[1, 1].set_ylabel("Simulation tokens")
    for bar, value in zip(bars, token_values):
        axes[1, 1].text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:,}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    axes[1, 1].text(
        0.5,
        0.92,
        f"Post-boundary share: {summary['post_boundary_token_share']:.1%}\n"
        f"Cost: ${summary['post_boundary_cost_usd']:.4f}",
        transform=axes[1, 1].transAxes,
        ha="center",
        va="top",
        fontsize=10,
    )

    fig.suptitle(
        "Chope long-horizon boundary analysis",
        x=0.055,
        y=0.985,
        ha="left",
        fontsize=20,
        fontweight="bold",
    )
    fig.text(
        0.055,
        0.95,
        f"{summary['runs']} GPT-4o-mini runs · {summary['fixed_horizon_rounds']}-round fixed horizon · no early stopping",
        ha="left",
        fontsize=11,
        color="#52606D",
    )
    fig.text(
        0.055,
        0.015,
        "Convergence means post-resolution saturation under the predeclared repetition rule; manual audit is still required.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0.03, 0.04, 0.98, 0.93))
    fig.savefig(output, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def create_manual_review(output: Path, run_rows: list[dict]) -> None:
    # The audit sheet becomes human-authored data after reviewers fill it in.
    # Re-running the deterministic analysis must not erase that work.
    if output.exists():
        return
    sample_size = max(1, math.ceil(len(run_rows) * 0.20))
    ranked = sorted(run_rows, key=lambda row: row["run_id"])
    if sample_size == 1:
        sampled = ranked[:1]
    else:
        indexes = np.linspace(0, len(ranked) - 1, sample_size, dtype=int)
        sampled = [ranked[index] for index in indexes]
    review_rows = [
        {
            "run_id": row["run_id"],
            "transcript": f"../transcripts/{row['run_id']}.md",
            "detected_resolution_round": row["resolution_round"],
            "detected_topic_drift_round": row["topic_drift_onset_round"],
            "detected_repetition_onset_round": row["repetition_onset_round"],
            "detected_saturation_round": row["saturation_round"],
            "detected_boundary_round": row["boundary_onset_round"],
            "resolution_agrees": "",
            "topic_drift_agrees": "",
            "repetition_onset_agrees": "",
            "saturation_agrees": "",
            "boundary_agrees": "",
            "notes": "",
        }
        for row in sampled
    ]
    write_csv(output, review_rows)


def analyze_experiment(experiment: Path) -> dict:
    manifest = read_json(experiment / "manifest.json")
    runs = [row for row in read_jsonl(experiment / "runs.jsonl") if row.get("status") == "completed"]
    resource_rows = read_csv(experiment / "round_metrics.csv")
    resources_by_run: dict[str, dict[int, dict]] = defaultdict(dict)
    for row in resource_rows:
        resources_by_run[row["run_id"]][int(row["round"])] = row

    run_results = []
    all_round_results = []
    for run in runs:
        transcript = read_json(experiment / "transcripts" / f"{run['run_id']}.json")
        result, round_results = analyze_run(
            run,
            transcript["events"],
            resources_by_run.get(run["run_id"]),
            transcript.get("round_embeddings"),
        )
        run_results.append(result)
        all_round_results.extend(round_results)

    output_dir = experiment / "boundary_analysis"
    output_dir.mkdir(exist_ok=True)
    summary = build_summary(run_results, all_round_results, manifest)
    write_csv(output_dir / "boundary_runs.csv", run_results)
    write_csv(output_dir / "boundary_round_metrics.csv", all_round_results)
    write_csv(output_dir / "category_summary.csv", summary["category_summary"])
    write_json(output_dir / "summary.json", summary)
    (output_dir / "report.md").write_text(render_report(summary), encoding="utf-8")
    create_manual_review(output_dir / "manual_review.csv", run_results)
    plot_first_event_counts(
        run_results,
        round_field="resolution_round",
        title="Runs first resolved at each round",
        color="#176B87",
        output=output_dir / "resolution_by_round.png",
        max_round=int(manifest["rounds"]),
    )
    plot_first_event_counts(
        run_results,
        round_field="repetition_onset_round",
        title="Runs first becoming repetitive at each round",
        color="#C84B31",
        output=output_dir / "repetition_by_round.png",
        max_round=int(manifest["rounds"]),
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", type=Path)
    args = parser.parse_args()
    summary = analyze_experiment(args.experiment.resolve())
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
