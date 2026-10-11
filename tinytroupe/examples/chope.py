"""Independent Singapore hawker-centre chope scenario.

The scenario contains exactly one injected event. Agent-specific observations
preserve the asymmetric knowledge present in the situation without telling all
agents how to interpret the tissue packet.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Mapping, Optional

from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld

from .loaders import load_example_agent_specification


DEFAULT_INITIAL_DATETIME = datetime(2026, 10, 10, 12, 30)
WORLD_NAME = "Neighbourhood Hawker Centre - Chope Experiment"
WORLD_DESCRIPTION = (
    "A busy neighbourhood hawker centre during lunch. The crowd is moderate: "
    "finding another place may take effort, but there is no severe seat shortage. "
    "The four people near this table are strangers with no prior interaction."
)

PARTICIPANT_SPECIFICATIONS = {
    "mr_lim": "Mr_Lim",
    "rachel": "Rachel_Pereira",
    "nur_aisyah": "Nur_Aisyah",
    "arjun": "Arjun",
}


@dataclass(frozen=True)
class ChopeEventState:
    """State recorded when the scenario's sole event is introduced."""

    key: str
    started_at: datetime
    summary: str


def create_chope_participants() -> Dict[str, TinyPerson]:
    """Create fresh participants from the authored persona specifications."""

    return {
        key: TinyPerson.load_specification(load_example_agent_specification(spec_name))
        for key, spec_name in PARTICIPANT_SPECIFICATIONS.items()
    }


class ChopeWorld(TinyWorld):
    """One-table environment where every spoken remark is publicly audible."""

    def _handle_talk(self, source_agent: TinyPerson, content: str, target: str):
        # A named addressee controls conversational intent, not audibility, in
        # this compact face-to-face setting. Everyone else at the table hears
        # the same utterance and can respond to the evolving interaction.
        self.broadcast(content, source=source_agent)


class ChopeScenario:
    """Controller for one independent run of the hawker-centre scenario."""

    def __init__(
        self,
        participants: Optional[Mapping[str, TinyPerson]] = None,
        initial_datetime: Optional[datetime] = None,
    ):
        self.participants = dict(participants or create_chope_participants())
        missing = set(PARTICIPANT_SPECIFICATIONS) - set(self.participants)
        if missing:
            raise ValueError(
                "Missing chope participants: " + ", ".join(sorted(missing))
            )

        self.world = ChopeWorld(
            WORLD_NAME,
            list(self.participants.values()),
            initial_datetime=initial_datetime or DEFAULT_INITIAL_DATETIME,
            # In a face-to-face dispute around one table, speech without an
            # explicit addressee is still audible to everyone nearby. This
            # prevents models that omit the optional target field from being
            # unfairly treated as if they had remained silent.
            broadcast_if_no_target=True,
        )
        self.event_state: Optional[ChopeEventState] = None
        self._place_and_connect_participants()

    def participant(self, key: str) -> TinyPerson:
        try:
            return self.participants[key]
        except KeyError as exc:
            raise KeyError(
                f"Unknown participant '{key}'. Expected one of: "
                f"{', '.join(self.participants)}"
            ) from exc

    def trigger(self) -> ChopeEventState:
        """Inject the one key event without making an LLM call."""

        if self.event_state is not None:
            raise RuntimeError("The chope event has already been triggered for this run.")

        summary = (
            "Rachel moves a tissue packet from an otherwise empty table and sits "
            "down just as Mr Lim returns carrying his food."
        )
        self.event_state = ChopeEventState(
            key="tissue_packet_moved",
            started_at=self.world.current_datetime,
            summary=summary,
        )

        self.participant("mr_lim").socialize(
            "You left your unopened tissue packet on this table before buying food, "
            "intending to reserve the seat. You now return carrying your food and see "
            "Rachel move your packet aside and sit down.",
            source=self.world,
        )
        self.participant("rachel").socialize(
            "You found an otherwise empty table with a small unopened tissue packet "
            "on it. You moved the packet carefully to the side and sat down. At that "
            "moment, Mr Lim returns carrying his food and notices you at the table.",
            source=self.world,
        )

        observer_stimulus = (
            "While looking for a place to sit nearby, you see Rachel move a small "
            "unopened tissue packet from an empty table and sit down just as Mr Lim "
            "returns to that table carrying his food. You do not know either person."
        )
        self.participant("nur_aisyah").socialize(
            observer_stimulus, source=self.world
        )
        self.participant("arjun").socialize(observer_stimulus, source=self.world)
        return self.event_state

    def run(
        self,
        rounds: int = 3,
        *,
        parallelize: bool = False,
        randomize_agents_order: bool = False,
    ):
        """Run a fixed number of rounds and return every generated action."""

        if rounds < 1:
            raise ValueError("rounds must be at least 1")
        if self.event_state is None:
            self.trigger()
        return self.world.run(
            rounds,
            return_actions=True,
            parallelize=parallelize,
            randomize_agents_order=randomize_agents_order,
        )

    def _place_and_connect_participants(self):
        for participant in self.participants.values():
            participant.move_to(
                "the seating area beside the same hawker-centre table",
                context=[
                    WORLD_DESCRIPTION,
                    "The people near you are strangers. Do not assume their motives, "
                    "relationships, or views before they communicate them.",
                ],
            )

        participants = list(self.participants.values())
        for source in participants:
            for target in participants:
                if source is not target:
                    source.make_agent_accessible(
                        target,
                        "A stranger close enough to see and hear at the hawker centre.",
                    )


def create_chope_scenario(
    initial_datetime: Optional[datetime] = None,
) -> ChopeScenario:
    """Create a fresh independent chope scenario."""

    return ChopeScenario(initial_datetime=initial_datetime)


__all__ = [
    "ChopeEventState",
    "ChopeScenario",
    "ChopeWorld",
    "DEFAULT_INITIAL_DATETIME",
    "PARTICIPANT_SPECIFICATIONS",
    "WORLD_DESCRIPTION",
    "WORLD_NAME",
    "create_chope_participants",
    "create_chope_scenario",
]
