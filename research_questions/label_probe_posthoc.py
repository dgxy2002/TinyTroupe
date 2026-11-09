"""POST-HOC breakdown of the label probe. Not part of the pre-set plan.

Questions: is the uses_right result a real label effect or an interaction, is a steady
concedes difference being missed, and is any of it the name rather than the label?
"""
import collections
import glob
import json
import random
from pathlib import Path

base = str(Path(__file__).parent / "outputs" / "label-probe-v1") + "/"
records = [
    json.loads(line)
    for path in glob.glob(base + "records/*.jsonl")
    for line in open(path, encoding="utf-8")
]
codes = json.load(open(base + "reply_codes.json", encoding="utf-8"))
for r in records:
    r.update(codes[r["key"]])
    r["label"] = (r["background"] or "none").replace("Singaporean ", "")
labels = ["Chinese", "Malay", "Indian", "Eurasian"]
labelled = [r for r in records if r["background"]]


def mean(rows, field):
    return sum(r[field] for r in rows) / len(rows) if rows else float("nan")


def pooled_p(rows, field, strata, group, permutations=5000, seed=1):
    """Between-group spread of pooled means, permuting within strata: sees steady shifts."""
    bins = collections.defaultdict(list)
    for r in rows:
        bins[strata(r)].append(r)

    def stat(assign):
        totals = collections.defaultdict(lambda: [0, 0])
        for g, v in assign:
            totals[g][0] += v
            totals[g][1] += 1
        grand = sum(t[0] for t in totals.values()) / sum(t[1] for t in totals.values())
        return sum(t[1] * (t[0] / t[1] - grand) ** 2 for t in totals.values())

    observed = stat([(group(r), r[field]) for r in rows])
    rng = random.Random(seed)
    hits = 0
    for _ in range(permutations):
        assign = []
        for members in bins.values():
            gs = [group(r) for r in members]
            rng.shuffle(gs)
            assign.extend((g, r[field]) for g, r in zip(gs, members))
        hits += stat(assign) >= observed - 1e-12
    return (hits + 1) / (permutations + 1)


print("UPTAKE BY LABEL x NAME TYPE x MOMENT (rule pooled; n=40 per cell)")
for field in ("uses_right", "concedes", "uses_power"):
    print(" ", field)
    for moment in ("A_hears_refusal", "B_hears_demand"):
        for names in ("neutral", "associated"):
            row = {
                l: round(mean([r for r in labelled if r["label"] == l and r["names"] == names and r["moment"] == moment], field), 2)
                for l in labels
            }
            print(f"    {moment:16} {names:10} {row}")
    base_row = {
        m: round(mean([r for r in records if r["label"] == "none" and r["moment"] == m], field), 2)
        for m in ("A_hears_refusal", "B_hears_demand")
    }
    print(f"    no label (n=40 per moment) {base_row}")

print("\nPOOLED TEST: do labels differ steadily? (permuted within moment x rule x names)")
for names_set, title in ((("neutral", "associated"), "all"), (("neutral",), "neutral names only: label alone"), (("associated",), "associated names: label+name")):
    subset = [r for r in labelled if r["names"] in names_set]
    result = {
        f: round(pooled_p(subset, f, lambda r: (r["moment"], r["rule"], r["names"]), lambda r: r["label"]), 4)
        for f in ("uses_interest", "uses_right", "concedes", "uses_power", "conditional_ask")
    }
    print(f"  {title:34} {result}")

print("\nGENDER CODING OF NAME (associated names only, permuted within moment x rule)")
assoc = [r for r in labelled if r["names"] == "associated"]
coded = lambda r: "male" if r["agent_name"] in ("John", "Arjun") else "female"
for f in ("uses_right", "concedes", "uses_power"):
    groups = {g: round(mean([r for r in assoc if coded(r) == g], f), 2) for g in ("male", "female")}
    print(f"  {f:12} {groups} p={pooled_p(assoc, f, lambda r: (r['moment'], r['rule']), coded):.4f}")
print("  same contrast on neutral-name cells, grouping by the label that would carry that name:")
neutral = [r for r in labelled if r["names"] == "neutral"]
would = lambda r: "male" if r["label"] in ("Chinese", "Indian") else "female"
for f in ("uses_right", "concedes", "uses_power"):
    groups = {g: round(mean([r for r in neutral if would(r) == g], f), 2) for g in ("male", "female")}
    print(f"  {f:12} {groups} p={pooled_p(neutral, f, lambda r: (r['moment'], r['rule']), would):.4f}")

print("\nDO THE LABELS CARRY CONTENT? words most distinctive in replies (label-only cells)")
counts = {l: collections.Counter() for l in labels}
for r in neutral:
    counts[r["label"]].update(set(w.strip(".,;:!?\u2014-'\"").lower() for w in r["talk"].split()))
print("  reply overlap: identical replies across all samples:", len(records) - len({r["talk"] for r in records}))
for r in random.Random(3).sample([x for x in labelled if x["moment"] == "A_hears_refusal"], 8):
    print(f"  [{r['label']:8} {r['names'][:5]} rule {r['rule']:3} right={r['uses_right']:d} concede={r['concedes']:d}] {r['talk'][:120]}".encode("ascii", "replace").decode())
