"""Inventory of type-3 case transcripts in outputs_old: D culture, A-C cultures, need, rounds, status.
Writes research_questions/culture_pair_inventory.csv. Run from the repo root."""
import glob, json, os, re, collections, csv, sys
ROOT = "research_questions/outputs_old"
CONTROLS = {"S37","S39","S41","S45","S49","S54","S58","S62","S66","S70","S74","S78","S81","S85","S89","S93","S97","S101"}
SCEN = {}
for lo, hi, name in [(36,41,"0 pan/incense"),(42,45,"1 housewarming v1"),(46,50,"1 housewarming v2"),(51,54,"3 rota"),
                     (55,58,"7 bereavement"),(59,62,"2 corner"),(63,66,"4 roster v1"),(67,70,"4 roster v2"),(71,74,"5 lunch"),
                     (75,78,"6 uniform"),(79,81,"8 wake"),(82,85,"10 language"),(86,89,"11 noise"),(90,93,"12 slot"),
                     (94,97,"13 room"),(98,101,"15 smells")]:
    for i in range(lo, hi + 1): SCEN[f"S{i}"] = name
rows = []
for path in sorted(glob.glob(ROOT + "/*/transcripts/*.json")):
    folder = path.replace("\\", "/").split("/")[-3]
    d = json.loads(open(path, encoding="utf-8").read(), strict=False)
    sid = d["run"]["scenario_id"]; n = int(sid[1:])
    if n < 36: continue
    ag = d["scenario"]["agents"]
    bio = ag["D"].get("biography", "")
    faith = (re.findall(r"You are (Muslim|Hindu|Buddhist|Catholic|Christian|Taoist)", bio) or ["none"])[0]
    ev = glob.glob(f"{ROOT}/{folder}/evaluations/{os.path.basename(path)}")
    status = json.load(open(ev[0], encoding="utf-8"))["evaluation"]["final_status"] if ev else "no-eval"
    k = d["run"]["configuration_id"]
    cast_type = "rotating K" if k.startswith("K") else "fixed"
    rounds = d["run"]["rounds"]
    need = "control" if sid in CONTROLS else ("culture (no faith)" if n >= 98 else ("race test" if k.startswith("HX") else "faith"))
    if n in range(82, 86): need = "language (D fixed Eurasian)"
    rows.append(dict(folder=folder, sid=sid, scen=SCEN[sid], cell=k, D=ag["D"]["cultural_background"], Dname=ag["D"]["display_name"],
                     Dfaith=faith, AC="/".join(ag[r]["cultural_background"] for r in "ABC"), need=need, cast=cast_type,
                     rounds=rounds, status=status))
w = csv.DictWriter(open("research_questions/culture_pair_inventory.csv", "w", newline="", encoding="utf-8"), fieldnames=rows[0].keys())
w.writeheader(); w.writerows(rows)
print("type-3 transcripts:", len(rows))
c = collections.Counter((r["need"], r["D"], r["Dfaith"]) for r in rows)
for k_, v in sorted(c.items()): print(v, k_)
print("--- by scenario, faith/culture runs, D culture")
s = collections.defaultdict(collections.Counter)
for r in rows: s[r["scen"]][(r["need"][:7], r["D"])] += 1
for k_ in sorted(s, key=lambda x: int(x.split()[0])): print(k_, dict(s[k_]))
print("--- status by need/D")
c = collections.Counter((r["need"], r["D"], r["status"]) for r in rows)
for k_, v in sorted(c.items()): print(v, k_)
print("--- flags: rounds!=12", sum(r["rounds"] != 12 for r in rows), "rotating", sum(r["cast"] != "fixed" for r in rows))
