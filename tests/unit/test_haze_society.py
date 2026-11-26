"""Society engine (research_questions/society/): channels, cutoff, checkpoints, forks. No API calls."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

from tinytroupe.agent import TinyPerson

from research_questions.scenario_presets import RUNNABLE_SCENARIOS
from research_questions.simulation import reset_simulation_state
from research_questions.society import SOCIETY_PRESETS
from research_questions.society import engine
from research_questions.society.engine import build_world, channel_order, run_society

PRESET = SOCIETY_PRESETS["HS1"]
NAMES = {aid: a.name for aid, a in PRESET.agents.items()}
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "research_questions" / "tools"))
import haze_stage_coder  # noqa: E402


def _last_text(person: TinyPerson) -> str:
    memories = person.episodic_memory.retrieve_all()
    return json.dumps(memories[-1], ensure_ascii=False) if memories else ""


def test_preset_cast_channels_and_wording():
    assert len(PRESET.agents) == 13
    assert sum(a.kind == "government" for a in PRESET.agents.values()) == 4
    assert {a.country for a in PRESET.agents.values()} == {"Singapore", "Malaysia", "Indonesia", "Brunei"}
    for channel in PRESET.channels:
        assert set(channel.speakers) | set(channel.readers) <= set(PRESET.agents)
        assert not set(channel.speakers) & set(channel.readers)
    channels = {c.channel_id: c for c in PRESET.channels}
    assert set(channels["diplomatic"].speakers) == {"SG-G", "MY-G", "ID-G", "BN-G"}
    assert "ID3" not in channels["public_feed"].speakers and "ID4" not in channels["public_feed"].speakers
    # No resolution goal or conduct words in anything the agents are given (build rule 10).
    texts = [PRESET.setting] + [
        t for a in PRESET.agents.values() for t in (a.immediate_priority, a.private_knowledge, a.biography)
    ]
    for text in texts:
        assert not re.search(r"\bmust\b", text, re.I), text
    # No real, named person plays an agent: governments are generic.
    for aid in ("SG-G", "MY-G", "ID-G", "BN-G"):
        assert PRESET.agents[aid].name.startswith("Government of ")
    assert len(PRESET.stages) == 8
    for stage in PRESET.stages:
        assert "room" not in stage.news.lower() and "room" not in stage.physical.lower()


def test_physical_updates_hold_no_decisions_after_the_cutoff():
    for stage in PRESET.stages[3:]:
        for word in ("said", "announced", "notices", "apolog", "task force", "boycott", "gas"):
            assert word not in stage.physical.lower(), (stage.number, word)


def test_talk_reaches_only_the_channel():
    world, people = build_world(PRESET)
    world.current_channel = "id_group"
    world._handle_talk(people["ID1"], "Kabut asap lagi.", target="")
    for aid in ("ID2", "ID3", "ID4", "ID-G"):
        assert "In the Indonesia group, Budi Santoso wrote: Kabut asap lagi." in _last_text(people[aid])
    for aid in ("SG1", "MY1", "BN1", "SG-G"):
        assert "Kabut asap" not in _last_text(people[aid])
    assert world.deliveries[-1]["recipients"] == [NAMES[a] for a in ("ID2", "ID3", "ID4", "ID-G")]

    world.current_channel = "diplomatic"
    world._handle_talk(people["SG-G"], "We should talk.", target=NAMES["ID-G"])
    assert set(world.deliveries[-1]["recipients"]) == {NAMES[a] for a in ("MY-G", "ID-G", "BN-G")}
    assert world.deliveries[-1]["target"] == NAMES["ID-G"]
    assert "We should talk" not in _last_text(people["SG1"])

    world.current_channel = None
    with pytest.raises(RuntimeError):
        world._handle_talk(people["SG1"], "outside", target="")
    reset_simulation_state()


def test_governments_speak_only_after_the_cutoff_and_order_rotates():
    before = dict(channel_order(PRESET, 1, after_cutoff=False))
    after = dict(channel_order(PRESET, 1, after_cutoff=True))
    assert "diplomatic" not in before
    assert not {"SG-G", "MY-G", "ID-G", "BN-G"} & set(before["public_feed"])
    assert set(after["diplomatic"]) == {"SG-G", "MY-G", "ID-G", "BN-G"}
    assert {"SG-G", "ID-G"} <= set(after["public_feed"])
    assert dict(channel_order(PRESET, 2, after_cutoff=False))["id_group"] == ["ID2", "ID3", "ID4", "ID1"]


def test_hs1_hash_unchanged_since_pilot_1():
    # Recorded in outputs/society-hs1-pilot1/manifest.json; the later switches must not change it.
    assert engine.preset_sha256(PRESET) == "7fcb85cb2145e030c0d255a78998c2bdc020aef7448ae61984b7d29241b0167e"


def test_hs2_fixes_and_government_facts():
    hs2 = SOCIETY_PRESETS["HS2"]
    assert engine.preset_sha256(hs2) != engine.preset_sha256(PRESET)
    # Same people and channels; only the four governments' private facts differ.
    for aid, agent in hs2.agents.items():
        if agent.kind == "government":
            old = PRESET.agents[aid].private_knowledge
            assert agent.private_knowledge.startswith(old.partition(" You read ")[0])
            assert agent.private_knowledge.endswith(old[old.index(" You read "):])
            assert len(agent.private_knowledge) > len(old)
            assert "2026" not in agent.private_knowledge
            assert not re.search(r"\bmust\b|\bshould\b", agent.private_knowledge, re.I)
        else:
            assert agent == PRESET.agents[aid]
    # Governments first in the public feed after the cutoff, each group rotating.
    feed = dict(channel_order(hs2, 2, after_cutoff=True))["public_feed"]
    assert feed[:4] == ["MY-G", "ID-G", "BN-G", "SG-G"] and "SG-G" not in feed[4:]
    assert dict(channel_order(hs2, 2, after_cutoff=False))["public_feed"][0] == "SG2"
    # Dates: stage dates on odd rounds, halfway to the next stage on even rounds.
    assert engine.round_date(hs2, 1) == "Friday 4 September 2026"
    assert engine.round_date(hs2, 2) == "Friday 11 September 2026"
    assert engine.round_date(hs2, 8) == "Wednesday 14 October 2026"
    assert engine.round_date(hs2, 16) == "Thursday 19 November 2026"


def test_old_four_agent_scenarios_untouched():
    # The society lives in its own module; the registry and the haze cast keep their shape.
    assert "S123" in RUNNABLE_SCENARIOS and "S124" in RUNNABLE_SCENARIOS
    assert set(RUNNABLE_SCENARIOS["S123"].agents) == {"A", "B", "C", "D"}


@pytest.fixture
def fake_agents(monkeypatch):
    from tinytroupe import config_manager
    from tinytroupe.clients import openai_client

    # As in real runs (runner.configure_simulation_runtime): no memory consolidation, which would call the model.
    previous = config_manager.get("enable_memory_consolidation")
    config_manager.update("enable_memory_consolidation", False)

    def no_network(*args, **kwargs):
        raise AssertionError("the society test tried to call the model")

    monkeypatch.setattr(openai_client.OpenAIClient, "send_message", no_network)
    calls = {"n": 0}

    def fake_act(self, return_actions=False, **kwargs):
        calls["n"] += 1
        self._fake = [
            {"type": "THINK", "content": f"STRATEGY: ASSERT. thinking {self.name}"},
            {"type": "TALK", "content": f"hello from {self.name}", "target": ""},
            {"type": "DONE", "content": ""},
        ]
        return [{"action": a} for a in self._fake]

    monkeypatch.setattr(TinyPerson, "act", fake_act)
    monkeypatch.setattr(TinyPerson, "pop_latest_actions", lambda self: getattr(self, "_fake", []))
    monkeypatch.setattr(engine, "_call_records", lambda: [])
    monkeypatch.setattr(engine, "_reset_usage", lambda: None)
    yield calls
    config_manager.update("enable_memory_consolidation", previous)
    reset_simulation_state()


def test_full_run_cutoff_checkpoint_fork_and_coder(fake_agents, tmp_path):
    transcript = run_society(
        preset=PRESET, run_id="R01", output_dir=tmp_path, cutoff_stage=1, free_rounds=2, simulation_model="m"
    )
    events = transcript["events"]
    talks = [e for e in events if e["type"] == "TALK"]
    gov_names = {NAMES[a] for a in ("SG-G", "MY-G", "ID-G", "BN-G")}
    assert all(e["round"] > 2 for e in talks if e["agent"] in gov_names)
    assert {e["channel"] for e in talks if e["round"] > 2} >= {"diplomatic", "public_feed"}
    # 15 citizen turns per round before the cutoff, 23 after (governments in the feed and the diplomatic channel).
    per_round = [sum(1 for e in talks if e["round"] == r) for r in (1, 2, 3)]
    assert per_round == [15, 15, 23]
    news = {e["round"]: e["content"] for e in events if e["type"] == "OBSERVE"}
    assert news[1] == PRESET.stages[0].news and news[3] == PRESET.stages[1].physical
    # Every agent keeps all news so far in its persona and has the longer memory window.
    cutoff_state = json.loads((tmp_path / "checkpoints" / "R01-cutoff.json").read_text(encoding="utf-8"))
    budi = next(a for a in cutoff_state["world_state"]["agents"] if a["name"] == NAMES["ID1"])
    assert budi["_persona"]["news_so_far"] == {PRESET.stages[0].date: PRESET.stages[0].news}
    assert budi["episodic_memory"]["lookback_length"] == PRESET.memory_lookback
    assert not (tmp_path / "checkpoints" / "R01.json").exists()
    md = (tmp_path / "transcripts" / "R01.md").read_text(encoding="utf-8")
    assert "### diplomatic channel" in md and "(free play)" in md

    run = haze_stage_coder.load_run(str(tmp_path / "transcripts" / "R01.json"))
    assert len(run["agents"]) == 13 and [s["first_round"] for s in run["stages"]] == [1, 3]
    text, counts = haze_stage_coder.stage_text(run, run["stages"][1])
    assert "[diplomatic]" in text and counts[NAMES["ID-G"]]["says"] == 4

    fork = run_society(
        preset=PRESET, run_id="F01", output_dir=tmp_path, cutoff_stage=1, free_rounds=2, simulation_model="m",
        fork_from=tmp_path / "checkpoints" / "R01-cutoff.json",
    )
    assert fork["run"]["history"]["forked_from_run"] == "R01"
    history = [e for e in fork["events"] if e["round"] <= 2]
    assert history == [e for e in events if e["round"] <= 2]
    assert max(e["round"] for e in fork["events"]) == 4


def test_hs2_run_dates_rounds_and_governments_open_the_feed(fake_agents, tmp_path):
    hs2 = SOCIETY_PRESETS["HS2"]
    transcript = run_society(
        preset=hs2, run_id="R01", output_dir=tmp_path, cutoff_stage=1, free_rounds=2, simulation_model="m"
    )
    observed = {(e["round"], e["channel"]): e["content"] for e in transcript["events"] if e["type"] == "OBSERVE"}
    assert observed[(2, "date")] == "It is now Friday 11 September 2026."
    assert observed[(3, "news")] == hs2.stages[1].physical
    assert observed[(4, "date")] == "It is now Monday 28 September 2026."
    feed = [e["agent"] for e in transcript["events"] if e["type"] == "TALK" and e["round"] == 3 and e["channel"] == "public_feed"]
    assert all(name.startswith("Government of ") for name in feed[:4])
    assert not any(name.startswith("Government of ") for name in feed[4:])
    assert "**Date:** It is now Friday 11 September 2026." in (tmp_path / "transcripts" / "R01.md").read_text(encoding="utf-8")


def test_hs2_hash_unchanged_since_history_pilot():
    # Recorded in outputs/society-hs2-history4/manifest.json.
    assert engine.preset_sha256(SOCIETY_PRESETS["HS2"]) == "1c1fba2d68c3daab7583867bb73feab5f055964075133b94caff63c6e9647cd5"


def test_hs3_governments_monitor_groups_silently():
    hs3 = SOCIETY_PRESETS["HS3"]
    assert "read its own country's group" not in hs3.setting
    for aid in ("SG-G", "MY-G", "ID-G"):
        assert "(its members are not told this)" in hs3.agents[aid].private_knowledge
    world, people = build_world(hs3)
    world.current_channel = "sg_group"
    world._handle_talk(people["SG1"], "Still no PSI drop.", target="")
    assert "Kelvin Tan wrote: Still no PSI drop." in _last_text(people["SG-G"])
    assert world.deliveries[-1]["recipients"] == [NAMES["SG2"], NAMES["SG-G"]]
    cue = engine._turn_cue(world, "sg_group", NAMES["SG1"])
    assert NAMES["SG2"] in cue and "Government" not in cue
    # Kelvin knows the Singapore government only through the public feed; the government knows him through both.
    def contacts(person):
        return {a["name"]: a["relation_description"] for a in person._mental_state["accessible_agents"]}

    assert "Singapore group" not in contacts(people["SG1"])[NAMES["SG-G"]]
    assert "Singapore group" in contacts(people["SG-G"])[NAMES["SG1"]]
    reset_simulation_state()


def test_hs3_hash_unchanged_since_free_play_test():
    # Recorded in outputs/society-hs3-pilot1/manifest.json.
    assert engine.preset_sha256(SOCIETY_PRESETS["HS3"]) == "c7d2609be7bfc8cfce72ce8f7f084a996768239600097dc44e4a3dc52ee5e87a"


def test_hs4_cue_says_public_or_private():
    hs4, hs3 = SOCIETY_PRESETS["HS4"], SOCIETY_PRESETS["HS3"]
    assert hs4.agents == hs3.agents and hs4.setting == hs3.setting
    world, people = build_world(hs4)
    feed = engine._turn_cue(world, "public_feed", NAMES["SG-G"])
    assert feed.endswith("This is public: anyone in the region can read it, including people and governments of other countries.")
    assert engine._turn_cue(world, "diplomatic", NAMES["SG-G"]).endswith("the public cannot.")
    assert engine._turn_cue(world, "sg_group", NAMES["SG1"]).endswith("seen only there.")
    reset_simulation_state()
    world, people = build_world(hs3)
    assert engine._turn_cue(world, "public_feed", NAMES["SG-G"]).endswith("seen only there.")
    reset_simulation_state()


def test_hs4_hash_unchanged_since_prediction_test():
    # Recorded in outputs/society-hs4-c4-test1/manifest.json.
    assert engine.preset_sha256(SOCIETY_PRESETS["HS4"]) == "59911de5e54e2a6dc77c7b016b453950ab6482a463a9072d15b293445703bbd9"


def test_hs5_splits_government_statements_into_posts():
    hs5, hs4 = SOCIETY_PRESETS["HS5"], SOCIETY_PRESETS["HS4"]
    assert hs5.agents == hs4.agents and hs5.channels == hs4.channels and hs5.setting == hs4.setting
    assert [s.physical for s in hs5.stages] == [s.physical for s in hs4.stages]
    assert [s.date for s in hs5.stages] == [s.date for s in hs4.stages]
    assert sum(len(s.posts) for s in hs5.stages) == 23
    for stage in hs5.stages:
        for agent_id, when, text in stage.posts:
            assert agent_id in ("SG-G", "MY-G", "ID-G")
            assert text and when
        # government statements are no longer in the news text
        assert "Prabowo" not in stage.news and "Grace Fu" not in stage.news and "Bahlil" not in stage.news
    # every quoted government line in HS4's news is in some HS5 post
    all_posts = " ".join(t for s in hs5.stages for _, _, t in s.posts)
    for quote in ("we send oxygen", "We will pursue this matter for as long as it takes", "Do not lecture us",
                  "Smoke can cross borders, so can money", "It is not our fault, but once again we apologise"):
        assert quote in all_posts


def test_hs5_full_timeline_delivers_posts_to_everyone(fake_agents, tmp_path):
    hs5 = SOCIETY_PRESETS["HS5"]
    transcript = run_society(
        preset=hs5, run_id="E01", output_dir=tmp_path, cutoff_stage=8, free_rounds=0, simulation_model="m"
    )
    posts = [e for e in transcript["events"] if e["type"] == "POST"]
    assert len(posts) == 23 and all(e["channel"] == "public_feed" for e in posts)
    # governments never generate anything in a full-timeline run
    gov = {NAMES[a] for a in ("SG-G", "MY-G", "ID-G", "BN-G")}
    assert not [e for e in transcript["events"] if e["type"] == "TALK" and e["agent"] in gov]
    assert max(e["round"] for e in transcript["events"]) == 16
    # posts reached the citizens and stay in their personas; the coder's stage text includes them
    scripted = [d for d in transcript["deliveries"] if d.get("scripted")]
    assert len(scripted) == 23 and NAMES["ID3"] in scripted[0]["recipients"]
    obs = transcript["scenario"]["round_observations"]
    assert "Government posts in the public feed" in (obs.get(3) or obs.get("3"))
    md = (tmp_path / "transcripts" / "E01.md").read_text(encoding="utf-8")
    assert "(real statement, scripted)" in md
    run = haze_stage_coder.load_run(str(tmp_path / "transcripts" / "E01.json"))
    assert len(run["stages"]) == 8


def test_hs5_hash_unchanged_since_full_run():
    # Recorded in outputs/society-hs5-e2e1/manifest.json.
    assert engine.preset_sha256(SOCIETY_PRESETS["HS5"]) == "09a62efba118199c032e61d8e577b8a26e7124e2fee029be3839cf327e97970a"


def test_hs6_governments_talk_only_in_the_diplomatic_channel(fake_agents, tmp_path):
    hs6 = SOCIETY_PRESETS["HS6"]
    assert hs6.stages == SOCIETY_PRESETS["HS5"].stages and hs6.agents == SOCIETY_PRESETS["HS5"].agents
    order = dict(channel_order(hs6, 3, after_cutoff=False))
    assert set(order["diplomatic"]) == {"SG-G", "MY-G", "ID-G", "BN-G"}
    assert not {"SG-G", "MY-G", "ID-G", "BN-G"} & set(order["public_feed"])
    transcript = run_society(
        preset=hs6, run_id="E01", output_dir=tmp_path, cutoff_stage=8, free_rounds=0, simulation_model="m"
    )
    gov = {NAMES[a] for a in ("SG-G", "MY-G", "ID-G", "BN-G")}
    gov_talk = [e for e in transcript["events"] if e["type"] == "TALK" and e["agent"] in gov]
    assert gov_talk and {e["channel"] for e in gov_talk} == {"diplomatic"}
    assert len(gov_talk) == 4 * 16
    # citizens never receive the diplomatic channel
    diplomatic = [d for d in transcript["deliveries"] if d["channel"] == "diplomatic"]
    assert all(set(d["recipients"]) <= gov for d in diplomatic)
    # 23 scripted posts as in HS5, and 15 + 4 turns per round
    assert len([e for e in transcript["events"] if e["type"] == "POST"]) == 23
    assert sum(1 for e in transcript["events"] if e["type"] == "TALK" and e["round"] == 1) == 19


def test_hs6_government_is_told_its_own_posts():
    hs6 = SOCIETY_PRESETS["HS6"]
    world, people = build_world(hs6)
    world.post_scripted("public_feed", NAMES["ID-G"], "10 October", "we send oxygen", tell_source=True)
    assert "You posted in the public regional feed (10 October): we send oxygen" in _last_text(people["ID-G"])
    reset_simulation_state()
