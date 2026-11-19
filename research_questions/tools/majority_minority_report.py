"""Majority/minority report for the scenario 15 rooms (3 housemates of one background + 1 Agent D of another).

Usage (from the repo root):
    python research_questions/tools/majority_minority_report.py <pass-a> <pass-b>

<pass-a> and <pass-b> are folders under research_questions/outputs/ written by pair_agreement.py over the same
transcripts. Scores from the two passes are averaged per pair, then averaged within each run, so every run counts
once. Majority-minority pairs are A-D, B-D and C-D; majority-majority pairs (A-B, A-C, B-C) are the same-culture
baseline. Writes runs.csv (one row per run) into <pass-a> and prints the tables.
"""

import csv
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

REPO = Path(__file__).resolve().parents[2]
NEW = REPO / "research_questions" / "outputs"
OLD = REPO / "research_questions" / "outputs_old"
MIXED = ("A-D", "B-D", "C-D")
SAME = ("A-B", "A-C", "B-C")


def run_folder(folder: str) -> Path:
    return NEW / folder if (NEW / folder / "transcripts").exists() else OLD / folder


def load(pass_dir: Path) -> dict[str, dict]:
    return {json.load(open(p, encoding="utf-8"))["folder"]: json.load(open(p, encoding="utf-8"))
            for p in glob.glob(str(pass_dir / "*.json"))}


def one_run(folder: str, a: dict, b: dict) -> dict:
    cast = a["cast"]
    pairs = {k: {f: mean(float(r["pairs"][k][f]) for r in (a, b)) for f in ("start", "end")} for k in MIXED + SAME}
    moved = defaultdict(int)
    for k in MIXED:
        for r in (a, b):
            m = r["pairs"][k]["moved"]
            moved["D" if m == "D" else "majority" if m in "ABC" and m else m] += 1
    root = run_folder(folder)
    status = json.load(open(glob.glob(str(root / "evaluations" / "*.json"))[0], encoding="utf-8"))["evaluation"]["final_status"]
    answers = json.load(open(glob.glob(str(root / "debriefs" / "*.json"))[0], encoding="utf-8"))["answers"]
    row = {
        "folder": folder,
        "majority": cast["A"]["culture"],
        "minority": cast["D"]["culture"],
        "status": status,
        "D_fairness": answers["D"]["fairness_to_me"],
        "majority_fairness": round(mean(answers[r]["fairness_to_me"] for r in "ABC"), 2),
        # share of the six judgements (3 pairs x 2 passes) naming each mover
        "moved_D": moved["D"] / 6,
        "moved_majority": moved["majority"] / 6,
        "moved_both": moved["both"] / 6,
    }
    for label, keys in (("mixed", MIXED), ("same", SAME)):
        for f in ("start", "end"):
            row[f"{label}_{f}"] = round(mean(pairs[k][f] for k in keys), 3)
        row[f"{label}_change"] = round(row[f"{label}_end"] - row[f"{label}_start"], 3)
    return row


def table(rows: list[dict], key, title: str) -> None:
    groups = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    print(f"\n{title}")
    print(f"{'group':<34}{'runs':>5}{'settled':>9}{'start':>8}{'end':>7}{'change':>8}{'D moved':>9}{'maj moved':>10}{'both':>6}{'fair D/maj':>12}")
    for g in sorted(groups):
        rs = groups[g]
        settled = sum(r["status"] in ("resolved", "partially_resolved") for r in rs)
        print(f"{g:<34}{len(rs):>5}{settled:>6}/{len(rs):<2}{mean(r['mixed_start'] for r in rs):>+8.2f}{mean(r['mixed_end'] for r in rs):>+7.2f}"
              f"{mean(r['mixed_change'] for r in rs):>+8.2f}{mean(r['moved_D'] for r in rs):>9.2f}{mean(r['moved_majority'] for r in rs):>10.2f}"
              f"{mean(r['moved_both'] for r in rs):>6.2f}{mean(r['D_fairness'] for r in rs):>7.1f}/{mean(r['majority_fairness'] for r in rs):.1f}")


def main() -> None:
    pass_a, pass_b = (NEW / p for p in sys.argv[1:3])
    a, b = load(pass_a), load(pass_b)
    rows = [one_run(f, a[f], b[f]) for f in sorted(set(a) & set(b))]
    with open(pass_a / "runs.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} runs; scores are majority-minority pairs averaged within each run")
    table(rows, lambda r: f"3 {r['majority']} + 1 {r['minority']}", "By room (majority + minority D)")
    table(rows, lambda r: f"D is {r['minority']}", "By the minority D's culture (same D, all rooms)")
    table(rows, lambda r: f"majority {r['majority']}", "By the majority's culture")
    table(rows, lambda r: " - ".join(sorted((r["majority"], r["minority"]))), "By culture pair, both directions pooled")
    print("\nSame-culture baseline (majority-majority pairs), by majority")
    for m in sorted({r["majority"] for r in rows}):
        rs = [r for r in rows if r["majority"] == m]
        print(f"  {m} - {m:<10} runs {len(rs):>2}  start {mean(r['same_start'] for r in rs):+.2f}  end {mean(r['same_end'] for r in rs):+.2f}")


if __name__ == "__main__":
    main()
