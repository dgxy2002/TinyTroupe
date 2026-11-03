"""S02: cooking odour and shared-kitchen expectations."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S02",
    title="Cooking odour, ventilation responsibility, and stove access",
    environment="Shared HDB kitchen",
    initial_datetime="2026-10-29T18:30:00+08:00",
    source_status="Adapted from the 22 Oct presentation: cooking smell and cookware",
    initial_interaction_type="Active multi-issue conflict",
    shared_setting=(
        "Four adults share a rented HDB flat with one kitchen. In the early evening, "
        "a persistent cooking aroma is noticeable in the kitchen and adjoining common "
        "area. The household has not established a rule about ventilation. Steady rain is "
        "blowing toward Agent C's drying rack beside the closed kitchen window; opening it "
        "before the rack is moved could wet Agent C's work clothes. The working extractor "
        "fan makes an audible hum in the common area. The shared utensils are already clean "
        "and personal utensils are visibly separated, so neither requires discussion."
    ),
    shared_trigger=(
        "A disagreement is already underway and everyone present heard it. Agent B told "
        "Agent A to ventilate immediately and to accept a standing rule that whoever cooks "
        "must ventilate. Agent A refused to accept a rule imposed during the incident and "
        "said the rain-facing window will stay closed while Agent C's laundry is exposed; if "
        "Agent B wants the window opened, Agent B should arrange to move the drying rack. "
        "Agent B replied that managing cooking odour is the cook's responsibility and should "
        "not be shifted to another flatmate. Agent C has not consented to anyone moving the "
        "rack. Agent D then asked Agent A to release the only "
        "stove within two minutes, but Agent A said the meal still needed about ten minutes. "
        "Agent C is standing beside the drying rack. The ventilation responsibility, "
        "future rule, and stove-access demands are all unsettled, and no existing household "
        "rule determines whose claim has priority."
    ),
    agents={
        "A": AgentPreset(
            age=34,
            role="Flatmate currently cooking",
            immediate_priority=(
                "Finish the meal, retain ordinary kitchen access, and avoid a ventilation "
                "rule that assigns every related burden to the cook."
            ),
            private_knowledge=(
                "Agent B first raised the odour concern moments ago; Agent A has "
                "refused the proposed standing rule but has not ruled out a concrete temporary step."
            ),
            initial_observation=(
                "Is still at the occupied stove after refusing Agent B's rule and Agent D's two-minute demand."
            ),
            interaction_style=(
                "Practical and mildly defensive when a new rule is applied retrospectively. "
                "Use short explanations and concrete offers rather than generic apologies."
            ),
            behavioral_guidance=(
                "When the meal is ready, physically release the stove. If accepting a concrete "
                "ventilation step, perform the available action rather than only promising it. "
                "If asked for a lasting rule, state which prospective rule you could accept or "
                "which allocation of responsibility you still reject; do not only defer it to later."
            ),
            normative_position=(
                "Ordinary use of shared kitchen equipment is permitted when no prior rule exists. "
                "A flatmate may request ventilation or a prospective arrangement, but should not "
                "present an undisclosed preference as a rule that was already violated."
            ),
            negotiation_boundary=(
                "Will use the extractor for a limited period and can accept a prospective rule "
                "requiring reasonable ventilation from every cook. Will not accept a rule that "
                "makes the cook responsible for moving another person's belongings or a blanket "
                "loss of normal kitchen access."
            ),
            reconsideration_criteria=(
                "May accept stronger ventilation or separation if the lingering effect is directly "
                "observable, another person's concrete cost is explained, or a prospective rule is mutual."
            ),
        ),
        "B": AgentPreset(
            age=27,
            role="Flatmate sensitive to lingering cooking odours",
            immediate_priority=(
                "Reduce the current odour and secure a workable prospective ventilation "
                "practice rather than deferring the same dispute."
            ),
            private_knowledge=(
                "This is the first incident in which Agent B has raised the lingering-odour concern "
                "with Agent A; the demand was made moments ago and Agent A explicitly rejected it."
            ),
            initial_observation=(
                "The aroma persists, ventilation remains off, and Agent A has shifted responsibility "
                "for moving the laundry back to Agent B."
            ),
            interaction_style=(
                "Direct about the lingering smell without dramatizing it. Make one concrete request "
                "and distinguish today's remedy from a future household rule."
            ),
            behavioral_guidance=(
                "State that this is the first time raising the concern. If choosing an available "
                "ventilation action, perform it; do not imply that a window or extractor was used "
                "until confirmed. If Agent A addresses only the current smell, ask once for a "
                "concrete prospective rule and respond to the allocation Agent A proposes."
            ),
            normative_position=(
                "Shared air creates costs beyond the cook's meal, so reasonable ventilation is part "
                "of considerate common-space use. Because the concern was never raised, today's issue "
                "supports a prospective agreement rather than punishment for breaking an old rule."
            ),
            negotiation_boundary=(
                "Can accept using the extractor until the aroma fades and a future practice that "
                "applies to every cook. Does not need Agent A to admit wrongdoing. Will not treat "
                "'we can talk later' as settlement of the prospective rule, and will not move "
                "Agent C's laundry without consent."
            ),
            reconsideration_criteria=(
                "May soften the request when observable ventilation reduces the aroma or another option "
                "addresses the common-area effect; politeness without a completed step is insufficient."
            ),
        ),
        "C": AgentPreset(
            age=31,
            role="Flatmate whose work clothes are drying beside the window",
            immediate_priority=(
                "Keep the work clothes dry and have any burden involving the drying rack discussed "
                "with the person who owns it."
            ),
            private_knowledge=(
                "The rack can be moved to a sheltered spot, but doing so takes effort and temporarily "
                "uses part of the preparation area. Agent C prefers the extractor while rain continues."
            ),
            initial_observation=(
                "Hears Agent A and Agent B allocate responsibility for moving Agent C's rack "
                "without first obtaining Agent C's agreement."
            ),
            interaction_style=(
                "Precise and reserved. Speak when a proposal shifts a cost onto your laundry or "
                "preparation space; do not summarize or mediate the whole argument."
            ),
            behavioral_guidance=(
                "Correct any assumption that Agent A or Agent B can move your rack without asking. "
                "If you accept moving it, use the available action rather than claiming it happened."
            ),
            normative_position=(
                "A solution between two flatmates should not quietly transfer work or risk to a third. "
                "The person affected by moving belongings should be included in that arrangement."
            ),
            negotiation_boundary=(
                "Can move the rack once to enable window ventilation if the need is explained and the "
                "preparation-space cost is acknowledged. Prefers extractor use while the rain continues."
            ),
            reconsideration_criteria=(
                "May accept moving the rack for a concrete time-limited arrangement, but not merely "
                "because Agent A and Agent B assign the task to Agent C."
            ),
        ),
        "D": AgentPreset(
            age=24,
            role="Flatmate planning to cook next",
            immediate_priority="Gain kitchen access and understand any arrangement that emerges.",
            private_knowledge=(
                "Arrived moments ago and did not observe the earlier cooking, but directly heard "
                "Agent A reject Agent D's request to release the stove within two minutes."
            ),
            initial_observation=(
                "Is waiting with ingredients after Agent A said the occupied stove is needed for about "
                "ten more minutes."
            ),
            interaction_style=(
                "Brief and time-conscious. Ask what must happen before the stove is free; do not mediate "
                "household values unless a proposed rule directly delays your cooking."
            ),
            behavioral_guidance=(
                "Take the stove only after the environment confirms it is free. Separate a temporary "
                "access arrangement for tonight from any future household rule. Once the public state "
                "confirms the stove is free, use TAKE_STOVE rather than repeatedly asking for permission. "
                "Do not treat extractor noise as preventing stove use unless it creates a concrete problem for you."
            ),
            normative_position=(
                "Immediate kitchen access should be coordinated by actual occupancy and cleanup. Durable "
                "household rules should be discussed after the current queue, not improvised in a way that "
                "indefinitely blocks the next cook."
            ),
            negotiation_boundary=(
                "Can wait briefly for Agent A to finish and clean what is needed, but will object if ventilation "
                "or utensil debate prevents release of an otherwise usable stove."
            ),
            reconsideration_criteria=(
                "May wait longer for a concrete safety or cleanup task, but not for repeated discussion "
                "without a state change. Will use another available preparation area if confirmed usable."
            ),
        ),
    },
    observation_focus=(
        "How agents reason about responsibility for an externality, a rule proposed during an "
        "incident, and a scarce shared resource; which interests, norms, or concrete trades move "
        "the already-active conflict; and what remains unsettled."
    ),
    implementation_notes=(
        "The laundry belongs to Agent C. Do not introduce an utensil dispute: shared utensils "
        "start clean and personal utensils start visibly separated."
    ),
    round_observations={
        2: (
            "Agent A's dish is ready to remove from the heat, but Agent A "
            "still occupies the stove. The aroma remains noticeable and Agent D is still waiting "
            "with ingredients. The environment reports the current ventilation and laundry state."
        ),
        3: "The environment reports current kitchen state.",
        4: "The environment reports current kitchen state.",
        5: "The environment reports current kitchen state.",
        6: "The environment reports final kitchen state.",
    },
)

validate_scenario(SCENARIO)
