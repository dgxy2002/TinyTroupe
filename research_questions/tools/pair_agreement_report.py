"""Summarise pair-agreement scores by culture pair.

Usage (from the repo root):
    python research_questions/tools/pair_agreement_report.py pair-agreement-v2-sonnet-a pair-agreement-v2-sonnet-b

Averages start and end across the passes given. "moved" is taken from the first pass when passes disagree is
counted separately. Only transcripts that culture_pair_runs.csv selects for a culture pair count towards it.
Writes research_questions/outputs/<first pass>/pairs_long.csv (one row per pair of agents) and prints tables.
"""

import csv
import glob
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "research_questions" / "outputs"
NAMES = {
    frozenset(["Chinese", "Malay"]): "Chinese - Malay",
    frozenset(["Chinese", "Indian"]): "Chinese - Indian",
    frozenset(["Indian", "Malay"]): "Malay - Indian",
    frozenset(["Chinese", "Eurasian"]): "Chinese - Eurasian",
    frozenset(["Eurasian", "Malay"]): "Malay - Eurasian",
    frozenset(["Eurasian", "Indian"]): "Indian - Eurasian",
}
ORDER = list(NAMES.values())


def main() -> None:
    passes = sys.argv[1:]
    selected = defaultdict(set)
    meta = {}
    for r in csv.DictReader(open(REPO / "research_questions" / "culture_pair_runs.csv", encoding="utf-8")):
        selected[r["pair"]].add(r["folder"])
        meta[r["folder"]] = r
    records = defaultdict(list)  # (folder, roles) -> list of pair dicts across passes
    for p in passes:
        for path in glob.glob(str(OUT / p / "*.json")):
            rec = json.load(open(path, encoding="utf-8"))
            for roles, s in rec["pairs"].items():
                s = dict(s, cast=rec["cast"])
                records[(rec["folder"], roles)].append(s)
    rows = []
    for (folder, roles), ss in records.items():
        a, b = roles.split("-")
        ca, cb = ss[0]["cast"][a]["culture"], ss[0]["cast"][b]["culture"]
        name = NAMES.get(frozenset([ca, cb]))
        if name is None or folder not in selected[name]:
            continue
        moved = [s["moved"] for s in ss]
        # translate role letters in "moved" into cultures
        def who(m):
            return {a: ca, b: cb}.get(m, m)
        rows.append({
            "culture_pair": name, "folder": folder, "roles": roles, "culture_a": ca, "culture_b": cb,
            "includes_D": "D" in (a, b), "D_culture": ss[0]["cast"]["D"]["culture"],
            "need": meta[folder]["need"], "scenario": meta[folder]["scenario"],
            "start": round(statistics.mean(float(s["start"]) for s in ss), 3),
            "end": round(statistics.mean(float(s["end"]) for s in ss), 3),
            "engaged": all(s["engaged"] for s in ss),
            "moved": who(moved[0]), "moved_agree": len(set(moved)) == 1,
            "start_gap": round(max(float(s["start"]) for s in ss) - min(float(s["start"]) for s in ss), 3),
            "end_gap": round(max(float(s["end"]) for s in ss) - min(float(s["end"]) for s in ss), 3),
        })
    for r in rows:
        r["change"] = round(r["end"] - r["start"], 3)
    path = OUT / passes[0] / "pairs_long.csv"
    w = csv.DictWriter(open(path, "w", newline="", encoding="utf-8"), fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

    def table(title, keep):
        print(f"\n## {title}\n")
        print("| Culture pair | Pairs | Runs | Start | End | Change | Moved (first / second / both / neither) |")
        print("|---|---|---|---|---|---|---|")
        for name in ORDER:
            rr = [r for r in rows if r["culture_pair"] == name and keep(r)]
            if not rr:
                continue
            c1, c2 = name.split(" - ")
            m = Counter(r["moved"] for r in rr)
            print(f"| {name} | {len(rr)} | {len({r['folder'] for r in rr})} | {statistics.mean(r['start'] for r in rr):+.2f} | "
                  f"{statistics.mean(r['end'] for r in rr):+.2f} | {statistics.mean(r['change'] for r in rr):+.2f} | "
                  f"{c1} {m[c1]} / {c2} {m[c2]} / both {m['both']} / neither {m['neither']} |")

    table("All pairs", lambda r: True)
    table("Pairs that include D (one of the two holds the need)", lambda r: r["includes_D"])
    table("Pairs among A-C only", lambda r: not r["includes_D"])
    table("Engaged pairs only (spoke to each other in both passes)", lambda r: r["engaged"])
    table("Cultural need runs only (no health controls)", lambda r: r["need"] != "control")
    print(f"\nPass agreement: mean start gap {statistics.mean(r['start_gap'] for r in rows):.2f}, "
          f"mean end gap {statistics.mean(r['end_gap'] for r in rows):.2f}, "
          f"'moved' same in {sum(r['moved_agree'] for r in rows)} of {len(rows)} pairs")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
