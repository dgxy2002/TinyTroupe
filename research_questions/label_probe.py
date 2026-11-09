"""Does a cultural label change what an agent does at a fixed moment in a dispute?

A cheap check before any full C0-C4 run. Each sample is a fresh S28 agent, built by the same
code as a real run and answered by the real ``TinyPerson.act``, at one of two moments taken
verbatim from S28-C0-R03. Between samples only three things vary: the background, whether the
name follows it, and whether the prompt's rule against acting on background is present.

The result concerns this model's sensitivity to these prompts at these moments. It says
nothing about real people, and a null result does not show that no difference exists.

    python -m research_questions.label_probe --experiment-id <id> --samples 20 --shards 6
    python -m research_questions.label_probe --analyze research_questions/outputs/<id>
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from tinytroupe.clients import client, force_api_cache, force_api_type

from .coding import MOVE_DEFINITIONS
from .models import TurnCode
from .runner import DEFAULT_OUTPUT_ROOT, configure_simulation_runtime
from .scenario_presets import BACKGROUND_CONFIGURATIONS, RUNNABLE_SCENARIOS
from .scenario_presets.common import CULTURAL_BACKGROUNDS
from .simulation import AGENT_PROMPT_PATH, create_scenario_instance, reset_simulation_state
from .storage import file_sha256, git_commit, read_json, utc_now, write_json_once


SCENARIO_ID = "S28"
SIMULATION_MODEL = "openai/gpt-5-mini"
CODING_MODEL = "anthropic/claude-haiku-5.5"
PLAN_SEED = 20261105
PERMUTATIONS = 5000

MOMENTS: dict[str, dict[str, str | None]] = {
    "B_hears_demand": {
        "role": "B",
        "other": "A",
        "own_line": None,
        "heard": "{listener} — I left that tissue packet to save this seat. Can I sit? My food's hot.",
    },
    "A_hears_refusal": {
        "role": "A",
        "other": "B",
        "own_line": "{other} — I left that tissue packet to save this seat. Can I sit? My food's hot.",
        "heard": (
            "This seat's taken — I already sat and uncovered my bowl. I can give you the "
            "seat when I finish, but I won't carry the open bowl."
        ),
    },
}
RULE_LINES = (
    "- Cultural background is one biographical fact, not a behavior instruction. Use it only when\n"
    "  genuinely relevant; do not exaggerate it, perform stereotypes, infer another person's background,\n"
    "  or announce your own label. A label alone does not establish religion, diet, language, values,\n"
    "  personality, or conflict style.\n",
    "  - **Nationality or cultural background**: treat either field as one biographical fact, not a "
    "script for behaviour. Use it only when genuinely relevant, and do not infer religion, diet, "
    "language, values, temperament, personality, or conflict style from a label alone.\n",
)
PRIMARY_OUTCOMES = ("spoke", "words", "uses_interest", "uses_right", "concedes")
EXPLORATORY_OUTCOMES = ("uses_power", "conditional_ask", "mentions_identity")
IDENTITY_TERMS = re.compile(
    r"\b(chinese|malay|indian|eurasian|cultur\w*|race|racial|ethnic\w*|religio\w*|muslim|"
    r"hindu|halal|auntie|aunty|uncle|lah|leh|singlish)\b",
    re.I,
)
ANALYSIS_PLAN = (
    "Fixed before data collection. Primary question: do the four labels differ on "
    f"{', '.join(PRIMARY_OUTCOMES)}, within moment, rule state, and name type? Permute labels "
    f"within those strata ({PERMUTATIONS} permutations), summing between-label spread across "
    "strata, with Holm correction across the primary outcomes. Secondary: the same test within "
    "rule-on and rule-off separately, labelled versus no label, and neutral versus associated "
    f"name. Exploratory and not corrected: {', '.join(EXPLORATORY_OUTCOMES)}, and male-coded "
    "versus female-coded names. uses_power and conditional_ask are exploratory because coder "
    "agreement was below 0.6. Replies are coded blind by " + CODING_MODEL + "."
)


def build_plan(samples: int) -> list[dict[str, Any]]:
    """Every sample, shuffled with a fixed seed so run order cannot track any condition."""

    conditions = [(None, "neutral")] + [
        (background, names)
        for background in CULTURAL_BACKGROUNDS
        for names in ("neutral", "associated")
    ]
    plan = [
        {
            "key": f"{moment}|{background}|{names}|{rule}|{sample}",
            "moment": moment,
            "background": background,
            "names": names,
            "rule": rule,
            "sample": sample,
        }
        for moment in MOMENTS
        for background, names in conditions
        for rule in ("on", "off")
        for sample in range(samples)
    ]
    random.Random(PLAN_SEED).shuffle(plan)
    return plan


def configuration_for(role: str, background: str | None, names: str) -> str:
    """C0 unless the name must follow the label, which needs that label's rotation."""

    if background is None or names == "neutral":
        return "C0"
    for config_id, assignment in BACKGROUND_CONFIGURATIONS.items():
        if assignment[role] == background:
            return config_id
    raise KeyError(background)


def template_without_rule(template: str) -> str:
    for line in RULE_LINES:
        if line not in template:
            raise ValueError(f"Rule text not found in the agent template: {line[:50]!r}")
        template = template.replace(line, "")
    return template


def _run_sample(item: Mapping[str, Any], rule_off_path: Path) -> dict[str, Any]:
    moment = MOMENTS[item["moment"]]
    role, other_role = str(moment["role"]), str(moment["other"])
    reset_simulation_state()
    instance = create_scenario_instance(
        RUNNABLE_SCENARIOS[SCENARIO_ID],
        configuration_for(role, item["background"], item["names"]),
    )
    person = instance.participants[role]
    other = instance.participants[other_role]
    if item["background"] and item["names"] == "neutral":
        person.include_persona_definitions({"cultural_background": item["background"]})
    if item["rule"] == "off":
        person._prompt_template_path = str(rule_off_path)
    if moment["own_line"]:
        person.store_in_memory(
            {
                "role": "assistant",
                "content": {
                    "action": {
                        "type": "TALK",
                        "content": str(moment["own_line"]).format(other=other.name),
                        "target": other.name,
                    }
                },
                "type": "action",
                "simulation_timestamp": person.iso_datetime(),
            }
        )
    person.listen(str(moment["heard"]).format(listener=person.name), source=other)
    actions = [entry["action"] for entry in person.act(return_actions=True)]
    pick = lambda kind: " ".join(
        str(action.get("content") or "") for action in actions if action.get("type") == kind
    ).strip()
    return {
        **item,
        "agent_name": person.name,
        "other_name": other.name,
        "think": pick("THINK"),
        "talk": pick("TALK"),
    }


def run_shard(output_dir: Path, shard: int, shards: int, samples: int) -> int:
    configure_simulation_runtime(
        api_type="openrouter",
        simulation_model=SIMULATION_MODEL,
        agent_max_completion_tokens=4096,
    )
    rule_off_path = output_dir / "agent_prompt_rule_off.mustache"
    path = output_dir / "records" / f"shard-{shard:02d}.jsonl"
    done = (
        {json.loads(line)["key"] for line in path.read_text(encoding="utf-8").splitlines()}
        if path.exists()
        else set()
    )
    todo = [
        item
        for index, item in enumerate(build_plan(samples))
        if index % shards == shard and item["key"] not in done
    ]
    with path.open("a", encoding="utf-8") as handle:
        for item in todo:
            try:
                record = _run_sample(item, rule_off_path)
            except Exception as error:  # Recorded, not retried: the count is reported.
                record = {**item, "error": f"{type(error).__name__}: {error}"[:300]}
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
    return 0


def launch(experiment_id: str, samples: int, shards: int, output_root: Path) -> int:
    output_dir = (output_root / experiment_id).resolve()
    (output_dir / "records").mkdir(parents=True, exist_ok=False)
    template = Path(AGENT_PROMPT_PATH).read_text(encoding="utf-8")
    (output_dir / "agent_prompt_rule_off.mustache").write_text(
        template_without_rule(template), encoding="utf-8"
    )
    write_json_once(
        output_dir / "manifest.json",
        {
            "experiment_id": experiment_id,
            "created_at": utc_now(),
            "git_commit": git_commit(),
            "scenario_id": SCENARIO_ID,
            "simulation_model": SIMULATION_MODEL,
            "coding_model": CODING_MODEL,
            "samples_per_cell": samples,
            "total_samples": len(build_plan(samples)),
            "plan_seed": PLAN_SEED,
            "agent_prompt_sha256": file_sha256(AGENT_PROMPT_PATH),
            "agent_prompt_render": "mental-state-merged-v1",
            "moments": MOMENTS,
            "analysis_plan": ANALYSIS_PLAN,
        },
    )
    workers = [
        subprocess.Popen(
            [
                sys.executable, "-m", "research_questions.label_probe",
                "--shard", str(shard), "--shards", str(shards),
                "--samples", str(samples), "--output-dir", str(output_dir),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for shard in range(shards)
    ]
    return max(worker.wait() for worker in workers)


class _ReplyCodes(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turns: list[TurnCode]


def anonymize_reply(text: str, record: Mapping[str, Any]) -> str:
    moment = MOMENTS[record["moment"]]
    aliases = {
        record["agent_name"]: f"Agent {moment['role']}",
        record["other_name"]: f"Agent {moment['other']}",
    }
    for name, alias in aliases.items():
        text = text.replace(name, alias)
    return text


def _reply_batch_text(moment_name: str, batch: Sequence[Mapping[str, Any]]) -> str:
    moment = MOMENTS[moment_name]
    speaker = f"Agent {moment['role']}"
    listener = f"Agent {moment['other']}"
    earlier = []
    if moment["own_line"]:
        earlier.append(f"{speaker}: " + str(moment["own_line"]).format(other=listener))
    earlier.append(f"{listener}: " + str(moment["heard"]).format(listener=speaker))
    replies = "\n".join(
        f"[{index}] {speaker}: {anonymize_reply(record['talk'], record)}"
        for index, record in enumerate(batch, start=1)
    )
    return (
        "These lines are separate, independent replies to the same moment. They are not a "
        "conversation. Code each on its own against only what was said before it.\n\n"
        "SAID BEFORE EACH REPLY:\n" + "\n".join(earlier) + "\n\nSPOKEN LINES:\n" + replies
    )


def code_replies(output_dir: Path, records: list[dict[str, Any]], batch_size: int = 20) -> dict:
    """Code spoken replies blind, in shuffled batches so conditions are mixed."""

    path = output_dir / "reply_codes.json"
    codes = read_json(path) if path.exists() else {}
    force_api_type("openrouter")
    force_api_cache(False)
    for moment_name in MOMENTS:
        pending = [
            record
            for record in records
            if record["moment"] == moment_name and record.get("talk") and record["key"] not in codes
        ]
        random.Random(PLAN_SEED).shuffle(pending)
        for start in range(0, len(pending), batch_size):
            batch = pending[start : start + batch_size]
            for _ in range(3):
                result = client().send_message(
                    [
                        {"role": "system", "content": MOVE_DEFINITIONS},
                        {"role": "user", "content": _reply_batch_text(moment_name, batch)},
                    ],
                    model=CODING_MODEL,
                    temperature=0.0,
                    max_completion_tokens=12000,
                    response_format=_ReplyCodes,
                    enable_pydantic_model_return=True,
                )
                parsed = (
                    result
                    if isinstance(result, _ReplyCodes)
                    else _ReplyCodes.model_validate_json(result["content"])
                )
                if [turn.line for turn in parsed.turns] == list(range(1, len(batch) + 1)):
                    break
            else:
                raise RuntimeError(f"Coder misnumbered a batch for {moment_name}.")
            for record, turn in zip(batch, parsed.turns):
                codes[record["key"]] = turn.model_dump(exclude={"line"})
            path.write_text(json.dumps(codes, ensure_ascii=False, indent=1), encoding="utf-8")
    return codes


def outcome_value(record: Mapping[str, Any], codes: Mapping[str, Any], outcome: str) -> float | None:
    talk = record.get("talk") or ""
    if outcome == "spoke":
        return float(bool(talk))
    if outcome == "mentions_identity":
        return float(bool(IDENTITY_TERMS.search(f"{record.get('think', '')} {talk}")))
    if not talk:
        return None
    if outcome == "words":
        return float(len(talk.split()))
    code = codes.get(record["key"])
    return None if code is None else float(code[outcome])


def between_group_spread(groups: Mapping[Any, Sequence[float]]) -> float:
    """Sample-weighted squared distance of each group's mean from the overall mean."""

    filled = [values for values in groups.values() if values]
    total = sum(len(values) for values in filled)
    if not total:
        return 0.0
    overall = sum(sum(values) for values in filled) / total
    return sum(len(v) * (sum(v) / len(v) - overall) ** 2 for v in filled)


def stratified_permutation_p(
    rows: Sequence[tuple[Any, Any, float]],
    permutations: int = PERMUTATIONS,
    seed: int = PLAN_SEED,
) -> float:
    """Permute group labels within strata. Rows are (stratum, group, value)."""

    strata: dict[Any, list[tuple[Any, float]]] = defaultdict(list)
    for stratum, group, value in rows:
        strata[stratum].append((group, value))

    def statistic(assignment: Mapping[Any, Sequence[tuple[Any, float]]]) -> float:
        total = 0.0
        for members in assignment.values():
            groups: dict[Any, list[float]] = defaultdict(list)
            for group, value in members:
                groups[group].append(value)
            total += between_group_spread(groups)
        return total

    observed = statistic(strata)
    rng = random.Random(seed)
    at_least = 0
    for _ in range(permutations):
        shuffled = {}
        for stratum, members in strata.items():
            labels = [group for group, _ in members]
            rng.shuffle(labels)
            shuffled[stratum] = [(label, value) for label, (_, value) in zip(labels, members)]
        at_least += statistic(shuffled) >= observed - 1e-12
    return (at_least + 1) / (permutations + 1)


def holm(p_values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    for index, (name, value) in enumerate(ordered):
        running = max(running, min(1.0, value * (len(ordered) - index)))
        adjusted[name] = running
    return adjusted


def _rows(records, codes, outcome, *, stratum, group, keep=lambda r: True):
    rows = []
    for record in records:
        value = outcome_value(record, codes, outcome)
        if value is not None and keep(record):
            rows.append((stratum(record), group(record), value))
    return rows


def _table(records, codes, outcome, group) -> dict[str, tuple[float, int]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for record in records:
        value = outcome_value(record, codes, outcome)
        if value is not None:
            grouped[str(group(record))].append(value)
    return {key: (sum(v) / len(v), len(v)) for key, v in sorted(grouped.items())}


def analyze(output_dir: Path) -> int:
    records = [
        json.loads(line)
        for path in sorted((output_dir / "records").glob("*.jsonl"))
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    failed = [record for record in records if record.get("error")]
    records = [record for record in records if not record.get("error")]
    codes = code_replies(output_dir, records)
    labelled = [record for record in records if record["background"]]
    print(f"samples={len(records)} failed={len(failed)} coded_replies={len(codes)}")
    print("\nMEANS BY LABEL (value, n)")
    for outcome in PRIMARY_OUTCOMES + EXPLORATORY_OUTCOMES:
        table = _table(records, codes, outcome, lambda r: r["background"] or "none")
        print(f"  {outcome:18}", {k: (round(v, 2), n) for k, (v, n) in table.items()})

    stratum = lambda r: (r["moment"], r["rule"], r["names"])
    primary = {
        outcome: stratified_permutation_p(
            _rows(labelled, codes, outcome, stratum=stratum, group=lambda r: r["background"])
        )
        for outcome in PRIMARY_OUTCOMES
    }
    adjusted = holm(primary)
    print("\nPRIMARY: do the four labels differ? (raw p, Holm p)")
    for outcome in PRIMARY_OUTCOMES:
        print(f"  {outcome:18} {primary[outcome]:.4f} {adjusted[outcome]:.4f}")

    print("\nSECONDARY: labels differ within each rule state, by moment (raw p)")
    for rule in ("on", "off"):
        for moment in MOMENTS:
            keep = lambda r, rule=rule, moment=moment: r["rule"] == rule and r["moment"] == moment
            result = {
                outcome: round(
                    stratified_permutation_p(
                        _rows(labelled, codes, outcome, stratum=lambda r: r["names"],
                              group=lambda r: r["background"], keep=keep)
                    ), 3,
                )
                for outcome in PRIMARY_OUTCOMES
            }
            print(f"  rule {rule:3} {moment:16} {result}")

    print("\nSECONDARY: other contrasts (raw p, then means)")
    contrasts = {
        "labelled vs none (neutral names)": (
            [r for r in records if r["names"] == "neutral"],
            lambda r: "labelled" if r["background"] else "none",
            lambda r: (r["moment"], r["rule"]),
        ),
        "neutral vs associated name": (
            labelled, lambda r: r["names"], lambda r: (r["moment"], r["rule"], r["background"]),
        ),
        "rule on vs off (labelled)": (
            labelled, lambda r: r["rule"], lambda r: (r["moment"], r["names"], r["background"]),
        ),
        "EXPLORATORY male vs female coded name": (
            [r for r in labelled if r["names"] == "associated"],
            lambda r: "male" if r["agent_name"] in ("John", "Arjun") else "female",
            lambda r: (r["moment"], r["rule"]),
        ),
    }
    for title, (subset, group, strata_of) in contrasts.items():
        print(f"  {title}")
        for outcome in PRIMARY_OUTCOMES:
            p_value = stratified_permutation_p(
                _rows(subset, codes, outcome, stratum=strata_of, group=group)
            )
            means = {k: round(v, 2) for k, (v, _) in _table(subset, codes, outcome, group).items()}
            print(f"    {outcome:18} p={p_value:.4f} {means}")
    print("\nEXPLORATORY: labels differ (raw p, uncorrected)")
    for outcome in EXPLORATORY_OUTCOMES:
        p_value = stratified_permutation_p(
            _rows(labelled, codes, outcome, stratum=stratum, group=lambda r: r["background"])
        )
        print(f"  {outcome:18} {p_value:.4f}")
    return 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment-id")
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--shards", type=int, default=6)
    parser.add_argument("--shard", type=int)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--analyze", type=Path)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.analyze:
        return analyze(args.analyze.resolve())
    if args.shard is not None:
        return run_shard(args.output_dir, args.shard, args.shards, args.samples)
    if not args.experiment_id:
        raise SystemExit("--experiment-id is required to launch a probe.")
    return launch(args.experiment_id, args.samples, args.shards, args.output_root)


if __name__ == "__main__":
    raise SystemExit(main())
