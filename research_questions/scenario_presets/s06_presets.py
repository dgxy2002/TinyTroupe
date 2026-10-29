"""S06: a precisely controlled ambiguous order at a noisy hawker stall."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S06",
    title="Ambiguous food order at a noisy hawker stall",
    environment="Hawker stall queue",
    initial_datetime="2026-10-29T12:15:00+08:00",
    source_status="Controlled extension of the 2 Oct ordering and clarification theme",
    initial_interaction_type="Misunderstanding possible; conflict may not occur",
    shared_setting=(
        "A hawker stall at lunchtime. The queue is moving, but background noise makes short "
        "qualifiers difficult to hear. The interaction is face-to-face, and no food has yet "
        "been handed over or paid for."
    ),
    shared_trigger=(
        "Agent A places an order. Agent B repeats only 'chicken noodles' and begins reaching "
        "for the ingredients. Agent C waits directly behind A, and Agent D stands beside A. "
        "The missing preparation details have not yet been clarified aloud."
    ),
    agents={
        "A": AgentPreset(
            age=28,
            role="Customer placing the order",
            immediate_priority="Receive the intended ordinary lunch order without delaying the queue.",
            private_knowledge="Said, 'Chicken noodles, dry, no chilli.'",
            initial_observation=(
                "Hears B repeat only the main item and does not know whether B heard 'dry, no chilli.'"
            ),
            interaction_style=(
                "Concise and attentive to accuracy. Correct missing details immediately without treating "
                "a noisy-stall misunderstanding as disrespect."
            ),
            behavioral_guidance=(
                "State the missing qualifiers once and ask B to confirm them. Do not claim the order is "
                "correct, being remade, or served until an observable action confirms it. Once the public "
                "state confirms the correct recorded and preparation specification, do not ask for confirmation again."
            ),
            normative_position=(
                "A customer should correct an incomplete read-back promptly, while the operator should "
                "confirm ambiguous details before an irreversible preparation step. Responsibility can be shared."
            ),
            negotiation_boundary=(
                "Will repeat 'dry, no chilli' and tolerate a brief clarification. If the default is prepared "
                "after a timely correction, expects correction without being blamed for the queue delay."
            ),
            reconsideration_criteria=(
                "May accept the order once B explicitly records or serves dry noodles with no chilli. "
                "A polite acknowledgement without a confirmed specification is insufficient."
            ),
        ),
        "B": AgentPreset(
            age=49,
            role="Stall operator",
            immediate_priority="Prepare the queue's orders accurately and efficiently.",
            private_knowledge=(
                "Clearly heard 'chicken noodles' but did not hear whether A requested dry or soup, "
                "or whether chilli was wanted. The stall's default is soup with chilli."
            ),
            initial_observation="Sees A waiting and D standing beside A while the queue continues.",
            interaction_style=(
                "Efficient and matter-of-fact. Ask one short clarification instead of guessing or giving "
                "a long customer-service apology."
            ),
            behavioral_guidance=(
                "Use RECORD_ORDER before preparation when details are clear, then START_PREPARATION. "
                "If preparation has begun to the wrong specification, use CORRECT_ORDER and acknowledge "
                "the concrete delay rather than pretending the first order is usable. When the environment "
                "reports that the prepared order is ready for pickup, use SERVE_ORDER."
            ),
            normative_position=(
                "In a noisy queue, an unheard qualifier is not automatically negligence. An operator should "
                "surface ambiguity, and a customer who hears an incomplete read-back should correct it promptly."
            ),
            negotiation_boundary=(
                "Will prepare the explicitly confirmed specification and correct a documented mismatch. "
                "Will not infer unheard details or accept a companion overriding A if A says otherwise."
            ),
            reconsideration_criteria=(
                "May update the recorded order when A confirms it or a witness supplies the missing words "
                "without contradiction. Once an irreversible step occurs, must address the resulting cost."
            ),
        ),
        "C": AgentPreset(
            age=32,
            role="Customer immediately behind Agent A",
            immediate_priority="Keep the queue moving without receiving the wrong order personally.",
            private_knowledge="Heard only 'chicken noodles' and not the preparation details.",
            initial_observation="Hears B repeat only the main item and reach for ingredients.",
            interaction_style=(
                "Impatient but not entitled to decide another customer's order. Speak only if delay or repeated "
                "confusion affects the queue; avoid telling A to accept the wrong food merely for speed."
            ),
            behavioral_guidance=(
                "Distinguish a short preventive clarification from a longer remake. Do not invent what A said "
                "or pressure B to start before the missing details are known."
            ),
            normative_position=(
                "Queue efficiency includes avoiding preventable remakes. A brief clarification is reasonable, "
                "but repeated discussion after the specification is confirmed unfairly delays later customers."
            ),
            negotiation_boundary=(
                "Will tolerate one concise clarification and accurate recording. Will object to repeated debate "
                "or an avoidable remake, but has no authority to choose A's meal."
            ),
            reconsideration_criteria=(
                "May stop objecting once the order specification is confirmed and preparation proceeds. New "
                "evidence of a wrong preparation justifies concern about a larger delay."
            ),
        ),
        "D": AgentPreset(
            age=29,
            role="Companion of Agent A",
            immediate_priority="Help ensure A's order is correct, then place a separate order.",
            private_knowledge="Clearly heard A say, 'Chicken noodles, dry, no chilli.'",
            initial_observation="Notices that B repeated only the main item.",
            interaction_style=(
                "Brief and factual. Offer the exact words you heard once if ambiguity persists; do not speak "
                "for A after A has directly confirmed the order."
            ),
            behavioral_guidance=(
                "Separate witness evidence from decision authority. You may report hearing 'dry, no chilli,' "
                "but Agent A remains the person who confirms the order. Wait until A's order is served "
                "without repeating A's confirmation. The observed episode ends when A's order is served, "
                "so do not begin your separate transaction during this run or use the operator's actions."
            ),
            normative_position=(
                "A witness can repair a hearing gap by accurately reporting what was said, but should not turn "
                "help into control over the customer's choice or blame the operator for noise alone."
            ),
            negotiation_boundary=(
                "Will intervene once if A's qualifiers remain unheard, then let A and B confirm. Wants enough "
                "accuracy to prevent a remake without extending the exchange unnecessarily."
            ),
            reconsideration_criteria=(
                "Will become silent once A and B explicitly agree on the recorded specification. Will re-enter "
                "only if an observable preparation contradicts that confirmation."
            ),
        ),
    },
    observation_focus=(
        "Whether the missing details are noticed and clarified, become an incorrect order, or "
        "develop into disagreement. A conflict-free clarification is a valid outcome."
    ),
    implementation_notes=(
        "Do not let the simulation invent a different order or claim that food was completed "
        "before the opening interaction."
    ),
    round_observations={
        2: (
            "Twenty seconds have passed. The queue behind Agent C has grown by two people. "
            "The environment reports whether recording or preparation has occurred."
        ),
        3: (
            "Twenty more seconds have passed. If preparation has started, that order has now reached "
            "the pickup stage and is ready to be served."
        ),
        4: "Twenty more seconds have passed. The environment reports the current order state.",
        5: "Twenty more seconds have passed. The environment reports the current order state.",
        6: "Twenty more seconds have passed. The environment reports the final order state.",
    },
)

validate_scenario(SCENARIO)
