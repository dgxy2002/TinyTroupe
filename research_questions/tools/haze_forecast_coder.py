"""Score forecasts against what really happened after a cutoff (haze project, 2026-11-26).

Two kinds of input, scored by the same written rules:
- society runs: the free-play rounds after the cutoff (spoken lines only, with channel tags), from
  research_questions/outputs/<folder>/transcripts/*.json;
- baseline forecasts: plain-text answers from tools/haze_baseline_forecast.py (outputs/<folder>/forecasts/*.txt).

For each fixed target the judge gives yes / partly / no, who did it and a quote (no quote, no credit). It also lists
every other major government action or public campaign in the forecast and classifies it as real within the window,
real but later, or not real, so a forecast that predicts everything does not score well on hits alone.

Usage (from the repo root):
    python research_questions/tools/haze_forecast_coder.py --out <new-id> --cutoff 4 --folders <folders>

Targets for the cutoff after stage 4 (13 October 2026), window 14-23 October; sources in
research_questions/haze_society_design.md section 11. Rules fixed 2026-11-26 before any forecast was scored.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
OUTPUTS = REPO / "research_questions" / "outputs"
RUBRIC_VERSION = "haze-forecast-coding-v2"

# Primary targets: government moves (used for the go / no-go rule). Secondary: public reactions.
TARGETS_CUTOFF_4 = [
    {
        "id": "G1", "kind": "primary", "date": "about 15 Oct", "actor": "Government of Indonesia",
        "event": "Indonesia agrees in principle to accept foreign firefighting help (offers had been left unanswered).",
        "yes": "The Indonesian government says it accepts, approves or welcomes other countries' firefighting help "
        "(aircraft, personnel) for its fires.",
        "partly": "The Indonesian government proposes coordinating firefighting with neighbours or says it is open to "
        "help, without accepting it.",
    },
    {
        "id": "G2", "kind": "primary", "date": "14-16 Oct", "actor": "Government of Indonesia",
        "event": "Indonesian police name 223 people and 9 companies as suspects.",
        "yes": "The Indonesian government says it has named, charged or arrested suspects (people or companies), or "
        "gives a number of suspects.",
        "partly": "The Indonesian government says it will name, charge or prosecute specific suspects soon. General "
        "lines such as 'investigating all parties' or 'firm action against those responsible' do NOT count.",
    },
    {
        "id": "G3", "kind": "primary", "date": "15-19 Oct", "actor": "Government of Singapore",
        "event": "Singapore serves notices under its Transboundary Haze Pollution Act on 7, then 10, Indonesian companies.",
        "yes": "The Singapore government says it has sent, or is sending, legal notices or legal action under its haze "
        "law to particular companies (named or counted).",
        "partly": "The Singapore government says legal action under its haze law could or will follow, or that it is "
        "identifying the companies responsible. A general wish for 'accountability' does NOT count.",
    },
    {
        "id": "G4", "kind": "primary", "date": "19-20 Oct", "actor": "Government of Singapore",
        "event": "Singapore says the Singapore Exchange is questioning 7 Singapore-listed agriculture companies.",
        "yes": "The Singapore government says it (or its stock exchange or regulators) is questioning or "
        "investigating Singapore-listed or Singapore-based companies over links to the fires.",
        "partly": "The Singapore government says Singapore-linked companies will be held to account or looked into, "
        "without saying it is doing so.",
    },
    {
        "id": "G5", "kind": "primary", "date": "16 Oct", "actor": "Government of Malaysia",
        "event": "Malaysia's cabinet is told no Malaysian plantation companies are involved in the fires.",
        "yes": "The Malaysian government says Malaysian companies are not involved or there is no evidence they are.",
        "partly": "The Malaysian government says it is checking whether Malaysian companies are involved.",
    },
    {
        "id": "G6", "kind": "primary", "date": "21 Oct", "actor": "Government of Malaysia",
        "event": "Malaysia says it is open to a law like Singapore's Transboundary Haze Pollution Act.",
        "yes": "The Malaysian government says it is considering or open to its own law to act against companies that "
        "cause haze in Malaysia.",
        "partly": "The Malaysian government mentions legal options against companies in general terms.",
    },
    {
        "id": "G7", "kind": "primary", "date": "21-22 Oct", "actor": "Government of Indonesia",
        "event": "Prabowo says foreign companies are involved, threatens to expose them and to revoke foreign firms' "
        "licences.",
        "yes": "The Indonesian government publicly blames foreign (e.g. Singapore- or Malaysia-linked) companies, or "
        "threatens to expose or punish them or revoke their licences.",
        "partly": "The Indonesian government says foreign companies are among those investigated, without blame or "
        "threat.",
    },
    {
        "id": "G8", "kind": "primary", "date": "21 Oct", "actor": "Government of Indonesia",
        "event": "Prabowo rebukes 'certain countries that like to insult the Indonesian nation' over the fires.",
        "yes": "The Indonesian government publicly rebukes neighbouring countries or their criticism (insult, "
        "lecturing, blaming Indonesia).",
        "partly": "The Indonesian government pushes back mildly on blame (e.g. 'this is a regional problem', 'not only "
        "Indonesia') without rebuking anyone.",
    },
    {
        "id": "G9", "kind": "primary", "date": "22 Oct", "actor": "Government of Indonesia",
        "event": "Indonesia's energy minister says Indonesia will reconsider energy exports to countries that do not "
        "respect it.",
        "yes": "The Indonesian government threatens or announces cutting energy or gas exports to Singapore or another "
        "country in connection with the dispute.",
        "partly": "The Indonesian government links trade or energy to the dispute without a threat.",
    },
    {
        "id": "C1", "kind": "secondary", "date": "from 13 Oct, reported 26 Oct", "actor": "Malaysian public",
        "event": "Malaysians boycott Indonesian products (Indocafe, Sosro, Kara coconut milk).",
        "yes": "A Malaysian citizen calls for or commits to boycotting Indonesian products or brands (a national "
        "boycott).",
        "partly": "A Malaysian citizen backs a boycott of companies linked to the fires (not of Indonesian products "
        "as such).",
    },
    {
        "id": "C2", "kind": "secondary", "date": "from 12 Oct, reported 22 Oct", "actor": "Indonesian public",
        "event": "Indonesians apologise online to neighbours and urge them to pressure Jakarta.",
        "yes": "An Indonesian citizen apologises to people of other countries for the haze, or asks other countries to "
        "pressure or sue Indonesia's government.",
        "partly": "An Indonesian citizen publicly criticises Indonesia's own government over the fires.",
    },
]

# Things that also really happened, so the judge does not count them as false alarms.
OTHER_REAL_IN_WINDOW = [
    "Singapore PM Lawrence Wong: Singapore checking which companies are responsible; legal action could follow (15 Oct)",
    "Singapore opens haze shelters, hands out N95 masks, schools stop outdoor activities (by 16 Oct)",
    "Former Indonesian trade minister Lutfi challenges Singapore to raid the offices of Singapore-linked firms (19 Oct)",
    "Singapore minister Shanmugam: Singapore will use every legal and regulatory lever; could change laws urgently (19 Oct)",
    "Indonesia identifies 97 companies suspected of involvement (about 19 Oct)",
    "NEA asks 10 Singapore-registered palm oil and forestry firms for information about Indonesian links (23 Oct)",
    "Malaysia's government avoids criticising Indonesia; its foreign minister rules out formal protests or legal action "
    "(date not confirmed)",
    "Malaysian school closures across several states",
]
REAL_LATER = [
    "Indonesia cuts pipeline gas to Singapore by about 8-9% (24 Oct); 'Do not lecture us' (26 Oct)",
    "Singapore and Indonesia agree a joint task force to follow the money, and ministerial hotlines (27 Oct)",
    "Singapore amends its haze law, raising the maximum fine to S$20 million (4 Nov)",
    "Prabowo apologises to Malaysia and Singapore at the ASEAN summit: 'It is not our fault' (15 Nov)",
]

RUBRIC = """You score a forecast of what happened in Southeast Asia's 2026 haze crisis in the days after 13 October
2026, against what really happened. The forecast is either (a) a transcript of a simulation in which people and the
governments of Singapore, Malaysia, Indonesia and Brunei talk in online channels, or (b) a written forecast. Treat an
action done or announced in the simulation and a prediction in a written forecast the same way.

For EACH target below, give "score": "yes", "partly" or "no", following its rules exactly; "who": who did or predicted
it; "where": the round and channel (simulation) or "forecast"; "quote": the shortest exact quote that supports the
score. No quote means "no". The quote must itself show what makes the score "yes" rather than "partly" (for C1,
that the boycott is of Indonesian products or brands); if it does not, the score is at most "partly". The actor must match: a citizen saying the government should do something is not the
government doing it. Vague lines ("we will act against those responsible", "we are investigating") do not earn
"partly" unless the target's rule says so.

TARGETS:
{targets}

Then list, under "other_actions", every other major action, announcement, policy or public campaign by a government
or a public that appears in the forecast and is not one of the targets (at most 15, most important first). For each
give "actor", "action" (one line), "quote", and "status": "real_in_window" if it matches one of the REAL IN WINDOW
items, "real_later" if it matches one of the REAL LATER items, otherwise "not_real". Ignore routine expressions of
concern, health advice and statements of intent with no content.

REAL IN WINDOW (14-23 October 2026), also true:
{real_in}

REAL LATER (after 23 October 2026):
{real_later}

Reply with JSON only:
{{"targets": {{"G1": {{"score": "no", "who": "", "where": "", "quote": ""}}, ...}},
"other_actions": [{{"actor": "", "action": "", "quote": "", "status": "not_real"}}]}}"""


def rubric(targets: list[dict]) -> str:
    lines = [
        f'{t["id"]} ({t["actor"]}, {t["date"]}): {t["event"]}\n  yes: {t["yes"]}\n  partly: {t["partly"]}'
        for t in targets
    ]
    return RUBRIC.format(
        targets="\n".join(lines),
        real_in="\n".join(f"- {x}" for x in OTHER_REAL_IN_WINDOW),
        real_later="\n".join(f"- {x}" for x in REAL_LATER),
    )


def society_documents(folder: Path) -> list[tuple[str, str]]:
    docs = []
    for path in sorted(glob.glob(str(folder / "transcripts" / "*.json"))):
        data = json.loads(open(path, encoding="utf-8").read(), strict=False)
        cutoff_round = data["run"]["cutoff_round"]
        lines = []
        for e in data["events"]:
            if e["round"] <= cutoff_round:
                continue
            if e["type"] == "OBSERVE":
                lines.append(f"Round {e['round']} [{e['channel']}]: {e['content']}")
            elif e["type"] == "TALK":
                to = f" (to {e['target']})" if e.get("target") else ""
                lines.append(f"Round {e['round']} [{e['channel']}] {e['agent']}{to}: {e['content']}")
        docs.append((data["run"]["run_id"], "Simulation transcript, free-play rounds only:\n" + "\n".join(lines)))
    return docs


def baseline_documents(folder: Path) -> list[tuple[str, str]]:
    return [
        (Path(p).stem, "Written forecast:\n" + open(p, encoding="utf-8").read())
        for p in sorted(glob.glob(str(folder / "forecasts" / "*.txt")))
    ]


def call(model: str, system: str, text: str) -> tuple[dict, dict]:
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
        "max_tokens": 12000,
        "usage": {"include": True},
    }
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json=body,
        timeout=300,
    )
    r.raise_for_status()
    resp = r.json()
    content = resp["choices"][0]["message"]["content"]
    return json.loads(re.search(r"\{.*\}", content, re.S).group(0)), resp.get("usage", {})


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--cutoff", type=int, default=4, choices=[4])
    p.add_argument("--model", default="anthropic/claude-sonnet-5.5")
    p.add_argument("--folders", nargs="+", required=True)
    args = p.parse_args()
    load_dotenv(REPO / ".env")
    out = OUTPUTS / args.out
    if out.exists():
        sys.exit(f"{out} exists; choose a new --out")
    out.mkdir(parents=True)
    targets = TARGETS_CUTOFF_4
    system = rubric(targets)
    (out / "rubric.txt").write_text(system, encoding="utf-8")
    total, rows, other_rows = 0.0, [], []
    for folder in args.folders:
        base = OUTPUTS / folder
        docs = society_documents(base) or baseline_documents(base)
        kind = "society" if (base / "transcripts").exists() else "baseline"
        for doc_id, text in docs:
            coded, usage = call(args.model, system, text)
            total += usage.get("cost") or 0
            record = {"rubric": RUBRIC_VERSION, "model": args.model, "folder": folder, "doc": doc_id, "kind": kind,
                      "usage": usage, **coded}
            (out / f"{folder}.{doc_id}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
            for t in targets:
                c = (coded.get("targets") or {}).get(t["id"]) or {}
                score = c.get("score", "no") if c.get("quote") else "no"
                rows.append({"folder": folder, "doc": doc_id, "kind": kind, "target": t["id"], "target_kind": t["kind"],
                             "score": score, "who": c.get("who", ""), "where": c.get("where", ""),
                             "quote": c.get("quote", "")})
            for o in coded.get("other_actions") or []:
                other_rows.append({"folder": folder, "doc": doc_id, "kind": kind, **{k: o.get(k, "") for k in
                                   ("actor", "action", "status", "quote")}})
            print(f"{folder} {doc_id}: ${usage.get('cost') or 0:.4f}", flush=True)
    for name, data in (("targets_long.csv", rows), ("other_actions.csv", other_rows)):
        if data:
            with open(out / name, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(data[0]))
                w.writeheader()
                w.writerows(data)
    print(f"total ${total:.4f}")


if __name__ == "__main__":
    main()
