"""Hand tags for the cutoff-4 forecasts and real events (2026-11-26). Run from research_questions/outputs (python ../tools/haze_capability_tags.py).

Type: COOP-V / COOP-M (cooperation between countries, said / done), CONF-V / CONF-M (conflict between countries or
peoples, said / done: CAMEO puts protest, boycott, reducing relations under done), ENF-V / ENF-M (enforcement against
companies, threatened or intended / done), DOM (domestic protection: masks, schools, relief, firefighting at home).
Actor: G government, P public. Specific: S concrete act (who, what, a number or a named target), Gn general intent.
"""

import pandas as pd

BASELINE = [  # index in haze-forecast-v2-baseline-c4/other_actions.csv -> (type, actor, specific)
    ("DOM", "G", "S"), ("COOP-V", "G", "S"), ("ENF-M", "G", "S"), ("CONF-V", "G", "S"), ("ENF-V", "G", "Gn"),
    ("COOP-V", "G", "Gn"), ("DOM", "G", "S"), ("DOM", "G", "Gn"), ("ENF-M", "P", "S"), ("DOM", "G", "S"),
    ("CONF-V", "P", "S"), ("CONF-V", "G", "S"), ("ENF-M", "G", "S"), ("DOM", "G", "S"), ("ENF-V", "G", "Gn"),
    ("DOM", "G", "S"), ("CONF-V", "G", "S"), ("ENF-M", "G", "S"), ("COOP-V", "G", "S"), ("ENF-M", "P", "S"),
    ("DOM", "P", "S"), ("DOM", "G", "S"), ("COOP-V", "G", "Gn"), ("ENF-M", "G", "S"), ("ENF-M", "G", "S"),
    ("DOM", "G", "S"), ("DOM", "G", "S"), ("CONF-V", "G", "S"), ("COOP-V", "G", "S"), ("COOP-V", "G", "S"),
    ("ENF-M", "P", "Gn"), ("ENF-V", "G", "Gn"), ("CONF-V", "G", "Gn"), ("COOP-V", "G", "Gn"), ("CONF-V", "P", "S"),
    ("DOM", "G", "S"), ("CONF-V", "G", "S"), ("ENF-M", "G", "S"), ("CONF-V", "G", "Gn"), ("DOM", "G", "S"),
    ("DOM", "G", "S"), ("CONF-V", "G", "S"), ("DOM", "G", "S"), ("COOP-V", "G", "S"), ("DOM", "G", "Gn"),
    ("ENF-M", "P", "S"), ("CONF-V", "G", "S"), ("COOP-V", "G", "S"), ("CONF-V", "G", "S"), ("COOP-V", "G", "Gn"),
    ("DOM", "G", "S"), ("CONF-V", "G", "S"), ("CONF-V", "P", "S"), ("ENF-V", "P", "S"), ("DOM", "G", "Gn"),
    ("DOM", "P", "S"), ("CONF-V", "G", "S"), ("COOP-V", "G", "S"), ("DOM", "G", "S"), ("DOM", "G", "S"),
    ("ENF-M", "G", "S"), ("CONF-V", "G", "S"), ("DOM", "G", "Gn"), ("DOM", "G", "S"), ("CONF-V", "G", "Gn"),
    ("CONF-V", "P", "S"), ("ENF-V", "G", "Gn"), ("CONF-V", "G", "S"), ("CONF-V", "G", "S"), ("COOP-V", "G", "S"),
    ("CONF-V", "G", "S"), ("ENF-M", "G", "S"), ("ENF-M", "G", "S"), ("ENF-M", "P", "S"), ("DOM", "G", "S"),
    ("DOM", "G", "S"), ("DOM", "G", "S"), ("CONF-V", "P", "S"), ("CONF-V", "G", "S"), ("DOM", "G", "S"),
    ("DOM", "G", "S"), ("ENF-M", "G", "S"), ("DOM", "G", "S"), ("COOP-V", "G", "S"), ("COOP-M", "G", "S"),
    ("DOM", "G", "S"), ("ENF-M", "P", "S"), ("DOM", "P", "S"), ("COOP-V", "G", "Gn"), ("CONF-V", "G", "S"),
    ("COOP-V", "G", "S"), ("DOM", "G", "S"), ("CONF-M", "P", "S"), ("CONF-V", "G", "S"), ("DOM", "G", "S"),
    ("DOM", "G", "S"), ("DOM", "G", "S"), ("COOP-V", "G", "Gn"), ("DOM", "P", "S"), ("DOM", "G", "S"),
    ("DOM", "G", "S"), ("CONF-V", "G", "S"), ("ENF-V", "G", "Gn"), ("DOM", "G", "S"), ("DOM", "G", "S"),
    ("COOP-V", "G", "S"), ("COOP-V", "G", "S"), ("COOP-V", "G", "Gn"), ("ENF-M", "P", "S"),
]
SOCIETY = [  # index in haze-forecast-v2-society-hs4-c4-a/other_actions.csv
    ("ENF-V", "G", "S"), ("DOM", "G", "S"), ("CONF-V", "G", "S"), ("COOP-V", "G", "S"), ("COOP-V", "G", "S"),
    ("CONF-V", "G", "S"), ("COOP-V", "G", "Gn"), ("ENF-M", "P", "Gn"), ("DOM", "G", "Gn"), ("DOM", "G", "Gn"),
    ("DOM", "G", "Gn"), ("COOP-M", "G", "S"), ("COOP-V", "G", "S"), ("DOM", "G", "S"), ("ENF-V", "G", "Gn"),
    ("ENF-V", "G", "S"), ("ENF-V", "G", "Gn"), ("COOP-M", "G", "S"), ("DOM", "G", "S"), ("COOP-V", "G", "S"),
    ("COOP-V", "G", "S"),
]
TARGETS = {  # real events after 13 Oct: (type, actor, specific, who acts)
    "G1": ("COOP-M", "G", "S", "Indonesia"), "G2": ("ENF-M", "G", "S", "Indonesia"),
    "G3": ("ENF-M", "G", "S", "Singapore"), "G4": ("ENF-M", "G", "S", "Singapore"),
    "G5": ("CONF-V", "G", "S", "Malaysia"), "G6": ("ENF-V", "G", "S", "Malaysia"),
    "G7": ("ENF-V", "G", "S", "Indonesia"), "G8": ("CONF-V", "G", "S", "Indonesia"),
    "G9": ("CONF-V", "G", "S", "Indonesia"), "C1": ("CONF-M", "P", "S", "Malaysia"),
    "C2": ("COOP-V", "P", "S", "Indonesia"),
}

b = pd.read_csv("haze-forecast-v2-baseline-c4/other_actions.csv")
s = pd.read_csv("haze-forecast-v2-society-hs4-c4-a/other_actions.csv")
assert len(b) == len(BASELINE) and len(s) == len(SOCIETY)
b[["type", "actor_t", "spec"]] = BASELINE
s[["type", "actor_t", "spec"]] = SOCIETY

# target hits (yes or partly) count as predicted actions of the target's type; partly is always general
def hits(path, fixes):
    t = pd.read_csv(path)
    for (doc, tg), sc in fixes.items():
        t.loc[(t.doc == doc) & (t.target == tg), "score"] = sc
    t = t[t.score != "no"].copy()
    t["type"] = t.target.map(lambda x: TARGETS[x][0])
    t["actor_t"] = t.target.map(lambda x: TARGETS[x][1])
    t["spec"] = t.score.map(lambda x: "S" if x == "yes" else "Gn")
    t["status"] = "target_" + t.score
    return t[["doc", "type", "actor_t", "spec", "status"]]

bh = hits("haze-forecast-v2-baseline-c4/targets_long.csv", {("B03", "G6"): "partly"})
sh = hits("haze-forecast-v2-society-hs4-c4-a/targets_long.csv", {("F01", "G7"): "partly"})
B = pd.concat([b[["doc", "type", "actor_t", "spec", "status"]], bh])
S = pd.concat([s[["doc", "type", "actor_t", "spec", "status"]], sh])
ndocs = {"baseline": 10, "society": 3}

print("Predicted actions per forecast, by type (all predictions: real, partly real, invented)")
tab = pd.DataFrame({
    "baseline": B.type.value_counts() / 10,
    "society": S.type.value_counts() / 3,
}).fillna(0).round(1)
tab["real events (targets)"] = pd.Series([v[0] for v in TARGETS.values()]).value_counts()
print(tab.fillna(0).to_string())

for name, D in (("baseline", B), ("society", S)):
    n = ndocs[name]
    print(f"\n{name}: share specific {round((D.spec == 'S').mean(), 2)}; "
          f"invented per forecast {round((D.status == 'not_real').sum() / n, 1)}; "
          f"real-or-hit per forecast {round((D.status != 'not_real').sum() / n, 1)}")
    print(" by type: share invented")
    print((D.groupby("type").status.apply(lambda x: round((x == "not_real").mean(), 2))).to_string())
    print(" between-country moves: cooperation vs conflict per forecast:",
          round(D.type.str.startswith("COOP").sum() / n, 1), "vs", round(D.type.str.startswith("CONF").sum() / n, 1))
    print(" enforcement: threatened vs done per forecast:",
          round((D.type == "ENF-V").sum() / n, 1), "vs", round((D.type == "ENF-M").sum() / n, 1),
          "| specific enforcement acts per forecast:", round(((D.type == "ENF-M") & (D.spec == "S")).sum() / n, 1))
    print(" public actions per forecast:", round((D.actor_t == "P").sum() / n, 1))

# who the predicted conflict comes from (baseline): read off the actors
print("\nbaseline CONF actors:", b[b.type.str.startswith("CONF")].actor.str.split().str[:3].str.join(" ").value_counts().to_dict())
print("society CONF actors:", s[s.type.str.startswith("CONF")].actor.to_list())
print("real CONF targets by actor:", {k: v[3] for k, v in TARGETS.items() if v[0].startswith("CONF")})
