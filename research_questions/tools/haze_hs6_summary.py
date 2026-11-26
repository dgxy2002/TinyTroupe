"""Write haze_hs6_results_summary.md: HS6 e2e runs against what really happened, in seven simple dimensions.

Each dimension is the equal-weight average of the judge (haze-similarity-v2) dimensions it covers, set after seeing the
results (user, 2026-11-27); Moves also averages in two hand scores. No model calls: reads the judge CSVs in outputs/ and
the hand scores in research_questions/haze_hs6_hand_scores.json. The quotes and comparison texts below were written
after reading every transcript; check them again when runs are added.

    python research_questions/tools/haze_hs6_summary.py --runs e2e1 e2e2 e2e3 e2e4 e2e5
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from haze_hs6_compare import judge, sign  # noqa: E402

RQ = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--runs", nargs="+", default=["e2e1", "e2e2", "e2e3", "e2e4", "e2e5"])
ap.add_argument("--hand", default=str(RQ / "haze_hs6_hand_scores.json"))
ap.add_argument("--out", default=str(RQ / "haze_hs6_results_summary.md"))
args = ap.parse_args()
RUNS = args.runs

HANDS = json.loads(Path(args.hand).read_text(encoding="utf-8"))
COOP = [HANDS["cooperation"][r] for r in RUNS]
CONF = [HANDS["conflict"][r] for r in RUNS]
ECHO = HANDS["echo_percent"]
NR = len(RUNS)
WORD = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}[NR]
fmt = lambda xs: ", ".join(f"{x:g}" for x in xs)

JDEF = {
    "emotion": "the emotions and tone expressed (anger, mockery, shame, frustration, fear, solidarity, resignation...)",
    "triggers": "which events or statements they react to most (and which they ignore)",
    "blame": "whom they hold responsible (Indonesian government, their own government, companies, nature, nobody)",
    "framing": "how they frame the crisis (nature vs human cause, companies vs governments, national pride, ordinary people suffer)",
    "division": "whether they turn against their OWN government (blame it, distrust it, are ashamed of it)",
    "stance": "how they treat other countries' governments and people (hostile, critical, neutral, solidary)",
    "actions": "what they do or say they will do (boycott, protest, lawsuit, apology, online campaign, nothing)",
    "demands": "what they ask for (apology, naming companies, emergency, compensation, legal action, aid)",
    "tone": "is the simulated government's stance towards the other governments (cooperative, defensive, confrontational) like the real one's?",
    "specificity": "does the simulated government name concrete acts (notices, numbers, named measures) the way the real one does, or stay vague?",
    "anticipation": "does the simulated government signal, propose, plan or argue for any of its real next moves before they happen?",
    "cooperation": "hand-scored by me: 1 if simulated Indonesia did not take up help before mid-October, as in reality; 0 if it accepted early",
    "conflict": "hand-scored by me: average of (a) Indonesia objects to Singapore's legal action in words, 1/0, and (b) it takes or threatens a concrete counter-measure such as the gas cut, 1/0",
}

# name, question, parts, simulated, real, how they compare
PEOPLE = [
    ("Feel", "How upset are they, and what news sets them off?", ["emotion", "triggers"],
     "\"Sending oxygen? Is that what you call this? I had a tour business. It's gone. ... This is our lives you're burning.\" (Lim Chee Keong, Malaysia, run 2, 13 Oct)",
     "\"Supply oxygen? Seriously?\" and \"How do you quantify O2? But we can definitely quantify haze.\" (Malaysian netizens, after the 10 Oct remark); \"We're truly sorry for the haze.\" (Jakarta doctor, Threads)",
     "Same anger and shame, at the same flashpoint (the \"oxygen\" remark). Real Malaysians also mocked; agents rarely did."),
    ("Blame", "Who or what do they say caused it, including their own government?", ["blame", "framing", "division"],
     "\"It's not 'nature', it's smoke from fires and it's making our families sick.\" (Kelvin Tan, Singapore, run 2); \"Please don't think that our government speaks for us.\" (Dewi Lestari, Indonesia, run 2)",
     "\"They are trying to disguise environmental and corporate crimes behind natural causes\" (Walhi, Indonesian NGO); \"The Indonesian (government) needs to do the right thing\" (Malaysian tour operator); \"Haze & Prabowo's Regime = National Disaster.\" (Greenpeace activists, Jakarta)",
     "Both say people and companies caused it, not nature. Real people named governments more, and real Indonesians protested against and sued their own government; agents were only embarrassed by one official."),
    ("Others", "Are they friendly or hostile towards the other countries?", ["stance"],
     "\"My anger is not with you, it is with the companies who are burning and the governments that let them get away with it, year after year.\" (Kelvin Tan, Singapore, to the Indonesians, run 3)",
     "Friendly: Indonesians apologising, \"SEAblings\". Hostile: \"If we don't teach them a lesson, they won't stop\" (KL boycotter of Indonesian products); \"treat them as an outcast in the region\" (MP Syed Saddiq)",
     "The friendly side matches; the hostile side (boycotting Indonesia, \"outcast\") never appears, and it is most of the real Malaysian record."),
    ("Act", "What do they do, and what do they demand?", ["actions", "demands"],
     "\"A boycott will only hurt us, the small people, the most.\" (Budi Santoso, Indonesia, run 3); \"We need financial assistance. What help is there for small businesses like mine?\" (Lim Chee Keong, run 2)",
     "Malaysians boycotted Indonesian brands; Indonesians protested and filed a class action in Pontianak; \"Stop making excuses and apologise\" (Johor Pakatan Harapan)",
     "Agents only talk and ask for money (run 5 backed a boycott, then dropped it a week later over workers' jobs); real people boycotted, marched, sued and demanded apologies."),
]
GOVS = [
    ("Tone", "Are they friendly or hostile towards each other?", ["tone"],
     "\"Talk is no longer sufficient. We demand immediate enforcement.\" (Singapore, run 3, 9 Oct)",
     "\"Do not lecture us, especially the energy ministry, on the importance of honoring contracts.\" (Indonesia's energy minister, 26 Oct)",
     "Both mostly diplomatic, so this scores well. When real Indonesia turned hostile, the simulated one stayed polite; the sharpest simulated words came from Malaysia (run 5), whose real government stayed restrained."),
    ("Foresight", "Does their talk point to what they really did next?", ["anticipation"],
     "\"we must express our serious concern regarding the legal notices issued to Indonesian companies by Singapore. This unilateral measure is not helpful\" (Indonesia, run 2, 16 Oct)",
     "21 Oct, Indonesia rebukes countries that \"like to insult\" it: \"Indonesia will not tolerate being continually provoked.\"",
     f"Right direction in 2 of {NR} runs (Indonesia objects to Singapore); no run foresaw the energy threat or the gas cut."),
    ("Moves", "What concrete steps do they take (help, push-back, measures)?", ["specificity", "cooperation", "conflict"],
     "\"We propose to hold the technical meeting this Wednesday, 28 October, at 10:00 Jakarta time.\" (Indonesia, run 3); \"Indonesia formally accepts Malaysia's generous offer of firefighting assets and personnel.\" (Indonesia, run 3, 18 Sep)",
     "Indonesia held off on help until 15 Oct, then said on 19 Oct it could manage alone; energy-export threat (22 Oct); gas to Singapore cut by about 8% (24 Oct); Singapore's notices to 10 companies; 17 concessions revoked",
     f"Simulated governments act through meetings and dates. Indonesia accepted help early ({COOP.count(0)} of {NR} runs) and pushed back only in words ({sum(1 for c in CONF if c > 0)} of {NR}); no run produced the gas cut, fines or revoked licences."),
]
HAND = {"cooperation", "conflict"}
LABEL = {"emotion": "emotion", "triggers": "triggers", "blame": "blame", "framing": "framing", "division": "division within a country",
         "stance": "stance between publics", "actions": "public actions", "demands": "demands", "tone": "tone",
         "specificity": "specificity", "anticipation": "anticipation", "diversity": "diversity of views", "cooperation": "government cooperation", "conflict": "conflict"}

# ---- data
data, agree, signs = {}, [], {}
for gov in (False, True):
    ms, ps = zip(*(judge(r, gov) for r in RUNS))
    agree += [float((m.score_a == m.score_b).mean()) for m in ms]
    A = pd.concat(ps).reset_index().groupby(["country", "stage"])[["matched", "control"]].mean()
    w, l = int((A.matched > A.control).sum()), int((A.matched < A.control).sum())
    signs[gov] = (len(A), w, l, len(A) - w - l, sign(w, l))
    M = pd.concat(ms).dropna(subset=["v"])
    mm = M[M.kind == "matched"].groupby(["run", "dimension"]).v.mean().unstack()
    cc = M[M.kind == "control"].groupby(["run", "dimension"]).v.mean().unstack()
    byc = M[M.kind == "matched"].groupby(["dimension", "country", "run"]).v.mean().groupby(["dimension", "country"]).mean()
    n = M[M.kind == "matched"].groupby(["dimension", "country"]).v.size()
    data[gov] = dict(mm=mm, cc=cc, byc=byc, n=n, P=pd.concat(ps))
data[True]["mm"]["cooperation"] = pd.Series(COOP, index=RUNS)
data[True]["mm"]["conflict"] = pd.Series(CONF, index=RUNS)

def score(gov, parts):
    mm = data[gov]["mm"]
    return sum(mm[k].mean() for k in parts) / len(parts)

c = lambda x: x.replace("|", "/")
HDR = "| Dimension | Exact definition | Simulated | Real | How they compare | How close to real (0-1) |\n|---|---|---|---|---|---|"

def main_table(gov, dims):
    rows = [HDR]
    for name, q, parts, sim, real, cmp_ in sorted(dims, key=lambda d: -score(gov, d[2])):
        made = "<br>".join(f"*{LABEL[k]}* ({data[gov]['mm'][k].mean():.2f}{', hand' if k in HAND else ''}): {JDEF[k]}" for k in parts)
        rows.append(f"| **{name}** | {c(q)}<br>{c(made)} | {c(sim)} | {c(real)} | {c(cmp_)} | **{score(gov, parts):.2f}** |")
    return "\n".join(rows)

def country_table(gov, dims):
    byc, n = data[gov]["byc"], data[gov]["n"]
    rows = [f"| Dimension | Indonesia | Malaysia | Singapore | All {WORD} |", "|---|---|---|---|---|"]
    for name, q, parts, *_ in sorted(dims, key=lambda d: -score(gov, d[2])):
        jparts = [k for k in parts if k not in HAND]
        cells = []
        for ctry in ["ID", "MY", "SG"]:
            have = [k for k in jparts if (k, ctry) in byc.index]
            cells.append(f"{sum(byc[(k, ctry)] for k in have) / len(have):.2f} ({sum(n[(k, ctry)] for k in have)})" if have else "no data")
        allv = sum(data[gov]["mm"][k].mean() for k in jparts) / len(jparts)
        label = name + (" (specificity only)" if jparts != parts else "")
        rows.append(f"| {label} | " + " | ".join(cells) + f" | {allv:.2f} |")
    return "\n".join(rows)

def run_table(gov, dims):
    mm, cc, P = data[gov]["mm"], data[gov]["cc"], data[gov]["P"]
    ds = sorted(dims, key=lambda d: -score(gov, d[2]))
    jp = [[k for k in d[2] if k not in HAND] for d in ds]
    names = [d[0] + (" (specificity only)" if len(j) != len(d[2]) else "") for d, j in zip(ds, jp)]
    rows = ["| | " + " | ".join(names) + " | Overall (0-10) |", "|---" * (len(ds) + 2) + "|"]
    avg = lambda t, r, ks: sum(t.loc[r, k] for k in ks) / len(ks)
    for i, r in enumerate(RUNS, 1):
        p = P[P.run == r]
        rows.append(f"| Run {i}, real stage | " + " | ".join(f"{avg(mm, r, j):.2f}" for j in jp) + f" | {p.matched.mean():.2f} |")
        rows.append(f"| Run {i}, wrong stage | " + " | ".join(f"{avg(cc, r, j):.2f}" for j in jp) + f" | {p.control.mean():.2f} |")
    rows.append("| **Mean, real stage** | " + " | ".join(f"**{sum(mm[k].mean() for k in j) / len(j):.2f}**" for j in jp) + f" | **{P.matched.mean():.2f}** |")
    rows.append("| Mean, wrong stage | " + " | ".join(f"{sum(cc[k].mean() for k in j) / len(j):.2f}" for j in jp) + f" | {P.control.mean():.2f} |")
    return "\n".join(rows)

def old_table():
    rows = ["| Who | Old dimension | Real stage | Wrong stage | Goes into |", "|---|---|---|---|---|"]
    into = {k: d[0] for d in PEOPLE + GOVS for k in d[2]}
    for gov, who in ((False, "People"), (True, "Governments")):
        mm, cc = data[gov]["mm"], data[gov]["cc"]
        for k in mm.mean().sort_values(ascending=False).index:
            ctrl = f"{cc[k].mean():.2f}" if k in cc else "none (hand)"
            rows.append(f"| {who} | {LABEL[k]} | {mm[k].mean():.2f} | {ctrl} | {into.get(k, 'left out (simulator property)')} |")
    return "\n".join(rows)

seven = {d[0]: score(False, d[2]) for d in PEOPLE} | {d[0]: score(True, d[2]) for d in GOVS}
div = data[False]["mm"]["diversity"].mean()
echo = [ECHO[r] for r in RUNS]

doc = f"""# HS6 results summary: {WORD} runs against what really happened (2026-11-27)

{WORD.capitalize()} full-timeline runs of the same design (HS6: 13 agents, real news and real government statements fed in eight
stages from 4 Sep to 16 Nov 2026; governments also talk privately). Backbone Gemini 2.5 Pro via OpenRouter, no web
access. Runs: `outputs/society-hs6-{RUNS[0]}` to `-{RUNS[-1]}`. Details in `haze_society_design.md` sections 14-16.

Results are given in seven simple dimensions: four for ordinary people (Feel, Blame, Others, Act) and three for
governments (Tone, Foresight, Moves).

## How to read the table

- **How close to real (0-1).** An outside LLM judge (Claude Sonnet 5.5, rubric `haze-similarity-v2`,
  `tools/haze_similarity_judge.py`) reads, for each run, stage and country, what the simulated citizens said aloud and
  the real reactions recorded for that stage and country, and rates each of its own dimensions: match 1, partly 0.5,
  mismatch 0, or no data (left out). Each judgement is made twice independently (the two passes agree
  {min(agree)*100:.0f}-{max(agree)*100:.0f}% of the time). Governments are judged the same way, comparing each government's private
  diplomatic talk with what it really did in the following days.
- **The seven dimensions** were set after the runs and are not separate judge scores. Each is the plain average of the
  judge's dimensions it covers, averaged over stages, countries and the {WORD} runs. The definition column lists those
  parts with their own scores and the exact wording the judge was given.
- **Moves** also contains two hand scores (government cooperation and conflict), which I scored from the transcripts,
  one per run. They are rougher than the judge scores.
- **Real** is real reactions by people and governments, from news reports and social media (`haze_ground_truth_*.csv`),
  not the news fed to the agents, which both sides share.
- **Coverage.** People rows cover Malaysia, Indonesia and Singapore (Brunei has no real record; Singapore's is thin).
- Quotes are examples; the numbers come from all stages. Rows are sorted by how close to real, highest first.

## Results

### People

{main_table(False, PEOPLE)}

### Governments

{main_table(True, GOVS)}

**Left out: how much people disagree.** The judge's "diversity of views" (whether people of one country disagree or all
say the same) scores {div:.2f}. It is reported as a property of the simulator rather than a dimension: agents agree with
each other too much ({min(echo)}-{max(echo)}% of citizen lines open by agreeing, "Yes", "Exactly", "Same here"), while real
people argued, for example over whether to boycott.

**Overall closeness (judge's own 0-10 rating, {NR}-run mean):** people {data[False]['P'].matched.mean():.2f}, governments {data[True]['P'].matched.mean():.2f}.

## By country

How close to real (0-1) for each country, averaged over the {WORD} runs. In brackets: how many judge scores the average
rests on (one per dimension part and stage with real data, per run). Averages resting on fewer than 7 scores are
shaky. Brunei has no real record. Moves by country uses its judge part (specificity) only, because the hand scores were
not given by country.

**People**

{country_table(False, PEOPLE)}

**Governments**

{country_table(True, GOVS)}

## In one paragraph

Across {WORD} runs, the simulated society reproduces how people feel and what sets them off (Feel {seven['Feel']:.2f}), and
partly whom they blame ({seven['Blame']:.2f}) and how they treat other countries ({seven['Others']:.2f}, the friendly side
only). It does not reproduce what people did or demanded (Act {seven['Act']:.2f}: no boycott beyond talk, no protests, class
action or apology demands). Governments sound roughly right (Tone {seven['Tone']:.2f}) because they are diplomatic most of
the time, real and simulated alike; their talk only sometimes points to what they did next (Foresight
{seven['Foresight']:.2f}), and their moves are vague (Moves {seven['Moves']:.2f}): Indonesia takes help too early and never
produces the real counter-measures (gas cut, energy threat). These are {WORD} runs of one design on one event.

## Appendix A: scores per run

"Real stage" is the how-close score used above. "Wrong stage" is a background check: the same agents compared with real
reactions from a different point in the crisis, which shows how much of a score would come anyway (for example,
governments sound diplomatic at any time). Moves shows only its judge part here, because the hand scores have no
wrong-stage version. Averaging each stage-country pair over the {WORD} runs, the judge's overall rating is higher at the
real stage in {signs[False][1]} of {signs[False][0]} people pairs ({signs[False][2]} lower, {signs[False][3]} tied; sign test
p = {signs[False][4]:.3f}) and in {signs[True][1]} of {signs[True][0]} government pairs ({signs[True][2]} lower, {signs[True][3]} tied;
p = {signs[True][4]:.3f}).

**People**

{run_table(False, PEOPLE)}

**Governments**

{run_table(True, GOVS)}

## Appendix B: the judge's original dimensions

The scores the seven dimensions are built from ({WORD}-run means). Hand scores per run: government cooperation
{fmt(COOP)}; conflict {fmt(CONF)}.

{old_table()}
"""
Path(args.out).write_text(doc, encoding="utf-8")
print("wrote", args.out)
