"""Singapore shared-housing example scenario.

This module turns the narrative in ``shared-housing-scenario.md`` into reusable
TinyTroupe building blocks.  It deliberately specifies situations, channels,
and observable facts while leaving the residents' reactions to the simulation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, Mapping, Optional

from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld

from .loaders import load_example_agent_specification


DEFAULT_INITIAL_DATETIME = datetime(2026, 2, 8, 18, 0)

FLAT_NAME = "Block 47 Clementi Shared Flat"
FLAT_DESCRIPTION = (
    "A roughly 90-square-metre four-room HDB flat at Block 47, Clementi "
    "Avenue 3, Singapore. It has four bedrooms, a shared kitchen with limited "
    "counter space, a living/dining room, Wei Ling's ensuite bathroom, and one "
    "bathroom shared by Ravi, Maria, and Zhang Wei."
)

HOUSEHOLD_RULES = (
    "Clean the kitchen after each use; keep common areas tidy; agree as a group "
    "before hosting overnight guests; share the cost of dish soap, bin bags, "
    "and toilet paper; use the household WhatsApp group for coordination."
)

RESIDENT_SPECIFICATIONS = {
    "wei_ling": "Wei_Ling_Chen",
    "ravi": "Ravi_Krishnamurthy",
    "maria": "Maria_Santos",
    "zhang_wei": "Zhang_Wei",
}


@dataclass(frozen=True)
class EpisodeDefinition:
    """Metadata for a situation that can be introduced into the simulation."""

    key: str
    title: str
    category: str
    summary: str


@dataclass(frozen=True)
class EpisodeState:
    """The situation most recently introduced to the household."""

    definition: EpisodeDefinition
    started_at: datetime


EPISODE_DEFINITIONS = (
    EpisodeDefinition(
        "kitchen_scheduling",
        "Kitchen Scheduling",
        "everyday",
        "Several residents need the small shared kitchen at overlapping times.",
    ),
    EpisodeDefinition(
        "bathroom_rush",
        "Bathroom Rush",
        "everyday",
        "An unexpected shift change puts Maria and Ravi on the same bathroom schedule.",
    ),
    EpisodeDefinition(
        "chore_negotiation",
        "Chore Negotiation",
        "everyday",
        "Uneven contributions become visible in a household with no formal rota.",
    ),
    EpisodeDefinition(
        "household_expenses",
        "Household Expenses",
        "everyday",
        "Wei Ling notices that Zhang Wei's transfer is two weeks late.",
    ),
    EpisodeDefinition(
        "noise_and_sleep",
        "Noise and Sleep",
        "everyday",
        "Wei Ling can hear Zhang Wei's late Mandarin video call after bedtime.",
    ),
    EpisodeDefinition(
        "ravi_guest_afternoon",
        "Ravi's Guest Afternoon",
        "episodic",
        "Three of Ravi's colleagues occupy the living room for a loud Saturday visit.",
    ),
    EpisodeDefinition(
        "chinese_new_year",
        "Chinese New Year Preparation",
        "episodic",
        "Wei Ling's parents begin a three-day Chinese New Year visit.",
    ),
    EpisodeDefinition(
        "deepavali_decorations",
        "Deepavali Decorations",
        "episodic",
        "Ravi decorates the corridor without consulting the household first.",
    ),
    EpisodeDefinition(
        "late_kitchen_incident",
        "Zhang Wei's Late Kitchen Incident",
        "episodic",
        "Wei Ling finds oil on the stove and posts an unnamed reminder.",
    ),
    EpisodeDefinition(
        "maintenance_request",
        "The Maintenance Request",
        "episodic",
        "The shared bathroom shower head breaks and the landlord must be contacted.",
    ),
    EpisodeDefinition(
        "maria_night_shift_return",
        "Maria's Night Shift Return",
        "episodic",
        "Maria cleans Ravi's guests' containers, then tells Wei Ling the next morning.",
    ),
)

EPISODES = {episode.key: episode for episode in EPISODE_DEFINITIONS}


def create_shared_housing_residents() -> Dict[str, TinyPerson]:
    """Create the four residents from their authored persona specifications."""

    return {
        key: TinyPerson.load_specification(load_example_agent_specification(spec_name))
        for key, spec_name in RESIDENT_SPECIFICATIONS.items()
    }


class SharedHousingScenario:
    """Controller for the multilingual Clementi shared-housing simulation.

    ``TinyWorld`` has no first-class concept of rooms or messaging channels.
    This controller represents location through ``move_to`` and represents the
    currently available interaction channel through agent accessibility. Text
    stimuli explicitly label WhatsApp, private messages, and observations so
    agents can reason about the social meaning of the channel.
    """

    def __init__(
        self,
        residents: Optional[Mapping[str, TinyPerson]] = None,
        initial_datetime: Optional[datetime] = None,
    ):
        self.residents = dict(residents or create_shared_housing_residents())
        missing = set(RESIDENT_SPECIFICATIONS) - set(self.residents)
        if missing:
            raise ValueError(
                "Missing shared-housing residents: " + ", ".join(sorted(missing))
            )

        self.world = TinyWorld(
            FLAT_NAME,
            list(self.residents.values()),
            initial_datetime=initial_datetime or DEFAULT_INITIAL_DATETIME,
            broadcast_if_no_target=False,
        )
        self.current_episode: Optional[EpisodeState] = None
        self._set_locations({key: "their bedroom" for key in self.residents})
        self._open_whatsapp_group()

    @property
    def available_episodes(self):
        """Return the episode definitions in their intended display order."""

        return EPISODE_DEFINITIONS

    def resident(self, key: str) -> TinyPerson:
        """Return a resident by stable scenario key."""

        try:
            return self.residents[key]
        except KeyError as exc:
            raise KeyError(
                f"Unknown resident '{key}'. Expected one of: "
                f"{', '.join(self.residents)}"
            ) from exc

    def trigger(self, episode_key: str) -> EpisodeState:
        """Introduce an episode without running any agent turns."""

        trigger = getattr(self, f"trigger_{episode_key}", None)
        if trigger is None or episode_key not in EPISODES:
            raise KeyError(
                f"Unknown episode '{episode_key}'. Expected one of: "
                f"{', '.join(EPISODES)}"
            )
        return trigger()

    def run_episode(
        self,
        episode_key: str,
        steps: int = 3,
        *,
        parallelize: bool = False,
        randomize_agents_order: bool = False,
    ):
        """Introduce an episode and run reproducible household interaction turns."""

        if steps < 1:
            raise ValueError("steps must be at least 1")
        self.trigger(episode_key)
        return self.world.run(
            steps,
            return_actions=True,
            parallelize=parallelize,
            randomize_agents_order=randomize_agents_order,
        )

    def post_whatsapp(
        self,
        sender_key: str,
        message: str,
        recipient_keys: Optional[Iterable[str]] = None,
    ):
        """Post a message to the household WhatsApp group or a subset of it."""

        sender = self.resident(sender_key)
        recipients = list(recipient_keys or self.residents.keys())
        self._open_whatsapp_group(recipients)
        wrapped = f"[Household WhatsApp group] {message}"

        sender.socialize(
            f'You have just posted this message in the household WhatsApp group: "{message}"',
            source=self.world,
        )
        for key in recipients:
            if key != sender_key:
                self.resident(key).listen(wrapped, source=sender)

    def send_private_message(self, sender_key: str, recipient_key: str, message: str):
        """Deliver a labelled one-to-one WhatsApp message."""

        sender = self.resident(sender_key)
        recipient = self.resident(recipient_key)
        sender.make_agent_accessible(
            recipient, "A flatmate reachable in a private WhatsApp conversation."
        )
        recipient.make_agent_accessible(
            sender, "A flatmate reachable in a private WhatsApp conversation."
        )
        sender.socialize(
            f'You have just sent {recipient.name} this private WhatsApp message: "{message}"',
            source=self.world,
        )
        recipient.listen(f"[Private WhatsApp message] {message}", source=sender)

    def trigger_kitchen_scheduling(self) -> EpisodeState:
        state = self._begin_episode(
            "kitchen_scheduling",
            datetime(2026, 2, 8, 17, 55),
            {
                "wei_ling": "shared kitchen",
                "ravi": "shared kitchen",
                "maria": "shared kitchen",
                "zhang_wei": "his bedroom",
            },
        )
        self._connect_group(
            ("wei_ling", "ravi", "maria"),
            "A flatmate physically present in the small shared kitchen.",
        )
        self._observe_many(
            ("wei_ling", "ravi", "maria"),
            "It is early Sunday evening. Maria is finishing a weekend dish, Wei Ling "
            "has arrived to begin her weekly cooking, and Ravi has ingredients ready "
            "for dinner. The stove has four burners but usable counter space is very "
            "limited, so their plans now overlap.",
        )
        return state

    def trigger_bathroom_rush(self) -> EpisodeState:
        state = self._begin_episode(
            "bathroom_rush",
            datetime(2026, 2, 9, 7, 20),
            {
                "wei_ling": "master bedroom and ensuite",
                "ravi": "corridor outside the shared bathroom",
                "maria": "shared bathroom",
                "zhang_wei": "NUS campus",
            },
        )
        self._connect_group(
            ("ravi", "maria"),
            "A flatmate present at the shared bathroom during the morning rush.",
        )
        self._observe_many(
            ("ravi", "maria"),
            "Maria was unexpectedly assigned an early hospital shift and needs the "
            "shared bathroom now. Ravi normally starts using it at 7:30 AM and must "
            "prepare for work. Neither had known about the collision in advance.",
        )
        return state

    def trigger_chore_negotiation(self) -> EpisodeState:
        state = self._begin_episode(
            "chore_negotiation",
            datetime(2026, 2, 15, 20, 0),
            {key: "their bedroom" for key in self.residents},
        )
        self._open_whatsapp_group()
        self._observe_many(
            self.residents,
            "It is Sunday evening. The flat still has no chore rota. Maria has cleaned "
            "the shared bathroom and taken out rubbish more than once this week; Ravi "
            "has done several visible chores; the common area and Zhang Wei's late-night "
            "kitchen residue have required extra attention. Nobody has yet started a "
            "household discussion about the imbalance.",
        )
        return state

    def trigger_household_expenses(self) -> EpisodeState:
        state = self._begin_episode(
            "household_expenses",
            datetime(2026, 2, 16, 19, 0),
            {key: "their bedroom" for key in self.residents},
        )
        self._open_whatsapp_group()
        self.resident("wei_ling").socialize(
            "While reconciling the monthly electricity, internet, and shared-grocery "
            "payments, you see that Ravi paid early with a friendly note, Maria paid on "
            "time, and Zhang Wei's transfer is now two weeks late. You have not raised "
            "the late payment yet and must decide how to handle it.",
            source=self.world,
        )
        return state

    def trigger_noise_and_sleep(self) -> EpisodeState:
        state = self._begin_episode(
            "noise_and_sleep",
            datetime(2026, 2, 18, 0, 40),
            {
                "wei_ling": "her bedroom",
                "ravi": "his bedroom",
                "maria": "hospital night shift",
                "zhang_wei": "his bedroom",
            },
        )
        self._open_whatsapp_group()
        self.resident("wei_ling").socialize(
            "It is 12:40 AM, well after your usual bedtime. Through the wall you can "
            "hear Zhang Wei speaking Mandarin on a video call. His voice is not shouting, "
            "but it has repeatedly become loud enough to wake you. No one has made a "
            "noise complaint tonight.",
            source=self.world,
        )
        return state

    def trigger_ravi_guest_afternoon(self) -> EpisodeState:
        state = self._begin_episode(
            "ravi_guest_afternoon",
            datetime(2026, 2, 21, 16, 0),
            {
                "wei_ling": "her bedroom",
                "ravi": "living and dining room",
                "maria": "living and dining room",
                "zhang_wei": "outside the flat",
            },
        )
        self._open_whatsapp_group()
        self._connect_group(
            ("ravi", "maria"),
            "A flatmate physically present with Ravi's guests in the living room.",
        )
        self._observe_many(
            self.residents,
            "Ravi invited three work colleagues for Saturday afternoon. They have been "
            "talking loudly, eating takeaway, and using the living room for nearly four "
            "hours. Maria joined them briefly. Wei Ling has stayed in her room, and Zhang "
            "Wei left the flat after the gathering became noisy.",
        )
        return state

    def trigger_chinese_new_year(self) -> EpisodeState:
        state = self._begin_episode(
            "chinese_new_year",
            datetime(2026, 2, 16, 18, 30),
            {key: "living and dining room" for key in self.residents},
        )
        self._connect_group(
            self.residents,
            "A flatmate physically present during Wei Ling's family visit.",
        )
        self._observe_many(
            self.residents,
            "Wei Ling's parents have arrived for a three-day Chinese New Year visit after "
            "she asked everyone to keep the flat especially tidy. Her mother speaks "
            "Mandarin and Hokkien but almost no English. The residents are together for "
            "the first greeting in the living room; no response or translation is assumed.",
        )
        return state

    def trigger_deepavali_decorations(self) -> EpisodeState:
        state = self._begin_episode(
            "deepavali_decorations",
            datetime(2026, 11, 7, 18, 0),
            {key: "flat entrance corridor" for key in self.residents},
        )
        self._connect_group(
            self.residents,
            "A flatmate physically present at the entrance corridor.",
        )
        self._observe_many(
            self.residents,
            "Ravi has just hung a small string of lights and a paper lantern in the shared "
            "corridor for Deepavali. He did not ask the household beforehand. Everyone "
            "can now see the decorations; nobody's reaction is predetermined.",
        )
        return state

    def trigger_late_kitchen_incident(self) -> EpisodeState:
        state = self._begin_episode(
            "late_kitchen_incident",
            datetime(2026, 2, 19, 6, 50),
            {
                "wei_ling": "shared kitchen",
                "ravi": "his bedroom",
                "maria": "her bedroom",
                "zhang_wei": "his bedroom",
            },
        )
        self.resident("wei_ling").socialize(
            "You have found fresh oil residue on the stove this morning. Zhang Wei cooked "
            "there around midnight, and the others are likely to infer this too, although "
            "you do not want to name or embarrass him publicly.",
            source=self.world,
        )
        self.post_whatsapp(
            "wei_ling", "Please clean the stove after cooking, thanks."
        )
        return state

    def trigger_maintenance_request(self) -> EpisodeState:
        state = self._begin_episode(
            "maintenance_request",
            datetime(2026, 2, 23, 19, 15),
            {
                "wei_ling": "living and dining room",
                "ravi": "corridor outside the shared bathroom",
                "maria": "corridor outside the shared bathroom",
                "zhang_wei": "corridor outside the shared bathroom",
            },
        )
        self._open_whatsapp_group()
        self._observe_many(
            self.residents,
            "The shower head in the bathroom shared by Ravi, Maria, and Zhang Wei has "
            "broken and cannot be used normally. The landlord needs to be contacted. Wei "
            "Ling normally handles the landlord and can communicate with him in English "
            "or Mandarin, but nobody has yet taken responsibility or relayed a plan.",
        )
        return state

    def trigger_maria_night_shift_return(self) -> EpisodeState:
        state = self._begin_episode(
            "maria_night_shift_return",
            datetime(2026, 2, 22, 8, 0),
            {
                "wei_ling": "shared kitchen",
                "ravi": "his bedroom",
                "maria": "shared kitchen",
                "zhang_wei": "NUS campus",
            },
        )
        self._connect_group(
            ("wei_ling", "maria"),
            "A flatmate physically present for a private morning conversation.",
        )
        self.resident("maria").socialize(
            "Last night at 12:30 AM, exhausted after your hospital shift, you found "
            "takeaway containers from Ravi's afternoon guests still on the dining table. "
            "You cleaned them without messaging anyone. This morning you have decided to "
            "mention what happened privately to Wei Ling rather than to Ravi.",
            source=self.world,
        )
        self.resident("wei_ling").listen(
            "[Private in-person conversation] I came home after my night shift and the "
            "takeaway containers from Ravi's guests were still on the table, so I cleaned "
            "them. I was really tired. I didn't want to make a big issue, but I wanted to "
            "tell you.",
            source=self.resident("maria"),
        )
        return state

    def _begin_episode(
        self,
        episode_key: str,
        started_at: datetime,
        locations: Mapping[str, str],
    ) -> EpisodeState:
        self.world.current_datetime = started_at
        for resident in self.residents.values():
            resident.make_all_agents_inaccessible()
        self._set_locations(locations, episode_key=episode_key)
        state = EpisodeState(EPISODES[episode_key], started_at)
        self.current_episode = state
        return state

    def _set_locations(
        self, locations: Mapping[str, str], episode_key: Optional[str] = None
    ):
        for key, resident in self.residents.items():
            location = locations.get(key, "outside the flat")
            context = [
                FLAT_DESCRIPTION,
                f"The household's informal rules are: {HOUSEHOLD_RULES}",
                f"Your current location is {location}.",
            ]
            if episode_key:
                context.append(
                    f"The current household situation is '{EPISODES[episode_key].title}'."
                )
            resident.move_to(location, context=context)

    def _connect_group(self, resident_keys: Iterable[str], description: str):
        keys = list(resident_keys)
        for source_key in keys:
            for target_key in keys:
                if source_key != target_key:
                    source = self.resident(source_key)
                    target = self.resident(target_key)
                    if target not in source.accessible_agents:
                        source.make_agent_accessible(target, description)

    def _open_whatsapp_group(self, resident_keys: Optional[Iterable[str]] = None):
        keys = list(resident_keys or self.residents.keys())
        self._connect_group(
            keys,
            "A flatmate currently reachable through the household WhatsApp group; "
            "this does not imply physical co-presence.",
        )

    def _observe_many(self, resident_keys: Iterable[str], observation: str):
        for key in resident_keys:
            self.resident(key).socialize(observation, source=self.world)


def create_shared_housing_scenario(
    initial_datetime: Optional[datetime] = None,
) -> SharedHousingScenario:
    """Convenience constructor for the complete scenario."""

    return SharedHousingScenario(initial_datetime=initial_datetime)


def extract_shared_housing_signals(scenario_or_world):
    """Extract the scenario's five research signals from the interaction history.

    This helper performs an LLM call through :class:`ResultsExtractor`; scenario
    construction and episode triggering themselves make no LLM calls.
    """

    from tinytroupe.extraction import ResultsExtractor

    world = getattr(scenario_or_world, "world", scenario_or_world)
    if not isinstance(world, TinyWorld):
        raise TypeError("scenario_or_world must be a SharedHousingScenario or TinyWorld")

    extractor = ResultsExtractor()
    return extractor.extract_results_from_world(
        world,
        extraction_objective=(
            "Analyze the household interaction without inventing events. Identify "
            "evidence about multilingual accommodation, social grouping, conflict "
            "resolution, spontaneous translation, and language-related inclusion or "
            "exclusion. Distinguish observed behavior from uncertain interpretation."
        ),
        situation=(
            "Four culturally and linguistically diverse residents share an HDB flat in "
            "Clementi, Singapore. English is the main common language, but proficiency, "
            "register, and access to Mandarin, Tamil, Filipino/Tagalog, Singlish, and "
            "Hokkien differ."
        ),
        fields=[
            "language_accommodation",
            "social_grouping",
            "conflict_resolution",
            "spontaneous_translation",
            "language_as_social_distance",
        ],
        fields_hints={
            "language_accommodation": "Who adjusted language, register, pace, or channel; cite concrete evidence.",
            "social_grouping": "Coalitions, bridges, isolation, or changes in closeness; cite concrete evidence.",
            "conflict_resolution": "Who raised issues, directly or indirectly, through which channel, and with what result.",
            "spontaneous_translation": "Any translation or clarification, who supplied it, and who remained excluded.",
            "language_as_social_distance": "How language ability affected participation, legitimacy, or perceived warmth.",
        },
    )


__all__ = [
    "DEFAULT_INITIAL_DATETIME",
    "EPISODE_DEFINITIONS",
    "EPISODES",
    "EpisodeDefinition",
    "EpisodeState",
    "FLAT_DESCRIPTION",
    "FLAT_NAME",
    "HOUSEHOLD_RULES",
    "RESIDENT_SPECIFICATIONS",
    "SharedHousingScenario",
    "create_shared_housing_residents",
    "create_shared_housing_scenario",
    "extract_shared_housing_signals",
]
