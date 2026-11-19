"""List every simulation run in outputs/ and outputs_old/ with the settings it used, one row per run.

Usage (from the repo root):
    python research_questions/tools/run_inventory.py

Writes research_questions/all_runs.csv. Everything is read from each run's saved record (transcript JSON,
manifest and evaluation), so a row shows what was actually run. No API calls.
"""

import csv
import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RQ = REPO / "research_questions"

# Numbered scenarios of scenarios.md, by scenario ID. Anything else is early development or a method test.
NUMBERED = {
    **{f"S{n}": "0 Pan and incense" for n in range(36, 42)},
    **{f"S{n}": "1 Housewarming drinks" for n in range(42, 51)},
    **{f"S{n}": "3 Dinner rota" for n in range(51, 55)},
    **{f"S{n}": "7 Bereavement" for n in [*range(55, 59), *range(111, 123)]},
    **{f"S{n}": "2 Living-room corner" for n in range(59, 63)},
    **{f"S{n}": "4 Festival-week roster" for n in range(63, 71)},
    **{f"S{n}": "5 Farewell lunch" for n in range(71, 75)},
    **{f"S{n}": "6 Uniform rule" for n in range(75, 79)},
    **{f"S{n}": "8 Void deck wake" for n in range(79, 82)},
    **{f"S{n}": "10 Meeting language" for n in range(82, 86)},
    **{f"S{n}": "11 Early-morning noise" for n in range(86, 90)},
    **{f"S{n}": "12 Weekly slot" for n in range(90, 94)},
    **{f"S{n}": "13 Spare office room" for n in range(94, 98)},
    **{f"S{n}": "15 Cooking smells" for n in range(98, 111)},
}
EARLY = {"S02": "S02 kitchen (original)", "S04": "S04 chope (original)", "S06": "S06 hawker order (original)"}


def scenario_name(sid: str) -> str:
    number = int(sid[1:])
    if sid in NUMBERED:
        return NUMBERED[sid]
    if sid in EARLY:
        return EARLY[sid]
    if 12 <= number <= 20:
        return "S02 kitchen variant"
    if 21 <= number <= 29:
        return "S04 chope variant"
    if number == 30:
        return "Shared flat (S30)"
    if number == 31:
        return "Pork in the shared pan (S31)"
    if 32 <= number <= 35:
        return "Smell tests (S32-S35)"
    return ""


def group(sid: str, folder: str) -> str:
    number = int(sid[1:])
    if number <= 29:
        return "1 early development"
    if number <= 35:
        return "2 culture-method tests"
    if number >= 102 or "-mm" in folder:
        return "5 majority/minority"
    return "3 case study"


def variant(sid: str, title: str) -> str:
    if int(sid[1:]) < 36:
        return ""
    return title.split(": ", 1)[1] if ": " in title else title


def read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"), strict=False)


def main() -> None:
    rows = []
    for transcript in glob.glob(str(RQ / "outputs*" / "*" / "transcripts" / "*.json")):
        path = Path(transcript)
        run_folder = path.parents[1]
        data = read_json(transcript)
        run, scenario = data["run"], data["scenario"]
        sid, run_id, folder = run["scenario_id"], run["run_id"], run_folder.name
        manifest = run_folder / "manifest.json"
        render = read_json(str(manifest)).get("agent_prompt_render", "") if manifest.exists() else ""

        outcome, evaluator, note = "not evaluated", "", []
        rescored = run_folder / "evaluations-conflict-trajectory-rubric-v2.6" / f"{run_id}.json"
        original = run_folder / "evaluations" / f"{run_id}.json"
        for source in (rescored, original):
            if source.exists():
                evaluation = read_json(str(source))
                outcome = evaluation["evaluation"].get("final_status", "")
                evaluator = evaluation.get("evaluator", {}).get("prompt_version", "")
                break
        if rescored.exists() and original.exists():
            first = read_json(str(original))
            note.append(f"re-scored with v2.6; original {first['evaluator'].get('prompt_version')}: "
                        f"{first['evaluation'].get('final_status')}")
        if "-r12b-" in folder or "-r12c-" in folder:
            note.append("second or third attempt")
        if sid in ("S98", "S99", "S100") and "-r12-" in folder:
            note.append("also run 1 of its 3-Eurasian majority/minority room")
        if int(sid[1:]) <= 27 and render != "mental-state-merged-v1":
            note.append("blank-prompt bug: not evidence")

        agents = {}
        for role in "ABCD":
            agent = scenario["agents"][role]
            culture = agent.get("cultural_background")
            name = agent.get("display_name") or "(name not recorded)"
            agents[role] = f"{name} ({culture})" if culture else name

        rows.append({
            "folder": folder,
            "location": run_folder.parent.name,
            "run_id": run_id,
            "date": (run.get("started_at") or "")[:10],
            "group": group(sid, folder),
            "scenario_id": sid,
            "scenario": scenario_name(sid),
            "variant": variant(sid, scenario["title"]),
            "title": scenario["title"],
            "cell": run["configuration_id"],
            "agent_A": agents["A"],
            "agent_B": agents["B"],
            "agent_C": agents["C"],
            "agent_D": agents["D"],
            "simulator": run.get("simulation_model", ""),
            "rounds": run.get("rounds", ""),
            "outcome": outcome,
            "evaluator": evaluator,
            "prompt_fix": "yes" if render == "mental-state-merged-v1" else "no",
            "note": "; ".join(note),
        })

    rows.sort(key=lambda r: (r["group"], int(r["scenario_id"][1:]), r["folder"], r["run_id"]))
    out = RQ / "all_runs.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} runs written to {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
