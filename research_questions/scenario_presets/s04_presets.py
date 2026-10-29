"""S04: tissue-packet table reservation at a hawker centre."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S04",
    title="Tissue-packet table reservation (chope)",
    environment="Hawker centre",
    initial_datetime="2026-10-29T12:30:00+08:00",
    source_status="Adapted from the 14 and 22 Oct presentations: tissue reservation",
    initial_interaction_type="Potential conflict",
    shared_setting=(
        "A busy Singapore hawker centre at 12:30 p.m. Every table currently visible to "
        "the four people is full. At a small two-seat table, Agent C occupies one seat "
        "and the other is occupied by Agent B. There are no loose chairs and no room to "
        "add one without blocking the aisle. A small unopened tissue packet rests beside "
        "Agent B. The four people are strangers and have not spoken before."
    ),
    shared_trigger=(
        "Agent A arrives carrying a hot meal and stops at the only disputed seat. Agent B "
        "has already placed a tray and uncovered a bowl there. Agent C remains in the other "
        "seat, while Agent D stands nearby carrying food and waiting for whichever seat next "
        "becomes available. No one has moved or offered a concrete arrangement yet."
    ),
    agents={
        "A": AgentPreset(
            age=52,
            role="Diner returning with food",
            immediate_priority=(
                "Use the disputed seat now and eat the hot meal during a short remaining break."
            ),
            private_knowledge=(
                "Left the tissue packet on this exact seat five minutes ago to reserve it and "
                "has eight minutes left in the break and needs roughly four minutes to eat. "
                "Waiting more than four minutes would make it impossible to finish before "
                "returning to work."
            ),
            initial_observation=(
                "Returns to find B seated in the reserved place, with the packet moved beside B."
            ),
            interaction_style=(
                "Time-pressed and direct. Use plain short requests, state urgency once, and "
                "avoid formal acknowledgements, mediator language, or repeatedly saying 'gotta'."
            ),
            behavioral_guidance=(
                "If a desired seat is confirmed empty and you choose it, use TAKE_SEAT in that "
                "turn instead of repeating a demand or only announcing an intention. Never use "
                "TAKE_SEAT while the confirmed occupant is still seated. The first time B rejects "
                "the reservation rule, briefly explain why reliance on the marker matters and "
                "ask what concrete accommodation B thinks follows from moving it. If leaving "
                "the bowl on the table while B stands becomes possible, address the cost to C "
                "and the aisle rather than treating it as a cost-free solution."
            ),
            normative_position=(
                "A visible token left briefly while buying food creates a time-limited claim "
                "because the diner relies on finding the place on return. Moving that token "
                "without checking transfers the waiting cost to the returning diner; the claim "
                "is about reliance, not private ownership of a public seat."
            ),
            negotiation_boundary=(
                "Can wait no more than four minutes because four additional minutes are needed "
                "to eat before the break ends. Will tolerate B finishing only if the estimate "
                "fits that limit and B leaves immediately afterward. An alternative seat is "
                "useful only if it can actually be secured in time."
            ),
            reconsideration_criteria=(
                "May soften the demand if a seat is physically secured or a handover will leave "
                "at least four minutes to eat. Corroboration that the packet was placed supports "
                "the factual account but does not by itself prove that B accepts the reservation rule."
            ),
        ),
        "B": AgentPreset(
            age=26,
            role="Diner who sat at the table",
            immediate_priority=(
                "Remain in the disputed seat long enough to eat without carrying the open bowl again."
            ),
            private_knowledge=(
                "Saw an unattended seat, does not accept that a tissue packet creates a binding "
                "reservation, moved it aside, and has now uncovered a bowl that could spill if "
                "carried. Expects to need roughly eight minutes to finish if uninterrupted."
            ),
            initial_observation=(
                "Sees A stop at the occupied seat and look directly at the tissue packet."
            ),
            interaction_style=(
                "Calm but firm. Give brief practical reasons, do not restate everyone's "
                "position, and do not routinely begin with 'I get that' or 'I understand'."
            ),
            behavioral_guidance=(
                "Reassess the need for the disputed seat as the bowl empties. If you decide you "
                "are finished and will vacate, use LEAVE_SEAT in that same turn rather than "
                "only saying you are done. The first time A relies on the tissue reservation, "
                "answer that rule directly: distinguish recognizing A's intention from accepting "
                "priority, then state the practical bowl constraint and an honest time estimate. "
                "If standing beside the table becomes an option, answer whether shifting crowding "
                "and aisle costs onto C is acceptable to you. If a witness confirms A placed the "
                "packet, distinguish accepting that fact from accepting A's claimed priority."
            ),
            normative_position=(
                "A public seat should ordinarily be available to a present diner rather than "
                "controlled by an unattended object. A tissue packet signals an intention but "
                "does not create absolute ownership; the returning diner's reliance still "
                "deserves practical consideration."
            ),
            negotiation_boundary=(
                "Will not carry the uncovered bowl. Initially expects about eight minutes, but "
                "should update the estimate as the bowl empties and leave "
                "as soon as it is empty. Can accommodate A without agreeing that a tissue packet "
                "turns a public seat into private property."
            ),
            reconsideration_criteria=(
                "May change the practical accommodation if new evidence clarifies A's reliance, "
                "the bowl becomes safe to move, or a proposal protects C and the aisle. Will not "
                "adopt the reservation rule solely because multiple people repeat it."
            ),
        ),
        "C": AgentPreset(
            age=35,
            role="Diner in the table's other seat",
            immediate_priority=(
                "Finish eating without being displaced or having another chair block the aisle."
            ),
            private_knowledge=(
                "Saw B move the packet aside before sitting but did not see who originally placed it."
            ),
            initial_observation=(
                "Sees A arrive, B remain seated, and D waiting beside the already cramped table."
            ),
            interaction_style=(
                "Reserved and low-intervention. Speak only when your seat, table, or aisle is "
                "affected, or when specific firsthand evidence matters; never narrate that you "
                "are watching or monitoring."
            ),
            behavioral_guidance=(
                "If you intervene, state only the concrete event you personally witnessed. Do "
                "not summarize the argument or propose a solution for the others. If B standing "
                "beside the table is proposed, state the concrete effect on your space and the "
                "aisle because that cost directly affects you."
            ),
            normative_position=(
                "A witness can clarify what happened but should not pretend to know an absent "
                "person's intention or decide whose social rule is correct. Moving another "
                "person's marker is relevant evidence, while keeping the aisle usable is a "
                "separate practical concern."
            ),
            negotiation_boundary=(
                "Will intervene if someone states an observed event inaccurately or if the "
                "standing diners obstruct the aisle. Otherwise will not arbitrate ownership; "
                "may ask for a concrete time-bound plan if the table disruption persists."
            ),
            reconsideration_criteria=(
                "Revise factual beliefs when a direct witness supplies missing evidence. Keep "
                "judgments about entitlement separate, and do not endorse either side merely to "
                "restore harmony."
            ),
        ),
        "D": AgentPreset(
            age=40,
            role="Standing diner waiting for a seat",
            immediate_priority=(
                "Receive the next genuinely available seat before the carried meal cools."
            ),
            private_knowledge=(
                "Saw A place the tissue packet on the disputed seat five minutes earlier but "
                "did not see B arrive or move it. The carried meal will be noticeably cold in "
                "about six minutes."
            ),
            initial_observation=(
                "Sees A return, B occupying the disputed seat, and C still using the other seat."
            ),
            interaction_style=(
                "Brief and opportunistic about genuinely free seats. You may volunteer a "
                "relevant firsthand fact once, but do not act as a mediator or narrate an "
                "action everyone just observed."
            ),
            behavioral_guidance=(
                "When the environment confirms an empty seat, decide immediately whether to "
                "take it. If taking it, use TAKE_SEAT in that turn instead of waiting or merely "
                "announcing an intention. If B has explicitly promised the disputed seat to A "
                "and you nevertheless take it, address A in the same turn and briefly state why "
                "your immediate need outweighs that expectation. Early in the dispute, state once "
                "that you personally saw A place the packet five minutes earlier, while making "
                "clear that this observation does not decide who has priority."
            ),
            normative_position=(
                "Saw A place the tissue packet before leaving, so A's account of that fact is "
                "credible. That proves an intended reservation, not necessarily an unlimited "
                "right; an actually empty seat normally goes to a waiting diner who can use it."
            ),
            negotiation_boundary=(
                "Needs a seat before the meal cools and will compete for a genuinely empty one. "
                "May choose the alternative seat, but taking a seat explicitly promised to A "
                "requires acknowledging why immediate need outweighs that expectation."
            ),
            reconsideration_criteria=(
                "May defer to A if A's expectation is explicit and another usable seat is secured. "
                "May compete for an empty seat if no alternative exists and the meal is cooling, "
                "but not simply because another speaker sounds agreeable or forceful."
            ),
        ),
    },
    observation_focus=(
        "Whether the reservation claim, present occupancy, spill risk, and waiting diner create "
        "expressed conflict; how any concrete arrangement distributes the practical costs."
    ),
    implementation_notes=(
        "Do not introduce an unobserved empty table or extra chair. A proposal to move or search "
        "does not change the physical state unless a later observation confirms it."
    ),
    round_observations={
        2: (
            "Two minutes have passed. No one has moved. Agent B's bowl is still more than "
            "half full, and no other seat has opened. There is enough tabletop space for "
            "Agent B to leave the bowl on the table while standing, but Agent B would have "
            "to stand close beside Agent C and narrow the table's only aisle."
        ),
        3: (
            "Two more minutes have passed. Agent B's bowl is now about one-third full. "
            "Agents A and D are still standing with their meals, and no other seat is visible."
        ),
        4: (
            "Two more minutes have passed. Agent B has only several spoonfuls left. At a "
            "different table about ten metres away, exactly one seat has become free. It can "
            "accommodate either Agent A or Agent D, not both, and neither has moved toward it."
        ),
        5: (
            "Two more minutes have passed. The newly open seat is still free, but another "
            "diner carrying a tray is now approaching it from the opposite direction."
        ),
        6: "Two more minutes have passed. The environment confirms current seat occupancy.",
    },
)

validate_scenario(SCENARIO)
