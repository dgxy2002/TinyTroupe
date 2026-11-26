"""Compare HS6 e2e runs from their judge and coder CSVs (no model calls).

Prints, for public and government mode: real-stage vs wrong-stage overall scores per run, sign tests, and the judge
dimensions per run and by country. With --anger, also anger curves by country and stage and citizen action-code counts.

    python research_questions/tools/haze_hs6_compare.py --runs e2e1 e2e2 e2e3 e2e4 e2e5 [--anger]

Reads outputs/haze-similarity-v2-hs6-<run>-a/-b and outputs/haze-coding-v3-hs6-<run>-a/-b (and HS5's for --anger).
`judge` and `sign` are imported by haze_hs6_summary.py.
"""
import argparse
from math import comb
from pathlib import Path

import pandas as pd

O = Path(__file__).resolve().parents[1] / "outputs"
VAL = {"match": 1.0, "partly": 0.5, "mismatch": 0.0}


def sign(w, l):
    """Two-sided sign test p-value for w wins and l losses (ties dropped)."""
    n = w + l
    k = max(w, l)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n) if n else 1.0


def judge(run, gov):
    """Merge judge passes a and b for one run. Returns (long frame with v = mean of the two passes, pivot of overall)."""
    name = "gov_scores_long.csv" if gov else "scores_long.csv"
    tk = "truth" if gov else "truth_stage"
    a = pd.read_csv(O / f"haze-similarity-v2-hs6-{run}-a" / name)
    b = pd.read_csv(O / f"haze-similarity-v2-hs6-{run}-b" / name)
    a, b = a[a.dimension != "all"], b[b.dimension != "all"]
    m = a.merge(b, on=["stage", "country", "kind", tk, "dimension"], suffixes=("_a", "_b"))
    m["v"] = (m.score_a.map(VAL) + m.score_b.map(VAL)) / 2
    ov = m.drop_duplicates(["stage", "country", "kind"]).copy()
    ov["overall"] = (pd.to_numeric(ov.overall_a) + pd.to_numeric(ov.overall_b)) / 2
    piv = ov.pivot_table(index=["country", "stage"], columns="kind", values="overall").dropna()
    piv["run"] = run
    m["run"] = run
    return m, piv


def compare(runs):
    for gov in (False, True):
        print("=" * 20, "GOVERNMENT" if gov else "PUBLIC")
        ms, ps = zip(*(judge(r, gov) for r in runs))
        P = pd.concat(ps)
        rows = []
        for r, p in P.groupby("run"):
            w, l = int((p.matched > p.control).sum()), int((p.matched < p.control).sum())
            rows.append([r, round(p.matched.mean(), 2), round(p.control.mean(), 2), w, l, len(p) - w - l, round(sign(w, l), 2)])
        A = P.reset_index().groupby(["country", "stage"])[["matched", "control"]].mean()
        w, l = int((A.matched > A.control).sum()), int((A.matched < A.control).sum())
        rows.append(["pairs averaged over runs", round(A.matched.mean(), 2), round(A.control.mean(), 2), w, l, len(A) - w - l,
                     round(sign(w, l), 3)])
        print(pd.DataFrame(rows, columns=["run", "matched", "control", "higher", "lower", "tied", "p"]).to_string(index=False))
        M = pd.concat(ms).dropna(subset=["v"])
        print(M.pivot_table(index="dimension", columns=["kind", "run"], values="v", aggfunc="mean").round(2).to_string())
        mm = M[M.kind == "matched"].pivot_table(index="dimension", columns="run", values="v", aggfunc="mean")
        print("matched: mean across runs / range")
        print(pd.DataFrame({"mean": mm.mean(axis=1).round(2), "min": mm.min(axis=1).round(2),
                            "max": mm.max(axis=1).round(2)}).to_string())
        print("matched by country:")
        print(M[M.kind == "matched"].pivot_table(index="dimension", columns="country", values="v", aggfunc="mean").round(2).to_string())


def anger(runs):
    print("=" * 20, "ANGER (citizens, says, mean of two coder passes)")
    sets = {"hs5": "hs5-e2e1", **{r: f"hs6-{r}" for r in runs}}
    curves = {}
    for k, s in sets.items():
        parts = []
        for p in "ab":
            c = pd.read_csv(O / f"haze-coding-v3-{s}-{p}" / "codes_long.csv")
            c = c[(c.channel == "says") & (~c.role.str.endswith("-G"))]
            c["anger"] = pd.to_numeric(c.anger, errors="coerce")
            parts.append(c.groupby(["country", "stage"]).anger.mean())
        curves[k] = pd.concat(parts, axis=1).mean(axis=1)
    C = pd.DataFrame(curves)
    print(C.round(2).to_string())
    print("correlations:")
    print(C.corr().round(2).to_string())
    print("peak stage by country and run:")
    print(C.groupby(level=0).idxmax().map(lambda x: x[1]).to_string())
    print("=" * 20, "CITIZEN ACTION CODES (says; agent-stage codes, pass a / pass b)")
    cols = ["action_boycott", "rejected_boycott", "action_apologise", "action_demand_apology", "action_protest_or_petition",
            "action_demand_government_action", "blame_indonesian_government", "defends_own_country"]
    out = {}
    for k, s in sets.items():
        vals = []
        for p in "ab":
            c = pd.read_csv(O / f"haze-coding-v3-{s}-{p}" / "codes_long.csv")
            c = c[(c.channel == "says") & (~c.role.str.endswith("-G"))]
            vals.append({col: int(pd.to_numeric(c[col], errors="coerce").fillna(0).astype(bool).sum()) for col in cols})
        out[k] = {col: f"{vals[0][col]}/{vals[1][col]}" for col in cols}
    print(pd.DataFrame(out).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="+", default=["e2e1", "e2e2", "e2e3", "e2e4", "e2e5"])
    ap.add_argument("--anger", action="store_true", help="also print anger curves and citizen action codes")
    args = ap.parse_args()
    compare(args.runs)
    if args.anger:
        anger(args.runs)
