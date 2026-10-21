"""Structured outcome evaluator for the MRT loud-audio scenario."""

from __future__ import annotations

from typing import Iterable, Literal, Mapping, Optional

from pydantic import BaseModel, Field, model_validator

from tinytroupe.clients import client


OUTCOMES = ("consensus", "compromise", "avoidance", "escalation", "unresolved")


class EvidenceItem(BaseModel):
    category: str
    agent: Optional[str] = None
    quote: str = Field(min_length=1, max_length=400)
    turn: Optional[int] = Field(default=None, ge=1)


class MRTEvaluation(BaseModel):
    conflict_emerged: bool
    resolution_achieved: bool
    outcome: Literal["consensus", "compromise", "avoidance", "escalation", "unresolved"]
    resolution_turn: Optional[int] = Field(default=None, ge=1)
    listener_goal_addressed: bool
    commuter_goal_addressed: bool
    audio_muted: bool
    headphones_used: bool
    volume_lowered: bool
    commuter_moved: bool
    staff_alerted: bool
    shouting_or_insults: bool
    evidence: list[EvidenceItem] = Field(min_length=1, max_length=12)
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def enforce_resolution_consistency(self):
        should_be_resolved = self.outcome in {"consensus", "compromise"}
        if self.resolution_achieved != should_be_resolved:
            raise ValueError(
                "resolution_achieved must be true only for consensus or compromise"
            )
        if self.resolution_achieved != (self.resolution_turn is not None):
            raise ValueError(
                "resolution_turn must be present exactly when resolution is achieved"
            )
        return self


def transcript_text(events: Iterable[Mapping]) -> str:
    return "\n".join(
        f"[round {event.get('round')}, turn {event.get('turn')}] "
        f"{event.get('agent')}: {str(event.get('content') or '').strip()}"
        for event in events
        if event.get("type") == "TALK" and str(event.get("content") or "").strip()
    )


def evaluate(events: Iterable[Mapping], judge_model: str) -> MRTEvaluation:
    transcript = transcript_text(events)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a conservative research coder. Score only observable public "
                "behaviour. Ethan and Meera are the principal parties; Farah and Lucas "
                "are bystanders and cannot accept a resolution on the principals' behalf. "
                "The listener's goal is personal entertainment/news during a "
                "long commute. The commuter's goal is quiet enough to rest, read, or "
                "process the day. Consensus means the listener acknowledges the impact "
                "and both explicitly accept muting or headphones. Compromise means both "
                "explicitly accept lowering the volume to a minimally audible level. "
                "Avoidance means no mutually accepted agreement and the commuter moves, "
                "only signals disapproval, disengages, or alerts staff. Escalation means "
                "aggressive confrontation, insults, threats, or a shouting match. "
                "Unresolved means no endpoint is sufficiently established. Resolution is "
                "true only for consensus or compromise, and resolution_turn is the first "
                "agent turn where mutual acceptance becomes observable. A civil request "
                "followed by an apology and an unambiguous commitment to mute or use "
                "headphones is sufficient; the commuter need not restate acceptance. A "
                "request alone, an unsupported apology, a topic change, or silence does not "
                "prove mutual acceptance. A bystander's proposed solution is not a "
                "resolution unless Ethan acts on it and Meera's quiet-environment goal "
                "is observably addressed."
            ),
        },
        {
            "role": "user",
            "content": (
                "Immutable facts: Ethan began playing a mobile news video through his "
                "speaker at a volume clearly audible to Meera. They are strangers in a "
                "moderately occupied MRT carriage; Ethan has working earphones in his bag. "
                "Farah and Lucas are nearby strangers who do not know about those earphones, "
                "and no staff member is currently present. Do not infer intent, prior "
                "contact, or acceptance without transcript evidence.\n\nPUBLIC TRANSCRIPT:\n"
                + (transcript or "[No public speech]")
            ),
        },
    ]
    result = client().send_message(
        messages,
        model=judge_model,
        temperature=1.0,
        max_completion_tokens=4096,
        response_format=MRTEvaluation,
        enable_pydantic_model_return=True,
    )
    if isinstance(result, MRTEvaluation):
        return result
    if isinstance(result, Mapping):
        if isinstance(result.get("content"), str):
            return MRTEvaluation.model_validate_json(result["content"])
        return MRTEvaluation.model_validate(result)
    raise RuntimeError("MRT evaluator did not return a valid structured result.")

