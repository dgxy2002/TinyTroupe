"""Reliability checks and tallies for move coding and strategy labels.

    python -m research_questions.coding_report <folder> [<folder> ...]

Prints agreement between each pair of coders, agreement with the reference labels, and per
batch tallies. Tally only what agrees well enough: a field with low kappa is noise.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
from collections.abc import Sequence
from itertools import combinations
from pathlib import Path
from typing import get_args

from .coding import CODING_PROMPT_VERSION
from .models import ConcernTag

CODE_FIELDS = ("uses_interest", "uses_right", "uses_power", "concedes", "conditional_ask")
CONCERN_TAGS = get_args(ConcernTag)
REFERENCE_PATH = Path(__file__).with_name("coding_reference_s28.json")


def cohen_kappa(first: Sequence[int], second: Sequence[int]) -> float | None:
    """Cohen's kappa for two binary raters; None when chance agreement is total."""

    total = len(first)
    if total == 0 or total != len(second):
        raise ValueError("Raters must code the same non-empty set of items.")
    observed = sum(a == b for a, b in zip(first, second)) / total
    rate_a, rate_b = sum(first) / total, sum(second) / total
    expected = rate_a * rate_b + (1 - rate_a) * (1 - rate_b)
    return None if expected == 1 else (observed - expected) / (1 - expected)


def _load_codings(folder: Path) -> dict[str, dict[str, dict]]:
    codings: dict[str, dict[str, dict]] = {}
    for directory in sorted(folder.glob("coding-*")):
        for path in sorted(directory.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("prompt_version") == CODING_PROMPT_VERSION:
                key = f"{folder.name}/{data['run_id']}"
                codings.setdefault(data["model"], {})[key] = data["coding"]
    return codings


def concern_presence(run: dict, where: str) -> set[tuple[str, str]]:
    """The (agent, tag) pairs one run shows in ``in_thoughts`` or ``in_speech``."""

    return {
        (agent["agent"], note["tag"])
        for agent in run["agents"]
        for note in agent["concerns"]
        if note[where]
    }


def _flatten(runs: dict[str, dict], run_ids: Sequence[str], field: str) -> list[int]:
    return [int(turn[field]) for run_id in run_ids for turn in runs[run_id]["turns"]]


def _kappa_text(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def report_concern_agreement(
    first: dict[str, dict], second: dict[str, dict], shared: Sequence[str]
) -> None:
    """Agreement on whether each agent shows each tag, overall and tag by tag."""

    agents = ("Agent A", "Agent B", "Agent C", "Agent D")
    for where in ("in_thoughts", "in_speech"):
        rows: dict[str, tuple[list[int], list[int]]] = {
            tag: ([], []) for tag in CONCERN_TAGS
        }
        for run_id in shared:
            present_a = concern_presence(first[run_id], where)
            present_b = concern_presence(second[run_id], where)
            for agent in agents:
                for tag in CONCERN_TAGS:
                    rows[tag][0].append(int((agent, tag) in present_a))
                    rows[tag][1].append(int((agent, tag) in present_b))
        all_a = [value for tag in CONCERN_TAGS for value in rows[tag][0]]
        all_b = [value for tag in CONCERN_TAGS for value in rows[tag][1]]
        by_tag = {
            tag: f"{_kappa_text(cohen_kappa(*rows[tag]))} ({sum(rows[tag][0])}/{sum(rows[tag][1])})"
            for tag in CONCERN_TAGS
        }
        print(f"    concerns {where}: kappa={_kappa_text(cohen_kappa(all_a, all_b))} n={len(all_a)}")
        print(f"      by tag, kappa (count a/count b): {by_tag}")
    same = sum(
        first[run_id]["arrangement"]["exists"] == second[run_id]["arrangement"]["exists"]
        for run_id in shared
    )
    print(f"    arrangement exists: same verdict in {same}/{len(shared)} runs")


def report_agreement(codings: dict[str, dict[str, dict]]) -> None:
    for first, second in combinations(sorted(codings), 2):
        shared = sorted(set(codings[first]) & set(codings[second]))
        if not shared:
            continue
        print(f"  {first} vs {second} ({len(shared)} runs):")
        for field in CODE_FIELDS:
            a, b = _flatten(codings[first], shared, field), _flatten(codings[second], shared, field)
            agree = sum(x == y for x, y in zip(a, b)) / len(a)
            print(
                f"    {field:16} agree={agree:.2f} kappa={_kappa_text(cohen_kappa(a, b))} "
                f"rates={sum(a) / len(a):.2f}/{sum(b) / len(b):.2f} n={len(a)}"
            )
        report_concern_agreement(codings[first], codings[second], shared)
    reference = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    for model, runs in sorted(codings.items()):
        matches = {
            run_id: next((key for key in runs if key.endswith(f"/{run_id}")), None)
            for run_id in reference["runs"]
        }
        shared = [run_id for run_id, key in matches.items() if key]
        if not shared:
            continue
        print(f"  {model} vs reference labels ({len(shared)} runs):")
        for index, field in enumerate(reference["fields"]):
            ours = [row[index] for run_id in shared for row in reference["runs"][run_id]]
            theirs = _flatten(runs, [matches[run_id] for run_id in shared], field)
            print(f"    {field:16} kappa={_kappa_text(cohen_kappa(ours, theirs))} n={len(ours)}")


def report_tallies(folder: Path, codings: dict[str, dict[str, dict]]) -> None:
    for model, runs in sorted(codings.items()):
        rates = {
            field: sum(_flatten(runs, sorted(runs), field)) for field in CODE_FIELDS
        }
        lines = sum(len(run["turns"]) for run in runs.values())
        settled = sum(run["arrangement"]["exists"] for run in runs.values())
        gap: collections.Counter = collections.Counter()
        thought: collections.Counter = collections.Counter()
        covered: collections.Counter = collections.Counter()
        open_at_end: collections.Counter = collections.Counter()
        for run in runs.values():
            said = concern_presence(run, "in_speech")
            for agent, tag in concern_presence(run, "in_thoughts"):
                thought[tag] += 1
                gap[tag] += (agent, tag) not in said
            covered.update(run["arrangement"]["covers"])
            open_at_end.update(run["arrangement"]["unsettled"])
        unsaid = {
            tag: f"{gap[tag]}/{thought[tag]}" for tag in sorted(thought, key=lambda t: -gap[t])
        }
        print(f"  {model}: {lines} lines, {settled}/{len(runs)} runs with an arrangement")
        print(f"    move counts: {rates}")
        print(f"    thought but never said (agent-runs): {unsaid}")
        print(f"    arrangements cover: {dict(covered)}; still open: {dict(open_at_end)}")
    labels: collections.Counter = collections.Counter()
    for path in sorted((folder / "transcripts").glob("*.json")):
        events = json.loads(path.read_text(encoding="utf-8"))["events"]
        spoken = {
            (event["round"], event["turn"], event["agent"])
            for event in events
            if event["type"] == "TALK"
        }
        for event in events:
            if event["type"] == "THINK" and (event["round"], event["turn"], event["agent"]) in spoken:
                labels.update(re.findall(r"STRATEGY:\s*([A-Z_]+)", event["content"]))
    print(f"  strategy labels on spoken turns ({sum(labels.values())}): {labels.most_common()}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folders", nargs="+", type=Path)
    args = parser.parse_args(argv)
    merged: dict[str, dict[str, dict]] = {}
    for folder in args.folders:
        print(f"\n{folder.name}")
        codings = _load_codings(folder)
        report_tallies(folder, codings)
        for model, runs in codings.items():
            merged.setdefault(model, {}).update(runs)
    print("\nAGREEMENT ACROSS ALL FOLDERS")
    report_agreement(merged)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
