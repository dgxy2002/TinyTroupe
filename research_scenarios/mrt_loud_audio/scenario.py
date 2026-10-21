"""One-event MRT loud-mobile-video-audio scenario."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld


DEFAULT_INITIAL_DATETIME = datetime(2026, 10, 24, 18, 20)
WORLD_NAME = "East-West Line MRT Carriage"
WORLD_DESCRIPTION = (
    "A moderately occupied East-West Line MRT carriage during the evening commute. "
    "The journey is long, ordinary train noise is present, and no staff member is "
    "currently in the carriage. Four nearby passengers are strangers to one another."
)
PERSONA_FILES = {
    "audio_listener": "ethan_goh.agent.json",
    "commuter": "meera_iyer.agent.json",
    "supportive_bystander": "farah_aziz.agent.json",
    "conflict_averse_bystander": "lucas_ong.agent.json",
}
PRINCIPAL_PARTICIPANTS = ("audio_listener", "commuter")


@dataclass(frozen=True)
class MRTEventState:
    key: str
    started_at: datetime
    summary: str


def create_participants() -> dict[str, TinyPerson]:
    persona_dir = Path(__file__).resolve().parent / "personas"
    return {
        key: TinyPerson.load_specification(str(persona_dir / filename))
        for key, filename in PERSONA_FILES.items()
    }


class MRTCarriageWorld(TinyWorld):
    """Close carriage interaction where both passengers hear all speech."""

    def _handle_talk(self, source_agent: TinyPerson, content: str, target: str):
        self.broadcast(content, source=source_agent)


class MRTLoudAudioScenario:
    def __init__(self, initial_datetime: Optional[datetime] = None):
        self.participants = create_participants()
        self.world = MRTCarriageWorld(
            WORLD_NAME,
            list(self.participants.values()),
            initial_datetime=initial_datetime or DEFAULT_INITIAL_DATETIME,
            broadcast_if_no_target=True,
        )
        self.event_state: Optional[MRTEventState] = None
        for participant in self.participants.values():
            participant.move_to(
                "seats in the same MRT carriage section",
                context=[WORLD_DESCRIPTION],
            )
        for source_key, source in self.participants.items():
            for target_key, target in self.participants.items():
                if source_key != target_key:
                    source.make_agent_accessible(target, "A stranger seated nearby.")

    def trigger(self) -> MRTEventState:
        if self.event_state is not None:
            raise RuntimeError("The MRT loud-audio event has already been triggered.")
        summary = (
            "Ethan starts watching a mobile video through his phone speaker at a "
            "volume clearly audible to Meera during a long MRT journey."
        )
        self.event_state = MRTEventState(
            key="loud_mobile_video_without_headphones",
            started_at=self.world.current_datetime,
            summary=summary,
        )
        self.participants["audio_listener"].socialize(
            "You start watching a news video through your phone speaker during the "
            "long journey. You are tired and focused on the screen and have not "
            "assessed how far the sound carries. Your working wired earphones are in "
            "your bag. Meera, a stranger, is seated nearby.",
            source=self.world,
        )
        self.participants["commuter"].socialize(
            "A stranger seated nearby, Ethan, starts watching a mobile video without "
            "headphones. The audio is clearly audible over ordinary train noise and "
            "is disrupting your attempt to read and decompress after work. You do "
            "not know whether he realises how loud it is.",
            source=self.world,
        )
        self.participants["supportive_bystander"].socialize(
            "Ethan, a stranger seated nearby, starts playing a mobile news video "
            "through his phone speaker. The audio is clearly audible over ordinary "
            "train noise. Meera, another stranger, is trying to read and appears "
            "disturbed. You do not know whether Ethan realises the volume, whether "
            "he owns headphones, or what either person privately intends. You cannot "
            "accept an arrangement on their behalf.",
            source=self.world,
        )
        self.participants["conflict_averse_bystander"].socialize(
            "You hear Ethan, a stranger nearby, playing a mobile news video loudly "
            "enough to carry across the carriage section. Meera, also a stranger, is "
            "trying to read and appears disturbed. No staff member is in the carriage. "
            "You do not know whether Ethan has headphones or what either person's "
            "private intentions are, and you cannot resolve the issue for them.",
            source=self.world,
        )
        return self.event_state


def create_scenario(initial_datetime: Optional[datetime] = None) -> MRTLoudAudioScenario:
    return MRTLoudAudioScenario(initial_datetime=initial_datetime)


__all__ = [
    "DEFAULT_INITIAL_DATETIME",
    "MRTEventState",
    "MRTLoudAudioScenario",
    "PERSONA_FILES",
    "PRINCIPAL_PARTICIPANTS",
    "WORLD_DESCRIPTION",
    "WORLD_NAME",
    "create_participants",
    "create_scenario",
]
