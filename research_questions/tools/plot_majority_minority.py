"""Charts of the 72 majority/minority runs for slides, from research_questions/minority_majority_runs.csv.

Usage (from the repo root): python research_questions/tools/plot_majority_minority.py

Writes three PNGs to research_questions/figures/:
  majmin_start_end.png       start -> end agreement (majority with the outnumbered person) for the 12 rooms
  majmin_standardised.png    standardised change, majority x outnumbered grid
  majmin_reversal_gaps.png   gap between the two directions of each culture pair, raw vs standardised change
Colours: reference palette of the dataviz skill (validated: blue/orange categorical, blue 250/550 ordinal).
"""

import csv
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

RQ = Path(__file__).resolve().parents[1]
OUT = RQ / "figures"
CULTURES = ["Chinese", "Malay", "Indian", "Eurasian"]
PAIRS = [("Chinese", "Malay"), ("Chinese", "Indian"), ("Malay", "Indian"),
         ("Chinese", "Eurasian"), ("Malay", "Eurasian"), ("Indian", "Eurasian")]

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
START, END = "#86b6ef", "#1c5cab"          # blue 250 / 550, one hue, two shades (ordinal check passed)
RAW, STD = "#2a78d6", "#eb6834"            # categorical slots 1 and 2 (all checks passed)
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 10,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "xtick.color": MUTED,
    "ytick.color": INK2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def rooms():
    data = {}
    with (RQ / "minority_majority_runs.csv").open(encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            data.setdefault((row["majority"], row["minority_D"]), []).append(row)
    out = {}
    for key, rows in data.items():
        def avg(field):
            return statistics.mean(float(r[field]) for r in rows)
        out[key] = {"start": avg("majority_D_start"), "end": avg("majority_D_end"),
                    "change": avg("majority_D_change"), "std": avg("majority_D_standardised_change"), "n": len(rows)}
    return out


def tidy(ax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)


def start_end(data):
    fig, ax = plt.subplots(figsize=(9, 7.2))
    labels, y = [], 0
    ys = []
    for a, b in PAIRS:
        for maj, mino in ((a, b), (b, a)):
            r = data[(maj, mino)]
            ax.plot([r["start"], r["end"]], [y, y], color=AXIS, lw=2, zorder=1, solid_capstyle="round")
            ax.scatter([r["start"]], [y], s=70, color=START, edgecolor=SURFACE, linewidth=2, zorder=3)
            ax.scatter([r["end"]], [y], s=70, color=END, edgecolor=SURFACE, linewidth=2, zorder=3)
            ax.text(max(r["start"], r["end"]) + 0.05, y, f"+{r['change']:.2f}", va="center", color=INK2, fontsize=9)
            labels.append(f"3 {maj} + {mino} D")
            ys.append(y)
            y += 1
        ax.text(-1.27, y - 2.5 + 0.02, f"{a} – {b}", ha="left", va="center", fontsize=9.5, color=INK, fontweight="bold",
                transform=ax.transData)
        y += 0.9
    ax.set_yticks(ys, labels)
    ax.invert_yaxis()
    ax.set_xlim(-0.95, 1.25)
    ax.set_xticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1.0])
    ax.axvline(0, color=AXIS, lw=1, zorder=0)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel("Agreement between the majority and the outnumbered person (−1 opposed, +1 aligned)")
    tidy(ax)
    ax.scatter([], [], s=70, color=START, label="Start")
    ax.scatter([], [], s=70, color=END, label="End")
    ax.legend(loc="lower right", frameon=False, labelcolor=INK2)
    ax.set_title("Agreement rises in every room; labels show the change (end − start)",
                 loc="left", color=INK, fontsize=12, pad=12)
    fig.text(0.01, 0.01, "72 runs (smells + bereavement), 6 per room. Rows sorted by culture pair, both directions.",
             color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "majmin_start_end.png", dpi=200)
    plt.close(fig)


def standardised(data):
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    lo, hi = 0.3, 0.8
    for i, maj in enumerate(CULTURES):
        for j, mino in enumerate(CULTURES):
            if maj == mino:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor="#f0efec", edgecolor=SURFACE, lw=2))
                ax.text(j + 0.5, i + 0.5, "—", ha="center", va="center", color=MUTED)
                continue
            r = data[(maj, mino)]
            level = (r["std"] - lo) / (hi - lo)
            colour = cmap(max(0, min(1, level)))
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=colour, edgecolor=SURFACE, lw=2))
            ink = "#ffffff" if level > 0.45 else INK
            ax.text(j + 0.5, i + 0.45, f"{r['std']:.2f}", ha="center", va="center", color=ink, fontsize=13, fontweight="bold")
            ax.text(j + 0.5, i + 0.72, f"start {r['start']:+.2f}", ha="center", va="center", color=ink, fontsize=8)
    ax.set_xlim(0, 4)
    ax.set_ylim(4, 0)
    ax.set_xticks([k + 0.5 for k in range(4)], CULTURES)
    ax.set_yticks([k + 0.5 for k in range(4)], CULTURES)
    ax.xaxis.tick_top()
    ax.set_xlabel("Outnumbered person (D)", labelpad=8)
    ax.xaxis.set_label_position("top")
    ax.set_ylabel("Majority (3 people)")
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(length=0)
    fig.text(0.02, 0.02, "Standardised change = share of the possible rise achieved, (end − start) / (1 − start).\n"
                         "Darker = more of the gap to full agreement closed. Overall 0.56.", color=MUTED, fontsize=8.5)
    fig.suptitle("Standardised agreement change by room", x=0.02, ha="left", color=INK, fontsize=12)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(OUT / "majmin_standardised.png", dpi=200)
    plt.close(fig)


def reversal(data):
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    names = [f"{a} – {b}" for a, b in PAIRS]
    raw = [abs(data[(a, b)]["change"] - data[(b, a)]["change"]) for a, b in PAIRS]
    std = [abs(data[(a, b)]["std"] - data[(b, a)]["std"]) for a, b in PAIRS]
    x = range(len(PAIRS))
    width = 0.36
    bars_raw = ax.bar([k - width / 2 - 0.01 for k in x], raw, width, color=RAW, label="Raw change (end − start)")
    bars_std = ax.bar([k + width / 2 + 0.01 for k in x], std, width, color=STD, label="Standardised change")
    for bars in (bars_raw, bars_std):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008, f"{bar.get_height():.2f}",
                    ha="center", va="bottom", fontsize=8.5, color=INK2)
    ax.set_xticks(list(x), names, fontsize=9)
    ax.set_ylabel("Gap between the two directions")
    ax.set_ylim(0, 0.42)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    tidy(ax)
    ax.spines["bottom"].set_color(AXIS)
    ax.legend(frameon=False, labelcolor=INK2, loc="upper left")
    ax.set_title("Swapping who is the majority: the big raw gaps shrink once the start is accounted for",
                 loc="left", color=INK, fontsize=11.5, pad=10)
    fig.text(0.01, 0.01, "Gap = |change with A as majority − change with B as majority|. Malay – Indian: 0.35 → 0.11; "
                         "Indian – Eurasian: 0.20 → 0.14. No gap is statistically reliable.", color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT / "majmin_reversal_gaps.png", dpi=200)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    data = rooms()
    assert all(r["n"] == 6 for r in data.values()) and len(data) == 12
    start_end(data)
    standardised(data)
    reversal(data)
    for key in (("Chinese", "Malay"), ("Indian", "Malay"), ("Eurasian", "Indian")):
        r = data[key]
        print(key, f"change {r['change']:+.2f} end {r['end']:+.2f} std {r['std']:.2f} start {r['start']:+.2f}")
    print("written to", OUT)


if __name__ == "__main__":
    main()
