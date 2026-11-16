"""Pick the transcripts for each culture pair. Pairs without Eurasian keep every run that holds them.
Pairs with Eurasian are capped at 35 runs: every one-of-each run first, then the rest in a fixed order
(sound design before flawed, 12 rounds before 8, cultural need before health control, then round-robin
across scenarios in scenario order). Outcomes are never looked at."""
import csv, itertools, re, collections

rows = list(csv.DictReader(open("research_questions/culture_pair_inventory.csv", encoding="utf-8")))
rows = [r for r in rows if not re.search(r"-r12[bc]-", r["folder"])]  # first attempts only
FLAWED = {"2 corner", "4 roster v1", "1 housewarming v1"}
NAMES = {("Chinese", "Malay"): "Chinese - Malay", ("Chinese", "Indian"): "Chinese - Indian",
         ("Indian", "Malay"): "Malay - Indian", ("Chinese", "Eurasian"): "Chinese - Eurasian",
         ("Eurasian", "Malay"): "Malay - Eurasian", ("Eurasian", "Indian"): "Indian - Eurasian"}
PAIRS = list(NAMES)
CAP = 35


def cultures(r):
    return r["AC"].split("/") + [r["D"]]


def has(r, p):
    return any(tuple(sorted(x)) == p for x in itertools.combinations(cultures(r), 2))


def scen_no(r):
    return int(r["scen"].split()[0])


out = []
for p in PAIRS:
    cand = [r for r in rows if has(r, p)]
    if "Eurasian" in p and len(cand) > CAP:
        four = [r for r in cand if len(set(cultures(r))) == 4]
        rest = [r for r in cand if r not in four]
        rest.sort(key=lambda r: (r["scen"] in FLAWED, r["rounds"] != "12", r["need"] == "control", r["need"] == "race test", scen_no(r), r["folder"]))
        # round-robin across scenarios within each tier, so no scenario fills the quota
        tiers = collections.OrderedDict()
        for r in rest:
            tiers.setdefault((r["scen"] in FLAWED, r["rounds"] != "12", r["need"] == "control", r["need"] == "race test"), []).append(r)
        ordered = []
        for tier in tiers.values():
            by = collections.OrderedDict()
            for r in tier:
                by.setdefault(r["scen"], []).append(r)
            while any(by.values()):
                for s in list(by):
                    if by[s]:
                        ordered.append(by[s].pop(0))
        pick = four + ordered[: CAP - len(four)]
    else:
        pick = cand
    for r in pick:
        out.append({"pair": NAMES[p], "folder": r["folder"], "scenario": r["scen"], "cell": r["cell"],
                    "D": r["D"], "A-C": r["AC"], "need": r["need"], "rounds": r["rounds"],
                    "room": "one of each" if len(set(cultures(r))) == 4 else "other",
                    "flawed_design": "yes" if r["scen"] in FLAWED else "no"})
    print(f"{NAMES[p]}: {len(pick)} runs (of {len(cand)})")

path = "research_questions/culture_pair_runs.csv"
w = csv.DictWriter(open(path, "w", newline="", encoding="utf-8"), fieldnames=out[0].keys())
w.writeheader(); w.writerows(out)
print("unique transcripts:", len({o["folder"] for o in out}))
