"""Measurement helpers for repeated runs of the chope scenario.

The module deliberately separates reproducible, observable counts from the
structured LLM judgement used for concepts such as compromise and mediation.
That separation makes it possible to audit every scored construct against the
saved public transcript.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from statistics import fmean, pstdev
from typing import Dict, Iterable, List, Literal, Mapping, Optional, Sequence

from pydantic import BaseModel, Field

from tinytroupe.clients import client


PARTICIPANT_NAMES = ("Mr Lim", "Rachel Pereira", "Nur Aisyah", "Arjun")
OUTCOMES = ("consensus", "compromise", "avoidance", "escalation", "unresolved")
EXECUTION_MODES = ("outcome", "stress")

CORE_BINARY_METRICS = (
    "conflict_emerged",
    "resolution_achieved",
    "norm_recognized",
    "rachel_acknowledged_norm",
    "mediator_emerged",
    "immediate_capitulation",
    "premature_yield",
    "age_deference",
)
CORE_CONTINUOUS_METRICS = (
    "resolution_turn_censored",
    "persona_adherence_mean",
    "perspective_diversity",
)

MARKER_PATTERNS = {
    "singlish": (
        r"\blah\b",
        r"\bleh\b",
        r"\blor\b",
        r"\bpaiseh\b",
        r"\bcan or not\b",
        r"\balready\b",
        r"\bthis one\b",
    ),
    "apology": (
        r"\bsorry\b",
        r"\bapologi[sz](?:e|ed|ing|ation)\b",
        r"\bmy apologies\b",
        r"\bpaiseh\b",
    ),
    "norm_reference": (
        r"\bchope(?:d|ing)?\b",
        r"\breserv(?:e|ed|ing|ation)\b",
        r"\bsav(?:e|ed|ing) (?:the |a )?(?:seat|table)\b",
        r"\btissue (?:packet )?(?:means|shows|marks)\b",
        r"\btable got people\b",
    ),
    "direct_disagreement": (
        r"\bno\b",
        r"\bi disagree\b",
        r"\bthat(?:'s| is) not (?:right|fair|true)\b",
        r"\byou (?:should not|shouldn't|cannot|can't)\b",
    ),
    "mitigation": (
        r"\bperhaps\b",
        r"\bmaybe\b",
        r"\bi understand\b",
        r"\bwould you mind\b",
        r"\bcould we\b",
        r"\blet(?:'s| us)\b",
    ),
    "code_switch": (
        r"\baiyoh?\b",
        r"\bwah\b",
        r"\bwalao\b",
        r"\bcan lah\b",
        r"\bterima kasih\b",
        r"\b谢谢\b",
        r"\bநன்றி\b",
    ),
}


class EvidenceItem(BaseModel):
    category: str
    agent: Optional[str] = None
    quote: str = Field(min_length=1, max_length=400)
    turn: Optional[int] = Field(default=None, ge=1)


class PersonaAdherence(BaseModel):
    mr_lim: int = Field(ge=0, le=9)
    rachel: int = Field(ge=0, le=9)
    nur_aisyah: int = Field(ge=0, le=9)
    arjun: int = Field(ge=0, le=9)


class ChopeEvaluation(BaseModel):
    """One auditable judgement of a completed public interaction."""

    conflict_emerged: bool
    resolution_achieved: bool
    outcome: Literal[
        "consensus", "compromise", "avoidance", "escalation", "unresolved"
    ]
    resolution_turn: Optional[int] = Field(default=None, ge=1)
    norm_recognized: bool
    rachel_acknowledged_norm: bool
    first_norm_recognizer: Optional[
        Literal["Mr Lim", "Rachel Pereira", "Nur Aisyah", "Arjun"]
    ] = None
    mediator_emerged: bool
    mediator_identity: Optional[
        Literal["Mr Lim", "Rachel Pereira", "Nur Aisyah", "Arjun"]
    ] = None
    resolution_initiator: Optional[
        Literal["Mr Lim", "Rachel Pereira", "Nur Aisyah", "Arjun"]
    ] = None
    immediate_capitulation: bool
    premature_yield: bool
    perspective_diversity: int = Field(ge=1, le=4)
    age_deference: bool
    persona_adherence: PersonaAdherence
    boundary_violations: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(min_length=1, max_length=12)
    confidence: float = Field(ge=0.0, le=1.0)


def flatten_actions(actions_over_time: Sequence[Mapping]) -> List[dict]:
    """Flatten TinyWorld actions while retaining round, turn, and speaker."""

    events: List[dict] = []
    turn = 0
    for round_number, round_actions in enumerate(actions_over_time, start=1):
        if not isinstance(round_actions, Mapping):
            continue
        for agent_name, agent_actions in round_actions.items():
            turn += 1
            for action_index, action_record in enumerate(agent_actions or [], start=1):
                action = action_record.get("action", action_record)
                if not isinstance(action, Mapping):
                    continue
                events.append(
                    {
                        "round": round_number,
                        "turn": turn,
                        "agent": agent_name,
                        "action_index": action_index,
                        "type": str(action.get("type", "UNKNOWN")).upper(),
                        "content": str(action.get("content") or ""),
                        "target": action.get("target"),
                    }
                )
    return events


def public_events(events: Iterable[Mapping]) -> List[dict]:
    """Return observable actions; private cognition is intentionally excluded."""

    private_types = {"THINK", "THOUGHT", "INTERNAL_MONOLOGUE"}
    return [dict(event) for event in events if event.get("type") not in private_types]


def public_transcript_text(events: Iterable[Mapping]) -> str:
    lines = []
    for event in public_events(events):
        content = str(event.get("content") or "").strip()
        if content:
            lines.append(
                f"[round {event.get('round')}, turn {event.get('turn')}] "
                f"{event.get('agent')} ({event.get('type')}): {content}"
            )
    return "\n".join(lines)


def detect_practical_resolution(events: Iterable[Mapping]) -> Optional[dict]:
    """Return a conservative, deterministic early-stop signal.

    The detector deliberately recognizes only explicit practical commitments by
    the two principals. Norm acknowledgement, apologies, mediator suggestions,
    conditional offers, and generic claims that an issue is "settled" do not
    stop a run on their own. This keeps outcome-mode stopping auditable and
    avoids adding an unreliable or costly LLM judge call after every round.
    """

    talks = sorted(
        (
            dict(event)
            for event in events
            if event.get("type") == "TALK"
            and event.get("agent") in {"Mr Lim", "Rachel Pereira"}
            and str(event.get("content") or "").strip()
        ),
        key=lambda event: int(event.get("turn") or 0),
    )

    def normalized(event: Mapping) -> str:
        return " ".join(str(event.get("content") or "").lower().split())

    def signal(kind: str, *evidence: Mapping) -> dict:
        final = evidence[-1]
        outcome_by_kind = {
            "rachel_commits_to_move": "consensus",
            "mr_lim_commits_to_other_table": "avoidance",
            "mr_lim_takes_seat_rachel_confirms": "consensus",
            "principals_commit_to_share": "compromise",
        }
        return {
            "detected": True,
            "kind": kind,
            "outcome": outcome_by_kind[kind],
            "turn": int(final.get("turn") or 0),
            "evidence": [
                {
                    "agent": item.get("agent"),
                    "turn": int(item.get("turn") or 0),
                    "quote": str(item.get("content") or "").strip(),
                }
                for item in evidence
            ],
        }

    candidates = []
    rachel_move = re.compile(
        r"\b(?:i(?:['’�]ll| will)|let me)\s+(?:"
        r"move(?:\s+(?:aside|over|now|away|to\s+(?:another|a different)\s+"
        r"(?:seat|table|spot)))|slide\s+over|find\s+(?:another|a different)\s+"
        r"(?:seat|table|spot))\b"
    )
    mr_lim_relinquishes = re.compile(
        r"\bi(?:['’�]ll| will)\s+(?:look|find|go)\s+for\s+"
        r"(?:another|a different)\s+(?:seat|table|spot)\b"
    )
    mr_lim_takes_seat = re.compile(
        r"\bi\s+(?:will\s+|['’�]ll\s+)?take\s+the\s+(?:seat|spot)\b"
    )
    rachel_confirms = re.compile(
        r"\b(?:glad\s+(?:that(?:'s| is)\s+)?sorted|okay|no problem|"
        r"that(?:'s| is) fine)\b"
    )
    share_mention = re.compile(r"\bshar(?:e|ing)\b")
    direct_share_commitment = re.compile(
        r"\b(?:we(?:['’�]ll| will| shall)\s+share(?:\s+the\s+table)?|"
        r"let(?:'s| us)\s+share(?:\s+the\s+table)?|"
        r"sharing(?:\s+the\s+table)?\s+is\s+(?:fine|okay))\b"
    )

    for event in talks:
        text = normalized(event)
        if event.get("agent") == "Rachel Pereira" and rachel_move.search(text):
            candidates.append(signal("rachel_commits_to_move", event))
        if event.get("agent") == "Mr Lim" and mr_lim_relinquishes.search(text):
            candidates.append(signal("mr_lim_commits_to_other_table", event))

    for index, event in enumerate(talks):
        if event.get("agent") != "Mr Lim" or not mr_lim_takes_seat.search(
            normalized(event)
        ):
            continue
        confirmation = next(
            (
                later
                for later in talks[index + 1 :]
                if later.get("agent") == "Rachel Pereira"
                and rachel_confirms.search(normalized(later))
            ),
            None,
        )
        if confirmation:
            candidates.append(
                signal("mr_lim_takes_seat_rachel_confirms", event, confirmation)
            )

    for index, event in enumerate(talks):
        if not share_mention.search(normalized(event)):
            continue
        confirmation = next(
            (
                later
                for later in talks[index + 1 :]
                if later.get("agent") != event.get("agent")
                and direct_share_commitment.search(normalized(later))
            ),
            None,
        )
        if confirmation:
            candidates.append(signal("principals_commit_to_share", event, confirmation))

    return min(candidates, key=lambda item: item["turn"]) if candidates else None


def transcript_markdown(events: Iterable[Mapping]) -> str:
    lines = ["# Chope simulation transcript", ""]
    current_round = None
    for event in events:
        if event.get("round") != current_round:
            current_round = event.get("round")
            lines.extend((f"## Round {current_round}", ""))
        content = str(event.get("content") or "").strip().replace("\n", " ")
        lines.append(
            f"- **Turn {event.get('turn')} · {event.get('agent')} · "
            f"{event.get('type')}**: {content}"
        )
    lines.append("")
    return "\n".join(lines)


def compute_observable_metrics(events: Iterable[Mapping]) -> dict:
    """Count transcript-level signals without interpreting intentions."""

    visible = public_events(events)
    counts = Counter(event.get("type", "UNKNOWN") for event in visible)
    text = "\n".join(str(event.get("content") or "") for event in visible).lower()
    result = {
        "observable_action_count": len(visible),
        "talk_action_count": counts["TALK"],
        "public_action_type_counts": dict(sorted(counts.items())),
    }
    for name, patterns in MARKER_PATTERNS.items():
        result[f"{name}_count"] = sum(
            len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns
        )
    result["speaking_agents"] = len(
        {
            event.get("agent")
            for event in visible
            if event.get("type") == "TALK" and event.get("content")
        }
    )
    talk_by_agent = defaultdict(list)
    for event in visible:
        if event.get("type") == "TALK" and event.get("content"):
            normalized = " ".join(
                re.findall(r"[a-z0-9]+", str(event["content"]).lower())
            )
            talk_by_agent[event.get("agent")].append(normalized)

    exact_pairs = 0
    near_pairs = 0
    max_similarity = 0.0
    for utterances in talk_by_agent.values():
        for left_index, left in enumerate(utterances):
            for right in utterances[left_index + 1 :]:
                similarity = SequenceMatcher(None, left, right).ratio()
                max_similarity = max(max_similarity, similarity)
                if left == right:
                    exact_pairs += 1
                if similarity >= 0.85:
                    near_pairs += 1
    result["exact_repeated_talk_pair_count"] = exact_pairs
    result["near_repeated_talk_pair_count"] = near_pairs
    result["max_same_agent_talk_similarity"] = round(max_similarity, 4)
    return result


def evaluate_chope_run(
    events: Iterable[Mapping],
    judge_model: str,
    *,
    max_completion_tokens: int = 6000,
) -> ChopeEvaluation:
    """Apply the fixed rubric using exactly one structured evaluator call."""

    transcript = public_transcript_text(events)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a conservative research coder. Score only behavior that is "
                "observable in the supplied transcript. Do not infer private beliefs. "
                "Treat the interaction as resolved only when an accepted practical "
                "outcome is evident. Outcome labels are mutually exclusive: consensus "
                "means the principal parties explicitly accept the same interpretation "
                "and outcome without a negotiated concession; compromise means they accept "
                "an accommodation in which at least one party changes or gives up part of "
                "their initially desired seating outcome, even if they later agree on the "
                "norm; avoidance means someone exits "
                "or yields without an explicit mutual resolution; escalation means the "
                "disagreement materially intensifies; unresolved means there is no clear "
                "endpoint or the evidence is insufficient. Conflict emerged requires an "
                "expressed incompatible claim or objection, not merely the triggering event. "
                "Resolution achieved requires an explicitly mutual practical outcome; a topic "
                "change or one-sided yield is not enough. Do not infer acceptance merely from "
                "phrases such as 'no problem' when the seating issue was ignored. "
                "Norm recognized requires an observable reference to the tissue packet as "
                "a reservation/chope convention. "
                "A mediator must actively help the other parties reach an outcome. "
                "Immediate capitulation means a principal party yields before expressing "
                "their own position. Premature yield means a principal abandons their stated "
                "position within their first two speaking turns without acknowledgment from "
                "the other party or an explicit negotiated outcome. Perspective diversity is "
                "the number (1-4) of "
                "meaningfully distinct viewpoints voiced. Boundary violations include "
                "impossible knowledge, broken scenario facts, repeated/empty content, "
                "stereotype caricature, or implausible role/persona behavior. Every major "
                "judgement must have a short verbatim evidence quote and its agent turn. "
                "Use no more than 12 evidence items."
            ),
        },
        {
            "role": "user",
            "content": (
                "Code this Singapore hawker-centre interaction. Immutable event facts: Mr Lim "
                "placed his unopened tissue packet on the table intending to reserve the seat, "
                "then left to buy food. Rachel found the otherwise empty table, moved the packet "
                "aside, and sat down. Nur Aisyah and Arjun observed Rachel move the packet; they "
                "did not observe her place it and initially did not know Mr Lim's intention. "
                "Flag claims that contradict these facts or reveal unavailable knowledge. "
                "Persona anchors: Mr Lim "
                "is moderately assertive and practical; Rachel is independent-minded and "
                "less familiar with chope etiquette; Nur Aisyah tends toward tactful "
                "mediation; Arjun is observant, direct, and open to local norms. A score "
                "of 0 means strongly contradicts the persona, 5 means mixed or insufficient "
                "evidence, and 9 requires repeated, distinctive evidence of strong consistency. "
                "Do not award above 5 to a mostly silent agent; repeated or clearly "
                "persona-inconsistent behavior should score 4 or below. Resolution turn "
                "refers to the numbered agent turn where an "
                "accepted outcome first becomes evident.\n\nPUBLIC TRANSCRIPT:\n"
                + (transcript or "[No public actions recorded]")
            ),
        },
    ]
    result = client().send_message(
        messages,
        model=judge_model,
        temperature=1.0,
        max_completion_tokens=max_completion_tokens,
        response_format=ChopeEvaluation,
        enable_pydantic_model_return=True,
    )
    if isinstance(result, ChopeEvaluation):
        return result
    if isinstance(result, Mapping):
        if isinstance(result.get("content"), str):
            return ChopeEvaluation.model_validate_json(result["content"])
        return ChopeEvaluation.model_validate(result)
    raise RuntimeError("Chope evaluator did not return a valid structured result.")


def evaluation_metrics(evaluation: ChopeEvaluation, max_turns: int = 12) -> dict:
    data = evaluation.model_dump(mode="json")
    scores = data.pop("persona_adherence")
    data["persona_adherence"] = scores
    data["persona_adherence_mean"] = fmean(scores.values())
    data["resolution_turn_censored"] = (
        evaluation.resolution_turn if evaluation.resolution_turn is not None else max_turns + 1
    )
    return data


def _binary_rate(rows: Sequence[Mapping], key: str) -> float:
    return fmean(1.0 if _convergence_value(row, key) else 0.0 for row in rows)


def _convergence_value(row: Mapping, key: str):
    """Prefer deterministic settlement fields for primary convergence signals."""

    deterministic_key = {
        "resolution_achieved": "deterministic_resolution_achieved",
        "resolution_turn_censored": "deterministic_resolution_turn_censored",
    }.get(key)
    if deterministic_key and row.get(deterministic_key) is not None:
        return row.get(deterministic_key)
    return row.get(key)


def _standardized_mean_difference(
    current: Sequence[Mapping], previous: Sequence[Mapping], key: str
) -> float:
    current_values = [float(_convergence_value(row, key)) for row in current]
    previous_values = [float(_convergence_value(row, key)) for row in previous]
    delta = abs(fmean(current_values) - fmean(previous_values))
    pooled = math.sqrt(
        (pstdev(current_values) ** 2 + pstdev(previous_values) ** 2) / 2.0
    )
    if pooled == 0:
        return 0.0 if delta == 0 else math.inf
    return delta / pooled


def _outcome_distribution(rows: Sequence[Mapping]) -> dict:
    total = len(rows)
    counts = Counter(
        row.get("deterministic_outcome") or row.get("outcome", "unresolved")
        for row in rows
    )
    return {outcome: counts[outcome] / total for outcome in OUTCOMES}


def _cosine_distance(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0 if list(left) == list(right) else 1.0
    return 1.0 - numerator / (left_norm * right_norm)


def _centroid(vectors: Sequence[Sequence[float]]) -> List[float]:
    if not vectors:
        return []
    width = len(vectors[0])
    if any(len(vector) != width for vector in vectors):
        raise ValueError("All transcript embeddings must have the same dimensions.")
    return [fmean(vector[index] for vector in vectors) for index in range(width)]


def compute_convergence(
    rows: Sequence[Mapping],
    embeddings_by_run: Optional[Mapping[str, Sequence[float]]] = None,
    *,
    min_runs: int = 10,
    batch_size: int = 5,
    max_runs: int = 30,
    outcome_tvd_threshold: float = 0.10,
    binary_change_threshold: float = 0.10,
    continuous_smd_threshold: float = 0.20,
    semantic_distance_threshold: float = 0.05,
) -> List[dict]:
    """Compare cumulative checkpoints and require two consecutive passes.

    The first checkpoint is recorded as a baseline. It cannot pass because no
    prior checkpoint exists; therefore convergence cannot be declared before
    ``min_runs + 2 * batch_size`` runs.
    """

    if min_runs < batch_size or batch_size < 1:
        raise ValueError("min_runs must be >= batch_size and batch_size must be positive")
    usable = list(rows)[:max_runs]
    checkpoints = range(min_runs, len(usable) + 1, batch_size)
    records: List[dict] = []
    consecutive_passes = 0

    for n in checkpoints:
        current = usable[:n]
        previous_n = n - batch_size
        record = {
            "n": n,
            "previous_n": previous_n if previous_n >= min_runs else None,
            "is_baseline": previous_n < min_runs,
            "outcome_tvd": None,
            "max_binary_rate_change": None,
            "max_continuous_smd": None,
            "semantic_centroid_distance": None,
            "semantic_available": False,
            "criteria_passed": False,
            "consecutive_passes": 0,
            "converged": False,
        }
        if previous_n < min_runs:
            records.append(record)
            continue

        previous = usable[:previous_n]
        current_outcomes = _outcome_distribution(current)
        previous_outcomes = _outcome_distribution(previous)
        record["outcome_tvd"] = 0.5 * sum(
            abs(current_outcomes[key] - previous_outcomes[key]) for key in OUTCOMES
        )
        record["max_binary_rate_change"] = max(
            abs(_binary_rate(current, key) - _binary_rate(previous, key))
            for key in CORE_BINARY_METRICS
        )
        record["max_continuous_smd"] = max(
            _standardized_mean_difference(current, previous, key)
            for key in CORE_CONTINUOUS_METRICS
        )

        semantic_pass = True
        if embeddings_by_run is not None:
            current_vectors = [
                embeddings_by_run[row["run_id"]]
                for row in current
                if row.get("run_id") in embeddings_by_run
            ]
            previous_vectors = [
                embeddings_by_run[row["run_id"]]
                for row in previous
                if row.get("run_id") in embeddings_by_run
            ]
            if len(current_vectors) == len(current) and len(previous_vectors) == len(previous):
                record["semantic_available"] = True
                record["semantic_centroid_distance"] = _cosine_distance(
                    _centroid(current_vectors), _centroid(previous_vectors)
                )
                semantic_pass = (
                    record["semantic_centroid_distance"]
                    <= semantic_distance_threshold
                )
            else:
                semantic_pass = False

        record["criteria_passed"] = bool(
            record["outcome_tvd"] <= outcome_tvd_threshold
            and record["max_binary_rate_change"] <= binary_change_threshold
            and record["max_continuous_smd"] <= continuous_smd_threshold
            and semantic_pass
        )
        consecutive_passes = consecutive_passes + 1 if record["criteria_passed"] else 0
        record["consecutive_passes"] = consecutive_passes
        record["converged"] = consecutive_passes >= 2
        records.append(record)

    return records


def boundary_events(run_record: Mapping) -> List[dict]:
    """Expand failures and rubric violations into queryable event records."""

    events = []
    run_id = run_record.get("run_id")
    model = run_record.get("model")
    if run_record.get("status") != "completed":
        events.append(
            {
                "run_id": run_id,
                "model": model,
                "category": "run_failure",
                "detail": run_record.get("error") or "Run did not complete.",
            }
        )
    for detail in run_record.get("boundary_violations") or []:
        events.append(
            {
                "run_id": run_id,
                "model": model,
                "category": "evaluator_boundary_violation",
                "detail": detail,
            }
        )
    if run_record.get("near_repeated_talk_pair_count", 0):
        events.append(
            {
                "run_id": run_id,
                "model": model,
                "category": "deterministic_repetitive_dialogue",
                "detail": (
                    f"Detected {run_record['near_repeated_talk_pair_count']} same-agent "
                    "TALK pair(s) with at least 0.85 normalized similarity."
                ),
            }
        )
    deterministic_signal_available = "deterministic_resolution_achieved" in run_record
    if deterministic_signal_available and "resolution_achieved" in run_record:
        stop_detected = bool(run_record.get("deterministic_resolution_achieved"))
        evaluator_resolved = bool(run_record.get("resolution_achieved"))
        if stop_detected != evaluator_resolved:
            events.append(
                {
                    "run_id": run_id,
                    "model": model,
                    "category": "resolution_source_disagreement",
                    "detail": (
                        "Deterministic practical-resolution signal was "
                        f"{'present' if stop_detected else 'absent'}, while the final "
                        "structured evaluator marked resolution as "
                        f"{'achieved' if evaluator_resolved else 'not achieved'}."
                    ),
                }
            )
        elif stop_detected:
            deterministic_outcome = run_record.get("deterministic_outcome")
            evaluator_outcome = run_record.get("outcome")
            if deterministic_outcome != evaluator_outcome:
                events.append(
                    {
                        "run_id": run_id,
                        "model": model,
                        "category": "outcome_source_disagreement",
                        "detail": (
                            f"Deterministic outcome was {deterministic_outcome!r}, "
                            f"while the evaluator outcome was {evaluator_outcome!r}."
                        ),
                    }
                )
    if run_record.get("exact_cost_complete") is False:
        events.append(
            {
                "run_id": run_id,
                "model": model,
                "category": "missing_exact_cost",
                "detail": "At least one API call lacked exact OpenRouter cost metadata.",
            }
        )
    failed_calls = (run_record.get("total_resources") or {}).get("failed_calls", 0)
    if failed_calls:
        error_types = (run_record.get("total_resources") or {}).get(
            "call_error_types", []
        )
        events.append(
            {
                "run_id": run_id,
                "model": model,
                "category": "billed_api_retry",
                "detail": (
                    f"{failed_calls} billed API call(s) failed before a usable parsed "
                    f"response. Error types: {', '.join(error_types) or 'unknown'}."
                ),
            }
        )
    return events


def json_dumps(value) -> str:
    """Stable JSON representation used by JSONL writers and tests."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


__all__ = [
    "CORE_BINARY_METRICS",
    "CORE_CONTINUOUS_METRICS",
    "EXECUTION_MODES",
    "ChopeEvaluation",
    "EvidenceItem",
    "OUTCOMES",
    "PARTICIPANT_NAMES",
    "PersonaAdherence",
    "boundary_events",
    "compute_convergence",
    "compute_observable_metrics",
    "detect_practical_resolution",
    "evaluate_chope_run",
    "evaluation_metrics",
    "flatten_actions",
    "json_dumps",
    "public_events",
    "public_transcript_text",
    "transcript_markdown",
]
