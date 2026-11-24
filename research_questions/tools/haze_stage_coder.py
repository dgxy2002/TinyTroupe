"""Code every agent at every news stage of a haze run: anger, blame, actions, stance, recall.

Prof's request (2026-11-24): quantitative per-agent, per-stage variables, so reactions can be counted across runs
and drawn as per-country curves over the news stages with the real events marked.

Usage (from the repo root):
    python research_questions/tools/haze_stage_coder.py --out haze-coding-test-a \
        --folders s123-case-v1-hz1 s123-case-v2-hz1

A stage is the news update plus the rounds until the next update (S123: rounds 1-2 are stage 1, 3-4 stage 2, ...).
One coder call per stage covers every agent; speech (TALK) and private thought (THINK) are coded separately. Names
and countries stay visible, because blame and stance only make sense relative to the agent's own country.

Writes, under research_questions/outputs/<out>/ (refuses an existing folder):
    <run_id>.json  raw coder output per stage, with usage
    codes_long.csv one row per run x stage x agent x channel (speech/thought), one 0/1 column per label
Run twice with different --out (pass a and b) to check agreement, as with the pair scores.
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
RUBRIC_VERSION = "haze-stage-coding-v3"

BLAME = [
    "indonesian_government",
    "malaysian_government",
    "singapore_government",
    "brunei_government",
    "indonesian_companies",
    "singapore_or_malaysia_linked_companies",
    "companies_unspecified",
    "smallholders_or_farmers",
    "nature_or_weather",
]
ACTIONS = [
    "boycott",
    "legal_action",
    "demand_apology",
    "apologise",
    "accept_or_offer_help",
    "regional_cooperation",
    "trade_or_energy_measures",
    "protest_or_petition",
    "accountability",
    "demand_government_action",
]
STANCES = ["hostile", "critical", "neutral", "solidary", "mixed"]

RUBRIC = f"""You will read one stage of a simulated public discussion about the 2026 Southeast Asian haze. Each
participant is a person, or a government, from one country (shown after the name). A [channel] tag, when
present, shows where a line was written: a national group, the public feed or the diplomatic channel. The stage starts with a dated news
update; then come the participants' lines in order. SAYS lines are spoken aloud to the others. THINKS lines are
private thoughts that nobody else hears.

For EVERY participant, code SAYS lines and THINKS lines separately, using only what that participant expresses in
this stage. If a participant has no lines of one kind in this stage, set that part to null.

Fields for each part:
- "anger": 1-5. 1 = no anger or frustration (worry or fear for family alone is 1); 2 = mild frustration or
  annoyance; 3 = clear anger or frustration at someone; 4 = strong anger, sharp criticism, sarcasm or insult aimed at
  someone; 5 = outrage or hostility, insults or calls to punish.
- "blame": list of the parties the participant holds responsible, in this stage, for the haze or for handling it
  badly. Only when they attribute responsibility, not when they merely mention a party. Allowed values:
  {", ".join(BLAME)}. Empty list if none.
- "actions": list of actions the participant proposes, asks for or endorses. Allowed values:
  boycott (stop buying from companies or a country's products); legal_action (a legal means: suing, prosecuting,
  fines, legal notices, revoking licences); demand_apology (asks someone to apologise); apologise (apologises on behalf of their
  own country, government or people); accept_or_offer_help (a government accepting or offering firefighting or other
  help); regional_cooperation (ASEAN action, joint task force, cross-border agreements); trade_or_energy_measures
  (cutting exports, sanctions, trade pressure); protest_or_petition; accountability (wants those responsible found, named or held responsible, with no
  specific means); demand_government_action (asks a government,
  their own or another, to act or do more, when none of the more specific values fits). Empty list if none.
- "rejected": list of actions, from the same allowed values, that the participant argues against or drops. If
  they propose an action and later in the stage withdraw it, list it under both "actions" and "rejected".
- "stance": how they treat other countries' governments, companies or people in this stage. One of
  {", ".join(STANCES)}. hostile = insults, mockery or us-versus-them about another country; critical = criticises
  another country's government or companies without hostility; neutral = no view on other countries; solidary =
  sympathy or shared suffering expressed towards people of another country, or defending them; general
  sympathy that is not about another country is neutral; mixed = clearly both critical or hostile and
  solidary.
- "defends_own_country": true if they defend their own country, government or people against blame or criticism.
- "recall": list of past haze episodes they refer to, as years ("1997", "2013", "2015", "2019"), or "earlier" for a
  vague reference ("like last time"). Empty list if none.
- "evidence": one short quote that best supports the anger and blame codes.

Do not judge who is right. Code what is expressed, not what you think the person feels.
Reply with JSON only, in this form:
{{"agents": {{"<name>": {{"says": {{"anger": 1, "blame": [], "actions": [], "rejected": [], "stance": "neutral",
"defends_own_country": false, "recall": [], "evidence": "..."}}, "thinks": {{...}} or null}}, ...}}}}"""


def load_run(path: str) -> dict:
    data = json.loads(open(path, encoding="utf-8").read(), strict=False)
    scen = data["scenario"]
    countries = (scen.get("profile_treatment") or {}).get("countries") or {}
    agents = {}
    for role, a in scen["agents"].items():
        agents[a["display_name"]] = {"role": role, "country": countries.get(role, "")}
    starts = sorted([1] + [int(r) for r in (scen.get("round_observations") or {})])
    news = {1: scen["shared_trigger"], **{int(r): t for r, t in (scen.get("round_observations") or {}).items()}}
    stages = []
    for i, start in enumerate(starts):
        end = starts[i + 1] - 1 if i + 1 < len(starts) else 10**6
        stages.append({"stage": i + 1, "first_round": start, "last_round": end, "news": news[start]})
    events = [e for e in data["events"] if e.get("type") in ("TALK", "THINK") and e.get("content")]
    return {"run_id": data["run"]["run_id"], "agents": agents, "stages": stages, "events": events}


def stage_text(run: dict, stage: dict) -> tuple[str, dict]:
    lines, counts = [], {name: {"says": 0, "thinks": 0} for name in run["agents"]}
    for e in run["events"]:
        if not stage["first_round"] <= e["round"] <= stage["last_round"]:
            continue
        name = e["agent"]
        text = re.sub(r"^\s*STRATEGY:\s*[A-Z_ ]+\.\s*", "", e["content"]).strip()
        kind = "SAYS" if e["type"] == "TALK" else "THINKS"
        counts[name]["says" if kind == "SAYS" else "thinks"] += 1
        where = f" [{e['channel']}]" if e.get("channel") else ""
        lines.append(f"Round {e['round']}{where}, {name} ({run['agents'][name]['country']}) {kind}: {text}")
    people = "\n".join(f"- {n} ({a['country']})" for n, a in run["agents"].items())
    text = f"Participants:\n{people}\n\nNews update:\n{stage['news']}\n\nLines:\n" + "\n".join(lines)
    return text, counts


def call(model: str, text: str) -> tuple[dict, dict]:
    body = {
        "model": model,
        "messages": [{"role": "system", "content": RUBRIC}, {"role": "user", "content": text}],
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


def rows_for(folder: str, run: dict, stage: dict, coded: dict, counts: dict, problems: list) -> list[dict]:
    rows = []
    for name, info in run["agents"].items():
        entry = (coded.get("agents") or {}).get(name) or {}
        for part in ("says", "thinks"):
            c = entry.get(part)
            if counts[name][part] == 0 or not c:
                if counts[name][part]:
                    problems.append(f"{run['run_id']} stage {stage['stage']} {name} {part}: lines but no code")
                continue
            row = {
                "folder": folder, "run_id": run["run_id"], "stage": stage["stage"], "agent": name,
                "role": info["role"], "country": info["country"], "channel": part, "n_lines": counts[name][part],
                "anger": c.get("anger"), "stance": c.get("stance"),
                "defends_own_country": int(bool(c.get("defends_own_country"))),
                "recall": ";".join(map(str, c.get("recall") or [])), "evidence": c.get("evidence", ""),
            }
            for field, allowed in (("blame", BLAME), ("actions", ACTIONS), ("rejected", ACTIONS)):
                got = set(c.get(field) or [])
                for bad in got - set(allowed):
                    problems.append(f"{run['run_id']} stage {stage['stage']} {name} {part}: unknown {field} {bad!r}")
                for label in allowed:
                    row[f"{field}_{label}" if field != "actions" else f"action_{label}"] = int(label in got)
            if row["stance"] not in STANCES:
                problems.append(f"{run['run_id']} stage {stage['stage']} {name} {part}: stance {row['stance']!r}")
            rows.append(row)
    return rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="anthropic/claude-sonnet-5.5")
    p.add_argument("--folders", nargs="+", required=True)
    args = p.parse_args()
    load_dotenv(REPO / ".env")
    out = OUTPUTS / args.out
    if out.exists():
        sys.exit(f"{out} exists; choose a new --out")
    out.mkdir(parents=True)
    total, rows, problems = 0.0, [], []
    for folder in args.folders:
        for path in sorted(glob.glob(str(OUTPUTS / folder / "transcripts" / "*.json"))):
            run = load_run(path)
            record = {"rubric": RUBRIC_VERSION, "model": args.model, "folder": folder, "run_id": run["run_id"], "stages": []}
            for stage in run["stages"]:
                text, counts = stage_text(run, stage)
                if not any(c["says"] or c["thinks"] for c in counts.values()):
                    continue
                coded, usage = call(args.model, text)
                total += usage.get("cost") or 0
                record["stages"].append({**{k: stage[k] for k in ("stage", "first_round", "last_round")}, "usage": usage, **coded})
                rows += rows_for(folder, run, stage, coded, counts, problems)
                print(f"{run['run_id']} stage {stage['stage']}: ${usage.get('cost') or 0:.4f}", flush=True)
            (out / f"{folder}.{run['run_id']}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    if rows:
        with open(out / "codes_long.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    for line in problems:
        print("CHECK:", line)
    print(f"total ${total:.4f}")


if __name__ == "__main__":
    main()
