"""Structured records shared by the simulation and V2 evaluator pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


RoundMovement = Literal[
    "no_conflict",
    "onset",
    "escalated",
    "unchanged",
    "deescalated",
    "resolved",
    "reopened",
    "uncertain",
]

FinalStatus = Literal[
    "no_conflict",
    "resolved",
    "partially_resolved",
    "unresolved",
    "avoided",
    "uncertain",
]

ResolutionMechanism = Literal[
    "none",
    "clarification",
    "compromise",
    "concession",
    "accommodation",
    "withdrawal",
    "third_party_intervention",
    "avoidance",
    "mixed",
    "uncertain",
]


class RoundConflictScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    round: int = Field(ge=1)
    peak_conflict_score: int = Field(ge=0, le=5)
    remaining_conflict_score: int = Field(ge=0, le=5)
    movement: RoundMovement
    evidence: str = Field(min_length=1, max_length=700)


class ConflictEvaluation(BaseModel):
    """One post-run assessment covering every completed simulation round."""

    model_config = ConfigDict(extra="forbid")

    round_scores: list[RoundConflictScore] = Field(min_length=1)
    conflict_ever_observed: bool
    conflict_topics: list[str] = Field(default_factory=list, max_length=5)
    final_status: FinalStatus
    resolution_round: int | None = Field(default=None, ge=1)
    resolution_mechanism: ResolutionMechanism
    final_reason: str = Field(min_length=1, max_length=1200)
    dialogue_naturalness_score: int = Field(ge=1, le=5)
    dialogue_repetition_score: int = Field(ge=0, le=5)
    dialogue_groundedness_score: int = Field(ge=1, le=5)
    dialogue_substantiveness_score: int = Field(ge=1, le=5)
    independent_reasoning_score: int = Field(ge=1, le=5)
    premature_consensus_observed: bool
    dialogue_quality_notes: list[str] = Field(min_length=1, max_length=5)
    substantive_insights: list[str] = Field(min_length=1, max_length=5)
    position_change_notes: list[str] = Field(min_length=1, max_length=5)
    _normalization_notes: list[str] = PrivateAttr(default_factory=list)

    @property
    def normalization_notes(self) -> tuple[str, ...]:
        """Deterministic structural corrections made after model generation."""

        return tuple(self._normalization_notes)

    def validate_round_count(self, expected_rounds: int) -> "ConflictEvaluation":
        expected = list(range(1, expected_rounds + 1))
        actual = [item.round for item in self.round_scores]
        if actual != expected:
            raise ValueError(
                f"Expected round scores {expected}, but evaluator returned {actual}."
            )

        observed = any(
            item.peak_conflict_score > 0 or item.remaining_conflict_score > 0
            for item in self.round_scores
        )
        if self.conflict_ever_observed != observed:
            original = self.conflict_ever_observed
            self.conflict_ever_observed = observed
            self._normalization_notes.append(
                "Adjusted conflict_ever_observed from "
                f"{original} to {observed} to match the round scores."
            )

        final_remaining = self.round_scores[-1].remaining_conflict_score
        if self.final_status == "no_conflict" and observed:
            self.final_status = "uncertain"
            self._normalization_notes.append(
                "Changed final_status from no_conflict to uncertain because at least "
                "one round contained a positive conflict score."
            )
        elif self.final_status == "resolved" and not observed:
            self.final_status = "no_conflict"
            self._normalization_notes.append(
                "Changed final_status from resolved to no_conflict because no round "
                "contained observable conflict."
            )
        elif self.final_status == "resolved" and final_remaining > 0:
            self.final_status = "partially_resolved"
            self._normalization_notes.append(
                "Changed final_status from resolved to partially_resolved because "
                "substantive conflict remained at the end."
            )
        elif self.final_status == "unresolved" and final_remaining == 0:
            self.final_status = "uncertain"
            self._normalization_notes.append(
                "Changed final_status from unresolved to uncertain because the final "
                "remaining-conflict score was zero."
            )

        if self.final_status != "resolved":
            if self.resolution_round is not None:
                self._normalization_notes.append(
                    f"Removed resolution_round {self.resolution_round} because the "
                    f"final status is {self.final_status}."
                )
                self.resolution_round = None
            return self

        # Derive the resolved round from the trajectory. It cannot predate the
        # last expression of conflict and must begin the final zero-remaining suffix.
        final_zero_start = expected_rounds
        for item in reversed(self.round_scores[:-1]):
            if item.remaining_conflict_score != 0:
                break
            final_zero_start = item.round
        last_conflict_round = max(
            item.round
            for item in self.round_scores
            if item.peak_conflict_score > 0 or item.remaining_conflict_score > 0
        )
        derived_resolution_round = max(final_zero_start, last_conflict_round)
        if self.resolution_round != derived_resolution_round:
            original = self.resolution_round
            self.resolution_round = derived_resolution_round
            self._normalization_notes.append(
                "Adjusted resolution_round from "
                f"{original} to {derived_resolution_round} to match the conflict "
                "trajectory."
            )
        return self


__all__ = ["ConflictEvaluation", "RoundConflictScore"]
