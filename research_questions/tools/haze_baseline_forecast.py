"""Baseline for the haze forecasts: ask the simulator's model directly what happens next (2026-11-26).

The society runs give 13 agents the real news up to a cutoff and let them act. This baseline gives the same news to
the same model (Gemini 2.5 Pro, via OpenRouter, no tools or web search) once per sample and asks for a forecast of
the next ten days. If the society does not beat this, the society adds nothing for prediction.

Usage (from the repo root):
    python research_questions/tools/haze_baseline_forecast.py --out <new-folder> --cutoff 4 --samples 10

Writes research_questions/outputs/<folder>/forecasts/B01.txt ..., usage.json and the prompt; refuses an existing folder.
Score with tools/haze_forecast_coder.py.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from research_questions.society import SOCIETY_PRESETS  # noqa: E402

QUESTION = (
    "It is {date}. Below is the news about the Southeast Asian haze so far this year, in order. Based on it, "
    "forecast what will happen over the next ten days: what the governments of Indonesia, Singapore, Malaysia and "
    "Brunei will do or say, and how ordinary people in each country will react. Give concrete, specific predictions "
    "(who does what), not general statements."
)


def prompt(cutoff: int) -> str:
    stages = SOCIETY_PRESETS["HS4"].stages[:cutoff]
    news = "\n\n".join(f"News update {s.number}:\n{s.news}" for s in stages)
    return QUESTION.format(date=stages[-1].news.split(".")[0].replace("It is now ", "").replace("It is ", "")) + \
        "\n\n" + news


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--cutoff", type=int, default=4)
    p.add_argument("--samples", type=int, default=10)
    p.add_argument("--model", default="google/gemini-2.5-pro")
    args = p.parse_args()
    load_dotenv(REPO / ".env")
    out = REPO / "research_questions" / "outputs" / args.out
    if out.exists():
        sys.exit(f"{out} exists; choose a new --out")
    (out / "forecasts").mkdir(parents=True)
    text = prompt(args.cutoff)
    (out / "prompt.txt").write_text(text, encoding="utf-8")
    usage_all, total = [], 0.0
    for i in range(1, args.samples + 1):
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
            json={"model": args.model, "messages": [{"role": "user", "content": text}], "max_tokens": 8000,
                  "usage": {"include": True}},
            timeout=300,
        )
        r.raise_for_status()
        resp = r.json()
        (out / "forecasts" / f"B{i:02d}.txt").write_text(resp["choices"][0]["message"]["content"], encoding="utf-8")
        usage = resp.get("usage", {})
        usage_all.append(usage)
        total += usage.get("cost") or 0
        print(f"B{i:02d}: ${usage.get('cost') or 0:.4f}", flush=True)
    (out / "usage.json").write_text(json.dumps({"model": args.model, "cutoff": args.cutoff, "usage": usage_all,
                                                "total_cost": total}, indent=2), encoding="utf-8")
    print(f"total ${total:.4f}")


if __name__ == "__main__":
    main()
