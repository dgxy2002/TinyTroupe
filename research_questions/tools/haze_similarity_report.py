"""Summarise two passes of tools/haze_similarity_judge.py (2026-11-26). No model calls.

Usage (from the repo root):
    python research_questions/tools/haze_similarity_report.py <pass-a folder> <pass-b folder> [--government]

Prints: agreement between passes; overall similarity (0-10, mean of the passes) for matched stages vs the wrong-stage
control, with a two-sided sign test over stage-country pairs; dimension scores (match 1, partly 0.5, mismatch 0;
no_data left out) for matched vs control, overall and by country.
"""

from __future__ import annotations

import argparse
from math import comb
from pathlib import Path

import pandas as pd

OUTPUTS = Path(__file__).resolve().parents[2] / "research_questions" / "outputs"
VALUE = {"match": 1.0, "partly": 0.5, "mismatch": 0.0}


def sign_test(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    k = max(wins, losses)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--government", action="store_true", help="summarise gov_scores_long.csv instead")
    args = p.parse_args()
    name = "gov_scores_long.csv" if args.government else "scores_long.csv"
    key_truth = "truth" if args.government else "truth_stage"
    a = pd.read_csv(OUTPUTS / args.a / name)
    b = pd.read_csv(OUTPUTS / args.b / name)
    a, b = a[a.dimension != "all"], b[b.dimension != "all"]
    keys = ["stage", "country", "kind", key_truth, "dimension"]
    m = a.merge(b, on=keys, suffixes=("_a", "_b"))
    print(f"pairs of scores: {len(m)}; passes agree exactly on {(m.score_a == m.score_b).mean():.2f}")
    ov = m.drop_duplicates(["stage", "country", "kind"]).copy()
    ov["overall"] = (pd.to_numeric(ov.overall_a) + pd.to_numeric(ov.overall_b)) / 2
    print(f"overall gap between passes: mean {(pd.to_numeric(ov.overall_a) - pd.to_numeric(ov.overall_b)).abs().mean():.2f}")
    piv = ov.pivot_table(index=["country", "stage"], columns="kind", values="overall")
    print(piv.round(1).to_string())
    print("mean overall:", ov.groupby("kind").overall.mean().round(2).to_dict())
    if {"matched", "control"} <= set(piv.columns):
        pp = piv.dropna()
        w, l = int((pp.matched > pp.control).sum()), int((pp.matched < pp.control).sum())
        print(f"paired {len(pp)}: matched higher {w}, lower {l}, tied {len(pp) - w - l}; "
              f"mean difference {(pp.matched - pp.control).mean():.2f}; sign test p = {sign_test(w, l):.2f}")
    m["v"] = (m.score_a.map(VALUE) + m.score_b.map(VALUE)) / 2
    d = m.dropna(subset=["v"])
    print(d.pivot_table(index="dimension", columns="kind", values="v", aggfunc="mean").round(2).to_string())
    print("matched, by country:")
    print(d[d.kind == "matched"].pivot_table(index="dimension", columns="country", values="v", aggfunc="mean")
          .round(2).to_string())


if __name__ == "__main__":
    main()
