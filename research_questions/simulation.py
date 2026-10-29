"""Construction and execution helpers for background-controlled TinyWorld runs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from tinytroupe import control
from tinytroupe.agent import TinyPerson
from tinytroupe.agent.mental_faculty import CustomMentalFaculty
from tinytroupe.environment import TinyWorld

from .scenario_presets.common import ScenarioPreset, materialize_configuration


AGENT_PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "tiny_person_conflict_pilot.mustache"
)


class FaceToFaceWorld(TinyWorld):
    """Face-to-face speech with direct addressees and passive overhearers."""

    PRIVATE_ACTION_TYPES = {"THINK", "DONE", "RECALL", "CONSULT"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_reply_agent: str | None = None
        self.scheduler_cursor = 0
        self.scheduler_direct_reply_streak = 0
        self.scheduler_events: list[dict[str, Any]] = []

    def _resolve_talk_target(self, target: str) -> TinyPerson | None:
        if not target:
            return None
        normalized = str(target).strip()
        direct = self.get_agent_by_name(normalized)
        if direct is not None:
            return direct
        if len(normalized) == 1 and normalized.upper() in {"A", "B", "C", "D"}:
            return self.get_agent_by_name(f"Agent {normalized.upper()}")
        if normalized.lower().startswith("agent "):
            return self.get_agent_by_name(
                f"Agent {normalized.split(maxsplit=1)[1].upper()}"
            )
        return None

    def _handle_talk(self, source_agent: TinyPerson, content: str, target: str):
        target_agent = self._resolve_talk_target(target)
        if target_agent is not None and target_agent is not source_agent:
            self.pending_reply_agent = target_agent.name
            target_agent.listen(content, source=source_agent)
            for observer in self.agents:
                if observer not in {source_agent, target_agent}:
                    observer.socialize(
                        f"You overhear {source_agent.name} say to "
                        f"{target_agent.name}: {content}",
                        source=source_agent,
                    )
            return

        # Untargeted speech is audible to the group, but it is an overheard
        # public remark rather than a direct demand that every person answer.
        for observer in self.agents:
            if observer is not source_agent:
                observer.socialize(
                    f"Public remark from {source_agent.name}: {content}",
                    source=source_agent,
                )

    def _scheduler_candidate_names(
        self, *, defer_direct_reply: bool = False
    ) -> list[str]:
        """Return direct-reply priority followed by deterministic rotating order."""

        names = [agent.name for agent in self.agents]
        if not names:
            return []
        cursor = self.scheduler_cursor % len(names)
        rotating = names[cursor:] + names[:cursor]
        if self.pending_reply_agent in names:
            others = [name for name in rotating if name != self.pending_reply_agent]
            if defer_direct_reply:
                return others + [self.pending_reply_agent]
            return [self.pending_reply_agent] + others
        return rotating

    def run_hybrid_round(
        self, *, timedelta_per_round: timedelta, max_public_turns: int = 4
    ) -> list[dict[str, list[Mapping]]]:
        """Run direct-reply-priority turns until silence or the public-turn cap."""

        self._advance_datetime(timedelta_per_round)
        self._simulation_steps += 1
        attempts: list[dict[str, list[Mapping]]] = []
        public_turns = 0
        slot = 0

        while public_turns < max_public_turns:
            direct_reply = self.pending_reply_agent
            defer_direct_reply = bool(
                direct_reply and self.scheduler_direct_reply_streak >= 2
            )
            candidate_names = self._scheduler_candidate_names(
                defer_direct_reply=defer_direct_reply
            )
            if not candidate_names:
                break
            self.pending_reply_agent = None
            if direct_reply is None:
                self.scheduler_direct_reply_streak = 0
            selected = False

            for candidate_name in candidate_names:
                slot += 1
                candidate = self.get_agent_by_name(candidate_name)
                if candidate is None:
                    continue
                generated = candidate.act(return_actions=True)
                actions = candidate.pop_latest_actions()
                self._handle_actions(candidate, actions)
                attempts.append({candidate_name: generated})
                action_types = [
                    str(action.get("type") or "UNKNOWN").upper()
                    for action in actions
                    if isinstance(action, Mapping)
                ]
                is_public = any(
                    action_type not in self.PRIVATE_ACTION_TYPES
                    for action_type in action_types
                )
                self.scheduler_events.append(
                    {
                        "round": getattr(self, "current_round_number", 0),
                        "slot": slot,
                        "candidate": candidate_name,
                        "priority": (
                            "deferred_direct_reply"
                            if candidate_name == direct_reply and defer_direct_reply
                            else (
                                "direct_reply"
                                if candidate_name == direct_reply
                                else (
                                    "open_floor_self_selection"
                                    if defer_direct_reply
                                    else "rotating_self_selection"
                                )
                            )
                        ),
                        "decision": "contribute" if is_public else "listen",
                        "action_types": action_types,
                    }
                )
                candidate_index = next(
                    index
                    for index, agent in enumerate(self.agents)
                    if agent.name == candidate_name
                )
                self.scheduler_cursor = (candidate_index + 1) % len(self.agents)
                if is_public:
                    if candidate_name == direct_reply:
                        self.scheduler_direct_reply_streak = (
                            1
                            if defer_direct_reply
                            else self.scheduler_direct_reply_streak + 1
                        )
                    else:
                        self.scheduler_direct_reply_streak = 0
                    public_turns += 1
                    selected = True
                    break

            if not selected:
                break

        return attempts


class KitchenConflictWorld(FaceToFaceWorld):
    """Observable ventilation, cleanup, and stove-access state for S02."""

    ACTION_TYPES = {
        "OPEN_WINDOW",
        "TURN_ON_EXTRACTOR",
        "TURN_OFF_EXTRACTOR",
        "MOVE_LAUNDRY",
        "WASH_SHARED_UTENSILS",
        "LABEL_PERSONAL_UTENSILS",
        "RELEASE_STOVE",
        "TAKE_STOVE",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_round_number = 0
        self.window_open = False
        self.extractor_on = False
        self.laundry_protected = False
        self.shared_utensils_clean = False
        self.personal_utensils_labeled = False
        self.stove_occupant = "Agent A"
        self.public_state_events: list[dict[str, Any]] = []

    def _record_state_event(self, content: str) -> None:
        self.public_state_events.append(
            {
                "round": self.current_round_number,
                "turn": 999,
                "agent": "Environment",
                "action_index": len(self.public_state_events) + 1,
                "type": "OBSERVE",
                "content": content,
                "target": None,
            }
        )
        for person in self.agents:
            person.socialize(content, source=self)

    def prepare_round(self, round_number: int, observation: str | None) -> str | None:
        self.current_round_number = round_number
        if round_number == 1:
            return observation
        ventilation = (
            "the aroma is fading"
            if self.window_open or self.extractor_on
            else "the aroma remains strong in the common area"
        )
        prefix = (
            "Two minutes have passed. Agent A's dish is ready to remove from the heat, "
            "but the current stove occupant has not necessarily released it."
            if round_number == 2
            else "Two more minutes have passed."
        )
        return (
            f"{prefix} {ventilation}. Confirmed state: "
            f"window={'open' if self.window_open else 'closed'}; "
            f"extractor={'on' if self.extractor_on else 'off'}; "
            f"laundry={'protected from rain' if self.laundry_protected else 'beside the window and exposed if it opens'}; "
            f"stove={self.stove_occupant or 'free'}; "
            f"shared utensils={'clean' if self.shared_utensils_clean else 'used and unwashed'}; "
            f"personal utensils={'labeled' if self.personal_utensils_labeled else 'not visibly labeled'}."
        )

    def _handle_kitchen_action(self, source_agent: TinyPerson, action: Mapping) -> None:
        action_type = str(action.get("type") or "").upper()
        if action_type == "OPEN_WINDOW":
            if not self.laundry_protected:
                result = (
                    f"{source_agent.name} cannot open the kitchen window yet; rain would wet "
                    "the laundry beside it."
                )
            elif self.window_open:
                result = "The kitchen window was already open."
            else:
                self.window_open = True
                result = f"{source_agent.name} physically opens the kitchen window."
        elif action_type == "TURN_ON_EXTRACTOR":
            if self.extractor_on:
                result = "The extractor fan was already on."
            else:
                self.extractor_on = True
                result = f"{source_agent.name} physically turns on the extractor fan."
        elif action_type == "TURN_OFF_EXTRACTOR":
            if not self.extractor_on:
                result = "The extractor fan was already off."
            else:
                self.extractor_on = False
                result = f"{source_agent.name} physically turns off the extractor fan."
        elif action_type == "MOVE_LAUNDRY":
            if self.laundry_protected:
                result = "The laundry was already moved away from the rain-facing window."
            else:
                self.laundry_protected = True
                result = f"{source_agent.name} moves the drying rack away from the rain-facing window."
        elif action_type == "WASH_SHARED_UTENSILS":
            if self.shared_utensils_clean:
                result = "The common utensils were already clean."
            else:
                self.shared_utensils_clean = True
                result = f"{source_agent.name} washes the common utensils currently on the counter."
        elif action_type == "LABEL_PERSONAL_UTENSILS":
            if source_agent.name != "Agent C":
                result = f"{source_agent.name} cannot label Agent C's personal utensils."
            elif self.personal_utensils_labeled:
                result = "Agent C's personal utensils were already visibly labeled."
            else:
                self.personal_utensils_labeled = True
                result = "Agent C visibly labels and separates Agent C's personal utensils."
        elif action_type == "RELEASE_STOVE":
            if self.stove_occupant != source_agent.name:
                result = f"{source_agent.name} cannot release the stove; they do not occupy it."
            else:
                self.stove_occupant = None
                result = f"{source_agent.name} removes the finished dish and physically releases the stove."
        else:  # TAKE_STOVE
            if self.stove_occupant is not None:
                result = (
                    f"{source_agent.name} cannot take the stove; it is occupied by "
                    f"{self.stove_occupant}."
                )
            else:
                self.stove_occupant = source_agent.name
                result = f"{source_agent.name} physically takes the free stove to begin cooking."
        self._record_state_event(result)

    def _handle_actions(self, source: TinyPerson, actions: list):
        for action in actions:
            if str(action.get("type") or "").upper() in self.ACTION_TYPES:
                self._handle_kitchen_action(source, action)
            else:
                super()._handle_actions(source, [action])


class OrderConflictWorld(FaceToFaceWorld):
    """Observable order recording, preparation, correction, and service state for S06."""

    ACTION_TYPES = {"RECORD_ORDER", "START_PREPARATION", "CORRECT_ORDER", "SERVE_ORDER"}
    ORDER_SPECS = {"dry_no_chilli", "soup_with_chilli"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_round_number = 0
        self.recorded_spec: str | None = None
        self.preparation_spec: str | None = None
        self.served = False
        self.correction_made = False
        self.public_state_events: list[dict[str, Any]] = []

    def _record_state_event(self, content: str) -> None:
        self.public_state_events.append(
            {
                "round": self.current_round_number,
                "turn": 999,
                "agent": "Environment",
                "action_index": len(self.public_state_events) + 1,
                "type": "OBSERVE",
                "content": content,
                "target": None,
            }
        )
        for person in self.agents:
            person.socialize(content, source=self)

    def _state_text(self) -> str:
        return (
            f"recorded specification={self.recorded_spec or 'none'}; "
            f"preparation={self.preparation_spec or 'not started'}; "
            f"served={'yes' if self.served else 'no'}; "
            f"correction required={'yes' if self.correction_made else 'no'}."
        )

    def prepare_round(self, round_number: int, observation: str | None) -> str | None:
        self.current_round_number = round_number
        if round_number == 1:
            return observation
        if round_number == 3 and self.preparation_spec is None:
            self.preparation_spec = self.recorded_spec or "soup_with_chilli"
            self._record_state_event(
                "With the queue waiting, preparation begins using "
                f"{self.preparation_spec}."
            )
        if round_number == 5 and self.preparation_spec is not None and not self.served:
            self.served = True
            self._record_state_event(
                f"The stall places one {self.preparation_spec} order at the pickup counter."
            )
        base = observation or "The environment reports the current order state."
        if self.served:
            base = (
                f"{base} The focal customer transaction is complete; later customers' "
                "orders fall outside this observed episode."
            )
        return f"{base} Confirmed state: {self._state_text()}"

    def _order_target(self, action: Mapping) -> str:
        raw = str(action.get("target") or "").strip()
        matches = [candidate for candidate in self.ORDER_SPECS if candidate in raw]
        return matches[0] if len(matches) == 1 else raw

    def _handle_order_action(self, source_agent: TinyPerson, action: Mapping) -> None:
        action_type = str(action.get("type") or "").upper()
        target = self._order_target(action)
        if source_agent.name != "Agent B":
            self._record_state_event(
                f"{source_agent.name} cannot perform {action_type}; only the stall operator records, prepares, corrects, or serves the order."
            )
            return
        if action_type != "SERVE_ORDER" and target not in self.ORDER_SPECS:
            self._record_state_event(
                f"Agent B's {action_type} failed because {target or 'no specification'} is not a recognized order specification."
            )
            return
        if action_type == "RECORD_ORDER":
            self.recorded_spec = target
            result = f"Agent B records the order specification as {target}."
        elif action_type == "START_PREPARATION":
            if self.served:
                result = "Agent B cannot start preparation; an order has already been served."
            elif self.preparation_spec is not None:
                result = f"Preparation had already started as {self.preparation_spec}."
            else:
                self.preparation_spec = target
                result = f"Agent B physically starts preparing {target}."
        elif action_type == "CORRECT_ORDER":
            if self.served:
                result = "Agent B cannot correct the order in place because it has already been served."
            elif self.preparation_spec is None:
                self.recorded_spec = target
                result = f"Agent B records {target} before preparation; no remake is needed."
            elif self.preparation_spec == target:
                result = f"The preparation was already {target}; no correction is needed."
            else:
                previous = self.preparation_spec
                self.preparation_spec = target
                self.recorded_spec = target
                self.correction_made = True
                result = (
                    f"Agent B stops the {previous} preparation and restarts it as {target}; "
                    "this creates a visible delay and discarded ingredients."
                )
        else:  # SERVE_ORDER
            if self.preparation_spec is None:
                result = "Agent B cannot serve the order because preparation has not started."
            elif self.served:
                result = "The prepared order was already served."
            else:
                self.served = True
                result = f"Agent B physically serves one {self.preparation_spec} order."
        self._record_state_event(result)

    def _handle_actions(self, source: TinyPerson, actions: list):
        for action in actions:
            if str(action.get("type") or "").upper() in self.ACTION_TYPES:
                self._handle_order_action(source, action)
            else:
                super()._handle_actions(source, [action])


class SeatConflictWorld(FaceToFaceWorld):
    """Small state machine for observable seat-taking and seat-leaving actions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_round_number = 0
        self.seat_occupants = {
            "disputed_seat": "Agent B",
            "other_table_seat": "Agent C",
            "alternative_seat": None,
        }
        self.seat_available = {
            "disputed_seat": True,
            "other_table_seat": True,
            "alternative_seat": False,
        }
        self.public_state_events: list[dict[str, Any]] = []

    def prepare_round(self, round_number: int, observation: str | None) -> str | None:
        self.current_round_number = round_number
        if round_number == 4:
            self.seat_available["alternative_seat"] = True
        if round_number == 5:
            alternative_occupant = self.seat_occupants["alternative_seat"]
            alternative_state = (
                f"The alternative seat is now occupied by {alternative_occupant}."
                if alternative_occupant
                else (
                    "The alternative seat is still free, but another diner carrying "
                    "a tray is approaching it from the opposite direction."
                )
            )
            return (
                "Two more minutes have passed. Agent B's bowl is now empty, although "
                f"Agent B remains in the disputed seat. {alternative_state}"
            )
        if round_number == 6:
            return (
                "Two more minutes have passed. Current confirmed occupants: "
                f"disputed seat = {self.seat_occupants['disputed_seat'] or 'empty'}; "
                f"alternative seat = {self.seat_occupants['alternative_seat'] or 'empty'}."
            )
        return observation

    def _record_state_event(self, content: str) -> None:
        self.public_state_events.append(
            {
                "round": self.current_round_number,
                "turn": 999,
                "agent": "Environment",
                "action_index": len(self.public_state_events) + 1,
                "type": "OBSERVE",
                "content": content,
                "target": None,
            }
        )
        for person in self.agents:
            person.socialize(content, source=self)

    def _handle_seat_action(self, source_agent: TinyPerson, action: Mapping) -> None:
        action_type = str(action.get("type") or "").upper()
        raw_seat_id = str(action.get("target") or "").strip()
        embedded_seat_ids = [
            candidate
            for candidate in self.seat_occupants
            if candidate in raw_seat_id
        ]
        seat_id = (
            embedded_seat_ids[0]
            if len(embedded_seat_ids) == 1
            else raw_seat_id
        )
        if seat_id not in self.seat_occupants:
            self._record_state_event(
                f"{source_agent.name}'s {action_type} attempt failed because "
                f"{seat_id or 'no seat'} is not a recognized seat."
            )
            return

        if action_type == "TAKE_SEAT":
            if not self.seat_available[seat_id]:
                result = f"{source_agent.name} could not take {seat_id}; it is not available yet."
            elif source_agent.name in self.seat_occupants.values():
                occupied_seat = next(
                    current_seat
                    for current_seat, occupant in self.seat_occupants.items()
                    if occupant == source_agent.name
                )
                result = (
                    f"{source_agent.name} could not take {seat_id}; they already occupy "
                    f"{occupied_seat}."
                )
            elif self.seat_occupants[seat_id] is not None:
                result = (
                    f"{source_agent.name} could not take {seat_id}; it is occupied by "
                    f"{self.seat_occupants[seat_id]}."
                )
            else:
                self.seat_occupants[seat_id] = source_agent.name
                result = f"{source_agent.name} physically takes {seat_id}."
        else:
            if self.seat_occupants[seat_id] != source_agent.name:
                result = f"{source_agent.name} could not leave {seat_id}; they do not occupy it."
            else:
                self.seat_occupants[seat_id] = None
                result = f"{source_agent.name} physically leaves {seat_id}; it is now empty."
        self._record_state_event(result)

    def _handle_actions(self, source: TinyPerson, actions: list):
        for action in actions:
            if str(action.get("type") or "").upper() in {"TAKE_SEAT", "LEAVE_SEAT"}:
                self._handle_seat_action(source, action)
            else:
                super()._handle_actions(source, [action])


def _seat_action_faculty() -> CustomMentalFaculty:
    return CustomMentalFaculty(
        "Observable seat actions",
        actions_configs={
            "TAKE_SEAT": {
                "description": (
                    "Physically take a seat. Set target exactly to disputed_seat or "
                    "alternative_seat. Use this instead of merely saying you will sit."
                ),
                "function": None,
            },
            "LEAVE_SEAT": {
                "description": (
                    "Physically leave a seat you occupy. Set target exactly to disputed_seat "
                    "or alternative_seat. Use this when you actually vacate it."
                ),
                "function": None,
            },
        },
        constraints=[
            "A spoken intention does not change seat occupancy; use TAKE_SEAT or LEAVE_SEAT.",
            "Do not TAKE_SEAT unless the environment has confirmed that the seat is empty.",
            "You may occupy at most one seat. Do not TAKE_SEAT while you already occupy another seat.",
            "Use target=disputed_seat only for the original seat beside Agent C. Use target=alternative_seat only for the later seat about ten metres away. The target must match the seat described in the action content.",
            "If the practical reason for occupying a seat has ended and you decide to vacate, use LEAVE_SEAT.",
        ],
    )


def _kitchen_action_faculty() -> CustomMentalFaculty:
    return CustomMentalFaculty(
        "Observable shared-kitchen actions",
        actions_configs={
            "OPEN_WINDOW": {
                "description": "Physically open the kitchen window. Set target=kitchen_window.",
                "function": None,
            },
            "TURN_ON_EXTRACTOR": {
                "description": "Physically turn on the extractor fan. Set target=extractor_fan.",
                "function": None,
            },
            "TURN_OFF_EXTRACTOR": {
                "description": "Physically turn off the extractor fan. Set target=extractor_fan.",
                "function": None,
            },
            "MOVE_LAUNDRY": {
                "description": (
                    "Move the drying rack away from the rain-facing kitchen window so the "
                    "window can be opened safely. Set target=drying_rack."
                ),
                "function": None,
            },
            "WASH_SHARED_UTENSILS": {
                "description": "Wash the used common utensils on the counter. Set target=common_utensils.",
                "function": None,
            },
            "LABEL_PERSONAL_UTENSILS": {
                "description": "Agent C visibly labels and separates personal utensils. Set target=personal_utensils.",
                "function": None,
            },
            "RELEASE_STOVE": {
                "description": "Remove your finished dish and physically release the stove. Set target=stove.",
                "function": None,
            },
            "TAKE_STOVE": {
                "description": "Physically take the stove after it is confirmed free. Set target=stove.",
                "function": None,
            },
        },
        constraints=[
            "Promises do not change kitchen state; perform the matching action when you actually do it.",
            "Only the current stove occupant can RELEASE_STOVE, and nobody can TAKE_STOVE until it is confirmed free.",
            "Only Agent C can label Agent C's personal utensils.",
            "The kitchen window cannot be opened safely until the laundry is moved away from the rain.",
            "Ventilation, utensil separation, cleanup, and stove access are distinct issues; one action does not settle the others.",
        ],
    )


def _order_action_faculty() -> CustomMentalFaculty:
    return CustomMentalFaculty(
        "Observable hawker-order actions",
        actions_configs={
            "RECORD_ORDER": {
                "description": (
                    "Stall operator records an order specification. Set target exactly to "
                    "dry_no_chilli or soup_with_chilli."
                ),
                "function": None,
            },
            "START_PREPARATION": {
                "description": (
                    "Stall operator physically begins preparing an order. Set target exactly "
                    "to dry_no_chilli or soup_with_chilli."
                ),
                "function": None,
            },
            "CORRECT_ORDER": {
                "description": (
                    "Stall operator corrects a recorded or started order. Set target exactly "
                    "to dry_no_chilli or soup_with_chilli."
                ),
                "function": None,
            },
            "SERVE_ORDER": {
                "description": "Stall operator physically serves the currently prepared order. Set target=order.",
                "function": None,
            },
        },
        constraints=[
            "Only Agent B, the stall operator, can record, prepare, correct, or serve the order.",
            "Speech does not record or prepare food; use the observable action in the same turn when acting.",
            "Use dry_no_chilli only for dry chicken noodles without chilli, and soup_with_chilli only for the stall default.",
            "Do not claim an order was corrected or served until the environment confirms it.",
        ],
    )


@dataclass
class ScenarioInstance:
    preset: dict[str, Any]
    participants: dict[str, TinyPerson]
    world: FaceToFaceWorld


def reset_simulation_state() -> None:
    control.reset()
    TinyPerson.clear_agents()
    TinyWorld.clear_environments()


def _agent_persona(agent_id: str, agent_preset: Mapping[str, Any]) -> dict[str, Any]:
    persona: dict[str, Any] = {
        "age": agent_preset["age"],
        "country_of_residence": "Singapore",
        "scenario_agent_id": agent_id,
        "scenario_role": agent_preset["role"],
        "common_language": "English",
        "immediate_priority": agent_preset["immediate_priority"],
        "style": (
            f"{agent_preset['interaction_style']} Use ordinary spoken English with short, "
            "context-dependent replies. Contractions and sentence fragments are allowed. "
            "Do not force slang, accent, or code-switching."
        ),
        "other_facts": [
            "Use only information you have observed or were explicitly given.",
            "Do not assume unstated traits, intentions, or identities of other agents.",
            "There is no required conflict, agreement, resolution, or target ending.",
            (
                "Treat your immediate priority as a genuine practical constraint; do not "
                "abandon it until its stated cost has been addressed."
            ),
            (
                "A proposed action is not completed unless a later observation confirms "
                "that it happened."
            ),
            "Do not invent friendship or prior familiarity with the other participants.",
            "Do not repeat thanks, encouragement, agreement, or an intention already stated.",
            agent_preset["behavioral_guidance"],
            f"Your interpretation of the situation: {agent_preset['normative_position']}",
            f"Your current negotiation boundary: {agent_preset['negotiation_boundary']}",
            f"What can justify reconsideration: {agent_preset['reconsideration_criteria']}",
            "If there is nothing relevant to add, wait by issuing DONE.",
        ],
    }
    cultural_background = agent_preset.get("cultural_background")
    if cultural_background is not None:
        persona["cultural_background"] = cultural_background
    return persona


def create_scenario_instance(
    scenario: ScenarioPreset, configuration_id: str
) -> ScenarioInstance:
    """Create four fresh agents with shared and private facts correctly separated."""

    preset = materialize_configuration(scenario, configuration_id)
    participants: dict[str, TinyPerson] = {}
    for agent_id, agent_preset in preset["agents"].items():
        person = TinyPerson(name=f"Agent {agent_id}")
        person._prompt_template_path = str(AGENT_PROMPT_PATH)
        if preset["scenario_id"] == "S02":
            person.add_mental_faculty(_kitchen_action_faculty())
        elif preset["scenario_id"] == "S04":
            person.add_mental_faculty(_seat_action_faculty())
        elif preset["scenario_id"] == "S06":
            person.add_mental_faculty(_order_action_faculty())
        person.include_persona_definitions(_agent_persona(agent_id, agent_preset))
        participants[agent_id] = person

    world_class = {
        "S02": KitchenConflictWorld,
        "S04": SeatConflictWorld,
        "S06": OrderConflictWorld,
    }.get(preset["scenario_id"], FaceToFaceWorld)
    world = world_class(
        name=f"{preset['scenario_id']} — {preset['title']}",
        agents=list(participants.values()),
        initial_datetime=datetime.fromisoformat(preset["initial_datetime"]),
        broadcast_if_no_target=True,
    )

    shared_context = [
        "You are participating in a simulated ordinary face-to-face interaction in Singapore.",
        preset["shared_setting"],
        preset["shared_trigger"],
        (
            "Act only on information you have been given or have encountered. Do not invent "
            "major external events or force a conflict, agreement, or resolution."
        ),
    ]
    for agent_id, person in participants.items():
        agent_preset = preset["agents"][agent_id]
        person.move_to(preset["environment"], context=shared_context)
        person._update_cognitive_state(
            goals=agent_preset["immediate_priority"],
            attention=agent_preset["initial_observation"],
        )
        person.socialize(
            (
                f"Your initial observation: {agent_preset['initial_observation']}\n"
                f"Your private knowledge: {agent_preset['private_knowledge']}\n"
                "Other participants do not automatically know this private information."
            ),
            source=world,
        )

    for source in participants.values():
        for target in participants.values():
            if source is not target:
                source.make_agent_accessible(
                    target,
                    (
                        "Another person in this face-to-face interaction. Do not assume "
                        "unstated traits or private information about them."
                    ),
                )

    return ScenarioInstance(preset=preset, participants=participants, world=world)


def run_one_round(
    instance: ScenarioInstance, conversation_mode: str = "fixed_round_robin"
) -> list[Mapping | Sequence[Mapping]]:
    """Run one fixed cycle or one direct-reply/self-selection interval."""

    elapsed = (
        timedelta(seconds=20)
        if instance.preset["scenario_id"] == "S06"
        else timedelta(minutes=2)
    )
    if conversation_mode == "hybrid_self_selection":
        return [
            instance.world.run_hybrid_round(
                timedelta_per_round=elapsed,
                max_public_turns=2,
            )
        ]
    if conversation_mode != "fixed_round_robin":
        raise ValueError(f"Unknown conversation mode: {conversation_mode}")
    return instance.world.run(
        1,
        timedelta_per_step=elapsed,
        return_actions=True,
        parallelize=False,
        randomize_agents_order=False,
    )


def inject_round_observation(
    instance: ScenarioInstance, round_number: int
) -> str | None:
    """Deliver a predefined, public world update before a simulation round."""

    observation = instance.preset.get("round_observations", {}).get(round_number)
    if hasattr(instance.world, "prepare_round"):
        observation = instance.world.prepare_round(round_number, observation)
    if not observation:
        return None
    for person in instance.participants.values():
        person.socialize(
            f"Public environment update before round {round_number}: {observation}",
            source=instance.world,
        )
    return observation


def flatten_actions(
    actions_over_time: Sequence[Mapping | Sequence[Mapping]],
) -> list[dict[str, Any]]:
    """Flatten TinyWorld actions while preserving round, turn, and private actions."""

    events: list[dict[str, Any]] = []
    turn = 0
    for round_number, round_actions in enumerate(actions_over_time, start=1):
        batches = (
            [round_actions]
            if isinstance(round_actions, Mapping)
            else round_actions
        )
        if not isinstance(batches, Sequence):
            continue
        for batch in batches:
            if not isinstance(batch, Mapping):
                continue
            for agent_name, agent_actions in batch.items():
                turn += 1
                for action_index, action_record in enumerate(agent_actions or [], start=1):
                    action = (
                        action_record.get("action", action_record)
                        if isinstance(action_record, Mapping)
                        else None
                    )
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


__all__ = [
    "AGENT_PROMPT_PATH",
    "FaceToFaceWorld",
    "KitchenConflictWorld",
    "OrderConflictWorld",
    "SeatConflictWorld",
    "ScenarioInstance",
    "create_scenario_instance",
    "flatten_actions",
    "inject_round_observation",
    "reset_simulation_state",
    "run_one_round",
]
