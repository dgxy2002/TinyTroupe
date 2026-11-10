from dataclasses import replace
"""S26/S27 scenario design and the private debrief."""

import collections
import re

import pytest

from research_questions.debrief import build_debrief_messages
from research_questions.evaluator import public_transcript_text
from research_questions.models import AgentDebrief
from research_questions.scenario_presets import RUNNABLE_SCENARIOS, materialize_configuration
from research_questions.runner import _anonymized_evaluator_input
from research_questions.scenario_presets.common import (
    BACKGROUND_NAMES,
    BIOGRAPHIES,
    VALUE_ORIENTATIONS,
)
from research_questions.scenario_presets.s04_variants import RESOLUTION_EXPECTATION
from research_questions.label_probe import template_without_rule
from research_questions.simulation import (
    AGENT_PROMPT_PATH,
    NO_CULTURE_RULE_PROMPT_PATH,
    _agent_persona,
    create_scenario_instance,
    reset_simulation_state,
)

S25 = RUNNABLE_SCENARIOS["S25"]
S26 = RUNNABLE_SCENARIOS["S26"]
S27 = RUNNABLE_SCENARIOS["S27"]
S28 = RUNNABLE_SCENARIOS["S28"]
S29 = RUNNABLE_SCENARIOS["S29"]


def _persona(scenario):
    preset = materialize_configuration(scenario, "C0")
    return _agent_persona(
        "A",
        preset["agents"]["A"],
        preset["resolution_expectation"],
        preset["timing_free"],
        preset["conversation_only"],
        preset["priced_priority"],
    )


def test_s27_differs_from_s26_only_in_the_notice():
    assert S26.resolution_expectation == RESOLUTION_EXPECTATION
    assert S27.resolution_expectation == ""
    assert S27.agents == S26.agents
    assert S27.shared_setting == S26.shared_setting
    assert S27.shared_trigger == S26.shared_trigger
    assert S27.conversation_only and S27.timing_free


def test_both_variants_get_the_same_priority_rule():
    for scenario in (S26, S27):
        persona = _persona(scenario)
        assert persona["priority_rule_open"] is True
        assert any("not a wall" in fact for fact in persona["other_facts"])


def test_priced_flag_leaves_earlier_scenarios_unchanged():
    assert _persona(S25)["priority_rule_open"] is True
    s24 = _persona(RUNNABLE_SCENARIOS["S24"])
    assert "priority_rule_open" not in s24
    assert not any("not a wall" in fact for fact in s24["other_facts"])


@pytest.mark.parametrize("config", ["C0", "C1"])
def test_role_letters_never_reach_the_agents(config):
    preset = materialize_configuration(S26, config)
    for agent in preset["agents"].values():
        for field in ("private_knowledge", "initial_observation", "immediate_priority"):
            assert not re.search(r"(?<![A-Za-z'])[BCD]\b", agent[field]), agent[field]
            assert "Agent " not in agent[field]


def test_scenario_text_states_no_outcome():
    banned = ("should accept", "should agree", "must agree", "apologis", "apologiz", "compromise")
    text = " ".join(
        [S26.shared_setting, S26.shared_trigger]
        + [a.private_knowledge + a.immediate_priority for a in S26.agents.values()]
    ).lower()
    assert not any(word in text for word in banned)


def test_second_seat_is_known_only_to_c():
    assert "finish before" in S26.agents["C"].private_knowledge
    public = S26.shared_setting + S26.shared_trigger
    assert "finish" not in public
    for agent_id in "ABD":
        assert "finish" not in S26.agents[agent_id].private_knowledge


def _transcript(configuration="C0"):
    preset = materialize_configuration(S26, configuration)
    first = preset["agents"]["A"]["display_name"]
    second = preset["agents"]["B"]["display_name"]
    return {
        "scenario": preset,
        "run": {"completed_rounds": 1},
        "events": [
            {"round": 1, "turn": 1, "agent": first, "type": "THINK", "content": "FIRST SECRET", "action_index": 1},
            {"round": 1, "turn": 1, "agent": first, "type": "TALK", "content": "That's my seat.", "action_index": 2},
            {"round": 1, "turn": 2, "agent": second, "type": "THINK", "content": "SECOND SECRET", "action_index": 1},
        ],
    }


def test_debrief_sees_only_that_agents_private_thoughts():
    transcript = _transcript()
    first = build_debrief_messages(transcript, "A")[1]["content"]
    second = build_debrief_messages(transcript, "B")[1]["content"]
    assert "FIRST SECRET" in first and "SECOND SECRET" not in first
    assert "SECOND SECRET" in second and "FIRST SECRET" not in second
    assert "That's my seat." in first


def test_debrief_carries_background_only_when_present():
    assert "Cultural background" not in build_debrief_messages(_transcript("C0"), "A")[1]["content"]
    labelled = build_debrief_messages(_transcript("C1"), "A")[1]["content"]
    assert "Cultural background: Singaporean Chinese" in labelled


def _section(prompt, start, end):
    return prompt[prompt.find(start) : prompt.find(end)]


def test_cognitive_state_is_rendered_into_the_agent_prompt():
    reset_simulation_state()
    jamie = create_scenario_instance(S26, "C0").participants["B"]
    prompt = jamie.generate_agent_system_prompt()
    section = _section(prompt, "## Current cognitive state", "### Working memory context")
    assert "Your current location is: Hawker centre" in section
    assert "no other free seat anywhere" in section
    assert "stops at the only disputed seat" in section
    assert "Alex:" in section and "Casey:" in section and "Robin:" in section
    assert jamie._mental_state["goals"].split(",")[0] in section


def test_setting_stays_visible_after_the_model_rewrites_context():
    for scenario, expected in ((S28, True), (S26, False)):
        reset_simulation_state()
        person = create_scenario_instance(scenario, "C0").participants["B"]
        person._update_cognitive_state(context=["Alex wants my seat."])
        prompt = person.generate_agent_system_prompt()
        assert ("no other free seat anywhere" in prompt) is expected


def test_opening_event_is_stored_in_memory_only_when_pinned():
    for scenario, expected in ((S28, True), (S26, False)):
        reset_simulation_state()
        person = create_scenario_instance(scenario, "C0").participants["A"]
        memory = str(person.retrieve_recent_memories())
        assert ("What has just happened" in memory) is expected


def test_s28_and_s29_only_add_the_pin():
    assert S28.agents == S26.agents and S29.agents == S27.agents
    assert S28.shared_setting == S26.shared_setting
    assert S28.resolution_expectation == S26.resolution_expectation
    assert S29.resolution_expectation == "" and S29.priced_priority


def test_s30_is_speech_only_with_no_notice_or_outcome():
    s30 = RUNNABLE_SCENARIOS["S30"]
    assert s30.conversation_only and s30.timing_free and s30.priced_priority
    assert s30.pin_shared_setting and s30.resolution_expectation == ""
    text = " ".join(
        [s30.shared_setting, s30.shared_trigger]
        + [a.private_knowledge + a.immediate_priority for a in s30.agents.values()]
    ).lower()
    for word in ("should accept", "should agree", "must agree", "compromise", "rota", "pork", "curry", "halal"):
        assert word not in text


def test_s30_shows_agents_names_not_role_letters():
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S30"], "C0")
    prompt = instance.participants["B"].generate_agent_system_prompt()
    section = _section(prompt, "## Current cognitive state", "### Working memory context")
    assert "Agent " not in section
    assert "for the rest of the lease" in prompt
    preset = materialize_configuration(RUNNABLE_SCENARIOS["S30"], "C0")
    for agent in preset["agents"].values():
        for field in ("private_knowledge", "initial_observation", "immediate_priority"):
            assert not re.search(r"(?<![A-Za-z'])[BCD]\b", agent[field]), agent[field]
            assert "Agent " not in agent[field]


@pytest.mark.parametrize("config", ["L1", "B1", "V1"])
def test_profile_cells_keep_neutral_names(config):
    preset = materialize_configuration(RUNNABLE_SCENARIOS["S30"], config)
    names = [agent["display_name"] for agent in preset["agents"].values()]
    assert names == ["Alex", "Jamie", "Casey", "Robin"]


def test_label_and_biography_cells_differ_only_in_biography():
    label = materialize_configuration(RUNNABLE_SCENARIOS["S30"], "L2")
    biography = materialize_configuration(RUNNABLE_SCENARIOS["S30"], "B2")
    for agent_id, agent in biography["agents"].items():
        assert agent["cultural_background"] == label["agents"][agent_id]["cultural_background"]
        assert BIOGRAPHIES[agent["cultural_background"]] == agent["biography"]
        assert "biography" not in label["agents"][agent_id]


def test_plain_label_cells_drop_only_the_word_singaporean():
    labelled = materialize_configuration(RUNNABLE_SCENARIOS["S30"], "L1")
    plain = materialize_configuration(RUNNABLE_SCENARIOS["S30"], "P1")
    for agent_id, agent in plain["agents"].items():
        expected = labelled["agents"][agent_id]["cultural_background"]
        assert agent["cultural_background"] == expected.replace("Singaporean ", "")
        assert agent["display_name"] == labelled["agents"][agent_id]["display_name"]
    reset_simulation_state()
    prompt = create_scenario_instance(
        RUNNABLE_SCENARIOS["S30"], "P1"
    ).participants["B"].generate_agent_system_prompt()
    assert '"cultural_background": "Malay"' in prompt
    assert '"country_of_residence": "Singapore"' in prompt


def test_first_speaker_is_balanced_across_roles_and_values():
    seen = []
    for config in ("W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"):
        preset = materialize_configuration(RUNNABLE_SCENARIOS["S30"], config)
        role = preset["profile_treatment"]["first_speaker"]
        harmony = preset["agents"][role]["personal_values"] == VALUE_ORIENTATIONS["harmony"]
        seen.append((role, harmony))
    assert sorted(seen) == [
        (role, value) for role in "ABCD" for value in (False, True)
    ]


@pytest.mark.parametrize("config, role, name", [("W2", "C", "Casey"), ("W3", "D", "Robin"), ("W4", "B", "Jamie")])
def test_scheduler_offers_the_first_turn_to_the_chosen_role(config, role, name):
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S30"], config)
    assert instance.world._scheduler_candidate_names()[0] == name
    assert instance.participants[role].name == name


def test_other_cells_still_start_with_the_first_role():
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S30"], "V1")
    assert instance.world._scheduler_candidate_names()[0] == "Alex"


NAMED_CELLS = tuple(f"N{number:02d}" for number in range(1, 11))


def _named(config):
    return materialize_configuration(RUNNABLE_SCENARIOS["S30"], config)


def test_named_schedule_is_balanced():
    gender_by_culture = collections.Counter()
    male_by_role = collections.Counter()
    opener_role = collections.Counter()
    opener_culture = collections.Counter()
    opener_gender = collections.Counter()
    used_names = collections.Counter()
    for config in NAMED_CELLS:
        preset = _named(config)
        treatment = preset["profile_treatment"]
        genders = treatment["name_genders"]
        assert sorted(genders.values()) == ["female", "female", "male", "male"]
        for role, agent in preset["agents"].items():
            full = f"Singaporean {agent['cultural_background']}"
            gender_by_culture[(agent["cultural_background"], genders[full])] += 1
            male_by_role[role] += genders[full] == "male"
            assert agent["display_name"] in BACKGROUND_NAMES[full][genders[full]]
            used_names[agent["display_name"]] += 1
        first = treatment["first_speaker"]
        opener = preset["agents"][first]["cultural_background"]
        opener_role[first] += 1
        opener_culture[opener] += 1
        opener_gender[genders[f"Singaporean {opener}"]] += 1
    assert set(gender_by_culture.values()) == {5}
    assert all(4 <= count <= 6 for count in male_by_role.values())
    assert all(2 <= count <= 3 for count in opener_role.values())
    assert all(2 <= count <= 3 for count in opener_culture.values())
    assert set(opener_gender.values()) == {5}
    assert len(used_names) == 16 and all(2 <= count <= 3 for count in used_names.values())


def test_named_cells_use_plain_labels_and_agents_see_the_name():
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S30"], "N01")
    person = instance.participants["D"]
    prompt = person.generate_agent_system_prompt()
    assert person.name == "Daniel Pereira"
    assert '"cultural_background": "Eurasian"' in prompt
    assert "Singaporean Eurasian" not in prompt
    assert instance.world._scheduler_candidate_names()[0] == "Daniel Pereira"


def test_blinding_hides_shortened_names_and_leaves_ordinary_words():
    preset = _named("N01")
    full = preset["agents"]["D"]["display_name"]
    transcript = {
        "scenario": preset,
        "events": [
            {"content": f"{full} and Daniel talked, and Pereira agreed.", "agent": full},
            {"content": "Mingling with Danielle is fine.", "agent": "x"},
        ],
    }
    events, _ = _anonymized_evaluator_input(transcript)
    assert events[0]["content"] == "Agent D and Agent D talked, and Agent D agreed."
    assert events[0]["agent"] == "Agent D"
    assert events[1]["content"] == "Mingling with Danielle is fine."


def test_s31_adds_the_pork_fact_and_removes_only_the_bothers_sentence():
    s30, s31 = RUNNABLE_SCENARIOS["S30"], RUNNABLE_SCENARIOS["S31"]
    assert "There is pork fat left in it" in s31.shared_trigger
    assert "pork" not in s30.shared_trigger
    assert s31.shared_setting == s30.shared_setting
    assert s31.resolution_expectation == ""
    for agent_id, agent in s31.agents.items():
        original = s30.agents[agent_id]
        assert "bothers" not in agent.private_knowledge
        assert "bother" in original.private_knowledge
        assert original.private_knowledge.startswith(agent.private_knowledge[:-1])
        assert agent.immediate_priority == original.immediate_priority
    text = " ".join(a.private_knowledge + a.immediate_priority for a in s31.agents.values()).lower()
    for word in ("pork", "halal", "muslim", "object"):
        assert word not in text


def test_pork_cells_put_the_muslim_biography_in_each_role_once():
    roles = []
    for config in ("M1", "M2", "M3", "M4"):
        preset = materialize_configuration(RUNNABLE_SCENARIOS["S31"], config)
        for role, agent in preset["agents"].items():
            if "Muslim" in agent["biography"]:
                roles.append(role)
                assert agent["cultural_background"] == "Malay"
    assert sorted(roles) == ["A", "B", "C", "D"]


def _s31_prompt(config, role):
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S31"], config)
    return instance.participants[role].generate_agent_system_prompt()


def test_no_rule_prompt_differs_from_the_main_prompt_only_by_the_rule():
    main = AGENT_PROMPT_PATH.read_text(encoding="utf-8")
    assert NO_CULTURE_RULE_PROMPT_PATH.read_text(encoding="utf-8") == template_without_rule(main)


def test_home_language_cells_think_in_the_language_and_speak_english():
    preset = materialize_configuration(RUNNABLE_SCENARIOS["S31"], "H2")
    languages = {a["cultural_background"]: a["thinking_language"] for a in preset["agents"].values()}
    assert languages == {"Malay": "Malay", "Indian": "Tamil", "Eurasian": "English", "Chinese": "Mandarin"}
    prompt = _s31_prompt("H2", "A")
    assert "write your private THINK actions in Malay" in prompt
    assert "When you TALK, speak English" in prompt


def test_explicit_cells_remove_the_rule_and_only_those_cells_do():
    explicit = _s31_prompt("E2", "A")
    assert "typical cultural values in Malay culture" in explicit
    assert "not a behavior instruction" not in explicit
    assert "not a script for behaviour" not in explicit
    usual = _s31_prompt("M2", "A")
    assert "typical cultural values" not in usual
    assert "not a behavior instruction" in usual


def test_same_culture_cells_use_one_background_and_balanced_names():
    openers = []
    for number, config in enumerate(("G1", "G2", "G3", "G4")):
        preset = materialize_configuration(RUNNABLE_SCENARIOS["S31"], config)
        cultures = {a["cultural_background"] for a in preset["agents"].values()}
        names = [a["display_name"] for a in preset["agents"].values()]
        assert len(cultures) == 1 and len(set(names)) == 4
        assert sorted(preset["profile_treatment"]["role_genders"].values()) == [
            "female", "female", "male", "male",
        ]
        openers.append(preset["profile_treatment"]["first_speaker"])
    assert openers == ["A", "B", "C", "D"]


def test_remaining_pork_cells_match_the_named_schedule():
    for number in range(5, 11):
        pork = materialize_configuration(RUNNABLE_SCENARIOS["S31"], f"M{number}")
        named = materialize_configuration(RUNNABLE_SCENARIOS["S30"], f"N{number:02d}")
        assert [a["display_name"] for a in pork["agents"].values()] == [
            a["display_name"] for a in named["agents"].values()
        ]
        assert all("biography" in a for a in pork["agents"].values())


SMELL_CASES = ("S32", "S33", "S34", "S35")


def test_smell_cases_differ_only_in_one_sentence():
    base = RUNNABLE_SCENARIOS["S31"]
    triggers = []
    for case in SMELL_CASES:
        scenario = RUNNABLE_SCENARIOS[case]
        assert scenario.agents == base.agents
        assert scenario.shared_setting == base.shared_setting
        triggers.append(scenario.shared_trigger)
    prefix = re.compile(r"^(.*and has said so\. ).*?(Agent D has just got home.*)$", re.S)
    assert len({prefix.sub(r"\1\2", trigger) for trigger in triggers}) == 1
    assert len(set(triggers)) == 4


@pytest.mark.parametrize("case", SMELL_CASES)
def test_smell_cases_state_no_resolution_goal(case):
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    text = (scenario.shared_setting + scenario.shared_trigger).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must"):
        assert phrase not in text
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, "M5").participants["A"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt
    assert "will end with everyone" not in prompt


def test_biographies_state_facts_not_conduct():
    frames = {
        re.sub(r"speaks .* at home and is \w+\. Goes home for .* every", "", text)
        for text in BIOGRAPHIES.values()
    }
    assert len(frames) == 1
    banned = ("polite", "harmony", "direct", "avoid", "respect", "indirect", "family-oriented")
    for text in BIOGRAPHIES.values():
        assert not any(word in text.lower() for word in banned)


def test_value_cells_have_no_label_and_balance_roles():
    counts = {agent_id: 0 for agent_id in "ABCD"}
    for config in ("V1", "V2", "V3", "V4"):
        preset = materialize_configuration(RUNNABLE_SCENARIOS["S30"], config)
        for agent_id, agent in preset["agents"].items():
            assert "cultural_background" not in agent
            counts[agent_id] += agent["personal_values"] == VALUE_ORIENTATIONS["harmony"]
    assert set(counts.values()) == {2}


def test_profile_fields_reach_the_agent_prompt():
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S30"], "B1")
    prompt = instance.participants["B"].generate_agent_system_prompt()
    assert "Hari Raya" in prompt and "Singaporean Malay" in prompt
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S30"], "V1")
    assert "keeping things peaceful" in instance.participants["A"].generate_agent_system_prompt()
    assert "saying plainly" in instance.participants["C"].generate_agent_system_prompt()


def test_private_thoughts_never_reach_the_evaluator_text():
    assert "SECRET" not in public_transcript_text(_transcript()["events"], 1)


def test_debrief_schema_rejects_out_of_range_fairness():
    with pytest.raises(ValueError):
        AgentDebrief(
            settled="settled",
            what_was_agreed="x",
            what_i_gave_up="x",
            what_i_got="x",
            why_i_went_along="x",
            what_still_bothers_me="x",
            fairness_to_me=6,
        )


PAN_CASES = ("S36", "S37")


def test_pan_cases_differ_only_in_residue_and_d_need():
    faith, control = (RUNNABLE_SCENARIOS[case] for case in PAN_CASES)
    assert faith.shared_setting == control.shared_setting
    assert faith.shared_trigger.replace("pork fat", "shellfish oil") == control.shared_trigger
    for role in ("A", "B", "C"):
        assert faith.agents[role] == control.agents[role]
    assert "sertu" in faith.agents["D"].private_knowledge
    assert "allergy" in control.agents["D"].private_knowledge
    assert "sertu" not in control.agents["D"].private_knowledge
    assert replace(faith.agents["D"], private_knowledge="") == replace(
        control.agents["D"], private_knowledge=""
    )


@pytest.mark.parametrize("case", PAN_CASES)
def test_pan_cases_keep_the_pan_as_the_only_problem(case):
    scenario = RUNNABLE_SCENARIOS[case]
    text = " ".join(
        [scenario.shared_setting, scenario.shared_trigger]
        + [
            " ".join((agent.immediate_priority, agent.private_knowledge, agent.initial_observation))
            for agent in scenario.agents.values()
        ]
    ).lower()
    for word in ("smell", "extractor", "window", "fair chance", "bedrooms"):
        assert word not in text


@pytest.mark.parametrize("case", PAN_CASES)
def test_pan_cases_state_no_resolution_goal_or_conduct(case):
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    text = (scenario.shared_setting + scenario.shared_trigger).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must"):
        assert phrase not in text
    need = scenario.agents["D"].private_knowledge.lower()
    for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must"):
        assert phrase not in need
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, "K1").participants["A"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt
    assert "will end with everyone" not in prompt


@pytest.mark.parametrize("case", PAN_CASES)
def test_k1_faiths_match_the_public_line_and_render_with_names(case):
    preset = materialize_configuration(RUNNABLE_SCENARIOS[case], "K1")
    agents = preset["agents"]
    assert [agents[role]["display_name"] for role in "ABCD"] == [
        "Suresh",
        "Daniel Pereira",
        "Hui Min",
        "Aisyah",
    ]
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Aisyah is Muslim and eats halal" in preset["shared_setting"]
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    for role, faith in zip("ABCD", ("Hindu", "Catholic", "Buddhist", "Muslim")):
        assert f"You are {faith}" in agents[role]["biography"]
        assert f"{agents[role]['display_name']} is {faith}" in preset["shared_setting"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]


def test_m_cells_keep_their_original_biographies():
    agents = materialize_configuration(RUNNABLE_SCENARIOS["S31"], "M3")["agents"]
    assert all(agent["biography"] in BIOGRAPHIES.values() for agent in agents.values())


BEEF_CASES = ("S38", "S39")


def test_pan_settings_unchanged_for_s36_and_differ_only_in_faith_order():
    s36, s38 = RUNNABLE_SCENARIOS["S36"], RUNNABLE_SCENARIOS["S38"]
    assert "Agent A is Hindu and does not eat beef, Agent B is Catholic, Agent C is Buddhist, and Agent D is Muslim and eats halal." in s36.shared_setting
    assert "Agent A is Catholic, Agent B is Buddhist, Agent C is Muslim and eats halal, and Agent D is Hindu and does not eat beef." in s38.shared_setting
    for role in ("A", "B", "C"):
        assert s36.agents[role] == s38.agents[role]
    assert s36.shared_trigger.replace("pork fat", "beef fat") == s38.shared_trigger


def test_beef_pair_differs_only_in_residue_and_d_need():
    faith, control = (RUNNABLE_SCENARIOS[case] for case in BEEF_CASES)
    assert faith.shared_setting == control.shared_setting
    assert faith.shared_trigger.replace("beef fat", "peanut oil") == control.shared_trigger
    for role in ("A", "B", "C"):
        assert faith.agents[role] == control.agents[role]
    assert "You are Hindu" in faith.agents["D"].private_knowledge
    assert "peanut allergy" in control.agents["D"].private_knowledge
    assert replace(faith.agents["D"], private_knowledge="") == replace(
        control.agents["D"], private_knowledge=""
    )


@pytest.mark.parametrize("case", BEEF_CASES)
def test_beef_pair_states_no_goal_and_k2_faiths_match(case):
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    text = (scenario.shared_setting + scenario.shared_trigger).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must", "smell"):
        assert phrase not in text
    need = scenario.agents["D"].private_knowledge.lower()
    for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must"):
        assert phrase not in need
    preset = materialize_configuration(scenario, "K2")
    agents = preset["agents"]
    assert [agents[role]["display_name"] for role in "ABCD"] == [
        "Rachel Pereira",
        "Wei Ming",
        "Nurul",
        "Karthik",
    ]
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    for role, faith in zip("ABCD", ("Catholic", "Buddhist", "Muslim", "Hindu")):
        assert f"You are {faith}" in agents[role]["biography"]
        assert f"{agents[role]['display_name']} is {faith}" in preset["shared_setting"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, "K2").participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


INCENSE_CASES = ("S40", "S41")


def test_incense_pair_differs_only_in_source_and_d_need():
    faith, control = (RUNNABLE_SCENARIOS[case] for case in INCENSE_CASES)
    assert faith.shared_setting == control.shared_setting
    assert faith.shared_trigger.replace(
        "Incense is burning at a small altar", "A bowl of strong-smelling medicated oil is steaming"
    ) == control.shared_trigger
    for role in ("A", "B", "C"):
        assert faith.agents[role] == control.agents[role]
    assert "You are Buddhist" in faith.agents["D"].private_knowledge
    assert "chest infection" in control.agents["D"].private_knowledge
    assert replace(faith.agents["D"], private_knowledge="") == replace(
        control.agents["D"], private_knowledge=""
    )


@pytest.mark.parametrize("case", INCENSE_CASES)
def test_incense_pair_states_no_goal_one_issue_and_k3_faiths_match(case):
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    text = (scenario.shared_setting + scenario.shared_trigger).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must", "pan", "kitchen", "stove"):
        assert phrase not in text
    need = scenario.agents["D"].private_knowledge.lower()
    for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must"):
        assert phrase not in need
    preset = materialize_configuration(scenario, "K3")
    agents = preset["agents"]
    assert [agents[role]["display_name"] for role in "ABCD"] == [
        "Hafiz",
        "Priya",
        "Marcus de Souza",
        "Xin Yi",
    ]
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    for role, faith in zip("ABCD", ("Muslim", "Hindu", "Catholic", "Buddhist")):
        assert f"You are {faith}" in agents[role]["biography"]
        assert f"{agents[role]['display_name']} is {faith}" in preset["shared_setting"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]
        for word in ("pan", "kitchen", "stove", "cook"):
            assert word not in (agents[role]["private_knowledge"] + agents[role]["immediate_priority"]).lower()
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, "K3").participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


HOUSEWARMING_CASES = {"S42": ("K1", "Aisyah", "Muslim"), "S43": ("K3", "Xin Yi", "Buddhist"), "S44": ("K2", "Karthik", "Hindu"), "S45": ("K4", "Daniel Pereira", "Catholic")}


def test_housewarming_variants_differ_only_in_faith_order_and_d_need():
    cases = [RUNNABLE_SCENARIOS[case] for case in HOUSEWARMING_CASES]
    assert len({case.shared_trigger for case in cases}) == 1
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    assert len({case.agents["D"].private_knowledge for case in cases}) == 4
    strip = lambda text: text.split("you eats:")[0] + text.split(". It is a weeknight")[1]
    assert len({strip(case.shared_setting) for case in cases}) == 1
    assert "sober" in RUNNABLE_SCENARIOS["S45"].agents["D"].private_knowledge


@pytest.mark.parametrize("case", sorted(HOUSEWARMING_CASES))
def test_housewarming_states_no_goal_and_casts_match(case):
    cell, key_name, faith = HOUSEWARMING_CASES[case]
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    text = (scenario.shared_setting + scenario.shared_trigger).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must"):
        assert phrase not in text
    need = scenario.agents["D"].private_knowledge.lower()
    for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must"):
        assert phrase not in need
    preset = materialize_configuration(scenario, cell)
    agents = preset["agents"]
    assert agents["D"]["display_name"] == key_name
    assert f"You are {faith}" in agents["D"]["biography"]
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    for role in "ABCD":
        assert f"{agents[role]['display_name']} is " in preset["shared_setting"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


HOUSEWARMING_V2 = {"S46": ("HW1", "Aisyah", "Muslim"), "S47": ("HW2", "Karthik", "Hindu"), "S48": ("HW3", "Xin Yi", "Buddhist"), "S49": ("HW4", "Daniel Pereira", "Catholic")}


def test_housewarming_v2_has_no_shared_fund_and_one_varying_fact():
    cases = [RUNNABLE_SCENARIOS[case] for case in HOUSEWARMING_V2]
    assert len({case.shared_trigger for case in cases}) == 1
    trigger = cases[0].shared_trigger
    assert "own money" in trigger and "house fund" not in trigger
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
        assert "fund" not in cases[0].agents[role].private_knowledge
        assert "cost" not in cases[0].agents[role].immediate_priority.lower()
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    for old, new in (("S42", "S46"), ("S44", "S47"), ("S43", "S48"), ("S45", "S49")):
        assert RUNNABLE_SCENARIOS[old].agents["D"].private_knowledge == RUNNABLE_SCENARIOS[new].agents["D"].private_knowledge


@pytest.mark.parametrize("case", sorted(HOUSEWARMING_V2))
def test_housewarming_v2_casts_keep_alcohol_rules_on_the_key_agent_only(case):
    cell, key_name, faith = HOUSEWARMING_V2[case]
    preset = materialize_configuration(RUNNABLE_SCENARIOS[case], cell)
    agents = preset["agents"]
    assert agents["A"]["display_name"] == "Natalie Rodrigues"
    assert agents["D"]["display_name"] == key_name
    assert f"You are {faith}" in agents["D"]["biography"]
    for role in "ABC":
        assert "Muslim" not in agents[role]["biography"]
        assert f"{agents[role]['display_name']} is " in preset["shared_setting"]
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    text = (preset["shared_setting"] + preset["shared_trigger"]).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must"):
        assert phrase not in text
    reset_simulation_state()
    prompt = create_scenario_instance(RUNNABLE_SCENARIOS[case], cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


def test_hw1_and_hw4_differ_only_in_agent_d():
    hw1, hw4 = (materialize_configuration(RUNNABLE_SCENARIOS["S46"], cell)["agents"] for cell in ("HW1", "HW4"))
    for role in "ABC":
        assert hw1[role]["display_name"] == hw4[role]["display_name"]
        assert hw1[role]["biography"] == hw4[role]["biography"]



def test_s50_differs_from_s47_only_in_karthiks_fact():
    s47, s50 = RUNNABLE_SCENARIOS["S47"], RUNNABLE_SCENARIOS["S50"]
    assert s47.shared_setting == s50.shared_setting
    assert s47.shared_trigger == s50.shared_trigger
    for role in "ABC":
        assert s47.agents[role] == s50.agents[role]
    assert replace(s47.agents["D"], private_knowledge="") == replace(s50.agents["D"], private_knowledge="")
    need = s50.agents["D"].private_knowledge
    assert "For you" in need and "not acceptable" in need and "for your family" not in need
    for phrase in ("insist", "refuse", "demand", "must"):
        assert phrase not in need.lower()


ROTA_CASES = {"S51": ("FR1", "Aisyah", "Muslim"), "S52": ("FR2", "Karthik", "Hindu"), "S53": ("FR3", "Xin Yi", "Buddhist"), "S54": ("FR4", "Daniel Pereira", "Catholic")}


def test_rota_variants_share_everything_but_d_need_and_have_no_shared_fund():
    cases = [RUNNABLE_SCENARIOS[case] for case in ROTA_CASES]
    assert len({case.shared_trigger for case in cases}) == 1
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    for case in cases:
        text = (case.shared_setting + case.shared_trigger).lower()
        assert "fund" not in text and "budget" not in text
        for role in "ABC":
            assert "fund" not in case.agents[role].private_knowledge.lower()
        assert "For you" in case.agents["D"].private_knowledge


@pytest.mark.parametrize("case", sorted(ROTA_CASES))
def test_rota_casts_keep_food_rules_on_the_key_agent_only(case):
    cell, key_name, faith = ROTA_CASES[case]
    preset = materialize_configuration(RUNNABLE_SCENARIOS[case], cell)
    agents = preset["agents"]
    assert agents["D"]["display_name"] == key_name
    assert f"You are {faith}" in agents["D"]["biography"]
    for role in "ABC":
        biography = agents[role]["biography"]
        assert "Muslim" not in biography and "Hindu" not in biography
        if faith == "Buddhist":
            assert "Buddhist" not in biography
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    text = (preset["shared_setting"] + preset["shared_trigger"]).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must"):
        assert phrase not in text
    need = RUNNABLE_SCENARIOS[case].agents["D"].private_knowledge.lower()
    for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must"):
        assert phrase not in need
    reset_simulation_state()
    prompt = create_scenario_instance(RUNNABLE_SCENARIOS[case], cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


KEY_PAIRS = {
    "bereavement": {"S55": ("K1", "Aisyah", "Muslim"), "S56": ("K2", "Karthik", "Hindu"), "S57": ("K3", "Xin Yi", "Buddhist"), "S58": ("K4", "Daniel Pereira", "Catholic")},
    "corner": {"S59": ("K1", "Aisyah", "Muslim"), "S60": ("K2", "Karthik", "Hindu"), "S61": ("K3", "Xin Yi", "Buddhist"), "S62": ("K4", "Daniel Pereira", "Catholic")},
}


@pytest.mark.parametrize("family", sorted(KEY_PAIRS))
def test_key_variants_share_roles_and_differ_only_in_d(family):
    cases = [RUNNABLE_SCENARIOS[case] for case in KEY_PAIRS[family]]
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    assert len({case.agents["D"].private_knowledge for case in cases}) == 4
    for case in cases:
        need = case.agents["D"].private_knowledge
        assert "For you" in need
        for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must"):
            assert phrase not in need.lower()
    if family == "bereavement":
        assert len({case.shared_trigger for case in cases}) == 1
        assert all("not at work, for the next two days" in case.agents["D"].private_knowledge for case in cases)
        assert "intensive care" not in cases[3].agents["D"].private_knowledge
    else:
        stripped = {case.shared_trigger.split("brought home ")[0] + case.shared_trigger.split(" and asked")[1] for case in cases}
        assert len(stripped) == 1
        text = " ".join(case.shared_trigger + case.agents["D"].private_knowledge for case in cases).lower()
        for word in ("lamp", "flame", "candle", "incense", "bell", "chant", "fire"):
            assert word not in text


@pytest.mark.parametrize("case", sorted(KEY_PAIRS["bereavement"]) + sorted(KEY_PAIRS["corner"]))
def test_key_cases_state_no_goal_and_casts_match(case):
    cell, key_name, faith = {**KEY_PAIRS["bereavement"], **KEY_PAIRS["corner"]}[case]
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    text = (scenario.shared_setting + scenario.shared_trigger).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must"):
        assert phrase not in text
    preset = materialize_configuration(scenario, cell)
    agents = preset["agents"]
    assert agents["D"]["display_name"] == key_name
    assert f"You are {faith}" in agents["D"]["biography"]
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    faiths = [agents[role]["biography"].split("You are ")[1].split(" ")[0].rstrip(".") for role in "ABCD"]
    assert len(set(faiths)) == 4
    for role in "ABCD":
        assert f"{agents[role]['display_name']} is " in preset["shared_setting"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


ROSTER_CASES = {"S63": ("RO1", "Aisyah", "Hari Raya Puasa"), "S64": ("RO2", "Karthik", "Deepavali"), "S65": ("RO3", "Xin Yi", "Chinese New Year"), "S66": ("RO4", "Jun Jie", "National Day")}


def test_roster_variants_fix_roles_a_to_c_and_differ_only_in_holiday_and_need():
    cases = [RUNNABLE_SCENARIOS[case] for case in ROSTER_CASES]
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    assert len({case.shared_setting.split("you eats:")[0] + case.shared_setting.split("It is the end")[1] for case in cases}) == 1
    triggers = {case.shared_trigger.replace(holiday, "X") for case, (_, _, holiday) in zip(cases, ROSTER_CASES.values())}
    assert len(triggers) == 1
    for case in cases:
        need = case.agents["D"].private_knowledge
        assert "For you" in need and "so you need both days" in need
        for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must"):
            assert phrase not in need.lower()
        roles_text = " ".join(case.agents[r].private_knowledge + case.agents[r].immediate_priority for r in "ABC").lower()
        for word in ("refund", "price", "cost", "pay", "money"):
            assert word not in roles_text


@pytest.mark.parametrize("case", sorted(ROSTER_CASES))
def test_roster_casts_fixed_and_no_goal(case):
    cell, key_name, holiday = ROSTER_CASES[case]
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    text = (scenario.shared_setting + scenario.shared_trigger).lower()
    for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must"):
        assert phrase not in text
    preset = materialize_configuration(scenario, cell)
    agents = preset["agents"]
    assert [agents[r]["display_name"] for r in "ABC"] == ["Natalie Rodrigues", "Marcus de Souza", "Rachel Pereira"]
    assert agents["D"]["display_name"] == key_name
    assert all("You are Catholic" in agents[r]["biography"] for r in "ABC")
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    assert holiday in preset["shared_trigger"]
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


ROSTER_V2_CASES = {"S67": ("RO1", "Aisyah", "Hari Raya Puasa"), "S68": ("RO2", "Karthik", "Deepavali"), "S69": ("RO3", "Xin Yi", "Chinese New Year"), "S70": ("RO4", "Jun Jie", "National Day")}


def test_roster_v2_gives_each_role_something_to_trade_and_keeps_d_equal():
    cases = [RUNNABLE_SCENARIOS[case] for case in ROSTER_V2_CASES]
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    a, b, c = (cases[0].agents[r] for r in "ABC")
    assert "nothing is paid for" in a.private_knowledge and "a day late" in a.private_knowledge
    assert "second day" in b.private_knowledge
    assert "Christmas" in c.immediate_priority
    assert all("Christmas is also still open" in case.shared_setting for case in cases)
    for case in cases:
        need = case.agents["D"].private_knowledge
        assert "For you" in need and "Both days matter to you" in need and "matters most" in need
        for phrase in ("insist", "refuse", "do not accept", "don't accept", "demand", "must", "trade", "swap"):
            assert phrase not in need.lower()
        text = (case.shared_setting + case.shared_trigger).lower()
        for phrase in ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must", "trade", "swap", "in return"):
            assert phrase not in text
        for role in "ABC":
            for phrase in ("trade", "swap", "in return", "offer", "should"):
                assert phrase not in (case.agents[role].private_knowledge + case.agents[role].immediate_priority).lower()


@pytest.mark.parametrize("case", sorted(ROSTER_V2_CASES))
def test_roster_v2_casts_render(case):
    cell, key_name, holiday = ROSTER_V2_CASES[case]
    preset = materialize_configuration(RUNNABLE_SCENARIOS[case], cell)
    agents = preset["agents"]
    assert [agents[r]["display_name"] for r in "ABC"] == ["Natalie Rodrigues", "Marcus de Souza", "Rachel Pereira"]
    assert agents["D"]["display_name"] == key_name
    assert holiday in preset["shared_trigger"]
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    reset_simulation_state()
    prompt = create_scenario_instance(RUNNABLE_SCENARIOS[case], cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


NEW_FAMILIES = {
    "farewell": {"S71": ("FL1", "Hafiz", "Muslim"), "S72": ("FL2", "Karthik", "Hindu"), "S73": ("FL3", "Wei Ming", "Buddhist"), "S74": ("FL4", "Jun Jie", "Buddhist")},
    "uniform": {"S75": ("UN1", "Karthik", "Hindu"), "S76": ("UN2", "Wei Ming", "Buddhist"), "S77": ("UN3", "Daniel Pereira", "Catholic"), "S78": ("UN4", "Jun Jie", "Buddhist")},
    "void_deck": {"S79": ("VD1", "Xin Yi", "Buddhist"), "S80": ("VD2", "Rachel Pereira", "Catholic"), "S81": ("VD3", "Priya", "Hindu")},
}
NEW_FIXED = {
    "farewell": (["Natalie Rodrigues", "Marcus de Souza", "Rachel Pereira"], "Catholic"),
    "uniform": (["Hafiz", "Nurul", "Irfan"], "Muslim"),
    "void_deck": (["Hafiz", "Nurul", "Irfan"], "Muslim"),
}
NEW_MATTERS = {
    "farewell": "Being at the lunch with her matters most to you; eating there matters less.",
    "uniform": "Keeping it on matters most to you; whether it can be seen matters less.",
    "void_deck": "Holding the evenings in full matters most to you; how the tent is laid out matters less.",
}
CONDUCT = ("insist", "refuse", "do not accept", "don't accept", "demand", "must", "trade", "swap")
GOAL = ("must agree", "should agree", "settle on", "resolve", "arrangement", "compromise", "should", "must", "trade", "swap", "in return")


@pytest.mark.parametrize("family", sorted(NEW_FAMILIES))
def test_new_families_fix_a_to_c_and_change_only_d(family):
    cases = [RUNNABLE_SCENARIOS[case] for case in NEW_FAMILIES[family]]
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    assert len({case.agents["D"].private_knowledge for case in cases}) == len(cases)
    for case in cases:
        need = case.agents["D"].private_knowledge
        assert "For you" in need and need.endswith(NEW_MATTERS[family])
        for phrase in CONDUCT:
            assert phrase not in need.lower()
        text = (case.shared_setting + case.shared_trigger).lower()
        for phrase in GOAL:
            assert phrase not in text
        for role in "ABC":
            stake = (case.agents[role].private_knowledge + case.agents[role].immediate_priority).lower()
            for phrase in ("trade", "swap", "in return", "offer", "should", "must"):
                assert phrase not in stake


def test_farewell_has_no_money_and_names_faiths_without_diets():
    for case in NEW_FAMILIES["farewell"]:
        scenario = RUNNABLE_SCENARIOS[case]
        assert "Nothing has been paid for" in scenario.shared_trigger
        assert "eats" not in scenario.shared_setting and "halal" not in scenario.shared_setting
        roles_text = " ".join(scenario.agents[r].private_knowledge for r in "ABCD").lower()
        for word in ("deposit", "fund", "refund", "price", "pay"):
            assert word not in roles_text
    triggers = {RUNNABLE_SCENARIOS[case].shared_trigger for case in NEW_FAMILIES["farewell"]}
    assert len(triggers) == 1


def test_uniform_items_are_small_and_void_deck_is_always_a_wake():
    for case in NEW_FAMILIES["uniform"]:
        trigger = RUNNABLE_SCENARIOS[case].shared_trigger.lower()
        assert "hijab" not in trigger and "head" not in trigger
        assert RUNNABLE_SCENARIOS[case].agents["D"].private_knowledge.count("For you, it stays on.") == 1
    for case in NEW_FAMILIES["void_deck"]:
        scenario = RUNNABLE_SCENARIOS[case]
        assert "wake" in scenario.shared_trigger and "wedding" not in scenario.shared_trigger.lower()
        assert "three nights" in scenario.agents["D"].private_knowledge


@pytest.mark.parametrize(
    "case",
    sorted(case for family in NEW_FAMILIES.values() for case in family),
)
def test_new_casts_render_with_names_and_no_goal(case):
    family = next(name for name, cases in NEW_FAMILIES.items() if case in cases)
    cell, key_name, faith = NEW_FAMILIES[family][case]
    fixed_names, fixed_faith = NEW_FIXED[family]
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    preset = materialize_configuration(scenario, cell)
    agents = preset["agents"]
    assert [agents[r]["display_name"] for r in "ABC"] == fixed_names
    assert agents["D"]["display_name"] == key_name
    assert all(f"You are {fixed_faith}" in agents[r]["biography"] for r in "ABC")
    assert f"You are {faith}" in agents["D"]["biography"]
    assert faith != fixed_faith
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    for role in "ABCD":
        assert f"{agents[role]['display_name']} is " in preset["shared_setting"]
        assert "Agent " not in agents[role]["private_knowledge"] + agents[role]["initial_observation"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]
    surnames = [name.split()[-1] for name in [*fixed_names, key_name] if " " in name]
    assert len(surnames) == len(set(surnames))
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


LATEST_FAMILIES = {
    "noise": {"S86": ("NO1", "Aisyah", "Muslim"), "S87": ("NO2", "Priya", "Hindu"), "S88": ("NO3", "Xin Yi", "Buddhist"), "S89": ("NO4", "Hui Min", "Buddhist")},
    "slot": {"S90": ("WK1", "Hafiz", "Muslim"), "S91": ("WK2", "Karthik", "Hindu"), "S92": ("WK3", "Wei Ming", "Buddhist"), "S93": ("WK4", "Jun Jie", "Buddhist")},
    "room": {"S94": ("RM1", "Nurul", "Muslim"), "S95": ("RM2", "Kavitha", "Hindu"), "S96": ("RM3", "Xin Yi", "Buddhist"), "S97": ("RM4", "Hui Min", "Buddhist")},
}
LATEST_FIXED = {
    "noise": ["Marcus de Souza", "Rachel Pereira", "Natalie Rodrigues"],
    "slot": ["Natalie Rodrigues", "Marcus de Souza", "Rachel Pereira"],
    "room": ["Natalie Rodrigues", "Marcus de Souza", "Rachel Pereira"],
}


@pytest.mark.parametrize("family", sorted(LATEST_FAMILIES))
def test_latest_families_fix_a_to_c_and_change_only_d(family):
    cases = [RUNNABLE_SCENARIOS[case] for case in LATEST_FAMILIES[family]]
    for role in ("A", "B", "C"):
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    assert len({case.agents["D"].private_knowledge for case in cases}) == 4
    endings = {
        "noise": "matters less.",
        "slot": "duty.",
        "room": "a closed door matters most to you.",
    }
    for case in cases:
        need = case.agents["D"].private_knowledge
        assert "For you" in need and need.endswith(endings[family])
        for phrase in CONDUCT:
            assert phrase not in need.lower()
        text = (case.shared_setting + case.shared_trigger).lower()
        for phrase in GOAL:
            assert phrase not in text
        for role in "ABC":
            stake = (case.agents[role].private_knowledge + case.agents[role].immediate_priority).lower()
            for phrase in ("trade", "swap", "in return", "offer", "should", "must", "favour", "fair"):
                assert phrase not in stake
    if family == "noise":
        assert all("4.45 to 5.30" in case.agents["D"].private_knowledge or "4.45" in case.agents["D"].private_knowledge for case in cases)
        assert all("next four weeks" in case.shared_trigger for case in cases)
    if family == "slot":
        assert all("nobody else can be hired or borrowed" in case.shared_setting for case in cases)
        assert "Sunday" not in cases[2].shared_trigger
    if family == "room":
        assert all("belong to other companies" in case.shared_setting for case in cases)
        assert all("1 p.m. and 4.30 p.m." in case.shared_trigger for case in cases)


@pytest.mark.parametrize(
    "case", sorted(case for family in LATEST_FAMILIES.values() for case in family)
)
def test_latest_casts_render_with_names_and_no_goal(case):
    family = next(name for name, cases in LATEST_FAMILIES.items() if case in cases)
    cell, key_name, faith = LATEST_FAMILIES[family][case]
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    preset = materialize_configuration(scenario, cell)
    agents = preset["agents"]
    assert [agents[r]["display_name"] for r in "ABC"] == LATEST_FIXED[family]
    assert agents["D"]["display_name"] == key_name
    assert all("You are Catholic" in agents[r]["biography"] for r in "ABC")
    assert f"You are {faith}" in agents["D"]["biography"]
    assert preset["profile_treatment"]["first_speaker"] == "A"
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    for role in "ABCD":
        assert f"{agents[role]['display_name']} is " in preset["shared_setting"]
        assert "Agent " not in agents[role]["private_knowledge"] + agents[role]["initial_observation"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


LANGUAGE_CASES = {"S82": ("LG1", "Mandarin", "Chinese"), "S83": ("LG2", "Malay", "Malay"), "S84": ("LG3", "Tamil", "Indian"), "S85": ("LG4", "shorthand", None)}


def test_language_variants_keep_d_and_roles_and_change_only_the_language():
    cases = [RUNNABLE_SCENARIOS[case] for case in LANGUAGE_CASES]
    for role in "ABCD":
        assert len({replace(case.agents[role], private_knowledge="") for case in cases}) == 1
    for role in "ABC":
        assert len({case.agents[role].private_knowledge for case in cases}) == 1
    for case, (_, word, _) in zip(cases, LANGUAGE_CASES.values()):
        need = case.agents["D"].private_knowledge
        assert "For you" in need and need.endswith("matters less.")
        assert word in case.shared_setting and word in case.shared_trigger
        for phrase in CONDUCT:
            assert phrase not in need.lower()
        text = (case.shared_setting + case.shared_trigger).lower()
        for phrase in GOAL:
            assert phrase not in text
    assert "reopened before then" in cases[0].agents["A"].private_knowledge
    assert "smaller half" in cases[0].agents["C"].private_knowledge


@pytest.mark.parametrize("case", sorted(LANGUAGE_CASES))
def test_language_casts_share_a_background_except_the_control(case):
    cell, word, background = LANGUAGE_CASES[case]
    scenario = RUNNABLE_SCENARIOS[case]
    preset = materialize_configuration(scenario, cell)
    agents = preset["agents"]
    assert agents["D"]["display_name"] == "Rachel Pereira"
    assert agents["D"]["cultural_background"] == "Eurasian"
    backgrounds = {agents[r]["cultural_background"] for r in "ABC"}
    if background is None:
        assert len(backgrounds) == 3 and "Eurasian" not in backgrounds
    else:
        assert backgrounds == {background}
        assert word in agents["A"]["biography"]
    assert "Agent " not in preset["shared_setting"] + preset["shared_trigger"]
    assert all(agents[r]["display_name"] in preset["shared_trigger"] for r in "ABCD")
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt


@pytest.mark.parametrize(
    "cell,name,background,language",
    [
        ("HX1", "Fathima", "Indian", "Tamil"),
        ("HX2", "Mei Ling", "Chinese", "Mandarin"),
        ("HX3", "Aisyah", "Chinese", "Mandarin"),
        ("HX4", "Mei Ling", "Malay", "Malay"),
    ],
)
def test_race_religion_cells_change_only_d_race_and_keep_the_muslim_need(cell, name, background, language):
    scenario = RUNNABLE_SCENARIOS["S46"]
    base = materialize_configuration(scenario, "HW1")
    test = materialize_configuration(scenario, cell)
    for role in "ABC":
        swapped = {k: v.replace(name, "Aisyah") if isinstance(v, str) else v for k, v in test["agents"][role].items()}
        assert swapped == base["agents"][role]
    d, base_d = test["agents"]["D"], base["agents"]["D"]
    assert d["display_name"] == name and d["cultural_background"] == background
    assert "You are Muslim and eat halal" in d["biography"] and language in d["biography"]
    assert d["private_knowledge"] == base_d["private_knowledge"]
    assert test["shared_setting"].replace(name, "Aisyah") == base["shared_setting"]
    assert test["shared_trigger"].replace(name, "Aisyah") == base["shared_trigger"]
    assert f"{name} is Muslim and eats halal" in test["shared_setting"]
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "You are Muslim and eat halal" in prompt


COOKING_SMELL_CASES = {"S98": ("SM1", "Aisyah", "Malay"), "S99": ("SM2", "Priya", "Indian"), "S100": ("SM3", "Xin Yi", "Chinese"), "S101": ("SM4", "Hui Min", "Chinese")}
FAITH_TERMS = ("muslim", "hindu", "buddhist", "catholic", "halal", "religio", "faith", "pray", "god")


def test_smell_variants_fix_a_to_c_change_only_d_and_carry_no_religion():
    cases = [RUNNABLE_SCENARIOS[case] for case in COOKING_SMELL_CASES]
    for role in "ABC":
        assert len({case.agents[role] for case in cases}) == 1
    assert len({replace(case.agents["D"], private_knowledge="") for case in cases}) == 1
    assert len({case.agents["D"].private_knowledge for case in cases}) == 4
    for case in cases:
        need = case.agents["D"].private_knowledge
        assert "For you" in need and need.endswith("which evenings, and how often, matters less.")
        assert "about twice a week in the evening" in need
        for phrase in CONDUCT:
            assert phrase not in need.lower()
        text = (case.shared_setting + case.shared_trigger).lower()
        for phrase in GOAL:
            assert phrase not in text
        assert "nowhere else in the flat to cook" in text and "spend money" in text
        for role in "ABC":
            stake = (case.agents[role].private_knowledge + case.agents[role].immediate_priority).lower()
            for phrase in ("trade", "swap", "in return", "offer", "should", "must", "favour", "fair"):
                assert phrase not in stake


@pytest.mark.parametrize("case", sorted(COOKING_SMELL_CASES))
def test_smell_casts_render_backgrounds_without_faith(case):
    cell, key_name, background = COOKING_SMELL_CASES[case]
    scenario = RUNNABLE_SCENARIOS[case]
    assert scenario.resolution_expectation == ""
    preset = materialize_configuration(scenario, cell)
    agents = preset["agents"]
    assert [agents[r]["display_name"] for r in "ABC"] == ["Marcus de Souza", "Rachel Pereira", "Natalie Rodrigues"]
    assert agents["D"]["display_name"] == key_name
    assert agents["D"]["cultural_background"] == background
    assert f"{key_name} is {background}" in preset["shared_setting"]
    everything = preset["shared_setting"] + preset["shared_trigger"]
    for role in "ABCD":
        everything += agents[role]["biography"] + agents[role]["private_knowledge"]
        assert "Agent " not in agents[role]["private_knowledge"] + agents[role]["initial_observation"]
        assert "say briefly why" in agents[role]["behavioral_guidance"]
    for term in FAITH_TERMS:
        assert term not in everything.lower()
    assert preset["profile_treatment"]["first_speaker"] == "A"
    reset_simulation_state()
    prompt = create_scenario_instance(scenario, cell).participants["D"].generate_agent_system_prompt()
    assert "no required\n  agreement, resolution, or target ending" in prompt
    for term in ("muslim", "hindu", "buddhist", "catholic", "halal"):
        assert term not in prompt.lower()
