"""Culture-pair agreement for the one-of-each rotation rooms (S125-S153).

Usage (from the repo root):
    python research_questions/tools/rotation_report.py rotation-sonnet-a rotation-sonnet-b

Every rotation room has one agent of each culture, so each run gives exactly one agent pair for each of the six
culture pairs. The two scoring passes are averaged per pair. Writes pairs_long.csv into the first pass folder and
prints: the culture-pair table (start, end, change, standardised change), the same split by whether the pair
includes the need-holder D, the gap between each culture pair and its own room's average, and a permutation test
that shuffles which culture sits in which seat within each run (roles stay fixed), so a culture effect has to beat
the role and run structure. No API calls.
"""

import csv
import itertools
import json
import random
import statistics
import sys
from pathlib import Path

OUTPUTS = Path(__file__).resolve().parents[1] / "outputs"
PAIRS = ["Chinese - Malay", "Chinese - Indian", "Malay - Indian", "Chinese - Eurasian", "Malay - Eurasian", "Indian - Eurasian"]


def pair_name(a: str, b: str) -> str:
    for name in PAIRS:
        if set(name.split(" - ")) == {a, b}:
            return name
    raise KeyError((a, b))


def load(pass_dirs):
    runs = {}
    for directory in pass_dirs:
        for path in sorted((OUTPUTS / directory).glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            run = runs.setdefault(data["folder"], {"cast": data["cast"], "pairs": {}})
            for roles, value in data["pairs"].items():
                run["pairs"].setdefault(roles, []).append(value)
    return runs


def main() -> None:
    pass_dirs = sys.argv[1:]
    runs = load(pass_dirs)
    rows = []
    for folder, run in runs.items():
        cast = run["cast"]
        for roles, values in run["pairs"].items():
            a, b = roles.split("-")
            start = statistics.mean(v["start"] for v in values)
            end = statistics.mean(v["end"] for v in values)
            rows.append({
                "folder": folder,
                "roles": roles,
                "culture_pair": pair_name(cast[a]["culture"], cast[b]["culture"]),
                "includes_D": "D" in roles,
                "D_culture": cast["D"]["culture"],
                "start": round(start, 3),
                "end": round(end, 3),
                "change": round(end - start, 3),
                "standardised_change": round((end - start) / (1 - start), 3) if start < 1 else 0.0,
                "moved_pass_a": values[0]["moved"],
                "moved_pass_b": values[-1]["moved"],
                "passes": len(values),
            })
    with (OUTPUTS / pass_dirs[0] / "pairs_long.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    def table(subset, label):
        print(f"\n{label}")
        print(f"{'pair':20} {'n':>3} {'start':>7} {'end':>7} {'change':>7} {'std chg':>8}")
        for name in PAIRS:
            group = [r for r in subset if r["culture_pair"] == name]
            if group:
                print(f"{name:20} {len(group):3} {statistics.mean(r['start'] for r in group):+7.2f} "
                      f"{statistics.mean(r['end'] for r in group):+7.2f} {statistics.mean(r['change'] for r in group):+7.2f} "
                      f"{statistics.mean(r['standardised_change'] for r in group):8.2f}")

    print(f"{len(runs)} runs, {len(rows)} agent pairs, passes: {pass_dirs}")
    gaps = [abs(a["start"] - b["start"]) for r in [runs[f]["pairs"] for f in runs] for a, b in [vals for vals in r.values() if len(vals) == 2]]
    print(f"mean gap between passes on start: {statistics.mean(gaps):.3f}")
    table(rows, "All pairs (each run gives one of each culture pair)")
    table([r for r in rows if r["includes_D"]], "Pairs that include the need-holder D")
    table([r for r in rows if not r["includes_D"]], "Pairs without D")

    # Gap between each culture pair and its own room's average (same conversation, so run effects cancel).
    by_run = {}
    for r in rows:
        by_run.setdefault(r["folder"], []).append(r)
    print("\nGap from own room's average (end and change)")
    for name in PAIRS:
        end_gaps, chg_gaps = [], []
        for group in by_run.values():
            mean_end = statistics.mean(x["end"] for x in group)
            mean_chg = statistics.mean(x["change"] for x in group)
            target = next(x for x in group if x["culture_pair"] == name)
            end_gaps.append(target["end"] - mean_end)
            chg_gaps.append(target["change"] - mean_chg)
        print(f"{name:20} end {statistics.mean(end_gaps):+.2f}   change {statistics.mean(chg_gaps):+.2f}")

    # Permutation test: shuffle the four culture labels across the four seats within each run.
    def spread(assignments, key):
        sums = {name: [] for name in PAIRS}
        for folder, group in by_run.items():
            cultures = assignments[folder]
            for x in group:
                a, b = x["roles"].split("-")
                sums[pair_name(cultures[a], cultures[b])].append(x[key])
        means = [statistics.mean(v) for v in sums.values()]
        grand = statistics.mean(means)
        return sum((m - grand) ** 2 for m in means)

    real = {folder: {role: run["cast"][role]["culture"] for role in "ABCD"} for folder, run in runs.items()}
    random.seed(7)
    print("\nPermutation test (cultures shuffled across seats within each run, 10000 shuffles)")
    for key in ("start", "end", "change"):
        observed = spread(real, key)
        hits = 0
        for _ in range(10000):
            shuffled = {}
            for folder, cultures in real.items():
                labels = list(cultures.values())
                random.shuffle(labels)
                shuffled[folder] = dict(zip("ABCD", labels))
            hits += spread(shuffled, key) >= observed
        print(f"  {key:7} p = {hits / 10000:.3f}")


if __name__ == "__main__":
    main()
