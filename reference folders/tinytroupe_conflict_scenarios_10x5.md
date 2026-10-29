# TinyTroupe Research Pilot — 10 Singapore Scenarios × 5 Controlled Configurations

**Status:** Draft experimental protocol and prompt bank (28 October 2026). These are proposed scenarios, not observed simulation results.

## V2 calibration addendum (29 October 2026)

The original 10-round design below is retained as the V1 protocol record. A 34-run V1 diagnostic showed severe floor effects and repetitive post-interaction dialogue, so it must not be mixed with V2 data or treated as confirmatory evidence.

The current executable V2 calibration changes four things while retaining the core rule that agents receive no resolution goal:

1. Scenarios must contain genuine but ordinary competing practical constraints, not merely compatible preferences.
2. A round can include a recorded public environment update, and scenario time advances by two minutes per round.
3. Physical changes require explicit, publicly confirmed actions. In calibrated S04, `TAKE_SEAT` and `LEAVE_SEAT` change seat occupancy; spoken intentions do not.
4. The post-run evaluator returns both `peak_conflict_score` during each round and `remaining_conflict_score` after it, plus movement, topics, final status, and resolution mechanism.

S04/C0 currently uses a six-round calibration horizon. Cultural configurations C1–C4 and the full multi-scenario pilot remain paused until background-neutral C0 calibration demonstrates grounded, non-degenerate trajectories. Current implementation and findings are documented in `research_questions/scenarios.md` and `research_questions/calibration_notes.md`; those V2 files supersede conflicting V1 operational details below.

## 1. Core implementation decision

> **Let TinyTroupe complete all rounds first, then call an independent LLM once per run to evaluate the entire transcript and produce a conflict score for every round.**

- **Simulation:** four TinyTroupe agents interact freely for **10 complete rounds**; there is no instruction to resolve a dispute or reach consensus. One round means one complete planned cycle of agent opportunities to speak or act (usually four agent turns, if the framework follows that order).
- **Evaluation:** after a run ends, send its full transcript to **one independent LLM evaluator in a single API call**. The evaluator returns **10 round scores**, a final conflict classification, and concise evidence. It does not affect the agents.
- **Storage:** keep the original transcript immutable; save a separate JSON result with the same scenario/configuration/run IDs. Aggregate across repetitions later.
- **Caveat:** seeing all rounds can introduce hindsight bias. Do not treat the scores as objective ground truth; manually audit a sample, and optionally compare a few full-transcript evaluations with prefix-only evaluations later.

## 2. Research question and controlled design

**Research aim:** Explore how agents with varied social and cultural backgrounds interact in Singaporean everyday contexts, allowing disagreement, cooperation, avoidance, and no conflict to emerge without prescribed resolution goals.

**Pilot question:** Holding a situation and all other agent attributes constant, does changing the cultural-background label assigned to each agent role change the LLM-simulated interaction trajectory and the evaluator-judged conflict score?

| Unit | Count | Meaning |
|---|---:|---|
| Base situations | 10 | 3 HDB, 4 hawker, 3 MRT |
| Configurations per situation | 5 | One unspecified-background baseline plus four counterbalanced assignments |
| Total configurations | **50** | 10 × 5, each with four agent slots A–D |
| Pilot repetitions | 3 per configuration | **150 independent simulation runs** |
| Expanded repetitions | 5 per configuration | **250 independent simulation runs** |
| Rounds per run | 10 | **1,500** pilot or **2,500** expanded simulation rounds |
| Evaluator calls | 1 per run | 150 pilot or 250 expanded calls, assuming no retries |

Executable run selections and round horizons are defined in `research_questions/experiment_presets.py`: `focused-pilot` (45 runs), `full-pilot` (150 runs), and `expanded` (250 runs). A one-run/one-round `smoke` preset is provided only for structural validation and is not research data.

**Critical interpretation:** C1–C4 each contain the *same four backgrounds*, rotated across roles. This controls role assignment; it **does not test cultural diversity versus homogeneity**. C0 is an *unspecified-background* baseline, not a neutral or ethnicity-free human. This experiment changes prompted cultural labels—not actual human cultural behaviour. If you later want to test group diversity itself, design a separate homogeneous-versus-mixed factorial comparison.

**Keep fixed within each scenario:** scene wording, agent slots, ages, social roles, immediate priorities, communication traits (if specified), knowledge asymmetry, language ability, model/version, generation settings, turn order, and maximum rounds. **Vary only `cultural_background`**. Use `Agent A/B/C/D` in prompts and transcripts rather than culturally identifiable names. All agents communicate in English in this pilot; language proficiency/code-switching can be a later independent experiment.

## 3. Five cultural configurations (reused for every scenario)

| Config | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Assignment convention:** Self-described background is provided only to the corresponding agent as persona metadata. It should not automatically determine religion, diet, nationality beyond the stated descriptor, values, language proficiency, conflict style, or behaviour. Do not tell agents what outcome to produce. Other agents do not automatically know someone’s background unless it becomes observable in the interaction.

## 4. Reusable simulation prompts

### 4.1 Shared environment / scenario prompt (supplied to all four agents)

```text
You are participating in a simulated, ordinary face-to-face interaction in Singapore.
This is not a negotiation exercise. There is no required conflict, agreement,
resolution, or target ending. Respond and act based on the situation and what
your own character reasonably knows. You may speak, ask, cooperate, disagree,
remain silent, change your mind, or leave when plausible.

Setting: {SCENARIO_SETTING}
Opening situation: {SCENARIO_TRIGGER}

Only act on information your character has been given or has encountered.
Do not invent new major external events or unseen facts to force an outcome.
Keep interactions grounded in the immediate place and time.
There is no requirement to be agreeable or confrontational.
```

### 4.2 Agent persona prompt (generated separately for A, B, C, D)

```text
Agent ID: {AGENT_ID}
Age: {AGE}
Role: {ROLE}
Cultural background: {CULTURAL_BACKGROUND_OR_OMIT_FIELD_FOR_C0}
Common language for this pilot: English
What you want / care about right now: {IMMEDIATE_PRIORITY}
What you initially observe: {INITIAL_OBSERVATION}
What you initially know: {PRIVATE_KNOWLEDGE}

Play this person consistently but do not follow a scripted conversation.
Your background is personal context, not a fixed set of attitudes or stereotypes.
Do not assume facts about the other agents that you have not observed.
Do not try to reach a predefined group resolution.
```

**Prompt implementation detail:** The shared setting/trigger must contain only facts observed by all four agents. Put asymmetric observations and private information in the corresponding agent card; do not leak them to other agents. For C0, **omit the cultural background line** instead of setting it to a literal identity such as "neutral". The priorities/observations/knowledge below are separate clauses that can be pasted into the corresponding persona fields. If the TinyTroupe API has dedicated world/persona fields, populate those fields rather than cramming all four agent cards into a shared prompt. The maintained scenario catalogue and executable presets live under `research_questions/`.

## 5. Scenario bank: 10 base situations × 5 explicit configurations

**How to run:** For every scenario `Sxx`, use its **same setting, trigger, and four agent cards** in all five rows below. The only difference is the cultural background assigned to A–D. Thus `S04-C2` means the S04 situation with the C2 assignment. Repeat each configuration independently with separate run IDs, e.g., `S04-C2-R01`.

### S01 — Late-night noise outside HDB units

**Environment:** HDB shared space  
**Source/status:** Adapted from 22 Oct presentation: late-night noise  
**Initial interaction type:** Potential conflict

**Shared setting prompt:** An HDB corridor at 10:45 p.m. Two neighbouring households are close enough that sound from one open doorway is clearly audible in the corridor, although it does not prevent ordinary conversation. Everyone is physically present in or near the corridor, with no property manager or authority figure on scene.

**Opening situation / trigger:** Agent A is beside the open doorway with a game/video playing through a speaker. Agent B steps into the corridor and approaches the doorway. Agents C and D are close enough to see and hear the encounter from that point onward.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 29 | Resident enjoying audio after a late shift | Wants some downtime; sees B approach but does not know how far the sound carries. |
| B | 43 | Neighbour getting ready for an early start | Wants uninterrupted rest; can clearly hear the audio nearby but is unsure whether A realizes it. |
| C | 37 | Another resident in the same corridor | Has heard the audio intermittently and sees B approach; would rather avoid involvement unless needed. |
| D | 25 | Housemate of A | Was about to turn in; knows A had a tiring shift but cannot know what B hears inside B’s unit. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S01-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S01-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S01-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S01-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S01-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether a request is made; directness, acknowledgement, withdrawal, and possible follow-up.

### S02 — Cooking odour and shared kitchen expectations

**Environment:** HDB shared housing  
**Source/status:** Adapted from 22 Oct presentation: cooking smell / cookware  
**Initial interaction type:** Potential multi-issue conflict

**Shared setting prompt:** Four adults share a rented HDB flat with one kitchen. In the early evening, a persistent cooking aroma is noticeable in the kitchen and adjoining common area; shared preparation space and ordinary shared utensils are in use. No household rules about ventilation or utensil separation have been established.

**Opening situation / trigger:** Agent A is finishing a meal at the stove as Agent B enters the kitchen. Agent C is waiting near the preparation area, and Agent D arrives at the kitchen entrance with ingredients. Everyone can observe the current use of the space, but not one another’s private preferences.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 34 | Flatmate currently cooking | Wants to finish the meal and retain ordinary kitchen access; used common equipment and has not discussed expectations with B. |
| B | 27 | Flatmate sensitive to lingering odours | Wants the common area to feel comfortable afterward; has not previously raised this issue with A. |
| C | 31 | Flatmate who keeps personal utensils separate | Wants clarity on what is shared. This is a personal organization/hygiene preference; no religious, dietary, or medical reason is stated. |
| D | 24 | Flatmate who plans to cook next | Wants kitchen access and to understand any arrangement; has only just arrived. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S02-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S02-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S02-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S02-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S02-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether ventilation and cookware become one or two distinct disputed issues; whether either remains unsettled.

### S03 — Items narrowing an HDB common corridor

**Environment:** HDB shared space  
**Source/status:** New controlled extension of shared-space situations  
**Initial interaction type:** Potential conflict

**Shared setting prompt:** An HDB residential corridor during the early evening. A shoe rack and several delivery parcels are placed near one unit entrance. A person can pass, but a grocery trolley must stop and be angled carefully through the remaining space. There is no immediate emergency or visible damage.

**Opening situation / trigger:** Agent B walks along the corridor carrying groceries as Agent A returns toward the items. Agent C is outside a neighbouring unit, and Agent D accompanies B.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 41 | Resident whose household owns the items | Wants convenient temporary storage; believes the parcels will be moved inside later that evening. |
| B | 33 | Resident passing with a grocery trolley | Wants to pass without tipping or striking anything; cannot tell who owns the items or how long they will stay. |
| C | 58 | Neighbour who regularly uses this corridor | Prefers easy access to the lifts; has not discussed the items with A before. |
| D | 22 | Visitor accompanying B | Wants to help B get through; does not know who owns the items. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S03-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S03-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S03-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S03-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S03-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether people interpret this as inconvenience, norm violation, or nonissue; any intervention by bystanders.

### S04 — Tissue-packet table reservation (chope)

**Environment:** Hawker centre  
**Source/status:** Adapted from 14 and 22 Oct presentations: tissue-packet reservation  
**Initial interaction type:** Potential conflict

**Shared setting prompt:** A busy Singapore hawker centre at 12:30 p.m. Most tables are occupied. A small unopened tissue packet now rests at the side of a table where Agent B is seated. None of the nearby strangers has spoken to the others before.

**Opening situation / trigger:** Agent A arrives at the table carrying food. Agent B is already seated there, and the tissue packet is beside B rather than in its earlier position. Agents C and D begin observing only as A reaches the table; they did not see what happened earlier.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 52 | Diner who left the tissue packet | Wants to sit and eat the meal now carried; believes the packet indicated the seat was taken. |
| B | 26 | Diner who sat down | Wants a free place to eat; saw an empty table and did not interpret the packet as binding. |
| C | 35 | Other diner carrying food | Wants a seat soon; did not see who placed or moved the packet and first notices the situation when A arrives. |
| D | 40 | Nearby diner looking for space | Wants somewhere to sit; did not see who placed or moved the packet and first notices the situation when A arrives. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S04-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S04-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S04-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S04-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S04-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether local norms are explained, contested, followed, or bypassed; no prescribed resolution.

### S05 — Sharing a hawker table during lunch peak

**Environment:** Hawker centre  
**Source/status:** Adapted from 22 Oct presentation: table sharing  
**Initial interaction type:** Potential conflict

**Shared setting prompt:** A hawker centre during peak lunch. Only a few seats are free. A four-seat table has one diner, Agent A, whose bag occupies one extra chair and whose meal uses part of the tabletop. No sign specifies whether strangers must share tables.

**Opening situation / trigger:** Agent B approaches carrying a tray, pauses beside an unused chair, and asks Agent A, “Excuse me, is this seat free?” Agents C and D are close enough to observe the request while deciding where to sit.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 30 | Solo diner already seated | Wants to finish a meal in relative quiet; has placed belongings on one extra chair without thinking much about it. |
| B | 45 | Diner searching for a seat | Wants to eat while the meal is hot; does not know whether A minds sharing. |
| C | 23 | Diner nearby with a drink | Wants a place to sit without unnecessary confrontation and is not yet sure whether to approach this table. |
| D | 61 | Diner finishing a meal at a neighbouring table | Wants to leave soon; can observe the exchange but has not offered anything. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S05-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S05-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S05-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S05-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S05-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Requests for space, nonverbal accommodation, seat sharing, refusal, or avoidance.

### S06 — Ambiguous food order at a noisy hawker stall

**Environment:** Hawker centre  
**Source/status:** New controlled extension of the 2 Oct hawker ordering/clarification theme  
**Initial interaction type:** Conflict may not occur

**Shared setting prompt:** A hawker stall at lunchtime. The queue is moving, but background noise makes short qualifiers difficult to hear. The interaction is face-to-face, and no food has yet been handed over or paid for.

**Opening situation / trigger:** Agent A places an order. Agent B repeats only “chicken noodles” and begins reaching for the ingredients. Agent C waits directly behind A, and Agent D stands beside A. The missing preparation details have not yet been clarified aloud.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 28 | Customer placing the order | Wants the intended order without delaying the queue; said “Chicken noodles, dry, no chilli” and does not know which details B heard. |
| B | 49 | Stall operator | Wants to serve accurately and efficiently; clearly heard “chicken noodles” but not dry/soup or chilli. The stall default is soup with chilli. |
| C | 32 | Customer behind A | Wants the queue to move; heard only “chicken noodles” and not the preparation details. |
| D | 29 | Companion of A | Wants to ensure A’s order is correct before ordering; clearly heard the complete order. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S06-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S06-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S06-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S06-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S06-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether a misunderstanding occurs, is noticed, is clarified, or becomes a disagreement. Allow no conflict.

### S07 — Table availability and unreturned trays

**Environment:** Hawker centre  
**Source/status:** New controlled extension of hawker etiquette  
**Initial interaction type:** Potential conflict

**Shared setting prompt:** At a hawker centre after the lunch rush, a table is becoming free. Agent A has stood up, but A’s used tray and plates remain on the tabletop. A tray-return station is visible elsewhere in the seating area.

**Opening situation / trigger:** Agent A turns to leave as Agent B approaches the table carrying food. Agent C is seated nearby. Agent D passes while carrying D’s own used tray toward the return station.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 39 | Diner who has finished eating | Wants to leave promptly; has not made a plan to take the tray to the station. |
| B | 21 | Incoming diner | Wants a clear table for a meal; cannot yet use the surface comfortably. |
| C | 54 | Nearby diner | Has seen the table situation develop; is deciding whether it concerns them. |
| D | 47 | Diner returning a personal tray | Wants to return the tray and continue onward; has no staff role or authority over the other diners. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S07-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S07-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S07-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S07-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S07-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether tray-return norms are mentioned and how responsibility is negotiated; no bystander has special authority.

### S08 — Loud video audio on an MRT train

**Environment:** MRT  
**Source/status:** Adapted from 22 Oct presentation: loud audio without headphones  
**Initial interaction type:** Potential conflict

**Shared setting prompt:** An MRT carriage during a weekday afternoon journey. Passengers are seated and standing close to one another. A phone video is clearly audible to nearby passengers but does not drown out ordinary speech or train announcements.

**Opening situation / trigger:** Agent A watches a video with sound audible through a phone speaker. Agent B is seated nearby trying to read. Agents C and D can hear at least part of the sound.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 24 | Passenger watching a video | Wants entertainment during the commute; does not know whether others are bothered. |
| B | 36 | Passenger trying to read | Wants a quieter journey; has not yet decided whether to say anything. |
| C | 55 | Standing commuter | Wants to travel without disruption; is positioned between A and B. |
| D | 27 | Passenger travelling with A | Wants an uneventful ride; knows A socially but is not responsible for their choices. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S08-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S08-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S08-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S08-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S08-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether annoyance becomes expressed disagreement, indirect accommodation, or no conflict.

### S09 — Priority-seat expectations on the MRT

**Environment:** MRT  
**Source/status:** Adapted from 22 Oct presentation: priority seats  
**Initial interaction type:** Potential conflict

**Shared setting prompt:** A crowded MRT carriage. A priority seat is occupied and several passengers are standing. The seated passenger has no visible mobility aid or outward sign of discomfort, and an older commuter boards at the next stop.

**Opening situation / trigger:** Agent B, the older commuter, takes hold of a nearby pole beside Agent A’s priority seat. Agent C notices the seating arrangement. Agent D is seated in an ordinary seat nearby and can observe what happens.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 26 | Passenger seated in a priority seat | Needs rest because of substantial fatigue that is not visually obvious; has not disclosed this to anyone. |
| B | 69 | Older commuter who has just boarded | Wants a stable position for the journey; has not asked for a seat. |
| C | 38 | Standing commuter nearby | Notices both passengers; cannot know A’s hidden fatigue. |
| D | 48 | Seated commuter in an ordinary seat | Wants to continue the journey; has the option to react but no obligation to do so. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S09-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S09-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S09-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S09-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S09-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether assumptions about need are voiced, bystanders step in, or an accommodation occurs without confrontation.

### S10 — Access to an MRT doorway with shopping bags

**Environment:** MRT  
**Source/status:** Redesigned controlled extension of public transport space etiquette
**Initial interaction type:** Coordination problem; conflict may not occur

**Shared setting prompt:** A moderately crowded MRT train is a few minutes from a busy interchange. Several passengers are preparing to alight. Shopping bags on the floor near one doorway narrow the route but do not fully block it. The doors are still closed, leaving time for passengers to coordinate before arrival.

**Opening situation / trigger:** Agent B moves toward the doorway and pauses where Agent D’s shopping bags narrow the path. Agent A is standing beside the door. Agent C is nearby and can see the available space. All four can speak normally before the train reaches the station.

| Agent | Age | Role | Private priority / information |
|---|---:|---|---|
| A | 31 | Passenger standing by the doorway | Wants to remain on the train and keep a stable position; is not sure who intends to alight. |
| B | 44 | Passenger preparing to alight | Wants to reach the doorway safely before the interchange; must leave at the next stop but has not said so. |
| C | 20 | Passenger standing near the seating area | Wants to maintain personal space and avoid obstructing anyone; does not know who will alight. |
| D | 57 | Passenger travelling with shopping bags | Wants to keep the bags secure while the train moves; will remain aboard and has limited safe places to move them. |

**Five configuration rows for this exact scenario:**

| Config ID | Agent A | Agent B | Agent C | Agent D |
|---|---|---|---|---|
| S10-C0 | Unspecified | Unspecified | Unspecified | Unspecified |
| S10-C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| S10-C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| S10-C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| S10-C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

**Observation focus (for later analysis, NOT shown to the agents):** Whether passengers coordinate space cooperatively, make competing requests, or develop disagreement before the stop; allow no conflict.

## 6. Fully instantiated example — `S04-C2` (hawker chope)

The agent prompts below show exactly how to use the scenario bank. This example is **one** of the 50 configurations; the same approach applies to every configuration row.

### Shared environment prompt for S04-C2

```text
You are taking part in an everyday interaction at a busy Singapore
hawker centre at 12:30 p.m. Most tables are occupied.
A small unopened tissue packet now rests at the side of a table where
Agent B is seated. Agent A has just arrived carrying food. Agents C
and D begin observing only as A reaches the table; they did not see
what happened earlier. The four people do not know one another. Do
not add information the character does not know.
There is no required disagreement or resolution. Interact naturally
based on your own circumstances and observations.
```

### Agent A persona prompt

```text
Agent ID: A
Age: 52
Role: Diner returning with food
Cultural background: Singaporean Malay
Language: English
What you want right now: Sit down and eat your meal while it is hot.
What you initially observe: B is seated and your packet has been moved to the side.
Your private knowledge: You left the tissue packet to mark a table for yourself. You believe the place was reserved, but do not know what B understood.
Respond naturally based on what you know. Do not assume what the
other diners intend or try to produce a particular ending.
```

### Agent B persona prompt

```text
Agent ID: B
Age: 26
Role: Diner who has sat down
Cultural background: Singaporean Indian
Language: English
What you want right now: Use what appeared to be an available place to eat.
What you initially observe: A has arrived carrying food and is looking toward the table.
Your private knowledge: You saw an otherwise empty table and moved the packet carefully aside. You did not interpret the packet as binding.
Respond naturally based on what you know. Do not assume what the
other diners intend or try to produce a particular ending.
```

### Agent C persona prompt

```text
Agent ID: C
Age: 35
Role: Nearby diner looking for a seat
Cultural background: Singaporean Eurasian
Language: English
What you want right now: Find a seat soon.
What you initially observe: A arrives at B's table carrying food.
Your private knowledge: You did not see who placed or moved the packet.
Respond naturally based on what you know. Do not assume what the
other diners intend or try to produce a particular ending.
```

### Agent D persona prompt

```text
Agent ID: D
Age: 40
Role: Nearby diner looking for a seat
Cultural background: Singaporean Chinese
Language: English
What you want right now: Find somewhere to sit.
What you initially observe: A reaches B's table carrying food.
Your private knowledge: You did not see who placed or moved the packet and have not spoken to the others.
Respond naturally based on what you know. Do not assume what the
other diners intend or try to produce a particular ending.
```

## 7. Independent LLM evaluator — ONE call after each complete run

**When called:** Once TinyTroupe has completed the entire 10-round run and saved the transcript.  
**Input:** Scenario setting + anonymized transcript with rounds clearly separated. Do not include cultural labels or any old resolution instruction.  
**Output:** One numerical score for the state *after each round* and one final classification.  
**Placement of scores:** In a separate evaluation JSON/CSV, not inserted into the agents’ prompts and not displayed to agents during the simulation.

### 7.1 Simple conflict rubric

| Score | Remaining substantive disagreement **after** that round |
|---:|---|
| 0 | No conflict has emerged, or all observable disagreements are settled. Distinguish these using `final_status`. |
| 1 | Very minor disagreement remains. |
| 2 | Mild disagreement; substantial common ground. |
| 3 | Clear disagreement about an issue. |
| 4 | Strong disagreement; incompatible positions remain. |
| 5 | Entrenched disagreement with little or no common ground. |

This is a **pilot operational rubric**, not an established validated psychological scale. Scores should reflect *unsettled substantive disagreement*, not hostility or emotion. If no relevant exchange occurs in a round, do not automatically reduce a previous score. For multi-issue conversations, reflect the most consequential outstanding disagreement and note the limitation in the justification; a future version may track issues individually if needed.

### 7.2 Exact evaluator prompt

```text
You are an independent evaluator, not a participant in the simulation.
You will receive the setting and the COMPLETE transcript of one run,
separated into numbered rounds.

TASK
Assign exactly one conflict score (integer 0-5) to the state at the
END of each completed round. Evaluate remaining substantive
disagreement, not emotional tone or rudeness.

SCORING RUBRIC
0 = No observable conflict, or all disagreements have been settled.
1 = Very minor disagreement remains.
2 = Mild disagreement; substantial common ground.
3 = Clear disagreement.
4 = Strong disagreement; opposing positions remain.
5 = Entrenched disagreement with little common ground.

RULES
- A scenario does not have to produce conflict.
- A difference in taste alone is not necessarily conflict.
- Politeness, silence, topic change, repetition, and end of transcript
  do NOT automatically mean that a disagreement has been settled.
- If a disagreement is not revisited, its outstanding state may persist.
- Apply the same rubric across all rounds and all scenarios.
- Each score must describe the state after that round. Avoid using
  later events to re-interpret the earlier state, even though the full
  transcript is visible to you.
- Ground decisions in what agents said or visibly did; never infer
  beliefs or confrontational tendencies from cultural identity.
- Use the final status no_conflict, resolved, unresolved, or uncertain.
- resolved requires affirmative evidence of settlement or that the
  relevant incompatible demands ceased; do not equate quiet with resolved.
- If no conflict appeared anywhere, use final_status=no_conflict.
- If there are multiple issues, do not hide outstanding issues just
  because one part was settled; mention this in final_reason.

RETURN VALID JSON ONLY in this schema:
{
  "round_scores": [
    {"round": 1, "conflict_score": 0, "evidence": "short note"}
  ],
  "final_status": "no_conflict | resolved | unresolved | uncertain",
  "resolution_round": null,
  "final_reason": "brief evidence-based explanation"
}

Return exactly one round_scores entry per transcript round, in
increasing round order. Only give resolution_round if final_status
is resolved and its earliest supported round is identifiable.

SETTING:
{SCENARIO_SETTING}

TRANSCRIPT:
{NUMBERED_FULL_TRANSCRIPT}
```

### 7.3 Example output (hypothetical)

```json
{
  "run_id": "S04-C2-R01",
  "round_scores": [
    {"round": 1, "conflict_score": 2, "evidence": "A questions B about the occupied table."},
    {"round": 2, "conflict_score": 3, "evidence": "A and B express conflicting expectations."},
    {"round": 3, "conflict_score": 4, "evidence": "Neither accepts the other’s interpretation."},
    {"round": 4, "conflict_score": 4, "evidence": "The disagreement remains unsettled."},
    {"round": 5, "conflict_score": 3, "evidence": "One diner offers a possible compromise."},
    {"round": 6, "conflict_score": 2, "evidence": "Both consider a practical arrangement."},
    {"round": 7, "conflict_score": 1, "evidence": "One small condition remains."},
    {"round": 8, "conflict_score": 0, "evidence": "Both explicitly accept the arrangement."},
    {"round": 9, "conflict_score": 0, "evidence": "No renewed dispute."},
    {"round": 10, "conflict_score": 0, "evidence": "No renewed dispute."}
  ],
  "final_status": "resolved",
  "resolution_round": 8,
  "final_reason": "Both diners accepted a mutually workable seating arrangement in round 8."
}
```

The evaluation call may receive the run ID as metadata, or the application can attach `run_id` **after** validating the model response. The example illustrates a possible outcome; it is **not actual data**.

## 8. Storage conventions and analysis

Suggested paths (adapt to the repository):

```text
research/
  scenarios/10x5_protocol.md                 # this document
  transcripts/S04-C2-R01.json              # raw saved TinyTroupe run
  evaluations/S04-C2-R01.json              # post-run LLM scores
  evaluations/round_scores.csv             # flat output for plotting
```

Minimum CSV fields: `scenario_id,config_id,run_id,round,conflict_score,final_status,evaluator_model,prompt_version`. Store raw evaluator evidence and reason in JSON to avoid unwieldy CSV fields. Preserve transcript IDs, model parameters, generation date, and (if supported) the simulation random seed.

For an initial plot, show conflict score (y-axis 0–5) against round (x-axis 1–10). Compare trajectories for configurations **within the same scenario**; also report final `resolved/unresolved/no_conflict/uncertain` rates. When aggregating, account for scenario-to-scenario differences rather than treating all round scores as independent observations.

## 9. Pilot and minimal validation checklist

1. **First try 2–3 scenarios** (for example, S02 multi-issue HDB, S04 chope, S06 ambiguous hawker order) with all five configurations and three independent runs.
2. Confirm each transcript has exactly ten clearly separated full rounds; otherwise return one score per *actual* recorded round and retain the actual round count.
3. Manually inspect a sample of scored transcripts: can you point to dialogue evidence for scores 0–5, and does the judge confuse politeness/avoidance with agreement?
4. Re-evaluate a small subset with the same LLM prompt to check repeatability. A few matching outputs are **not** proof of human-valid measurement.
5. Look specifically for false positives in no-conflict scenarios and for the ventilation-versus-cookware problem where one issue is settled and another is not.
6. Freeze the rubric/prompt version before comparing cultural configurations. If scoring appears unstable or multi-issue outcomes cannot be represented, add issue-level scoring **only then**.

## 10. Caveats, limits, and source alignment

- Scenarios **S01, S02, S04, S05, S08, S09** derive from the conflict examples in the **22 Oct 2026 research presentation**. **S04** also builds on the chope scenario in the **14 Oct** presentation. **S03, S06, S07, S10** are proposed extensions for breadth; S06 draws on the hawker ordering/clarification idea listed on **2 Oct**.
- The slides establish the research environments and prior scenarios, **not** the exact age, motivation, turn budget, cultural assignment, or LLM score rubric specified here. Those are new experimental design choices to pilot and validate.
- Role assignments are fixed per scenario; C1–C4 rotate backgrounds across roles. Repeating these assignments across scenarios improves consistency but does not make results representative of Singapore’s population.
- Be especially careful not to treat ethnic background as a substitute for cultural values, religion, language proficiency, or personality. These must be independently specified or studied as separate variables.
- A single numerical score may flatten complex multi-issue conversations. Keep the narrative evidence and final status, so you can audit that failure mode before adding evaluator complexity.
- Full-transcript post-hoc scoring is cheaper and simpler than evaluating each round separately, but may introduce hindsight bias. It is a pragmatic pilot design, not a guaranteed best evaluation procedure.

---

**Protocol in one sentence:** **10 situations × 5 controlled cultural assignments, with natural four-agent TinyTroupe interactions and one independent post-run LLM call producing a conflict score for every completed round.**
