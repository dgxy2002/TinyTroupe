"""Plot convergence, audit limitations, efficiency, and cost for Chope runs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter


MODEL_NAMES = {
    "openai/gpt-4o-mini": "GPT-4o mini",
    "openai/gpt-5-mini": "GPT-5 Mini",
}
COLORS = {
    "outcome_4o": "#176B87",
    "outcome_5": "#64CCC5",
    "stress_4o": "#B2533E",
    "stress_5": "#E9B824",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized_convergence_score(row: dict, thresholds: dict) -> float:
    """Largest convergence statistic divided by its declared threshold."""

    ratios = [
        float(row["outcome_tvd"]) / thresholds["outcome_tvd"],
        float(row["max_binary_rate_change"]) / thresholds["binary_rate_change"],
        float(row["max_continuous_smd"]) / thresholds["continuous_smd"],
    ]
    if row.get("semantic_centroid_distance"):
        ratios.append(
            float(row["semantic_centroid_distance"])
            / thresholds["semantic_centroid_distance"]
        )
    return max(ratios)


def percent_label(value: float) -> str:
    return f"{value:.0%}"


def plot_dashboard(experiments: list[Path], output: Path) -> None:
    records = []
    summaries = []
    for experiment in experiments:
        manifest = load_json(experiment / "manifest.json")
        summary = load_json(experiment / "analysis_v2" / "summary.json")
        convergence = load_csv(experiment / "analysis_v2" / "convergence.csv")
        mode = summary["execution_mode"]
        summaries.append(summary)
        for row in convergence:
            if row.get("is_baseline") == "True":
                continue
            model_key = "4o" if "4o" in row["model"] else "5"
            records.append(
                {
                    "mode": mode,
                    "model": row["model"],
                    "n": int(row["n"]),
                    "score": normalized_convergence_score(
                        row, manifest["thresholds"]
                    ),
                    "criteria_passed": row["criteria_passed"] == "True",
                    "converged": row["converged"] == "True",
                    "color": COLORS[f"{mode}_{model_key}"],
                }
            )

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )
    fig = plt.figure(figsize=(16, 10), facecolor="#F7F5F0")
    grid = fig.add_gridspec(
        2, 3, height_ratios=(1.25, 1), hspace=0.34, wspace=0.30
    )
    ax_convergence = fig.add_subplot(grid[0, :])
    ax_audit = fig.add_subplot(grid[1, 0])
    ax_rounds = fig.add_subplot(grid[1, 1])
    ax_cost = fig.add_subplot(grid[1, 2])

    for axis in (ax_convergence, ax_audit, ax_rounds, ax_cost):
        axis.set_facecolor("white")
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", color="#D8D8D8", linewidth=0.7, alpha=0.65)
        axis.set_axisbelow(True)

    # Panel A: convergence. A score <= 1 means every declared criterion passed.
    ax_convergence.axhspan(0, 1, color="#DCEFE1", alpha=0.75)
    ax_convergence.axhline(1, color="#3A6B35", linewidth=1.2, linestyle="--")
    ax_convergence.text(
        30.2,
        0.96,
        "all criteria pass",
        ha="right",
        va="top",
        fontsize=9,
        color="#3A6B35",
    )
    for mode in ("outcome", "stress"):
        for model in MODEL_NAMES:
            series = [
                row
                for row in records
                if row["mode"] == mode and row["model"] == model
            ]
            if not series:
                continue
            series.sort(key=lambda row: row["n"])
            label = f"{mode.title()} · {MODEL_NAMES[model]}"
            linestyle = "-" if mode == "outcome" else "--"
            ax_convergence.plot(
                [row["n"] for row in series],
                [row["score"] for row in series],
                marker="o",
                linewidth=2.3,
                markersize=6,
                linestyle=linestyle,
                color=series[0]["color"],
                label=label,
            )
            for row in series:
                if row["converged"]:
                    ax_convergence.scatter(
                        row["n"],
                        row["score"],
                        marker="*",
                        s=210,
                        color=series[0]["color"],
                        edgecolor="#222222",
                        linewidth=0.7,
                        zorder=5,
                    )
                    ax_convergence.annotate(
                        f"converged @ {row['n']}",
                        (row["n"], row["score"]),
                        xytext=(5, 12),
                        textcoords="offset points",
                        fontsize=8,
                        color="#333333",
                    )
    ax_convergence.set_title(
        "A. Numerical convergence by cumulative checkpoint", loc="left"
    )
    ax_convergence.set_xlabel("Completed runs per model")
    ax_convergence.set_ylabel("Worst criterion ÷ its threshold")
    ax_convergence.set_xticks([15, 20, 25, 30])
    ax_convergence.set_ylim(0, 2.15)
    ax_convergence.legend(ncol=2, frameon=False, loc="upper right")
    ax_convergence.text(
        0.01,
        0.97,
        "Lower is more stable. Two consecutive checkpoints at or below 1 are required.",
        transform=ax_convergence.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color="#555555",
    )

    # Panel B: audit reliability.
    total_reviewed = sum(item["manual_audit"]["reviewed_runs"] for item in summaries)
    audit_keys = [
        "judge_resolution_agreement",
        "judge_outcome_agreement",
        "judge_boundary_agreement",
        "detector_v2_resolution_agreement",
    ]
    audit_labels = [
        "Judge:\nresolution",
        "Judge:\noutcome",
        "Judge:\nboundaries",
        "Detector v2*:\nresolution",
    ]
    audit_values = [
        sum(
            item["manual_audit"][key]
            * item["manual_audit"]["reviewed_runs"]
            for item in summaries
        )
        / total_reviewed
        for key in audit_keys
    ]
    audit_colors = ["#4B8B8B", "#4B8B8B", "#C84B31", "#6B5B95"]
    bars = ax_audit.bar(
        np.arange(len(audit_values)),
        audit_values,
        color=audit_colors,
        width=0.68,
    )
    bars[-1].set_hatch("///")
    for bar, value in zip(bars, audit_values):
        ax_audit.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.025,
            percent_label(value),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    ax_audit.set_title("B. Measurement limitation", loc="left")
    ax_audit.set_xticks(np.arange(len(audit_labels)), audit_labels)
    ax_audit.set_ylim(0, 1.14)
    ax_audit.yaxis.set_major_formatter(PercentFormatter(1))
    ax_audit.text(
        0.02,
        0.96,
        "Boundary failures were usually missed",
        transform=ax_audit.transAxes,
        va="top",
        fontsize=9,
        color="#8C2F1B",
    )
    ax_audit.text(
        0.01,
        -0.27,
        f"n={total_reviewed} audited runs. *Detector v2 was fitted on this sample; not held-out accuracy.",
        transform=ax_audit.transAxes,
        fontsize=8,
        color="#555555",
    )

    # Panel C: observed rounds versus detector-v2 stopping projection.
    labels = []
    actual_rounds = []
    projected_rounds = []
    cohort_colors = []
    for summary in summaries:
        for model, values in summary["models"].items():
            short_model = "4o" if "4o" in model else "5"
            labels.append(f"{summary['execution_mode'].title()}\n{MODEL_NAMES[model]}")
            actual_rounds.append(values["mean_actual_rounds"])
            projected_rounds.append(values["mean_projected_stop_round_v2"])
            cohort_colors.append(COLORS[f"{summary['execution_mode']}_{short_model}"])
    x = np.arange(len(labels))
    width = 0.36
    observed_bars = ax_rounds.bar(
        x - width / 2,
        actual_rounds,
        width,
        label="Observed",
        color=cohort_colors,
    )
    projected_bars = ax_rounds.bar(
        x + width / 2,
        projected_rounds,
        width,
        label="Projected stop",
        facecolor="white",
        edgecolor=cohort_colors,
        linewidth=1.8,
        hatch="//",
    )
    for observed, projected, actual, stop in zip(
        observed_bars, projected_bars, actual_rounds, projected_rounds
    ):
        saved = actual - stop
        ax_rounds.text(
            (observed.get_x() + projected.get_x() + projected.get_width()) / 2,
            max(actual, stop) + 0.08,
            f"−{saved:.2f}",
            ha="center",
            fontsize=8,
            fontweight="bold",
        )
    ax_rounds.set_title("C. Repetition after practical resolution", loc="left")
    ax_rounds.set_ylabel("Mean rounds per run")
    ax_rounds.set_xticks(x, labels, rotation=12, ha="right")
    ax_rounds.set_ylim(0, 3.5)
    ax_rounds.legend(frameon=False, fontsize=8, loc="upper left")

    # Panel D: cost per run and counterfactual stopping estimate.
    actual_costs = []
    projected_costs = []
    for summary in summaries:
        for values in summary["models"].values():
            actual_costs.append(values["actual_cost_usd"] / values["runs"])
            projected_costs.append(values["projected_cost_usd_v2"] / values["runs"])
    actual_cost_bars = ax_cost.bar(
        x - width / 2,
        actual_costs,
        width,
        label="Observed",
        color=cohort_colors,
    )
    ax_cost.bar(
        x + width / 2,
        projected_costs,
        width,
        label="Projected stop*",
        facecolor="white",
        edgecolor=cohort_colors,
        linewidth=1.8,
        hatch="//",
    )
    for bar, value in zip(actual_cost_bars, actual_costs):
        ax_cost.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.0012,
            f"${value:.3f}",
            ha="center",
            fontsize=8,
            fontweight="bold",
        )
    ax_cost.set_title("D. Token-cost implication", loc="left")
    ax_cost.set_ylabel("USD per main run")
    ax_cost.set_xticks(x, labels, rotation=12, ha="right")
    ax_cost.set_ylim(0, max(actual_costs) * 1.28)
    ax_cost.legend(frameon=False, fontsize=8, loc="upper left")
    ax_cost.text(
        0.01,
        -0.27,
        "*Estimated by prorating simulation cost by rounds; not an observed charge.",
        transform=ax_cost.transAxes,
        fontsize=8,
        color="#555555",
    )

    fig.suptitle(
        "Chope simulation: convergence, findings, and limitations",
        x=0.055,
        y=0.985,
        ha="left",
        fontsize=20,
        fontweight="bold",
        color="#1F2933",
    )
    fig.text(
        0.055,
        0.948,
        "100 main runs · 20-run stratified manual audit · 19/20 audited runs resolved by compromise",
        ha="left",
        fontsize=11,
        color="#52606D",
    )
    fig.text(
        0.055,
        0.018,
        "Interpretation: convergence demonstrates within-cohort numerical stability—not external validity. "
        "The strongest framework finding is the repeated post-resolution dialogue and weak automatic boundary detection.",
        ha="left",
        fontsize=9,
        color="#444444",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(
        output.with_suffix(".svg"),
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "experiments",
        nargs="+",
        type=Path,
        help="Experiment directories containing manifest and analysis_v2 outputs.",
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    plot_dashboard([path.resolve() for path in args.experiments], args.output.resolve())
    print(f"Wrote dashboard: {args.output.resolve()}")
    print(f"Wrote vector dashboard: {args.output.resolve().with_suffix('.svg')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
