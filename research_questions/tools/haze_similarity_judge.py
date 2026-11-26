"""Compare simulated citizens' reactions with real public reactions, stage by stage (haze project, 2026-11-26).

For each news stage and country (Malaysia, Indonesia, Singapore), the judge reads (a) what the simulated citizens of that
country said in that stage's rounds (spoken lines only, all channels) and (b) the real public reactions classified for
the same stage (research_questions/haze_ground_truth_stages1_4.csv and haze_ground_truth_later.csv), and scores each
dimension: match / partly / mismatch / no_data, with a reason and a supporting simulated quote, plus an overall 0-10.

Control: each simulated stage is also scored against the real reactions of a different stage with data for the same
country (the judge is not told which is which). If the matched scores are not clearly higher than the control scores,
the measure is only picking up generic haze talk.

Usage (from the repo root):
    python research_questions/tools/haze_similarity_judge.py --out <new-id> --folder <society run folder>

Writes research_questions/outputs/<out>/ (refuses an existing folder): judgements.jsonl, scores_long.csv, rubric.txt.
Run twice with different --out for two passes.
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
RQ = REPO / "research_questions"
OUTPUTS = RQ / "outputs"
# v2 (2026-11-26): adds the two agreed public dimensions v1 left out (triggers, division within a country) and a
# government mode. v1 and v2 scores are not pooled; runs compared on v2 must all be scored with v2.
RUBRIC_VERSION = "haze-similarity-v2"
COUNTRIES = {"MY": "Malaysia", "ID": "Indonesia", "SG": "Singapore"}
DIMENSIONS = {
    "emotion": "the emotions and tone expressed (anger, mockery, shame, frustration, fear, solidarity, resignation...)",
    "blame": "whom they hold responsible (Indonesian government, their own government, companies, nature, nobody)",
    "stance": "how they treat other countries' governments and people (hostile, critical, neutral, solidary)",
    "actions": "what they do or say they will do (boycott, protest, lawsuit, apology, online campaign, nothing)",
    "demands": "what they ask for (apology, naming companies, emergency, compensation, legal action, aid)",
    "framing": "how they frame the crisis (nature vs human cause, companies vs governments, national pride, "
               "ordinary people suffer)",
    "diversity": "whether people of this country disagree with each other or all say the same",
    "triggers": "which events or statements they react to most (and which they ignore)",
    "division": "whether they turn against their OWN government (blame it, distrust it, are ashamed of it)",
}

GOV_DIMENSIONS = {
    "anticipation": "does B signal, propose, plan or argue for any of the moves in A before they happen?",
    "tone": "is B's stance towards the other governments (cooperative, defensive, confrontational) like A's?",
    "specificity": "does B name concrete acts (notices, numbers, named measures) the way A does, or stay vague?",
}

GOV_RUBRIC = """You compare (A) what one government REALLY did or said publicly during Southeast Asia's 2026 haze crisis
in the days that FOLLOW a given moment, with (B) what a simulated version of that government said PRIVATELY to the
other governments at that moment, in a diplomatic channel. B could not know A. Judge how far B foreshadows A.

For each dimension give "score": "match", "partly", "mismatch" or "no_data" (if B is silent or A gives nothing to
compare), a one-sentence "reason" and the shortest supporting "quote" from B.

Dimensions:
{dims}

Then "overall": 0-10 (0 = B gives no hint of A, 10 = B clearly foreshadows A) and "overall_reason".
Reply with JSON only:
{{"dimensions": {{"anticipation": {{"score": "match", "reason": "", "quote": ""}}, ...}}, "overall": 0,
"overall_reason": ""}}"""

RUBRIC = """You compare two sets of reactions to the same moment in Southeast Asia's 2026 haze crisis: (A) reactions
of the PUBLIC of one country as found in real news reports, and (B) lines written by simulated ordinary citizens of
that country in an online simulation. Judge how similar B is to A on each dimension below. Use only what is written.

For each dimension give "score": "match" (B clearly shows what A shows), "partly" (some overlap, or B shows it more
weakly or about a different target), "mismatch" (A shows something B does not, or B shows the opposite), or "no_data"
(A says nothing on this dimension, so it cannot be judged). Give a one-sentence "reason" and, unless no_data or B is
silent, the shortest "quote" from B that supports the score.

Dimensions:
{dims}

Note that A often comes from NGOs, commentators or politicians while B is ordinary people; judge the content, and in
"voice_note" say in one sentence whether the matches are to ordinary people's reactions or only to activists'.
Then give "overall": 0-10 (0 = nothing in common beyond the haze itself, 10 = same reactions), and "overall_reason".

Reply with JSON only:
{{"dimensions": {{"emotion": {{"score": "match", "reason": "", "quote": ""}}, ...}}, "voice_note": "",
"overall": 0, "overall_reason": ""}}"""


def rubric() -> str:
    return RUBRIC.format(dims="\n".join(f"- {k}: {v}" for k, v in DIMENSIONS.items()))


def load_truth() -> dict[tuple[int, str], list[dict]]:
    truth: dict[tuple[int, str], list[dict]] = {}
    for name in ("haze_ground_truth_stages1_4.csv", "haze_ground_truth_later.csv"):
        with open(RQ / name, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                truth.setdefault((int(row["stage"]), row["country"]), []).append(row)
    return truth


def truth_text(rows: list[dict]) -> str:
    out = []
    for r in rows:
        out.append(
            f"- {r['date']}, {r['actor']} ({r['actor_type']}). Reacting to: {r['trigger']}. Emotion: {r['emotion']}. "
            f"Blames: {r['blame']}. Stance: {r['stance_to_other_country']}. Action: {r['action']}. "
            f"Demand: {r['demand']}. Framing: {r['framing']}. Quote: \"{r['quote']}\""
        )
    return "\n".join(out)


def sim_lines(transcript: dict, stage: int, country: str) -> str:
    agents = transcript["scenario"]["agents"]
    citizens = {a["display_name"] for a in agents.values() if a.get("country") == COUNTRIES[country]
                and a.get("kind") != "government"}
    first, last = 2 * stage - 1, 2 * stage
    lines = [
        f"[{e['channel']}] {e['agent']}: {e['content']}"
        for e in transcript["events"]
        if e["type"] == "TALK" and e["agent"] in citizens and first <= e["round"] <= last
    ]
    return "\n".join(lines)


def call(model: str, system: str, text: str, attempts: int = 3) -> tuple[dict, dict]:
    """Ask the judge; retry when the reply is not valid JSON (pass b crashed once on 2026-11-26). Costs add up."""

    total_cost = 0.0
    for attempt in range(1, attempts + 1):
        judged, usage = _call_once(model, system, text)
        total_cost += usage.get("cost") or 0
        if judged is not None:
            return judged, {**usage, "cost": total_cost, "attempts": attempt}
        print(f"  malformed JSON, retry {attempt}", flush=True)
    raise ValueError("judge returned malformed JSON three times")


def _call_once(model: str, system: str, text: str) -> tuple[dict | None, dict]:
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
              "max_tokens": 8000, "usage": {"include": True}},
        timeout=300,
    )
    r.raise_for_status()
    resp = r.json()
    content = resp["choices"][0]["message"]["content"]
    try:
        return json.loads(re.search(r"\{.*\}", content, re.S).group(0)), resp.get("usage", {})
    except (AttributeError, json.JSONDecodeError):
        return None, resp.get("usage", {})


def control_stage(stage: int, country: str, truth: dict) -> int | None:
    """A different stage with real data for this country: the next one after it, wrapping round."""

    stages = sorted(s for (s, c) in truth if c == country and s != stage)
    if not stages:
        return None
    later = [s for s in stages if s > stage]
    return later[0] if later else stages[0]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--folder", required=True, help="society run folder under research_questions/outputs")
    p.add_argument("--model", default="anthropic/claude-sonnet-5.5")
    p.add_argument("--stages", type=int, nargs="*", help="limit to these stages")
    p.add_argument("--government", action="store_true",
                   help="also score the governments' private diplomatic talk against their real moves not yet posted")
    args = p.parse_args()
    load_dotenv(REPO / ".env")
    out = OUTPUTS / args.out
    if out.exists():
        sys.exit(f"{out} exists; choose a new --out")
    out.mkdir(parents=True)
    system = rubric()
    (out / "rubric.txt").write_text(system, encoding="utf-8")
    truth = load_truth()
    rows, total = [], 0.0
    with open(out / "judgements.jsonl", "w", encoding="utf-8") as jf:
        for path in sorted(glob.glob(str(OUTPUTS / args.folder / "transcripts" / "*.json"))):
            transcript = json.loads(open(path, encoding="utf-8").read(), strict=False)
            run_id = transcript["run"]["run_id"]
            last_real_stage = transcript["run"]["cutoff_stage"]
            for stage in range(1, last_real_stage + 1):
                if args.stages and stage not in args.stages:
                    continue
                for country in COUNTRIES:
                    sim = sim_lines(transcript, stage, country)
                    pairs = [("matched", stage)]
                    ctrl = control_stage(stage, country, truth)
                    if ctrl is not None:
                        pairs.append(("control", ctrl))
                    for kind, truth_stage in pairs:
                        real = truth.get((truth_stage, country))
                        if not real:
                            rows.append({"run": run_id, "stage": stage, "country": country, "kind": kind,
                                         "truth_stage": truth_stage, "dimension": "all", "score": "no_data",
                                         "overall": ""})
                            continue
                        text = (f"(A) Real public reactions in {COUNTRIES[country]}:\n{truth_text(real)}\n\n"
                                f"(B) Simulated citizens of {COUNTRIES[country]}:\n{sim or '(no lines)'}")
                        judged, usage = call(args.model, system, text)
                        total += usage.get("cost") or 0
                        jf.write(json.dumps({"run": run_id, "stage": stage, "country": country, "kind": kind,
                                             "truth_stage": truth_stage, "usage": usage, **judged},
                                            ensure_ascii=False) + "\n")
                        for dim in DIMENSIONS:
                            d = (judged.get("dimensions") or {}).get(dim) or {}
                            rows.append({"run": run_id, "stage": stage, "country": country, "kind": kind,
                                         "truth_stage": truth_stage, "dimension": dim,
                                         "score": d.get("score", "no_data"), "overall": judged.get("overall", "")})
                        print(f"{run_id} stage {stage} {country} {kind} (truth {truth_stage}): overall "
                              f"{judged.get('overall')} ${usage.get('cost') or 0:.4f}", flush=True)
    with open(out / "scores_long.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    if args.government:
        total += judge_governments(args, out)
    print(f"total ${total:.4f}")


# ---- government mode (v2): private diplomatic talk vs the government's real moves not yet posted ----
GOV_NAMES = {"SG": "Government of Singapore", "MY": "Government of Malaysia", "ID": "Government of Indonesia"}


def load_gov_truth() -> list[dict]:
    with open(RQ / "haze_ground_truth_government.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        m = re.search(r"stage (\d)", r["in_injected_news"])
        r["posted_stage"] = int(m.group(1)) if m and r["in_injected_news"].startswith(("yes", "partly")) else None
        r["window_n"] = int(r["window"][1:])
    return rows


def gov_truth_after(rows: list[dict], country: str, stage: int) -> list[dict]:
    """Moves by this government in windows `stage` and `stage + 1` that agents had not yet seen as posts."""

    return [r for r in rows if r["country"] == country and r["window_n"] in (stage, stage + 1)
            and (r["posted_stage"] is None or r["posted_stage"] > stage)]


def gov_control(rows: list[dict], country: str, stage: int) -> tuple[int, list[dict]] | None:
    """The same government's moves from a window at least two away (wrong-time control)."""

    windows = sorted({r["window_n"] for r in rows if r["country"] == country})
    far = [w for w in windows if abs(w - stage) >= 2 and abs(w - (stage + 1)) >= 2]
    if not far:
        return None
    w = far[len(far) // 2]
    return w, [r for r in rows if r["country"] == country and r["window_n"] == w]


def gov_lines(transcript: dict, stage: int, name: str) -> str:
    first, last = 2 * stage - 1, 2 * stage
    return "\n".join(
        f"{e['agent']}: {e['content']}" for e in transcript["events"]
        if e["type"] == "TALK" and e["agent"] == name and e["channel"] == "diplomatic" and first <= e["round"] <= last
    )


def judge_governments(args, out: Path) -> float:
    system = GOV_RUBRIC.format(dims="\n".join(f"- {k}: {v}" for k, v in GOV_DIMENSIONS.items()))
    (out / "gov_rubric.txt").write_text(system, encoding="utf-8")
    rows_truth = load_gov_truth()
    rows, total = [], 0.0
    with open(out / "gov_judgements.jsonl", "w", encoding="utf-8") as jf:
        for path in sorted(glob.glob(str(OUTPUTS / args.folder / "transcripts" / "*.json"))):
            transcript = json.loads(open(path, encoding="utf-8").read(), strict=False)
            run_id = transcript["run"]["run_id"]
            for stage in range(1, 8):
                for country, name in GOV_NAMES.items():
                    sim = gov_lines(transcript, stage, name)
                    if not sim:
                        continue
                    pairs = [("matched", f"W{stage}-W{stage + 1}", gov_truth_after(rows_truth, country, stage))]
                    ctrl = gov_control(rows_truth, country, stage)
                    if ctrl:
                        pairs.append(("control", f"W{ctrl[0]}", ctrl[1]))
                    for kind, label, real in pairs:
                        if not real:
                            continue
                        moves = "\n".join(f"- {r['date']}: {r['move']}" for r in real)
                        text = f"(A) Real moves by the {name}:\n{moves}\n\n(B) The simulated {name}, privately:\n{sim}"
                        judged, usage = call(args.model, system, text)
                        total += usage.get("cost") or 0
                        jf.write(json.dumps({"run": run_id, "stage": stage, "country": country, "kind": kind,
                                             "truth": label, "usage": usage, **judged}, ensure_ascii=False) + "\n")
                        for dim in GOV_DIMENSIONS:
                            d = (judged.get("dimensions") or {}).get(dim) or {}
                            rows.append({"run": run_id, "stage": stage, "country": country, "kind": kind,
                                         "truth": label, "dimension": dim, "score": d.get("score", "no_data"),
                                         "overall": judged.get("overall", "")})
                        print(f"{run_id} gov stage {stage} {country} {kind} ({label}): overall {judged.get('overall')}"
                              f" ${usage.get('cost') or 0:.4f}", flush=True)
    if rows:
        with open(out / "gov_scores_long.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    return total


if __name__ == "__main__":
    main()
