"""Private post-run debrief: each participant's own account of how the interaction ended.

This runs after the simulation and the evaluator have finished, so it cannot affect the
conversation or the evaluation. It rebuilds each participant from the saved run (persona
facts, the public transcript, and that participant's own private thoughts) and asks fixed
questions. Answers are the model's reported account, not a measurement of what it "really"
thought. Results live in ``debriefs/`` and are never passed to the evaluator.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from tinytroupe.clients import client

from .evaluator import public_transcript_text
from .models import AgentDebrief


DEBRIEF_PROMPT_VERSION = "private-debrief-v1"

DEBRIEF_SYSTEM_PROMPT = """You took part in the face-to-face interaction described below, as the person described below. It is over. You are now answering a few private questions about it. Nobody else who was there will see your answers.

Answer as yourself, in plain words, and only from what actually happened. Do not tidy it up: if nothing was settled, say so; if you gave up nothing, say "nothing"; if you are unsure what was agreed, say that. A statement of what one person intended is not an agreement unless the others accepted it. Do not invent anything that was not said.

Questions:
- settled: was the situation settled, partly settled, or not settled?
- what_was_agreed: what, if anything, did people actually agree? Who does what?
- what_i_gave_up: what did you give up, compared with what you wanted when you arrived?
- what_i_got: what did you get, including anything that matters to you besides a seat?
- why_i_went_along: why did you accept or refuse what was on the table? Give your real reason.
- what_still_bothers_me: what, if anything, is still bothering you?
- fairness_to_me: how fair was the outcome to you, from 1 (very unfair) to 5 (very fair)?"""


def debrief_prompt_sha256() -> str:
    return hashlib.sha256(DEBRIEF_SYSTEM_PROMPT.encode("utf-8")).hexdigest()


def _private_thoughts(events: list[Mapping[str, Any]], display_name: str) -> str:
    thoughts = [
        f"- Round {event.get('round')}: {str(event.get('content')).strip()}"
        for event in events
        if str(event.get("type") or "").upper() == "THINK"
        and event.get("agent") == display_name
        and str(event.get("content") or "").strip()
    ]
    return "\n".join(thoughts) if thoughts else "(none recorded)"


def build_debrief_messages(
    transcript: Mapping[str, Any], agent_id: str
) -> list[dict[str, str]]:
    scenario = transcript["scenario"]
    agent = scenario["agents"][agent_id]
    events = transcript["events"]
    identity = [
        f"Name: {agent['display_name']}",
        f"Age: {agent['age']}",
        f"Role: {agent['role']}",
    ]
    if agent.get("cultural_background"):
        identity.append(f"Cultural background: {agent['cultural_background']}")
    if agent.get("biography"):
        identity.append(f"Your background: {agent['biography']}")
    if agent.get("personal_values"):
        identity.append(f"What you value: {agent['personal_values']}")
    identity.extend(
        [
            f"What you wanted: {agent['immediate_priority']}",
            f"What you privately knew: {agent['private_knowledge']}",
        ]
    )
    return [
        {"role": "system", "content": DEBRIEF_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "WHO YOU ARE:\n"
                + "\n".join(identity)
                + f"\n\nSETTING:\n{scenario['shared_setting']}\n\n"
                f"OPENING SITUATION:\n{scenario['shared_trigger']}\n\n"
                "WHAT WAS SAID:\n"
                + public_transcript_text(events, transcript["run"]["completed_rounds"])
                + "\nYOUR PRIVATE THOUGHTS DURING IT:\n"
                + _private_thoughts(events, agent["display_name"])
            ),
        },
    ]


def _coerce_debrief(result: Any) -> AgentDebrief:
    if isinstance(result, AgentDebrief):
        return result
    if isinstance(result, Mapping):
        if isinstance(result.get("content"), str):
            return AgentDebrief.model_validate_json(result["content"])
        return AgentDebrief.model_validate(result)
    raise RuntimeError("Debrief did not return a valid structured result.")


def debrief_agent(
    *,
    transcript: Mapping[str, Any],
    agent_id: str,
    model: str,
    max_completion_tokens: int,
) -> AgentDebrief:
    result = client().send_message(
        build_debrief_messages(transcript, agent_id),
        model=model,
        temperature=0.0,
        max_completion_tokens=max_completion_tokens,
        response_format=AgentDebrief,
        enable_pydantic_model_return=True,
    )
    return _coerce_debrief(result)


__all__ = [
    "DEBRIEF_PROMPT_VERSION",
    "DEBRIEF_SYSTEM_PROMPT",
    "build_debrief_messages",
    "debrief_agent",
    "debrief_prompt_sha256",
]
