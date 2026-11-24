"""Channel-based society runs: who can read what, news by stage, a cutoff, and forks from the cutoff.

A round: the stage's news reaches everyone (full news up to the cutoff stage, physical facts only after it), then
each channel in turn offers every speaker one turn, in an order that rotates by round. Before a turn the agent is
told which channel it is in and who can read it; whatever it says (TALK) reaches only that channel's speakers and
readers. Governments speak only after the cutoff; before it their real decisions are in the news.

Kept apart from the four-agent engine (simulation.py, runner.py) so no older scenario, cast or prompt hash changes.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld

from ..scenario_presets.common import AgentPreset
from ..scenario_presets.haze_presets import _GUIDANCE
from ..simulation import _agent_persona, reset_simulation_state
from ..storage import (
    aggregate_resources,
    file_sha256,
    git_commit,
    read_json,
    utc_now,
    write_json_once,
    write_json_replace,
    write_text_once,
)
from .haze_society import SocietyPreset

SOCIETY_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "tiny_person_society.mustache"
CHECKPOINT_VERSION = 1
TRANSCRIPT_SCHEMA_VERSION = 1
START_TIME = "T20:00:00+08:00"


class ChannelWorld(TinyWorld):
    """Speech reaches only the members and readers of the channel the speaker is in."""

    def __init__(self, *args, channels: dict[str, dict], **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = channels
        self.current_channel: str | None = None
        self.current_round = 0
        self.deliveries: list[dict[str, Any]] = []

    def audience(self, channel_id: str, source_name: str) -> list[str]:
        """Everyone who receives a line written here, hidden readers included."""

        channel = self.channels[channel_id]
        names = list(dict.fromkeys(channel["speakers"] + channel["readers"] + channel.get("hidden_readers", [])))
        return [name for name in names if name != source_name]

    def visible_audience(self, channel_id: str, source_name: str) -> list[str]:
        """Who the writer is told can read this: hidden readers (HS3: governments in national groups) left out."""

        hidden = set(self.channels[channel_id].get("hidden_readers", []))
        return [name for name in self.audience(channel_id, source_name) if name not in hidden]

    def _handle_talk(self, source_agent: TinyPerson, content: str, target: str):
        if self.current_channel is None:
            raise RuntimeError("TALK outside a channel turn")
        channel = self.channels[self.current_channel]
        recipients = self.audience(self.current_channel, source_agent.name)
        addressee = target if target in recipients else None
        to = f" (to {addressee})" if addressee else ""
        for name in recipients:
            self.get_agent_by_name(name).socialize(
                f"In the {channel['name']}, {source_agent.name}{to} wrote: {content}", source=source_agent
            )
        self.deliveries.append(
            {
                "round": self.current_round,
                "channel": self.current_channel,
                "source": source_agent.name,
                "target": addressee,
                "recipients": recipients,
            }
        )

    def _handle_reach_out(self, source_agent: TinyPerson, content: str, target: str):
        # Nobody can open a new line to someone outside their channels.
        return None


# Preset fields added after pilot 1; left out of the hash while off, so HS1 keeps the hash pilot 1 recorded.
_LATER_SWITCHES = ("date_every_round", "governments_post_first")


def preset_sha256(preset: SocietyPreset) -> str:
    value = asdict(preset)
    for key in _LATER_SWITCHES:
        if not value[key]:
            del value[key]
    for channel in value["channels"]:
        for key in ("hidden_readers", "cue_note"):
            if not channel[key]:
                del channel[key]
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _persona(preset: SocietyPreset, agent) -> dict[str, Any]:
    style = preset.government_style if agent.kind == "government" else preset.style
    base = AgentPreset(
        age=agent.age or 18,
        role=agent.role,
        immediate_priority=agent.immediate_priority,
        private_knowledge=agent.private_knowledge,
        initial_observation=agent.initial_observation,
        interaction_style=style,
        behavioral_guidance=_GUIDANCE,
    )
    fields = {**asdict(base), "country_of_residence": agent.country}
    if agent.biography:
        fields["biography"] = agent.biography
    persona = _agent_persona(
        agent.agent_id,
        fields,
        timing_free=True,
        conversation_only=True,
        priced_priority=True,
        pinned_setting=preset.setting,
    )
    if agent.age is None:
        persona.pop("age")
    return persona


def channel_order(preset: SocietyPreset, round_number: int, after_cutoff: bool) -> list[tuple[str, list[str]]]:
    """Channels in fixed order; each channel's speakers rotate by round; governments only after the cutoff."""

    order = []
    for channel in preset.channels:
        speakers = [
            s for s in channel.speakers if after_cutoff or preset.agents[s].kind != "government"
        ]
        if not speakers:
            continue
        if preset.governments_post_first:
            groups = [
                [s for s in speakers if preset.agents[s].kind == "government"],
                [s for s in speakers if preset.agents[s].kind != "government"],
            ]
        else:
            groups = [speakers]
        ordered = []
        for group in groups:
            if group:
                shift = (round_number - 1) % len(group)
                ordered += group[shift:] + group[:shift]
        order.append((channel.channel_id, ordered))
    return order


def round_date(preset: SocietyPreset, round_number: int) -> str:
    """Date of a round: the stage's date for its first round, then evenly spread towards the next stage's date."""

    from datetime import date, timedelta

    rps = preset.rounds_per_stage
    index, offset = divmod(round_number - 1, rps)
    if index >= len(preset.stages):
        index, offset = len(preset.stages) - 1, offset + (index - len(preset.stages) + 1) * rps
    start = date.fromisoformat(preset.stages[index].date)
    if index + 1 < len(preset.stages):
        gap = (date.fromisoformat(preset.stages[index + 1].date) - start).days
    else:
        gap = 3 * rps
    day = start + timedelta(days=gap * offset // rps)
    return day.strftime("%A %d %B %Y").replace(" 0", " ")


def build_world(preset: SocietyPreset) -> tuple[ChannelWorld, dict[str, TinyPerson]]:
    reset_simulation_state()
    people: dict[str, TinyPerson] = {}
    for agent_id, agent in preset.agents.items():
        person = TinyPerson(name=agent.name)
        person._prompt_template_path = str(SOCIETY_PROMPT_PATH)
        person.include_persona_definitions(_persona(preset, agent))
        person.episodic_memory.lookback_length = preset.memory_lookback
        people[agent_id] = person
    channels = {
        c.channel_id: {
            "name": c.name,
            "description": c.description,
            "speakers": [preset.agents[s].name for s in c.speakers],
            "readers": [preset.agents[s].name for s in c.readers],
            "hidden_readers": [preset.agents[s].name for s in c.hidden_readers],
            "cue_note": c.cue_note,
        }
        for c in preset.channels
    }
    world = ChannelWorld(
        name=f"{preset.preset_id} — {preset.title}",
        agents=list(people.values()),
        initial_datetime=datetime.fromisoformat(preset.stages[0].date + START_TIME),
        broadcast_if_no_target=False,
        channels=channels,
    )
    context = [
        "You are taking part in a simulated online society of people and governments in Singapore, Malaysia, "
        "Indonesia and Brunei.",
        preset.setting,
        "Act only on information you have been given or have encountered. Do not invent major external events or "
        "force a conflict, agreement, or resolution.",
    ]
    for agent_id, person in people.items():
        agent = preset.agents[agent_id]
        person.move_to("Online", context=context)
        person._update_cognitive_state(goals=agent.immediate_priority, attention=agent.initial_observation)
        person.socialize(
            f"Your initial observation: {agent.initial_observation}\n"
            f"Your private knowledge: {agent.private_knowledge}\n"
            "Other people do not automatically know this private information.",
            source=world,
        )
    # Each agent knows the people it shares a channel with (as speaker or reader). A hidden reader knows the
    # channel's members; the members are not told about it.
    for agent_id, person in people.items():
        name = preset.agents[agent_id].name
        for other_id, other in people.items():
            if other is person:
                continue
            shared = [
                c["name"]
                for c in channels.values()
                if name in c["speakers"] + c["readers"] + c["hidden_readers"]
                and other.name in c["speakers"] + c["readers"]
            ]
            if shared:
                person.make_agent_accessible(
                    other,
                    f"From {preset.agents[other_id].country}; you are both in: {', '.join(shared)}. Do not assume "
                    "unstated traits or private information about them.",
                )
    return world, people


def _turn_cue(world: ChannelWorld, channel_id: str, speaker: str) -> str:
    channel = world.channels[channel_id]
    others = world.visible_audience(channel_id, speaker)
    note = f" {channel['cue_note']}" if channel.get("cue_note") else ""
    return (
        f"You are now in the {channel['name']}, {channel['description']}. Who can read what you write here: "
        f"{', '.join(others)}. Anything you write now is seen only there.{note}"
    )


def _call_records() -> list[dict]:
    from tinytroupe.clients import client

    llm_client = client()
    return llm_client.get_call_records() if hasattr(llm_client, "get_call_records") else []


def _reset_usage() -> None:
    from tinytroupe.clients import client

    llm_client = client()
    if hasattr(llm_client, "reset_usage_tracking"):
        llm_client.reset_usage_tracking()


def _restore_call_records(records: list[dict]) -> None:
    from tinytroupe.clients import client

    llm_client = client()
    if records and hasattr(llm_client, "restore_call_records"):
        llm_client.restore_call_records(records)


def run_society(
    *,
    preset: SocietyPreset,
    run_id: str,
    output_dir: Path,
    cutoff_stage: int,
    free_rounds: int,
    simulation_model: str,
    fork_from: Path | None = None,
) -> dict[str, Any]:
    """Run (or resume, or fork from a cutoff checkpoint) one society run and save its transcript."""

    transcript_path = output_dir / "transcripts" / f"{run_id}.json"
    if transcript_path.exists():
        return read_json(transcript_path)
    rps = preset.rounds_per_stage
    cutoff_round = cutoff_stage * rps
    total_rounds = cutoff_round + free_rounds
    sha = preset_sha256(preset)
    expected = {
        "version": CHECKPOINT_VERSION,
        "preset_id": preset.preset_id,
        "preset_sha256": sha,
        "agent_prompt_sha256": file_sha256(SOCIETY_PROMPT_PATH),
        "simulation_model": simulation_model,
        "cutoff_stage": cutoff_stage,
    }

    world, people = build_world(preset)
    _reset_usage()
    checkpoint_path = output_dir / "checkpoints" / f"{run_id}.json"
    events: list[dict] = []
    actions: list[dict] = []
    round_records: list[dict] = []
    history: dict[str, Any] | None = None
    completed = 0
    started_at = utc_now()

    resuming = checkpoint_path.exists()
    if resuming:
        saved = read_json(checkpoint_path)
    elif fork_from is not None:
        saved = read_json(fork_from)
        if saved.get("completed_round") != cutoff_round:
            raise ValueError(f"{fork_from} is not a cutoff checkpoint for stage {cutoff_stage}")
        history = {
            "forked_from_run": saved["run_id"],
            "checkpoint": str(fork_from),
            "history_resources": aggregate_resources(saved.get("api_calls", [])),
        }
    else:
        saved = None
    if saved is not None:
        mismatches = {k: (saved.get(k), v) for k, v in expected.items() if saved.get(k) != v}
        if mismatches:
            raise ValueError(f"Checkpoint does not match this run: {mismatches}")
        world.decode_complete_state(saved["world_state"])
        if resuming:
            # A fork's own cost starts at zero; only a resumed run carries its earlier calls.
            _restore_call_records(saved.get("api_calls", []))
            history = saved.get("history")
            started_at = saved.get("started_at", started_at)
        events, actions, round_records = saved["events"], saved["actions"], saved["round_records"]
        completed = saved["completed_round"]

    turn = max([e["turn"] for e in events], default=0)
    wall_start = time.perf_counter()
    for round_number in range(completed + 1, total_rounds + 1):
        print(f"[{run_id}] round {round_number}/{total_rounds}", flush=True)
        call_start = len(_call_records())
        round_start = time.perf_counter()
        world.current_round = round_number
        after_cutoff = round_number > cutoff_round
        news = None
        if (round_number - 1) % rps == 0:
            stage_number = (round_number - 1) // rps + 1
            if stage_number <= len(preset.stages):
                stage = preset.stages[stage_number - 1]
                news = stage.news if stage_number <= cutoff_stage else stage.physical
                for person in people.values():
                    person.socialize(f"News update: {news}", source=world)
                    # Kept in the persona too, so earlier news stays in every prompt after the memory window moves on.
                    person.include_persona_definitions({"news_so_far": {stage.date: news}})
                events.append(
                    {"round": round_number, "turn": 0, "agent": "Environment", "action_index": 0, "type": "OBSERVE",
                     "content": news, "target": None, "channel": "news"}
                )
        if news is None and preset.date_every_round:
            dated = f"It is now {round_date(preset, round_number)}."
            for person in people.values():
                person.socialize(dated, source=world)
            events.append(
                {"round": round_number, "turn": 0, "agent": "Environment", "action_index": 0, "type": "OBSERVE",
                 "content": dated, "target": None, "channel": "date"}
            )
        for channel_id, speakers in channel_order(preset, round_number, after_cutoff):
            for agent_id in speakers:
                person = people[agent_id]
                world.current_channel = channel_id
                person.socialize(_turn_cue(world, channel_id, person.name), source=world)
                generated = person.act(return_actions=True)
                popped = person.pop_latest_actions()
                world._handle_actions(person, popped)
                world.current_channel = None
                turn += 1
                actions.append({"round": round_number, "channel": channel_id, "agent": person.name, "generated": generated})
                for index, action in enumerate(popped, start=1):
                    events.append(
                        {"round": round_number, "turn": turn, "agent": person.name, "action_index": index,
                         "type": str(action.get("type", "UNKNOWN")).upper(),
                         "content": str(action.get("content") or ""), "target": action.get("target"),
                         "channel": channel_id}
                    )
        round_records.append(
            {"round": round_number, "after_cutoff": after_cutoff, "news": news,
             "wall_time_ms": round((time.perf_counter() - round_start) * 1000, 3),
             "call_start": call_start, "call_end": len(_call_records())}
        )
        state = {
            **expected,
            "run_id": run_id,
            "started_at": started_at,
            "checkpointed_at": utc_now(),
            "completed_round": round_number,
            "history": history,
            "events": events,
            "actions": actions,
            "round_records": round_records,
            "api_calls": _call_records(),
            "world_state": world.encode_complete_state(),
        }
        write_json_replace(checkpoint_path, state)
        if round_number == cutoff_round:
            # Kept after the run, so free-play forecasts can be forked from the end of the real history.
            write_json_replace(output_dir / "checkpoints" / f"{run_id}-cutoff.json", state)

    call_records = _call_records()
    delivered = {r["round"]: r["news"] for r in round_records if r.get("news")}
    transcript = {
        "schema_version": TRANSCRIPT_SCHEMA_VERSION,
        "kind": "society",
        "run": {
            "run_id": run_id,
            "preset_id": preset.preset_id,
            "cutoff_stage": cutoff_stage,
            "cutoff_round": cutoff_round,
            "free_rounds": free_rounds,
            "rounds": total_rounds,
            "simulation_model": simulation_model,
            "started_at": started_at,
            "finished_at": utc_now(),
            "wall_time_ms": round((time.perf_counter() - wall_start) * 1000, 3),
            "simulation_resources": aggregate_resources(call_records),
            "history": history,
        },
        "provenance": {
            "git_commit": git_commit(),
            "preset_sha256": sha,
            "agent_prompt_sha256": file_sha256(SOCIETY_PROMPT_PATH),
        },
        "society": asdict(preset),
        # Same keys the four-agent transcripts use, so tools/haze_stage_coder.py reads both.
        "scenario": {
            "agents": {
                aid: {"display_name": a.name, "country": a.country, "kind": a.kind}
                for aid, a in preset.agents.items()
            },
            "profile_treatment": {"countries": {aid: a.country for aid, a in preset.agents.items()}},
            "shared_setting": preset.setting,
            "shared_trigger": delivered.get(1, ""),
            "round_observations": {r: text for r, text in delivered.items() if r != 1},
        },
        "events": events,
        "private_and_public_actions": actions,
        "round_records": round_records,
        "deliveries": world.deliveries,
    }
    write_text_once(output_dir / "transcripts" / f"{run_id}.md", transcript_markdown(transcript, world))
    write_json_replace(
        output_dir / "resources" / f"{run_id}.json",
        {"run_id": run_id, "simulation_api_calls": call_records, "simulation_resources": aggregate_resources(call_records)},
    )
    write_json_once(transcript_path, transcript)
    checkpoint_path.unlink(missing_ok=True)
    return transcript


def transcript_markdown(transcript: dict, world: ChannelWorld) -> str:
    run = transcript["run"]
    lines = [
        f"# {run['run_id']} — society transcript",
        "",
        f"Cutoff after stage {run['cutoff_stage']} (round {run['cutoff_round']}); {run['free_rounds']} free rounds.",
        "",
        "## Setting",
        "",
        transcript["society"]["setting"],
    ]
    by_round: dict[int, list[dict]] = {}
    for e in transcript["events"]:
        by_round.setdefault(e["round"], []).append(e)
    for round_number in sorted(by_round):
        free = " (free play)" if round_number > run["cutoff_round"] else ""
        lines += ["", f"## Round {round_number}{free}"]
        current = None
        for e in by_round[round_number]:
            if e["type"] == "OBSERVE":
                label = "Date" if e.get("channel") == "date" else "News"
                lines += ["", f"**{label}:** {e['content']}"]
                continue
            if e["type"] != "TALK":
                continue
            if e["channel"] != current:
                current = e["channel"]
                lines += ["", f"### {world.channels[current]['name']}", ""]
            to = f" (to {e['target']})" if e.get("target") else ""
            lines.append(f"- **{e['agent']}**{to}: {e['content']}")
    return "\n".join(lines) + "\n"
