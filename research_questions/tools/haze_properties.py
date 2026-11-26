"""Simulator properties of a society run, computed from the transcript, no model calls (2026-11-26).

- echo: share of citizens' spoken lines that open by agreeing with someone ("Yes", "Exactly", "X is right", ...).
- parroting: share of citizens' spoken lines that repeat five or more consecutive words from the news or the scripted
  government posts delivered so far.
- recall: number of stage-coder codes that mention an earlier haze episode (needs the coder's codes_long.csv).
- per-agent turn use: share of offered turns where the agent said something (not DONE only).

Usage (from the repo root):
    python research_questions/tools/haze_properties.py --folder society-hs5-e2e1 [--codes haze-coding-v3-hs5-e2e1-a]
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUTS = REPO / "research_questions" / "outputs"
AGREE = re.compile(
    r"^\s*(yes|yeah|ya|exactly|same|true|agree|i agree|totally|tell me about it|that's (right|true|it)|so true|"
    r"[A-Z][\w ]{0,30} is (right|so right|absolutely right)|you're right|you are right|well said|"
    r"[A-Z][\w ]{0,30} and [A-Z][\w ]{0,30} are right)\b",
    re.I,
)


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def ngrams(ws: list[str], n: int = 5) -> set[tuple[str, ...]]:
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", required=True)
    p.add_argument("--codes", help="stage-coder output folder (for recall)")
    args = p.parse_args()
    for path in sorted(glob.glob(str(OUTPUTS / args.folder / "transcripts" / "*.json"))):
        t = json.loads(open(path, encoding="utf-8").read(), strict=False)
        citizens = {a["display_name"] for a in t["scenario"]["agents"].values() if a.get("kind") != "government"}
        seen: set[tuple[str, ...]] = set()
        talk = []
        by_round: dict[int, list[dict]] = {}
        for e in t["events"]:
            by_round.setdefault(e["round"], []).append(e)
        for r in sorted(by_round):
            for e in by_round[r]:
                if e["type"] in ("OBSERVE", "POST"):
                    seen |= ngrams(words(e["content"]))
                elif e["type"] == "TALK" and e["agent"] in citizens:
                    ws = words(e["content"])
                    talk.append({"agent": e["agent"], "echo": bool(AGREE.search(e["content"])),
                                 "parrot": bool(ngrams(ws) & seen), "round": r})
        n = len(talk)
        turns = Counter(a["agent"] for a in t["private_and_public_actions"])
        spoke = Counter(e["agent"] for e in t["events"] if e["type"] == "TALK")
        print(f"{t['run']['run_id']} ({args.folder}): {n} citizen lines")
        print(f"  echo (opens by agreeing): {sum(x['echo'] for x in talk)}/{n} = {sum(x['echo'] for x in talk) / n:.2f}")
        print(f"  parroting (5+ words from news/posts): {sum(x['parrot'] for x in talk)}/{n} = "
              f"{sum(x['parrot'] for x in talk) / n:.2f}")
        silent = {a: round(1 - spoke[a] / turns[a], 2) for a in turns if turns[a]}
        print(f"  share of offered turns left silent: {silent}")
        if args.codes:
            with open(OUTPUTS / args.codes / "codes_long.csv", encoding="utf-8") as f:
                codes = list(csv.DictReader(f))
            rec = [c for c in codes if c.get("recall")]
            print(f"  recall of past episodes in coder codes: {len(rec)} of {len(codes)} "
                  f"({Counter(c['recall'] for c in rec).most_common()})")


if __name__ == "__main__":
    main()
