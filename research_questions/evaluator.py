"""Blinded, single-call post-run conflict evaluation."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence

from tinytroupe.clients import client

from .models import ConflictEvaluation


EVALUATOR_PROMPT_VERSION = "conflict-trajectory-rubric-v2.5"

EVALUATOR_SYSTEM_PROMPT = """You are an independent evaluator, not a participant in the simulation.
You will receive the setting and the COMPLETE transcript of one run,
separated into numbered rounds.

TASK
For every completed round, separately score:
1. peak_conflict_score: the highest substantive conflict expressed or
   observably enacted DURING that round; and
2. remaining_conflict_score: substantive conflict still unsettled at
   the END of that round.

Conflict means incompatible claims, demands, expectations, or practical
interests that matter to at least one participant. Evaluate substantive
disagreement, not emotional tone or rudeness.

SCORING RUBRIC
0 = No observable substantive conflict.
1 = Very minor disagreement remains.
2 = Mild disagreement; substantial common ground.
3 = Clear disagreement.
4 = Strong disagreement; opposing positions remain.
5 = Entrenched disagreement with little common ground.

RULES
- A scenario does not have to produce conflict.
- A difference in taste alone is not necessarily conflict.
- A disagreement that appears and is settled within one round must have
  peak_conflict_score greater than zero and may have
  remaining_conflict_score equal to zero.
- Politeness, silence, topic change, repetition, and end of transcript
  do NOT automatically mean that a disagreement has been settled.
- If a disagreement is not revisited, its outstanding state may persist.
- Apply the same rubric across all rounds and all scenarios.
- Score each round from what occurred by that point. Avoid using later
  events to re-interpret an earlier round, even though the full transcript
  is visible to you.
- Ground decisions in what agents said or observably did; never infer
  beliefs or confrontational tendencies from cultural identity.
- Proposed actions are not completed actions. "Let's move" or "we can look"
  is not evidence that somebody moved or found another place.
- A promise to move, leave, yield, or take a seat may count as de-escalation,
  but it does not settle an incompatible practical state while the promised
  action remains unconfirmed. When the transcript contains explicit environment
  confirmations or observable action records, use those as the authority for
  physical state. In particular, occupied remains occupied until a confirmed
  LEAVE action, and a person has not obtained a seat until a confirmed TAKE action.
- Repeated agreement without a completed arrangement is not resolution.
- Use final_status no_conflict, resolved, partially_resolved, unresolved,
  avoided, or uncertain.
- resolved requires affirmative evidence of settlement or that the
  relevant incompatible demands ceased; do not equate quiet with resolved.
- If no conflict appeared anywhere, use final_status=no_conflict.
- If there are multiple issues, do not hide outstanding issues just
  because one part was settled; mention this in final_reason.
- resolution_round is the round in which the last substantive conflict was
  affirmatively settled and remained settled through the end.
- movement=resolved requires remaining_conflict_score=0. Use deescalated when
  positions soften or a promise is made but an incompatible practical state remains.
- Classify the main resolution mechanism as none, clarification, compromise,
  concession, accommodation, withdrawal, third_party_intervention, avoidance,
  mixed, or uncertain.
- movement must be one of no_conflict, onset, escalated, unchanged,
  deescalated, resolved, reopened, or uncertain.

DIALOGUE QUALITY
Also assess the dialogue across the whole run. These scores measure presentation
quality, not whether the participants reached agreement:
- dialogue_naturalness_score (1-5): 1 is conspicuously robotic, formal, or
  assistant-like; 3 is mixed; 5 resembles concise, context-dependent ordinary speech.
- dialogue_repetition_score (0-5, higher is worse): 0 has no needless repetition;
  5 repeatedly restates positions, acknowledgements, or proposed arrangements.
  Evaluate semantic repetition, not just exact wording. If three or more rounds after a
  confirmed settlement contain near-duplicate closure, thanks, encouragement, or statements
  of already-obvious activity, the score should normally be at least 3.
- dialogue_groundedness_score (1-5): 1 frequently confuses roles, speakers, known facts,
  or physical state; 5 stays consistent with the public transcript and setting.
- dialogue_substantiveness_score (1-5): 1 merely repeats demands or refusals; 3 exposes
  at least one meaningful reason or trade-off; 5 develops multiple competing principles,
  uncertainties, concession conditions, or belief updates that help explain why the
  conflict changes. Do not award points merely for length, hostility, or resolution.
- independent_reasoning_score (1-5): 1 shows agents mirroring others or abandoning positions
  without a relevant reason; 3 shows stable, independently grounded positions but limited
  engagement; 5 shows well-grounded retention or revision, including clear distinctions
  between factual agreement, normative agreement, and practical accommodation.
- premature_consensus_observed: true only if substantive conflict disappears because agents
  echo, reassure, or agree without new evidence, a fulfilled condition, or a completed action.
  Politeness alone is not evidence of sycophancy. A justified concession is not premature
  consensus, and continued disagreement is not automatically desirable.
- dialogue_quality_notes: 1-5 brief, concrete observations. Quote or identify recurring
  formulaic language, needless bystander speech, role confusion, or especially natural
  exchanges. Do not infer dialogue quality from cultural identity.
- substantive_insights: 1-5 concise findings actually supported by the conversation.
  Identify tensions such as fact versus norm, right versus practical accommodation,
  competing costs, conditions that changed a position, or why an apparent settlement
  failed. Later rounds add insight only if they introduce new evidence, a new incompatibility,
  a meaningful consequence, or a reasoned position change. Social closure and repeated
  statements of settled activity do not count. If the dialogue contains little insight, say
  so directly rather than inventing it.
- position_change_notes: 1-5 concrete notes tracking whether a participant retained, softened,
  or changed a position and what transcript evidence justified it. If nobody changed position,
  include one note saying so. Do not infer private beliefs that were not spoken or enacted.

Return exactly one round_scores entry per numbered transcript round,
in increasing order. Return valid structured data only."""


def evaluator_prompt_sha256() -> str:
    return hashlib.sha256(EVALUATOR_SYSTEM_PROMPT.encode("utf-8")).hexdigest()


def public_transcript_text(events: Sequence[Mapping], completed_rounds: int) -> str:
    """Render every round while excluding private THINK and framework actions."""

    lines: list[str] = []
    for round_number in range(1, completed_rounds + 1):
        lines.append(f"## Round {round_number}")
        round_events = [
            event
            for event in events
            if event.get("round") == round_number
            and (
                (
                    str(event.get("type") or "").upper() in {"TALK", "OBSERVE"}
                    and str(event.get("content") or "").strip()
                )
                or str(event.get("type") or "").upper()
                in {"TAKE_SEAT", "LEAVE_SEAT"}
            )
        ]
        if not round_events:
            lines.append("[No public speech or observable action recorded]")
        else:
            for event in round_events:
                if str(event.get("type") or "").upper() == "OBSERVE":
                    lines.append(
                        f"- Public environment update: {str(event.get('content')).strip()}"
                    )
                elif str(event.get("type") or "").upper() == "TALK":
                    lines.append(
                        f"- Turn {event.get('turn')} — {event.get('agent')}: "
                        f"{str(event.get('content')).strip()}"
                    )
                else:
                    lines.append(
                        f"- Observable action: {event.get('agent')} "
                        f"{event.get('type')} target={event.get('target')}"
                    )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_evaluator_messages(
    *, shared_setting: str, transcript: str, completed_rounds: int
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"COMPLETED ROUNDS: {completed_rounds}\n\n"
                f"SETTING:\n{shared_setting}\n\n"
                f"TRANSCRIPT:\n{transcript}"
            ),
        },
    ]


def _coerce_evaluation(result) -> ConflictEvaluation:
    if isinstance(result, ConflictEvaluation):
        return result
    if isinstance(result, Mapping):
        if isinstance(result.get("content"), str):
            return ConflictEvaluation.model_validate_json(result["content"])
        return ConflictEvaluation.model_validate(result)
    raise RuntimeError("Evaluator did not return a valid structured result.")


def evaluate_transcript(
    *,
    events: Sequence[Mapping],
    shared_setting: str,
    completed_rounds: int,
    evaluator_model: str,
    max_completion_tokens: int = 4096,
) -> ConflictEvaluation:
    """Make one logical evaluator call after the simulation has completed."""

    transcript = public_transcript_text(events, completed_rounds)
    messages = build_evaluator_messages(
        shared_setting=shared_setting,
        transcript=transcript,
        completed_rounds=completed_rounds,
    )
    result = client().send_message(
        messages,
        model=evaluator_model,
        temperature=0.0,
        max_completion_tokens=max_completion_tokens,
        response_format=ConflictEvaluation,
        enable_pydantic_model_return=True,
    )
    evaluation = _coerce_evaluation(result)
    return evaluation.validate_round_count(completed_rounds)


__all__ = [
    "EVALUATOR_PROMPT_VERSION",
    "EVALUATOR_SYSTEM_PROMPT",
    "build_evaluator_messages",
    "evaluate_transcript",
    "evaluator_prompt_sha256",
    "public_transcript_text",
]
