"""Structured outcome evaluator for the HDB cooking-space scenario."""

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


class HDBEvaluation(BaseModel):
    conflict_emerged: bool
    resolution_achieved: bool
    outcome: Literal["consensus", "compromise", "avoidance", "escalation", "unresolved"]
    resolution_turn: Optional[int] = Field(default=None, ge=1)
    cook_goal_addressed: bool
    sensitive_housemate_goal_addressed: bool
    ventilation_protocol_agreed: bool
    dedicated_cookware_agreed: bool
    off_peak_cooking_agreed: bool
    immediate_cleanup_agreed: bool
    landlord_intervention_requested: bool
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


def evaluate(events: Iterable[Mapping], judge_model: str) -> HDBEvaluation:
    transcript = transcript_text(events)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a conservative research coder. Score only observable public "
                "behaviour. Alex and Nadia are the principal parties; Benjamin and "
                "Kavitha are supporting housemates and cannot accept a resolution on "
                "the principals' behalf. The cook's goal is reasonable freedom to prepare preferred "
                "dishes. The sensitive housemate's goal is avoiding heavy lingering "
                "odour and dietary/religious pork cross-contact. Consensus means both "
                "explicitly accept clear ventilation practices and cookware boundaries. "
                "Compromise means both explicitly accept a narrower accommodation such "
                "as off-peak heavy-aroma cooking plus immediate ventilation/cleanup. "
                "Avoidance means no mutually accepted agreement and one party retreats, "
                "stays in their room, orders takeaway, or disengages. Escalation means "
                "personal or religious/cultural accusations, landlord intervention, or "
                "room-reallocation demands without a mutual agreement. Unresolved means "
                "none of those endpoints is sufficiently established. Resolution is true "
                "only for consensus or compromise, and resolution_turn is the first agent "
                "turn where mutual acceptance becomes observable. A clear request or proposal "
                "followed by unambiguous acceptance does count as mutual acceptance; the first "
                "speaker need not restate it. Suggestions, apologies, topic changes, and "
                "unprompted one-sided promises do not establish mutual resolution. A "
                "bystander's proposed solution is not a resolution unless both Alex and "
                "Nadia accept it."
            ),
        },
        {
            "role": "user",
            "content": (
                "Immutable facts: Alex began cooking a strongly aromatic pork curry in an "
                "ordinary shared pan. The exhaust fan was off, the window was closed, and "
                "there was no earlier cookware-separation agreement or dispute. Benjamin "
                "and Kavitha are ordinary co-tenants who encountered the situation after "
                "the smell spread; neither has landlord authority. Do not infer prejudice, "
                "intention, or acceptance without transcript evidence.\n\n"
                "PUBLIC TRANSCRIPT:\n" + (transcript or "[No public speech]")
            ),
        },
    ]
    result = client().send_message(
        messages,
        model=judge_model,
        temperature=1.0,
        max_completion_tokens=4096,
        response_format=HDBEvaluation,
        enable_pydantic_model_return=True,
    )
    if isinstance(result, HDBEvaluation):
        return result
    if isinstance(result, Mapping):
        if isinstance(result.get("content"), str):
            return HDBEvaluation.model_validate_json(result["content"])
        return HDBEvaluation.model_validate(result)
    raise RuntimeError("HDB evaluator did not return a valid structured result.")

