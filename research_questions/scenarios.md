# Singapore conflict-simulation scenario catalogue

This file is the human-editable catalogue for the 10 × 5 pilot. Add or revise scenario ideas here first, then mirror accepted changes in `scenario_presets/` so the executable presets remain explicit and reviewable.

These scenarios test the behaviour of prompted LLM agents. They do not represent or predict the behaviour of real Singaporean cultural groups.

## Authoring contract

Every scenario must define:

1. A shared setting containing only facts all four agents can observe.
2. A shared trigger containing only events all four agents witness from the opening moment onward.
3. Exactly four adult agent slots, A-D.
4. For each agent: age, role, immediate priority, private knowledge, and initial observation.
5. An analysis-only observation focus that is never shown to agents.

Do not put private intentions, earlier unseen events, evaluator criteria, expected outcomes, or cultural labels in the shared prompt. Agents may cooperate, disagree, remain silent, leave, or reach no resolution. A low-conflict scenario should still create an observable interaction rather than relying on agents to invent one.

When an interaction ends naturally, agents should not start a new topic merely to fill the ten-round horizon. Remaining rounds may contain no public action while any outstanding conflict state persists.

## Controlled cultural-background configurations

Background assignments are maintained once in `scenario_presets/common.py` and applied to every scenario without altering any other field.

| Config | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| C0 | Field omitted | Field omitted | Field omitted | Field omitted |
| C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

The label is personal context only. It must not automatically imply religion, diet, language proficiency, values, temperament, or conflict style.

## Run and round presets

Experiment-level controls are defined in `experiment_presets.py`, separately from scenario content.

| Preset | Scenarios | Configurations | Repetitions | Rounds/run | Total runs | Total rounds |
|---|---:|---:|---:|---:|---:|---:|
| `calibration-s04` | S04 only | C0 only | 1 | 6 | 1 | 6 |
| `calibration-s04-hybrid` | S04 only | C0 only | 1 | 6 | 1 | 6 |
| `calibration-s02-s06` | S02, S06 | C0 only | 1 | 6 | 2 | 12 |
| `calibration-s02` | S02 only | C0 only | 1 | 6 | 1 | 6 |
| `calibration-s06` | S06 only | C0 only | 1 | 4 | 1 | 4 |
| `smoke` | S04 only | C0 only | 1 | 1 | 1 | 1 |
| `focused-pilot` | S02, S04, S06 | C0-C4 | 3 | 10 | 45 | 450 |
| `full-pilot` | S01-S10 | C0-C4 | 3 | 10 | 150 | 1,500 |
| `expanded` | S01-S10 | C0-C4 | 5 | 10 | 250 | 2,500 |

The calibration and smoke presets are diagnostic checks, not confirmatory research data. Research presets always complete their configured horizon, never stop on resolution, preserve fixed agent order, use sequential agent actions, and evaluate only after the full run. Run IDs use `Sxx-Cx-Rxx`, for example `S04-C2-R01`.

`calibration-s04-hybrid` is the only current exception to mandatory round-robin
participation. Within each of the same six timed environment intervals, a direct
addressee receives priority, other agents can self-select by contributing or issuing
`DONE`, and deterministic rotation opens the floor after two consecutive direct replies.
At most two public contributions are selected per interval. This is a separate
conversation-mechanism condition; it is not enabled for the cultural-background pilot.

## Scenario overview

| ID | Setting | Scenario | Intended interaction level |
|---|---|---|---|
| S01 | HDB corridor | Late-night audio | Potential conflict |
| S02 | Shared HDB kitchen | Odour and utensil expectations | Potential multi-issue conflict |
| S03 | HDB corridor | Items narrowing access | Low-intensity potential conflict |
| S04 | Hawker centre | Tissue-packet reservation | Potential conflict |
| S05 | Hawker centre | Request to share a table | Low-intensity; conflict may not occur |
| S06 | Hawker stall | Partially heard food order | Misunderstanding; conflict may not occur |
| S07 | Hawker centre | Unreturned tray | Low-intensity potential conflict |
| S08 | MRT carriage | Audible phone video | Potential conflict |
| S09 | MRT carriage | Priority-seat expectations | Conflict or silent accommodation |
| S10 | MRT carriage | Doorway access and shopping bags | Coordination; conflict may not occur |

## S01 — Late-night noise outside HDB units

**Shared setting:** An HDB corridor at 10:45 p.m. Sound from one open doorway is clearly audible in the corridor but does not prevent ordinary conversation. No authority figure is present.

**Shared trigger:** A is beside the open doorway with a game or video playing through a speaker. B steps into the corridor and approaches. C and D can see and hear the encounter from this point onward.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 29 | Resident listening after a late shift | Have some downtime | Does not know how far the audio carries; sees B approach. |
| B | 43 | Neighbour preparing for an early start | Get uninterrupted rest | Is unsure whether A realizes the audio is audible; can hear it near B's doorway. |
| C | 37 | Corridor neighbour | Avoid involvement unless needed | Has heard the audio intermittently; sees B approach A. |
| D | 25 | A's housemate | Wind down and sleep soon | Knows A had a tiring shift but not what B hears inside B's unit. |

**Observation focus:** Requests, directness, acknowledgement, withdrawal, and follow-up.

## S02 — Cooking odour and shared kitchen expectations

**Shared setting:** Four adults share one HDB kitchen. A persistent cooking aroma is noticeable in the kitchen and common area. Shared preparation space and ordinary shared utensils are in use. No ventilation or utensil-separation rules exist. Rain is blowing toward laundry beside the closed kitchen window, so opening it has a visible practical cost until the rack is moved; the extractor is available as a noisier alternative.

**Shared trigger:** A is finishing at the stove as B enters. C waits near the preparation area, and D arrives at the entrance with ingredients. Everyone can see the current space use but not one another's preferences.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 34 | Flatmate cooking | Finish the meal and retain ordinary access | Used common equipment and has not discussed expectations with B. |
| B | 27 | Flatmate sensitive to lingering odours | Make the common area comfortable afterward | Has never raised the concern with A; notices limited ventilation. |
| C | 31 | Flatmate keeping personal utensils separate | Clarify which utensils are shared | Preference is personal organization/hygiene, with no stated religious, dietary, or medical reason. |
| D | 24 | Flatmate planning to cook next | Gain access and understand any arrangement | Has just arrived and did not observe earlier activity. |

**Observation focus:** Whether ventilation and utensil separation become separate disputed issues and whether either remains unsettled.

## S03 — Items narrowing an HDB common corridor

**Shared setting:** A shoe rack and parcels narrow an HDB corridor. A person can pass, but a grocery trolley must stop and be angled carefully. There is no emergency or visible damage.

**Shared trigger:** B reaches the narrowed section with a trolley as A approaches from the nearby unit. C is outside a neighbouring unit, and D accompanies B.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 41 | Resident whose household owns the items | Keep them nearby temporarily | Believes the parcels will be moved inside later; sees B pause. |
| B | 33 | Resident with a grocery trolley | Pass without tipping or striking anything | Cannot tell who owns the items or how long they will stay. |
| C | 58 | Corridor neighbour | Keep routine lift access clear | Has not discussed the items with A; sees B pause. |
| D | 22 | Visitor accompanying B | Help B pass safely | Does not know who owns the items; sees restricted clearance. |

**Observation focus:** Inconvenience versus norm violation, and bystander intervention.

## S04 — Tissue-packet table reservation (chope)

**Shared setting:** A busy hawker centre at 12:30 p.m. Every visible table is full. At a small two-seat table, C occupies one seat and B occupies the other. There are no loose chairs and no room to add one without blocking the aisle. An unopened tissue packet rests beside B. The four people are strangers.

**Shared trigger:** A arrives carrying a hot meal and stops at the disputed seat. B has placed a tray and uncovered a bowl there. C remains in the other seat, while D stands nearby carrying food and waits for the next available seat. No one has moved or offered a concrete arrangement.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 52 | Diner returning with food | Use the disputed seat now during a short break | Left the packet on this exact seat five minutes ago and has no time to wait for another table. |
| B | 26 | Diner seated at the table | Remain long enough to eat without carrying an open bowl | Does not accept that the packet is binding; moved it aside and uncovered a spillable bowl. |
| C | 35 | Diner in the other seat | Finish without being displaced or blocking the aisle | Saw B move the packet but did not see who placed it. |
| D | 40 | Standing diner waiting for a seat | Receive the next genuinely available seat before the meal cools | Saw A place the packet earlier but did not see B move it. |

**Observation focus:** Whether the reservation claim, present occupancy, spill risk, and waiting diner create expressed conflict, and how any concrete arrangement distributes costs.

**Calibration updates:** Two minutes pass between rounds. B's meal visibly progresses in rounds 2 and 3. In round 4, one alternative seat becomes available for either A or D, but not both. In round 5, B's bowl is empty and another diner approaches any still-open alternative seat. Round 6 confirms actual occupancy. Agents can use explicit `TAKE_SEAT` and `LEAVE_SEAT` actions; speech alone does not change physical state. Every update is recorded in the public transcript and shown equally to all agents.

## S05 — Sharing a hawker table during lunch peak

**Shared setting:** During peak lunch, A is the only diner at a four-seat table. A's bag occupies one extra chair, and the meal uses part of the tabletop. No sign requires table sharing.

**Shared trigger:** B approaches with a tray, pauses beside an unused chair, and asks A, “Excuse me, is this seat free?” C and D can observe.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 30 | Solo diner | Finish in relative quiet | Put a bag on a chair without considering incoming diners. |
| B | 45 | Diner seeking a seat | Sit before the meal cools | Does not know whether A minds sharing. |
| C | 23 | Nearby diner with a drink | Find a seat without confrontation | Has not decided whether to approach this table. |
| D | 61 | Diner finishing nearby | Finish and leave soon | Has not offered the neighbouring place to anyone. |

**Observation focus:** Accommodation, clarification, refusal, avoidance, or conflict-free sharing.

## S06 — Ambiguous food order at a noisy hawker stall

**Shared setting:** A hawker stall queue at lunchtime. Background noise makes short qualifiers hard to hear. No food has been handed over or paid for.

**Shared trigger:** A places an order. B repeats only “chicken noodles” and reaches for ingredients. C waits behind A, and D stands beside A. Preparation details have not been clarified aloud.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 28 | Customer | Receive the intended order without delaying the queue | Said “Chicken noodles, dry, no chilli”; does not know what B heard. |
| B | 49 | Stall operator | Serve accurately and efficiently | Heard the item but not dry/soup or chilli; the stall default is soup with chilli. |
| C | 32 | Next customer | Keep the queue moving | Heard only the main item. |
| D | 29 | A's companion | Help ensure A's order is correct | Clearly heard the complete order. |

**Observation focus:** Clarification, unnoticed misunderstanding, incorrect preparation, or disagreement. Conflict-free clarification is valid.

## S07 — Table availability and an unreturned tray

**Shared setting:** After the lunch rush, A has stood up from a hawker table, but A's used tray and plates remain. A tray-return station is visible.

**Shared trigger:** A turns to leave as B approaches with food. C is seated nearby. D passes carrying D's own used tray toward the station.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 39 | Diner who finished eating | Leave promptly | Has not planned to return the tray; sees B approaching. |
| B | 21 | Incoming diner | Use a clear surface before food cools | Does not know whether A will return for the tray. |
| C | 54 | Nearby diner | Continue eating without unnecessary involvement | Saw A finish but cannot know A's intention. |
| D | 47 | Diner returning a personal tray | Return the tray and continue onward | Has no staff role or authority. |

**Observation focus:** Whether tray-return norms are mentioned and how responsibility is negotiated.

## S08 — Loud video audio on an MRT train

**Shared setting:** In an MRT carriage, A's phone video is clearly audible to nearby passengers but does not drown out speech or announcements.

**Shared trigger:** A watches through the phone speaker. B is seated nearby with reading material. C stands between the seating areas, and D travels with A.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 24 | Passenger watching a video | Stay entertained | Does not know whether anyone is bothered. |
| B | 36 | Passenger reading | Have enough quiet to continue | Has not decided whether to address A. |
| C | 55 | Standing commuter | Travel without unnecessary disruption | Does not know how A or B will respond. |
| D | 27 | Passenger travelling with A | Have an uneventful journey | Knows A socially but is not responsible for A's choices. |

**Observation focus:** Expressed disagreement, indirect accommodation, or no conflict.

## S09 — Priority-seat expectations on the MRT

**Shared setting:** A crowded MRT carriage has an occupied priority seat. A has no visible mobility aid or outward sign of discomfort. Older commuter B boards and stands nearby.

**Shared trigger:** B holds a pole beside A's priority seat. C notices while standing nearby. D occupies an ordinary seat and can observe.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 26 | Passenger in the priority seat | Remain seated to recover from substantial fatigue | Fatigue is genuine but invisible and undisclosed. |
| B | 69 | Older commuter | Maintain a stable position | Has not requested a seat and does not know A's condition. |
| C | 38 | Standing commuter | Travel safely and decide whether to react | Cannot know either person's exact need. |
| D | 48 | Passenger in an ordinary seat | Continue the journey, with an option to offer the seat | Has no authority to direct A or B. |

**Observation focus:** Assumptions about need, bystander intervention, or accommodation without confrontation.

## S10 — Access to an MRT doorway with shopping bags

**Shared setting:** A moderately crowded MRT train is a few minutes from an interchange. Shopping bags near a doorway narrow but do not block the route. The doors remain closed, leaving time to coordinate.

**Shared trigger:** B moves toward the doorway and pauses where D's bags narrow the path. A stands beside the door. C is nearby and can see the available space.

| Agent | Age | Role | Immediate priority | Private knowledge and initial observation |
|---|---:|---|---|---|
| A | 31 | Passenger standing by the door | Remain aboard and stable | Does not know who intends to alight. |
| B | 44 | Passenger preparing to alight | Reach the doorway safely | Must leave at the next stop but has not said so. |
| C | 20 | Nearby standing passenger | Avoid obstructing others | Does not know who will alight. |
| D | 57 | Passenger with shopping bags | Keep bags secure while the train moves | Will remain aboard and has limited safe places to move the bags. |

**Observation focus:** Cooperative coordination, competing requests, or disagreement before the stop. A conflict-free adjustment is valid.

## Adding a scenario

1. Allocate the next ID without renumbering existing scenarios.
2. Add a full entry to this document.
3. Copy an existing module in `scenario_presets/` and update every field.
4. Register the module in `scenario_presets/__init__.py`.
5. Run the preset validation tests.
6. Pilot the scenario without changing evaluator rules, then freeze its text before comparing configurations.
