"""Scenario 6: the uniform rule (S75-S78), plus its casts UN1-UN4.

S75 Hindu thread, S76 Buddhist beads, S77 Catholic cross, S78 control (medical alert bracelet). Roles A-C are
three Malay Muslims.
"""

from __future__ import annotations

from .case_common import _key_case
from .common import _cast, _MALAY_FIXED, PROFILE_CONFIGURATIONS, ScenarioPreset


# Scenario 6: the uniform rule (S75 Hindu UN1, S76 Buddhist UN2, S77 Catholic UN3, S78 control UN4).
# Fix from the draft: the hijab is dropped, because it is a far bigger demand than a thread, so every
# variant is now a small item at the wrist or neck, against a medical alert bracelet. The rule covers
# jewellery and accessories, not head coverings. Roles A-C are the same three Malay Muslims, since
# Hindu, Buddhist and Catholic are the variant faiths. B's earrings give B a stake in the same rule.
UN_BACKGROUNDS = {
    "UN1": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Indian"},
    "UN2": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Chinese"},
    "UN3": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Eurasian"},
    "UN4": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Chinese"},
}
_UNIFORM_SETTING = (
    "Four sales staff work together at a retail store and have done so for two years. Head office has "
    "issued a new uniform rule that starts tomorrow: no jewellery or accessories may be visible apart "
    "from a watch. The area manager visits the store tomorrow morning, and head office cannot be "
    "reached tonight. You all know each other's faith and what each of you eats: {faiths} It is "
    "closing time, and all four are at the counter."
)
_UNIFORM_ROLES = {
    "A": dict(
        role="Shift lead",
        immediate_priority="Get the shift through tomorrow's visit.",
        private_knowledge=(
            "Tomorrow you have to sign that everyone on the shift follows the rule, and the area "
            "manager warned you after the last audit. The rule is about what can be seen."
        ),
        initial_observation="Sees the others listening as you finish reading the rule.",
    ),
    "B": dict(
        role="Sales assistant",
        immediate_priority="Be treated the same as everyone else.",
        private_knowledge=(
            "This afternoon you were told to stop wearing the earrings your late mother gave you, and "
            "you took them off. What bothers you is being treated differently, not the rule itself."
        ),
        initial_observation="Sees what Agent D is wearing.",
    ),
    "C": dict(
        role="Longest-serving sales assistant",
        immediate_priority="Keep your job.",
        private_knowledge=(
            "You have been with the company eleven years, and your contract is up for renewal next "
            "month. The area manager has known you for years and listens to you."
        ),
        initial_observation="Sees the others look at Agent D.",
    ),
    "D": dict(
        role="Newest sales assistant",
        immediate_priority="Keep your job, and not be overlooked as the newest person here.",
        private_knowledge="You joined three months ago and are still on probation.",
        initial_observation="Sees the others look at what you are wearing.",
    ),
}
_KEEP_ON = " Keeping it on matters most to you; whether it can be seen matters less."


def _uniform(scenario_id: str, title: str, item: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Uniform rule: {title}",
        "Retail store, at the counter",
        _UNIFORM_SETTING,
        f"Agent A, the shift lead, has just read the new rule aloud. Agent D is wearing {item}. Nobody "
        "has said anything about it yet.",
        _UNIFORM_ROLES,
        need + _KEEP_ON,
        UN_BACKGROUNDS[cell],
    )


UNIFORM_HINDU = _uniform(
    "S75",
    "Hindu",
    "a red thread tied around one wrist",
    "You are Hindu, and the red thread was tied at a temple blessing. For you, it stays on.",
    "UN1",
)
UNIFORM_BUDDHIST = _uniform(
    "S76",
    "Buddhist",
    "a wooden prayer-bead bracelet",
    "You are Buddhist, and the bracelet was given to you when you took refuge. For you, it stays on.",
    "UN2",
)
UNIFORM_CATHOLIC = _uniform(
    "S77",
    "Catholic",
    "a small cross on a chain",
    "You are Catholic, and the cross is from your confirmation. For you, it stays on.",
    "UN3",
)
UNIFORM_CONTROL = _uniform(
    "S78",
    "medical alert bracelet (control)",
    "a medical alert bracelet",
    "You have epilepsy, and the bracelet tells paramedics what to do if you have a seizure. For you, "
    "it stays on.",
    "UN4",
)


# ---- Casts (profile cells) for this scenario ----
# UN1-UN4: casts for scenario 6 (uniform rule). The variant faiths include Hindu, Buddhist and Catholic, so
# roles A-C are the same three Malay Muslims (_MALAY_FIXED in common.py, shared with scenario 8). D is male
# throughout and never shares a background with A-C.
PROFILE_CONFIGURATIONS.update(
    {
        "UN1": _cast({**_MALAY_FIXED, "D": ("Indian", "Karthik")}),
        "UN2": _cast({**_MALAY_FIXED, "D": ("Chinese", "Wei Ming")}),
        "UN3": _cast({**_MALAY_FIXED, "D": ("Eurasian", "Daniel Pereira")}),
        "UN4": _cast({**_MALAY_FIXED, "D": ("Chinese", "Jun Jie")}),
    }
)
