"""Blind move-level coding of saved runs.

The frozen evaluator judges whole conversations. This pass records what the research
question needs and the evaluator schema has no field for: who concedes, what they ask in
return, the kind of reason they give, and which concerns stay in thought without being
spoken. It reads anonymised text with strategy labels removed, so a code cannot come from an
agent's name or self-reported intent. Thoughts are the model's reported reasoning, not a
measure of what it "really" thinks.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from tinytroupe.clients import client

from .models import RunCoding


CODING_PROMPT_VERSION = "move-coding-v3"

MOVE_DEFINITIONS = """You code a transcript of an everyday dispute for research. You are not judging who is right. Code only what is in the text. Do not infer anything from how a person might be expected to behave.

For EVERY numbered spoken line, return these yes/no codes. They are independent: a line can have several, or none. A bare "Okay" with nothing else is false on all of them.

- uses_interest: this line itself states the speaker's own need or practical cost, such as something that will be lost, spoiled, or made harder for them ("My dinner's going cold", "I can't sleep with that smell"). Agreeing to wait, or asking a question, is false unless the line also states the need.
- uses_right: the speaker appeals to a rule, an entitlement, who was first, fairness, or a promise made ("I was here first", "you said I could", "it's only fair", "we agreed").
- uses_power: the speaker asserts control by declaration, giving no reason and asking nothing ("It's mine, end of story", "That's how it's going to be"), or treats something they have already done as settling the matter ("I'm already here, so that's that"). A question, a request, or a line that gives a reason or claim is false.
- concedes: the speaker gives up, reduces, or offers something they have not already given in an earlier line: agrees to wait, takes on a task, drops a claim, or changes what they do for someone else. Repeating an earlier offer is false.
- conditional_ask: the speaker ties what they will do to something another person does, or asks for something in return ("I'll do it if you", "Fine, provided that", "I'll give way, can I go next?"). A plain request with nothing offered is false.
"""

CODING_SYSTEM_PROMPT = MOVE_DEFINITIONS + """
For each of Agent A, B, C and D, list the concerns they show. Each tag is a kind of concern, not a particular object, and an agent uses a tag at most once. Use only these tags, and apply each tag's limit:
- access: who gets to use something limited, and when, such as a place, a turn, a slot, or equipment. Queue order and turn-taking belong here, not under fair_share.
- practical_cost: a concrete harm or inconvenience to them, such as lost sleep, spoiled food, or crowding.
- fair_share: who does a chore, pays, or carries an effort for the group. Using a shared thing is access, not fair_share.
- rule_or_norm: arguing over whether a rule or custom exists or applies, as a matter of principle. Merely proposing a practical arrangement is not this, even if it is called a rule.
- respect: how they were treated in that moment: not asked, ignored, spoken to rudely, or brushed aside.
- blame_or_reputation: being held responsible for a problem, or being labelled as a kind of person. Being called out for causing something belongs here, not under respect.
- recognition: their presence or contribution going unnoticed: being overlooked in the queue or taken for granted. Not being asked first is respect, not recognition.

Tag the concern the person is actually raising, not every tag it could touch. If one statement could fit two tags, use the one closest to what they object to, and use only that one.

For each concern give: detail (a few words naming what is specifically at stake), in_thoughts (true if it appears in their private thoughts), and in_speech (true if they say it aloud in a spoken line, in any words). Answering someone else's concern does not make it the speaker's own concern. List only concerns with evidence in the text.

Then code the arrangement at the end of the transcript:
- exists: true only if everyone whose claims conflict on at least one issue said they accept the same concrete arrangement for it, in their own words. A one-sided promise is false. Competing promises that nobody reconciled are false.
- covers: which of the tags above that arrangement settles. Empty if exists is false.
- unsettled: which tags were raised aloud and are still open at the end, even if something else was agreed.
- gave_way: who accepted less than they asked for. Empty if exists is false.
- summary: one plain sentence saying what was or was not settled.

Return one entry in turns for every spoken line, in order, numbered exactly as given."""


_STRATEGY_PREFIX = re.compile(r"^\s*STRATEGY:\s*[A-Z_]+\s*[.:;,—–-]*\s*")


def coding_prompt_sha256() -> str:
    return hashlib.sha256(CODING_SYSTEM_PROMPT.encode("utf-8")).hexdigest()


def strip_strategy_label(text: str) -> str:
    return _STRATEGY_PREFIX.sub("", text, count=1)


def build_coding_input(
    events: Sequence[Mapping[str, Any]], setting: str
) -> tuple[str, int]:
    """Render anonymised events for the coder; returns the text and spoken-line count."""

    spoken = [
        event
        for event in events
        if event.get("type") == "TALK" and str(event.get("content") or "").strip()
    ]
    lines = [
        f"[{index}] (round {event.get('round')}) {event.get('agent')}: "
        f"{str(event.get('content')).strip()}"
        for index, event in enumerate(spoken, start=1)
    ]
    thoughts: dict[str, list[str]] = {}
    for event in events:
        if event.get("type") == "THINK" and str(event.get("content") or "").strip():
            thoughts.setdefault(str(event.get("agent")), []).append(
                strip_strategy_label(str(event["content"])).strip()
            )
    thought_block = "\n".join(
        f"{agent}:\n" + "\n".join(f"- {item}" for item in items)
        for agent, items in sorted(thoughts.items())
    )
    text = (
        f"SETTING:\n{setting}\n\n"
        "SPOKEN LINES:\n" + "\n".join(lines) + "\n\n"
        "PRIVATE THOUGHTS:\n" + (thought_block or "(none recorded)")
    )
    return text, len(spoken)


def _coerce(result: Any) -> RunCoding:
    if isinstance(result, RunCoding):
        return result
    if isinstance(result, Mapping):
        if isinstance(result.get("content"), str):
            return RunCoding.model_validate_json(result["content"])
        return RunCoding.model_validate(result)
    raise RuntimeError("Coder did not return a valid structured result.")


def code_run(
    *,
    events: Sequence[Mapping[str, Any]],
    setting: str,
    model: str,
    max_completion_tokens: int,
    attempts: int = 2,
) -> RunCoding:
    """Code one run, asking again once if the coder skips or misnumbers a line."""

    text, expected = build_coding_input(events, setting)
    last_error: Exception | None = None
    for _ in range(attempts):
        result = client().send_message(
            [
                {"role": "system", "content": CODING_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            model=model,
            temperature=0.0,
            max_completion_tokens=max_completion_tokens,
            response_format=RunCoding,
            enable_pydantic_model_return=True,
        )
        try:
            return _coerce(result).validate_lines(expected)
        except ValueError as error:
            last_error = error
    raise RuntimeError(f"Coder failed after {attempts} attempts: {last_error}")


__all__ = [
    "CODING_PROMPT_VERSION",
    "CODING_SYSTEM_PROMPT",
    "MOVE_DEFINITIONS",
    "build_coding_input",
    "code_run",
    "coding_prompt_sha256",
    "strip_strategy_label",
]
