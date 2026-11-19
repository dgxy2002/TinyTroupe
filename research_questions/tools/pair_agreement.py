"""Score how far each pair of agents agreed with each other within one run (undirected).

Usage (from the repo root):
    python research_questions/tools/pair_agreement.py --out pair-agreement-test-v1 \
        --models anthropic/claude-sonnet-5.5 openai/gpt-5-mini \
        --folders s57-case-r12-k3 s46-case-r12-hw1

Reads research_questions/outputs/<folder>/transcripts/*.md, or outputs_old/ if the run is not in outputs/. Names are replaced with Agent A-D and the
opening sentence that lists backgrounds or faiths is removed, so the coder does not see who is which culture.
Culture is joined back from the run's cast afterwards. Writes one JSON per transcript and model to
research_questions/outputs/<out>/ and refuses to overwrite an existing folder.
"""

import argparse
import glob
import itertools
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
OLD = REPO / "research_questions" / "outputs_old"
NEW = REPO / "research_questions" / "outputs"
RUBRIC_VERSION = "pair-agreement-v2"

RUBRIC = """You will read the public transcript of a conversation between four people, Agent A, Agent B, Agent C
and Agent D, about one shared problem. For EACH of the six pairs (A-B, A-C, A-D, B-C, B-D, C-D), judge how far
the two agreed with each other about the main issue. Use only what is said in the transcript.

Scores (the same scale for start and end):
 2  clearly aligned: on the same side, or both endorse the same arrangement
 1  mostly aligned: same side, differing only on details
 0  no clear relation: they never took positions on the same point, or one of them said too little to tell
-1  partly opposed: disagree on some points while overlapping on others
-2  clearly opposed: on opposite sides, or rejecting each other's proposals

For each pair give:
- "start": their agreement when both had first stated a position
- "end": their agreement at the end of the conversation
- "engaged": true if they spoke to or about each other's position at least once, otherwise false
- "moved": who shifted their position towards the other between start and end: the letter of one of the two
  (for pair A-D, "A" or "D"), "both", or "neither"
- "evidence": one short quote or paraphrase with turn numbers that justifies "end" and "moved"

Judge agreement only. Do not judge who was right, how fair anything was, or anyone's background.
Reply with JSON only, in this form:
{"main_issue": "<one line>", "pairs": {"A-B": {"start": 0, "end": 0, "engaged": true, "moved": "neither", "evidence": "..."}, ...}}"""

SCALES = {
    "points": """Scores (the same scale for start and end):
 2  clearly aligned: on the same side, or both endorse the same arrangement
 1  mostly aligned: same side, differing only on details
 0  no clear relation: they never took positions on the same point, or one of them said too little to tell
-1  partly opposed: disagree on some points while overlapping on others
-2  clearly opposed: on opposite sides, or rejecting each other's proposals""",
    "decimal": """Scores (the same scale for start and end): any number from -1.00 to 1.00, with two decimals.
 1.00  completely aligned: on the same side, and both endorse the same arrangement
 0.00  no clear relation: they never took positions on the same point, or one of them said too little to tell
-1.00  completely opposed: on opposite sides, rejecting each other's proposals
Use any value in between to show how far they agreed.""",
}


def rubric(scale: str) -> str:
    return RUBRIC.replace(SCALES["points"], SCALES[scale])


def masked_transcript(folder: str) -> tuple[str, dict]:
    # new runs live in outputs/, the case-study runs in outputs_old/
    tj = (glob.glob(str(NEW / folder / "transcripts" / "*.json")) or glob.glob(str(OLD / folder / "transcripts" / "*.json")))[0]
    md = tj[:-5] + ".md"
    data = json.loads(open(tj, encoding="utf-8").read(), strict=False)
    agents = data["scenario"]["agents"]
    text = open(md, encoding="utf-8").read()
    # drop sentences that list backgrounds or faiths
    text = re.sub(r"[^.\n]*\b(?:faith|background)s?\b[^.\n]*:[^\n]*?\.(?=\s|$)", "", text)
    text = re.sub(r"[^.\n]*\bis (?:Muslim|Hindu|Buddhist|Catholic|Malay|Chinese|Indian|Eurasian)\b[^\n]*?\.(?=\s|$)", "", text)
    names = []
    for role, a in agents.items():
        full = a["display_name"]
        names.append((full, role))
        first = full.split()[0]
        if first != full:
            names.append((first, role))
    for name, role in sorted(names, key=lambda x: -len(x[0])):
        text = re.sub(rf"\b{re.escape(name)}\b", f"Agent {role}", text)
    cast = {role: {"culture": a["cultural_background"], "name": a["display_name"]} for role, a in agents.items()}
    return text, cast


def call(model: str, transcript: str, scale: str) -> tuple[dict, dict]:
    body = {
        "model": model,
        "messages": [{"role": "system", "content": rubric(scale)}, {"role": "user", "content": transcript}],
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
    match = re.search(r"\{.*\}", content, re.S)
    return json.loads(match.group(0)), resp.get("usage", {})


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--models", nargs="+", required=True)
    p.add_argument("--folders", nargs="+", required=True)
    p.add_argument("--scale", choices=sorted(SCALES), default="decimal")
    args = p.parse_args()
    assert rubric(args.scale) != RUBRIC or args.scale == "points"
    load_dotenv(REPO / ".env")
    out = NEW / args.out
    if out.exists():
        sys.exit(f"{out} exists; choose a new --out")
    out.mkdir(parents=True)
    total = 0.0
    for folder in args.folders:
        transcript, cast = masked_transcript(folder)
        (out / f"{folder}.masked.md").write_text(transcript, encoding="utf-8")
        for model in args.models:
            scores, usage = call(model, transcript, args.scale)
            cost = usage.get("cost") or 0
            total += cost
            for pair, s in scores.get("pairs", {}).items():
                a, b = pair.split("-")
                s["roles"] = pair
                s["cultures"] = f"{cast[a]['culture']} - {cast[b]['culture']}"
                s["includes_D"] = "D" in (a, b)
                s["change"] = round(float(s["end"]) - float(s["start"]), 2)
            record = {"rubric": f"{RUBRIC_VERSION}-{args.scale}", "model": model, "folder": folder, "cast": cast, "usage": usage, **scores}
            (out / f"{folder}.{model.replace('/', '_')}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{folder} {model}: ${cost:.4f}", flush=True)
    print(f"total ${total:.4f}")


if __name__ == "__main__":
    main()
