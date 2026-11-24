"""Run society simulations (research_questions/society/; design in research_questions/haze_society_design.md).

Usage (from the repo root):
    # pilot: real news for stages 1-3, then 4 free rounds
    python research_questions/tools/run_society.py --out society-hs1-pilot1 --cutoff-stage 3 --free-rounds 4 \
        --runs R01
    # forks: start free play again from a saved cutoff (the end of the real history) of run R01
    python research_questions/tools/run_society.py --out society-hs1-pilot1 --cutoff-stage 3 --free-rounds 4 \
        --runs F01 F02 --fork-from research_questions/outputs/society-hs1-pilot1/checkpoints/R01-cutoff.json

Writes research_questions/outputs/<out>/transcripts/<run>.json and .md, resources/, checkpoints/ (the
<run>-cutoff.json checkpoint is kept for forks) and a manifest. Prints each run's cost. Runs one after another.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from dotenv import load_dotenv  # noqa: E402

from research_questions.runner import configure_simulation_runtime  # noqa: E402
from research_questions.society import SOCIETY_PRESETS  # noqa: E402
from research_questions.society.engine import SOCIETY_PROMPT_PATH, preset_sha256, run_society  # noqa: E402
from research_questions.storage import file_sha256, git_commit, utc_now, write_json_replace  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, help="folder name under research_questions/outputs/")
    p.add_argument("--preset", default="HS1", choices=sorted(SOCIETY_PRESETS))
    p.add_argument("--cutoff-stage", type=int, required=True)
    p.add_argument("--free-rounds", type=int, default=4)
    p.add_argument("--runs", nargs="+", required=True, help="run ids, e.g. R01 R02")
    p.add_argument("--fork-from", type=Path, help="a <run>-cutoff.json checkpoint to start free play from")
    p.add_argument("--model", default="google/gemini-2.5-pro")
    p.add_argument("--api-type", default="openrouter")
    p.add_argument("--agent-max-completion-tokens", type=int, default=4096)
    args = p.parse_args()

    load_dotenv(REPO / ".env")
    preset = SOCIETY_PRESETS[args.preset]
    out = REPO / "research_questions" / "outputs" / args.out
    out.mkdir(parents=True, exist_ok=True)
    configure_simulation_runtime(
        api_type=args.api_type,
        simulation_model=args.model,
        agent_max_completion_tokens=args.agent_max_completion_tokens,
    )
    manifest = out / "manifest.json"
    if not manifest.exists():
        write_json_replace(
            manifest,
            {
                "kind": "society",
                "created_at": utc_now(),
                "git_commit": git_commit(),
                "preset_id": preset.preset_id,
                "preset_sha256": preset_sha256(preset),
                "agent_prompt_sha256": file_sha256(SOCIETY_PROMPT_PATH),
                "simulation_model": args.model,
                "api_type": args.api_type,
                "agent_max_completion_tokens": args.agent_max_completion_tokens,
                "cutoff_stage": args.cutoff_stage,
                "free_rounds": args.free_rounds,
            },
        )
    total = 0.0
    for run_id in args.runs:
        transcript = run_society(
            preset=preset,
            run_id=run_id,
            output_dir=out,
            cutoff_stage=args.cutoff_stage,
            free_rounds=args.free_rounds,
            simulation_model=args.model,
            fork_from=args.fork_from,
        )
        cost = transcript["run"]["simulation_resources"]["cost_usd"]
        total += cost
        print(f"{run_id}: ${cost:.2f} ({transcript['run']['simulation_resources']['calls']} calls)", flush=True)
    print(f"total ${total:.2f}")


if __name__ == "__main__":
    main()
