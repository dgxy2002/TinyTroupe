"""Run case-study attempts in parallel on Gemini 2.5 Pro, then code them with Haiku.

Usage (from the repo root):
    python research_questions/tools/run_cases.py S46:HW1:r12:12 S48:HW3:r12:12

Each argument is SCENARIO:CELL[:VERSION[:ROUNDS]]. The output folder is
research_questions/outputs/<scenario>-case-<version>-<cell> (version defaults to v1). A folder
that already exists is skipped, so nothing is ever overwritten. ROUNDS overrides the preset's 8.
Prints the simulation-plus-evaluation cost of each run; debrief and coding costs are not counted.
"""

import glob
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUTS = REPO / "research_questions" / "outputs"


def cost(folder: str) -> float:
    total = 0.0
    for path in glob.glob(str(OUTPUTS / folder / "resources" / "*.json")):
        data = json.load(open(path, encoding="utf-8"))
        for key in ("simulation_resources", "evaluator_resources"):
            total += (data.get(key) or {}).get("cost_usd") or 0
    return total


def attempt(pair: str) -> str:
    scenario, cell, *rest = pair.split(":")
    folder = f"{scenario.lower()}-case-{rest[0] if rest else 'v1'}-{cell.lower()}"
    if (OUTPUTS / folder).exists():
        return f"{folder}: already exists, not run"
    rounds = ["--rounds", rest[1]] if len(rest) > 1 else []
    result = subprocess.run(
        [
            sys.executable, "-m", "research_questions",
            "--preset", "case-study-smell", "--scenario", scenario, "--configuration", cell,
            "--api-type", "openrouter", "--simulation-model", "google/gemini-2.5-pro",
            "--evaluator-model", "openai/gpt-5-mini", "--evaluator-max-completion-tokens", "12000",
            "--experiment-id", folder, *rounds,
        ],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode == 0:
        subprocess.run(
            [
                sys.executable, "-m", "research_questions", "--code", f"research_questions/outputs/{folder}",
                "--api-type", "openrouter", "--coding-model", "anthropic/claude-haiku-5.5",
                "--evaluator-max-completion-tokens", "12000",
            ],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    tail = [line[:160] for line in (result.stdout + result.stderr).splitlines() if "Traceback" in line or "Error:" in line][-1:]
    return f"{folder}: exit {result.returncode} ${cost(folder):.3f} {tail}"


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        for line in pool.map(attempt, sys.argv[1:]):
            print(line, flush=True)
