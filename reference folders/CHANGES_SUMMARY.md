# TinyTroupe Conflict-Pilot — Changes Applied and Suggestions for Richer Dialogue

This document has two parts:

- **Part A — Applied edits.** The exact changes already made to the repository, with before/after text, rationale, and expected effect.
- **Part B — Suggested edits.** A longer, creative list of further changes that would make the generated dialogue more valuable *without* scripting the agents or forcing a specific outcome.

The project's stated goal (from `scenarios.md` and `calibration_notes.md`) is to test whether adding a Singaporean cultural-background label (configurations C1–C4) changes how four LLM agents talk through everyday local friction scenes, compared with no-label C0. Every suggestion below is justified against that goal: it tries to **widen the space of possible conversations** rather than steer them toward a particular answer.

---

# Part A — Changes already applied

## A1. `AgentPreset.negotiation_boundary` default

**File:** `research_questions/scenario_presets/common.py`  
**Location:** inside the `@dataclass(frozen=True) class AgentPreset:` block.

### Before (original)

```python
negotiation_boundary: str = (
    "You may revise a position when its practical cost is addressed, but do not agree "
    "merely to end the conversation."
)
```

### After (applied)

```python
negotiation_boundary: str = (
    "Agree only when the other party has addressed the specific practical cost named in "
    "your immediate_priority. Polite framing, apology, or repetition do not count as "
    "addressing that cost."
)
```

### Why

The original let the model treat *any* "practical cost" as addressed — including vague cost. The new wording forces the model to check its *own* `immediate_priority` field for the specific thing that must be fixed before it concedes, and explicitly rules out apology/politeness as sufficient.

### Expected effect

Agent A no longer caves on turn 1 just because B apologises politely. A must now see B offer something that addresses A's actual stated cost (e.g. "I'll take the far end of the table so your laptop isn't jostled") before agreeing. This should widen the number of turns before resolution and allow partial concessions.

---

## A2. `AgentPreset.reconsideration_criteria` default

**File:** `research_questions/scenario_presets/common.py`  
**Location:** same dataclass, next field down.

### Before (original)

```python
reconsideration_criteria: str = (
    "Change or soften your position only when a new observed fact, a relevant reason, or "
    "a concrete proposal addresses the basis for it; politeness and repetition alone are "
    "not reasons to agree."
)
```

### After (applied)

```python
reconsideration_criteria: str = (
    "Change or soften your position only when a new observed fact, a relevant reason, or "
    "a concrete proposal addresses the basis for it; politeness and repetition alone are "
    "not reasons to agree. If no such fact, reason, or proposal has appeared yet, keep "
    "your position; you may still issue DONE instead of restating it."
)
```

### Why

The original gave only one exit from a turn — concede or restate — so the model would concede to avoid repeating itself. The appended sentence creates a third option: **stay silent via DONE without conceding**.

### Expected effect

Fewer "yeah I agree, let's move on" surrenders. Agents with nothing new to say can quietly DONE instead of fake-agreeing. Transcripts should show more unresolved-but-stable disagreement, which is actually a realistic outcome in Singaporean public-space friction.

---

## A3. S05 `shared_trigger` — tissue packet added

**File:** `research_questions/scenario_presets/s05_presets.py`

### Before (original)

```python
shared_trigger=(
    "Agent B approaches with a tray, pauses beside an unused chair, and asks Agent A, "
    "'Excuse me, is this seat free?' Agents C and D are close enough to observe the "
    "request while deciding where to sit."
),
```

### After (applied)

```python
shared_trigger=(
    "Agent B approaches with a tray, pauses beside the chair occupied by Agent A's bag, "
    "and asks Agent A, 'Excuse me, is this seat free?' A small packet of tissues lies on "
    "the tabletop in front of that chair. Agents C and D are close enough to observe the "
    "request while deciding where to sit."
),
```

### Why

Two problems with the original. (1) It said "unused chair" but A's bag was on it elsewhere in the scenario — a contradiction the model had to silently resolve. (2) There was no cultural signal, so C0 and C1–C4 had nothing to diverge on. The tissue packet is the real-world Singaporean "chope" marker; no agent is told what it means, so **the only way it enters the dialogue is through the cultural-background label**.

### Expected effect

The tissue packet becomes the single observable item that could discriminate C0 (no label → may ignore it) from C1–C4 (background assigned → may or may not recognise it). This is exactly where between-condition variance should show up if it exists.

---

## A4. S05 Agent A `immediate_priority` — concrete stake

**File:** `research_questions/scenario_presets/s05_presets.py`

### Before (original)

```python
"A": AgentPreset(
    age=30,
    role="Solo diner already seated",
    immediate_priority="Finish the meal in relative quiet.",
```

### After (applied)

```python
"A": AgentPreset(
    age=30,
    role="Solo diner already seated",
    immediate_priority=(
        "Finish the meal in relative quiet; the bag on the extra chair holds a "
        "laptop you would rather not have jostled."
    ),
```

### Why

The original gave A no concrete reason to resist. "Quiet" costs nothing to abandon — so A always said yes. "Laptop in the bag" gives A a specific, physical thing to protect, which `negotiation_boundary` can now anchor to.

### Expected effect

A should pause before clearing the chair and may propose "I'll move it to my lap" instead of "please take it, no problem." Resolution should still happen — the point is **how** it is reached, not **whether** it is reached.

---

## A5. S05 Agent B `immediate_priority` — concrete stake

**File:** `research_questions/scenario_presets/s05_presets.py`

### Before (original)

```python
"B": AgentPreset(
    age=45,
    role="Diner searching for a seat",
    immediate_priority="Sit down before the meal becomes cold.",
```

### After (applied)

```python
"B": AgentPreset(
    age=45,
    role="Diner searching for a seat",
    immediate_priority=(
        "Sit down before the meal becomes cold; your knees are sore and "
        "standing with a full tray is uncomfortable."
    ),
```

### Why

Same reasoning as A4 on the other side. The original let B walk away without cost. Sore knees + heavy tray mean B has a physical stake in not just backing off.

### Expected effect

B should push a little when A hesitates, instead of instantly saying "no problem, I'll find another seat." Both sides now have something to lose, which is what produces negotiation instead of mutual deference.

---

# Part B — Suggested further edits

The guiding principle: **enlarge the space of plausible things an agent might say**, don't shrink it. We want the LLM to talk, including in ways we didn't anticipate. Each suggestion below either removes an over-constraint, adds concrete stakes, or introduces ambiguity the agents can genuinely puzzle over.

---

## B1. Soften the "cultural background is personal context only" paragraph

**File:** `research_questions/prompts/tiny_person_conflict_pilot.mustache`  
**Location:** last paragraph of the `## Conflict-pilot constraints` section (near the end of the file, just before `## Persona`).

### Current text

> "Cultural background is personal context only. Never infer religion, diet, language ability, values, personality, conflict style, or behaviour from that label, and do not announce it without a situation-specific reason."

### Suggested text

> "Your cultural background is part of who you are and may shape what you notice first, which examples come to mind, and your tone. Let it influence your perspective naturally. Do not stereotype others or assume their background from how they speak, and do not announce your own background unless the situation calls for it."

### Why

The current wording tells the model to **suppress** cultural effects — which is precisely the variable the C0–C4 experiment is designed to measure. If the model is doing its job, C0 and C1–C4 transcripts should look identical under the current prompt, and the experiment has no signal.

This is the single most important suggested change, because without it the other changes below have less variance to work with. The new wording does not instruct the model to perform a stereotype; it allows background to colour attention and framing, which is how it works for real people.

### Why it still aligns with the project goal

The goal is to measure whether the label changes dialogue. If the prompt forbids the label from doing anything, the measurement is null by construction.

### Expected effect

C1–C4 transcripts should begin to diverge from C0 — for example, a Malay persona may notice the pork smell in S02 before anyone names it; an older Chinese persona may read the tissue packet in S05 as a reservation; an Indian persona may frame the lift-button scenario around waiting culture. **None of these are forced** — the model only draws on them when relevant.

---

## B2. Reframe DONE so silence is a real choice, not a last resort

**File:** `research_questions/prompts/tiny_person_conflict_pilot.mustache`  
**Location:** `#### Realistic behavior` section, under `## Additional actions instructions and constraints`.

### Current line

> "Emergency stop: if your next action would be unrealistic/repetitive/low-quality, issue DONE instead."

### Suggested addition (right after that line)

> "DONE is also appropriate when you have made your point, when the other party has not addressed your concern, when you want time to think, or when staying silent is in character. Silence is not surrender."

### Why

The current framing paints DONE as a failure mode ("emergency stop", "low-quality"). This nudges the model to speak even when staying silent would be more realistic — producing the "thank you / no problem / anytime" tail that dominates rounds 6–10 of existing transcripts.


### Expected effect

Shorter, more realistic turns. More unresolved endings (which are honest). Lower token cost. Allows C and D (bystanders) to genuinely stay out when they would in real life.

---

## B3. Give every scenario concrete stakes on both sides (not just S05)

**File:** every `research_questions/scenario_presets/s0X_presets.py` except S05 (already done).  
**Location:** `immediate_priority` field of agents A and B in each scenario.

### Pattern

For A and B (the two protagonists), rewrite `immediate_priority` so it names a **physical, time-bound, or financial cost** — not an abstract goal. Leave C and D alone; bystanders don't need stakes.

### Examples

| Scenario      | Agent                          | Weak original (illustrative) | Stronger rewrite                                                                           |
| ------------- | ------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------ |
| S02 kitchen   | A (resident with new cookware) | "Keep the kitchen clean."    | "Keep the kitchen clean; the new wok was a wedding gift and the coating scratches easily." |
| S02 kitchen   | B (new flatmate cooking curry) | "Cook dinner before class."  | "Cook dinner before class; you have a lab at 7pm and only one meal prepped."               |
| S04 void deck | A (resident annoyed by noise)  | "Have a quiet evening."      | "Have a quiet evening; you work a 6am shift and need to sleep by ten."                     |
| S04 void deck | B (teen with speaker)          | "Hang out with friends."     | "Hang out with friends; your mum made you leave the flat because your sister is studying." |
| S09 lift      | A (person holding door)        | "Wait for a friend."         | "Wait for a friend coming up from the carpark with heavy groceries."                       |
| S09 lift      | B (person in a hurry)          | "Catch a bus."               | "Catch the 8:12 bus; the next one is in 20 minutes and you have an interview at 9."        |

### Why

Without concrete stakes, "yes/no" has no price, so the model picks yes by default. With concrete stakes, concession costs something, which forces reasoning. Note that **neither side is told to resist** — they are just told what they stand to lose.

### Expected effect

The `negotiation_boundary` default (change A1) now has something to anchor to in every scenario, not just S05. Resolution still happens, but through genuine trade-offs rather than instant deference.

---

## B4. Add one ambiguous observable cue per scenario — don't explain it

**File:** every `research_questions/scenario_presets/s0X_presets.py`.  
**Location:** append one sentence to `shared_trigger`.

### Pattern

Add one neutral, observable detail that **different cultural backgrounds would plausibly interpret differently** — and give no agent any hint of what it means.

### Examples (one per scenario)

| Scenario           | Add to trigger                                                                       |
| ------------------ | ------------------------------------------------------------------------------------ |
| S01 (bus seat)     | "A small plastic bag with Chinese newspaper hangs on the seat's handrail."           |
| S02 (kitchen)      | "A jar of belacan is open on the stove and a pandan plant sits on the window ledge." |
| S03 (lift lobby)   | "A pair of shoes is lined up outside one of the unit doors on the landing."          |
| S04 (void deck)    | "A folded cardboard sign in Chinese characters leans against the chess table."       |
| S06 (hawker order) | "A styrofoam box labelled 'nasi padang' sits on the next table, lid half open."      |
| S07 (MRT)          | "A paper fan with faded Tamil script lies on the empty seat opposite."               |
| S08 (coffee shop)  | "A faded red-and-gold religious altar is mounted above the drinks counter."          |
| S09 (lift)         | "Someone has taped a Hari Raya greeting card to the inside of the lift."             |
| S10 (bus stop)     | "An elderly woman is folding yellow joss paper on the bench next to the queue."      |

### Why

These are everyday Singaporean sights, not plot devices. A model given a cultural background may notice them, name them, or ignore them — exactly the behaviour we are trying to measure. A model with no background (C0) is likely to ignore them. **The cue is not a puzzle to be solved**; it is simply a feature of the world the agents can engage with or not.

### Risks and mitigations

- **Risk:** cues might become too prominent and dominate the conversation. **Mitigation:** keep each cue to one short clause; do not refer to it again in `round_observations`.
- **Risk:** cues might read as stereotype prompts. **Mitigation:** choose cues that are genuinely ambiguous (a tissue packet could be a chope marker, or just napkins; a pandan plant could be for cooking, or just a plant). Avoid cues that have only one culturally coded meaning.

### Expected effect

Three possible outcomes, all informative:

1. All agents mention the cue → the cue is too loud; dial it back.
2. Only C1–C4 agents (sometimes) mention the cue → **this is the signal the experiment is looking for**.
3. No agent ever mentions the cue → B1 (loosen the suppression paragraph) is still blocking it.

---

## B5. Vary the agent order to break the A→B→C→D rhythm

**File:** `research_questions/experiment_presets.py`  
**Location:** either toggle `randomize_agent_order` on existing presets, or create a new calibration preset.

### Current state

Default is `randomize_agent_order: bool = False`, so A always speaks first every round.

### Suggested change

Set `randomize_agent_order=True` for at least one calibration preset so you can compare.

### Why

Fixed order creates a predictable rhythm: A opens, B responds, C and D fill. The model learns that pattern across turns and the conversation calcifies. Random order means C or D might open round 3, which forces B to react to something other than A for the first time.

### Why it still aligns with the project goal

Round-robin was presumably chosen for reproducibility, which matters for a confirmatory study. For **exploratory** runs trying to find out *whether the signal exists*, breaking the rhythm is more useful than reproducing it.

### Expected effect

More spontaneous moments. C and D stop being wallpaper. Reduces one source of fake-looking "and then C says..." bystander narration.

---

## B6. Shorten the round horizon to 5 (not 10)

**File:** `research_questions/experiment_presets.py`  
**Location:** `DEFAULT_ROUNDS_PER_RUN = 10`

### Suggested change

```python
DEFAULT_ROUNDS_PER_RUN = 5
```

### Why

Review of existing transcripts in `research_scenarios/results/hdb-space/` shows every scenario resolves by round 2 or 3, with rounds 4–10 filled by "thanks / sounds good / let's catch up next week" bureaucracy. Those extra rounds are:

- Statistically wasted (no new events, no variance).
- Expensive (each round is 4 agent calls).
- Actively misleading (they inflate "resolution_mechanism" scores by rewarding the model for being polite in a vacuum).

Five rounds matches the natural arc of these short public-space scenes.

### Expected effect

Halves cost per run. Removes filler. Lets you run 2× as many C0–C4 reps for the same budget — much more useful for a study comparing conditions.

---

## B7. Add a `rounds_remaining` hint to the mustache

**File:** `research_questions/prompts/tiny_person_conflict_pilot.mustache`  
**Location:** inside `### Temporal and spatial perception`, after the `location` line. Would require a small wiring change in `simulation.py` to pass the value.

### Suggested text

> "This interaction has roughly {{rounds_remaining}} turns left before people naturally move on. Don't rush, but also don't restate things you've already said."

### Why

Right now agents don't know whether they have one turn or ten left, so they pace by vibe — which produces either (a) immediate resolution followed by filler or (b) stretched-out politeness. Giving them a soft horizon lets them pace realistically. This is **information, not a command**: they can still DONE early or push late.

### Risk

Could cause meta-reasoning ("we only have 2 rounds left so I'll agree"). Mitigated by using a vague word like "roughly".

### Expected effect

Pacing becomes less bimodal. Variance in round-of-resolution becomes meaningful again.

---

## B8. Loosen the "do not invent major external events" clause — slightly

**File:** `research_questions/prompts/tiny_person_conflict_pilot.mustache`  
**Location:** `## Conflict-pilot constraints` section.

### Current line

> "Do not invent major external events, rules, diagnoses, motives, or unseen facts to force an outcome."

### Suggested replacement

> "Do not invent major external events or hidden rules that would force an outcome. You may draw on ordinary everyday knowledge (what a hawker centre is like at lunch, how void decks work in the evening, bus routes you plausibly know) without being told these facts."

### Why

The current wording is strict enough that models hedge away from local context altogether. A Singaporean persona should be able to say "wah lau, lunch crowd coming in already" without the prompt flagging that as "invented". The suggestion allows **ordinary ambient knowledge** while keeping the ban on plot-twist inventions.

### Expected effect

More specific, grounded dialogue. Fewer generic lines like "I understand this is a shared space." More lines like "The 174's just coming in, you'll have no seats in two minutes." That's the kind of local texture the whole project is set up to produce.

---

## B9. Let `interaction_style` vary per agent, don't rely on the default

**File:** every `s0X_presets.py`.  
**Location:** each `AgentPreset` currently uses the default `interaction_style`.

### Why

Right now every agent in every scenario shares the default: *"Brief and conversational; speak only when directly involved or when adding useful information."* That default produces four identically polite voices. Varying this field is where the model gets permission to sound different.

### Suggested variants (mix and match per scenario)

- "Blunt and direct; doesn't bother with social cushions."
- "Hesitant and apologetic even when in the right."
- "Dry, slightly sarcastic; underreacts to friction."
- "Warm and chatty; happy to volunteer unsolicited opinions."
- "Formal and careful; speaks in complete sentences, pauses often."
- "Code-switches when flustered; drops into shorter, choppier phrases under pressure."

Assign one variant per agent per scenario — different combinations across S01–S10.

### Why it still aligns with the project goal

The variation is **individual, not cultural**. Nothing says "the Malay agent is warm" — the warm agent might be C's slot in S02 and D's slot in S07, so it rotates with the C1–C4 background rotation. This means voice differences and background differences are decoupled, which is exactly what you want for a clean experimental manipulation.


### Expected effect

Agents stop sounding like each other. More variance in who speaks when. The evaluator should see meaningfully different peak-conflict dynamics across scenarios because the voices actually differ.

---

## B10. Add an optional "mood" field to `AgentPreset`

**File:** `research_questions/scenario_presets/common.py` (add field), each scenario file (populate it).

### Suggested addition to the dataclass

```python
mood: str = ""  # e.g. "tired after a long shift", "mildly impatient", "distracted by a text message"
```

Pipe it into the mustache via `simulation.py` as part of the persona payload.

### Why

Real people are not emotionally neutral. The current personas describe long-term personality but not current state, so every agent in every scenario starts from baseline calm — which is unrealistic for a *conflict pilot*. A mood field lets you add a short situational modifier without touching personality.

### Example moods, scenario by scenario

- S01 bus seat: A — "resentful from a bad meeting"; B — "worried about picking up a kid late".
- S02 kitchen: A — "proud of the new flat"; B — "stressed about a deadline".
- S04 void deck: A — "frustrated after being woken twice this week"; B — "giddy, trying to impress a crush".
- S09 lift: A — "worried about elderly parent arriving"; B — "late and knows it".

### Why it still aligns with the project goal

Moods are not conflict-forcing — a tired person can still be polite. But they create **asymmetries in emotional capacity**, which is realistic and which the cultural-background label can plausibly colour (e.g. how different cultures express frustration under fatigue).

### Expected effect

More heterogeneous dialogue across repetitions of the same scenario. Peak-conflict scores stop being all identical because the entry emotional state is no longer identical.

---

## B11. Add an optional "unstated private history" per agent

**File:** each `s0X_presets.py`.  
**Location:** `private_knowledge` field (already exists, often underused).

### Current state

`private_knowledge` is usually a one-line fact ("placed a bag on the chair"). It's rarely a story.

### Suggested pattern

Expand `private_knowledge` to include one short piece of **recent history** that would plausibly colour the agent's reaction, without naming it in dialogue.

### Example

> "Your last flatmate ignored your requests about the kitchen for six months and you promised yourself you'd speak up sooner this time."

### Why

Human reactions are rarely about the current event alone. Priming the agent with a short backstory gives it something to react from without scripting what it says. It also makes the C0 vs C1–C4 comparison more meaningful: the same backstory read through a different cultural label can produce genuinely different framings.

### Risk

Over-long backstories could dominate reasoning. **Mitigation:** cap at two sentences; make it concrete rather than philosophical.

### Expected effect

Agents react with a sense of history. Reduces the "sanitised customer-service" tone that dominates current transcripts.

---

## B12. Replace the "Examples" block in the mustache with ones that reward brevity, not performance

**File:** `research_questions/prompts/tiny_person_conflict_pilot.mustache`  
**Location:** the `Examples:` block inside `### Ordinary spoken-language contract`.

### Current examples

```
- Too formal: "I understand your concern, and I appreciate that your meal is getting cold."
- More natural: "Sorry, I can't carry this bowl while it's open."
- Too formal: "Perhaps we can agree on a mutually acceptable compromise."
- More natural: "Give me five minutes, then the seat's yours."
- Too formal for a bystander: "I acknowledge both perspectives and encourage a calm solution."
- More natural for an uninvolved bystander: issue DONE.
```

### Suggested additions (keep existing, add these)

```
- Too eager: "Of course, let me move my bag right away!"
- More natural: "Give me a sec, there's a laptop in there."

- Too generic: "That's a fair point, I can see where you're coming from."
- More natural: "Mm. Still, the smell gets into everything."

- Too neat: "Let's agree to disagree then."
- More natural: issue DONE.
```

### Why

The existing examples warn against formal register but still show every exchange ending with a tidy agreement. The additions model three things the current examples don't: (1) partial concession, (2) sticking to a point after another agent raises a different one, (3) walking away without closure.

### Why it still aligns with the project goal

Examples are a strong lever on the model. Giving it examples where disagreement persists expands the output distribution without instructing it to disagree.

### Expected effect

Fewer "sounds good, see you next week" endings. More transcripts where the issue is parked rather than resolved — which is realistic and interesting.

---

## B13. Model upgrade (not a prompt edit, but the biggest single lever)

**File:** `config.ini` or environment.

### Current

`MODEL=gpt-5-mini` (in `config.ini`); existing transcripts were produced with `gpt-4o-mini`.

### Suggested

`openai/gpt-4.1-mini` for routine runs, `openai/gpt-4o` or `anthropic/claude-sonnet-4` for the comparison batch that actually goes into the writeup.

### Why

The project's own `calibration_notes.md` notes `gpt-4o-mini` is "basal". Models in that class have strong RLHF toward politeness and agreement — which is exactly the behaviour this experiment is trying to measure variance **against**. All the prompt edits above have 2–3× stronger effect on a stronger model, because stronger models can hold a position without needing the prompt to beg them to.

### Expected effect

Qualitatively different runs. More distinct personas. More cultural colour (if B1 is also applied). Better signal-to-noise for the C0 vs C1–C4 comparison.

---

# Suggested order of operations

If applying piece by piece, this order maximises the chance of seeing an effect without over-constraining:

1. **B1** (loosen the cultural-suppression paragraph). Without this, nothing else involving backgrounds does anything.
2. **B6** (shorten rounds to 5). Immediately halves cost.
3. **B13** (model upgrade). Biggest single lever on quality.
4. **B3** (concrete stakes everywhere). Already done for S05 as A4/A5.
5. **B4** (ambiguous cultural cues per scenario). Already done for S05 as A3.
6. **B9** + **B10** + **B11** (voice, mood, history). Compounding diversity.
7. **B2** + **B8** + **B12** (prompt softening + examples). Final polish.
8. **B5** + **B7** (randomised order, round hint). Only if 1–7 still leave transcripts feeling mechanical.

---

# Minimum viable test (unchanged from before)

```bash
python3 -m research_questions \
  --scenario S05 --configuration C0 --repetitions 3 --rounds 5 \
  --simulation-model openai/gpt-4.1-mini \
  --experiment-id s05-c0-postedit

python3 -m research_questions \
  --scenario S05 --configuration C1 --repetitions 3 --rounds 5 \
  --simulation-model openai/gpt-4.1-mini \
  --experiment-id s05-c1-postedit
```

Six runs, roughly $0.30 on `gpt-4.1-mini`. Compare `transcripts/*.md` and `round_scores.csv` across the two folders. Three questions to decide what to do next:

1. Does Agent A delay moving the bag past turn 1? If yes → changes A1 + A4 landed.
2. Does anyone mention the tissue packet? If no → B1 still needed.
3. Do C0 and C1 transcripts read noticeably differently? If no → either B1 or B13 (or both) is the gating issue.

---

# What is deliberately *not* suggested

To keep this honest, here are things that would make conversations "more interesting" at the cost of validity:

- **No "disagree for at least N turns" instruction.** This fakes conflict rather than measuring it.
- **No scripted role templates ("you are the stubborn one").** This replaces LLM behaviour with authored behaviour.
- **No few-shot dialogues from real people.** Models copy their style verbatim and you lose the exploratory variance you want.
- **No "steelman the other side" instruction.** It forces balance where none would naturally exist.
- **No changes to the evaluator prompt yet.** Change one layer at a time; evaluator changes should come after the simulation layer stabilises.

Every suggestion in Part B expands the space of plausible outputs rather than steering toward a specific outcome. That is the right lever for a study whose goal is to detect whether a label matters.
