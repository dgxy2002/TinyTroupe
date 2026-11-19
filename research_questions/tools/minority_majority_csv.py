"""Write research_questions/minority_majority_runs.csv: one row per majority/minority run (72).

Usage (from the repo root): python research_questions/tools/minority_majority_csv.py

Combines each run's saved record (who sat where, outcome) with the run-weighted agreement scores in
outputs/majmin-s15-sonnet-a/runs.csv and outputs/majmin-s7-sonnet-a/runs.csv (two Sonnet passes averaged).
No API calls.
"""

import csv
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RQ = REPO / "research_questions"

NEEDS = {
    "smells": {
        "Chinese": "family dish: fried salted fish",
        "Eurasian": "family dish: devil curry",
        "Indian": "family dish: fish curry",
        "Malay": "family dish: sambal belacan",
    },
    "bereavement": {
        "Chinese": "Buddhist: grandmother's wake, monks chanting, two nights",
        "Eurasian": "Catholic: rosary at the wake tonight, funeral Mass and burial tomorrow",
        "Indian": "Hindu: prayers and rites, cremation tomorrow",
        "Malay": "Muslim: burial today before sunset, tahlil prayers in the evenings",
    },
}


def transcript(folder: str) -> dict:
    for root in ("outputs", "outputs_old"):
        files = list((RQ / root / folder / "transcripts").glob("*.json"))
        if files:
            return json.loads(files[0].read_text(encoding="utf-8"), strict=False)
    raise FileNotFoundError(folder)


def main() -> None:
    rows = []
    for scenario, path in (("smells", "majmin-s15-sonnet-a"), ("bereavement", "majmin-s7-sonnet-a")):
        for score in csv.DictReader((RQ / "outputs" / path / "runs.csv").open(encoding="utf-8")):
            folder = score["folder"]
            data = transcript(folder)
            run, agents = data["run"], data["scenario"]["agents"]
            match = re.search(r"-mm(\d)-", folder)
            start, end = float(score["mixed_start"]), float(score["mixed_end"])
            rows.append({
                "folder": folder,
                "location": "outputs_old" if "-r12-" in folder else "outputs",
                "scenario": "15 cooking smells" if scenario == "smells" else "7 bereavement",
                "scenario_id": run["scenario_id"],
                "cell": run["configuration_id"],
                "run": int(match.group(1)) if match else 1,
                "majority": score["majority"],
                "minority_D": score["minority"],
                "agent_A": agents["A"]["display_name"],
                "agent_B": agents["B"]["display_name"],
                "agent_C": agents["C"]["display_name"],
                "agent_D": agents["D"]["display_name"],
                "D_need": NEEDS[scenario][score["minority"]],
                "outcome": score["status"],
                "majority_D_start": round(start, 3),
                "majority_D_end": round(end, 3),
                "majority_D_change": round(float(score["mixed_change"]), 3),
                "majority_D_standardised_change": round((end - start) / (1 - start), 3),
                "same_culture_start": round(float(score["same_start"]), 3),
                "same_culture_end": round(float(score["same_end"]), 3),
                "same_culture_change": round(float(score["same_change"]), 3),
                "share_D_moved": round(float(score["moved_D"]), 3),
                "share_majority_moved": round(float(score["moved_majority"]), 3),
                "share_both_moved": round(float(score["moved_both"]), 3),
                "D_fairness": score["D_fairness"],
                "majority_fairness": score["majority_fairness"],
            })
    rows.sort(key=lambda r: (r["scenario"], r["majority"], r["minority_D"], r["run"]))
    out = RQ / "minority_majority_runs.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} runs written to {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
