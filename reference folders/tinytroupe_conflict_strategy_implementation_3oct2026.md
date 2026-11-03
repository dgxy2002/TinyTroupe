# Reusable Conflict & Resolution Strategies for TinyTroupe

> **Implementation brief for a VS Code coding agent**  
> **Project:** Singapore multicultural social-interaction research  
> **Goal:** Add an optional, scenario-agnostic conversational-strategy layer to a multi-agent simulation so agents can naturally disagree, negotiate, and sometimes resolve conflicts—without forcing an argument or an agreement.

## 0. Instructions for the coding agent

1. **Inspect the existing repository first.** Identify how TinyTroupe agents are created, given persona/goals, stepped through a round, and how transcripts/metrics are saved. Reuse the existing pipeline; do not replace it unnecessarily.
2. Implement a **small, configurable experiment**, not a new simulation framework. Prefer modular, testable code and minimal dependencies.
3. **Verify TinyTroupe APIs against the installed version** before relying on them. `TinyPerson.internalize_goal(...)` may be useful if available; do not assume other methods or method signatures.
4. Do not change baseline behaviour unless the strategy layer is explicitly enabled. Make it possible to compare runs **with and without** the intervention.
5. Maintain the agents' freedom to agree, resist, compromise, walk away, or remain unresolved. **Never hardcode a minimum argument length, a mandatory escalation, or a forced resolution.**
6. If the repo has an existing experiment runner or metrics definitions, extend those rather than creating a conflicting second system.
7. After implementing, run the project's tests plus a small smoke simulation and report what succeeded, what failed, and what remains unverified.

## 1. Research motivation

**Research question:** Can a shared set of conversational strategies, combined with scenario-specific goals and agent-level conflict styles, generate realistic and varied conflict trajectories across scenarios without writing a custom argument prompt for every scenario?

**Working hypothesis (to test, not assume):** Strategy-guided prompting produces more substantive disagreement and/or reduces premature concessions relative to an unguided baseline, while preserving natural resolution and persona consistency.

A longer argument is **not** automatically a better result. Repetitive contradiction, artificial stubbornness, or refusal to accept a valid compromise should count against quality.

### Research-informed foundations

- **ISO 24617-2 (dialogue-act annotation):** Motivates having a reusable, domain-independent vocabulary for conversational acts. The 11 strategies below are **our proposed operational taxonomy**, *not* an official ISO taxonomy. <https://www.iso.org/standard/76443.html>
- **Rehearsal: Simulating Conflict to Teach Conflict Resolution (CHI 2024):** Motivates choosing a conflict-management strategy before generating dialogue; draws on **Interests–Rights–Power (IRP)** approaches. Our selector below is an adaptation, *not* a verbatim reproduction of its implementation. <https://doi.org/10.1145/3613904.3642159>
- **SOTOPIA (ICLR 2024):** Motivates explicit private social goals and agent-specific background information rather than issuing a blanket “argue” command. <https://arxiv.org/abs/2310.11667>
- **Thomas–Kilmann conflict-handling model:** Motivates modelling how assertively or cooperatively different agents approach disagreements. These trait values are simulation design variables, **not validated psychological measurements** of synthetic characters. See also <https://doi.org/10.1177/001316447703700204>.

## 2. What is universal vs. scenario-specific?

| Component | Reuse across scenarios? | Notes |
|---|---|---|
| Strategy names and definitions | **Yes** | Same taxonomy for HDB, MRT, hawker centre, etc. |
| Strategy-selection and generation prompt structure | **Yes** | Templates take injected context. |
| Conflict-style dimensions | **Yes** | Same dimensions; numerical trait values differ. |
| Agent persona and beliefs | No | Agent-specific. |
| Private goals and acceptable compromises | No | Agent- and scenario-specific. |
| World events and information asymmetry | No | Scenario-specific. |
| Available actions and feasibility constraints | No | Scenario-specific. |
| Criteria for an actual resolution | No | Must match the scenario's substantive issues. |
| Strategy choice and generated dialogue | No | Emerge at runtime. |

## 3. Universal conversational strategy taxonomy

Start with exactly these **11 core strategies**. Expose the enum and descriptions centrally so experiments, prompts, logging, and evaluation share the same definitions.

| Category | Strategy | Meaning |
|---|---|---|
| Conflict | `ASSERT` | Introduce a claim, opinion, preference, or demand. |
| Conflict | `DEFEND` | Maintain and justify an existing position. |
| Conflict | `CHALLENGE` | Question or dispute another agent's position. |
| Information | `CLARIFY` | Ask for facts or correct misunderstandings. |
| Information | `EXPLAIN_NEED` | Express an underlying need, constraint, or concern. |
| Information | `ACKNOWLEDGE` | Show understanding without necessarily agreeing. |
| Negotiation | `PROPOSE` | Suggest a practical resolution. |
| Negotiation | `COUNTER_PROPOSE` | Modify or reject a proposal with an alternative. |
| Resolution | `CONCEDE` | Revise some or all of one's prior stance. |
| Resolution | `ACCEPT` | Explicitly accept a concrete proposal or arrangement. |
| Disengagement | `WITHDRAW` | Leave, defer, avoid, or end participation in the disagreement. |

Optional future extensions: `SEEK_MEDIATION`, `APPEAL_TO_AUTHORITY`. Do **not** add these in the first iteration unless the existing project already uses them.

### Important classification distinctions

- `ACKNOWLEDGE` ≠ `ACCEPT`: “I see why that matters” does not mean “I agree to the proposal.”
- `CONCEDE` ≠ `ACCEPT`: Revising a belief or demand is not the same as agreeing on a full arrangement.
- `WITHDRAW` ≠ `RESOLVED`: Ending an interaction may leave the conflict unresolved.
- `CHALLENGE` need not involve anger, aggression, or insults.
- Utterances may contain multiple dialogue acts. For the MVP, store **one primary intended strategy** and optionally keep secondary labels for future analysis.

## 4. Agent and scenario input schema

Prefer existing project representations if they already capture these fields. Otherwise use a lightweight Python dataclass/Pydantic model or validated dictionary.

```yaml
scenario:
  id: hawker_choping
  title: Tissue-packet seat reservation
  setting: Peak-hour Singapore hawker centre
  shared_context: >
    A diner sits at a table after moving an unattended tissue packet.
    Another diner returns carrying food and says the packet reserved the seat.
  resolution_requirements:
    - Both parties explicitly reach a workable seating arrangement.
  # Don't expose private goals/beliefs to other agents.

agents:
  - id: mr_lim
    persona: Older local diner, familiar with choping customs
    goal: Reclaim reserved seat or agree to an acceptable seating arrangement
    beliefs:
      - Leaving a tissue packet is a locally recognised way to reserve a seat.
    constraints:
      - Wants somewhere to eat while food is warm.
    acceptable_compromises:
      - Share the table if there is enough room.
    conflict_style:
      assertiveness: 7
      cooperativeness: 5
      conflict_avoidance: 4

  - id: rachel
    persona: Diner with a different interpretation of the tissue-packet norm
    goal: Find a place to eat without feeling unfairly displaced
    beliefs:
      - An unattended packet does not necessarily reserve an entire table.
    constraints:
      - Lunch break is short.
    acceptable_compromises:
      - Share a table if there is enough room.
    conflict_style:
      assertiveness: 6
      cooperativeness: 6
      conflict_avoidance: 5
```

Values on 0–10 scales are **experimental inputs**, not a statistically calibrated trait-to-behaviour model. Avoid encoding cultural identity or age as deterministic causes of aggression, compliance, or cooperativeness.

### Additional test scenarios

- **MRT loud audio:** A commuter wants to play audio; another needs quiet. Resolution might involve muting, lowering volume, or headphones. Withdrawal or moving away is **not automatically mutual resolution**.
- **HDB shared kitchen:** Housemates disagree about cooking odours **and** cookware boundaries. Resolution may require agreements on both dimensions. Partial agreement should remain **partially resolved**, not “resolved.”

## 5. Proposed architecture

Implement the following without coupling strategy selection to a particular scenario:

```text
Scenario + agent-private goals/personas + conversation history
                            |
                            v
                  Strategy Selector (LLM)
                  -> primary strategy label
                            |
                            v
                  Dialogue Generator (LLM)
                  -> natural agent utterance
                            |
                            v
            Existing TinyTroupe turn / world state
                            |
                            v
           Append structured transcript / metadata
                            |
                            v
                Separate offline evaluator
            -> conflict / resolution / repetition
```

If TinyTroupe's turn-generation API cannot safely support a separate selector and generator, implement the **least invasive adapter** available. Do not falsely present strategy selection as guaranteed to control native TinyTroupe generation. Log which mode actually ran:

- `baseline`: native conversation, unchanged.
- `strategy_two_stage`: separate strategy selection + dialogue generation (preferred if integration permits).
- `strategy_one_stage`: one prompted generation returning a primary strategy label and dialogue (fallback, explicitly reported).

Where possible, keep the same model, sampling settings, round/turn policy, and context window between baseline and treatment. Record exceptions.

## 6. Prompt templates

### 6.1 Strategy selector (stage 1)

```text
You are selecting ONE conversational strategy for a fictional social agent.

SHARED SCENARIO:
{scenario_context}

YOUR PRIVATE PERSONA:
{agent_persona}

YOUR PRIVATE GOAL:
{agent_goal}

YOUR PRIVATE BELIEFS AND CONSTRAINTS:
{agent_beliefs_and_constraints}

YOUR CONFLICT STYLE (0-10; behavioural tendencies, not absolute rules):
Assertiveness: {assertiveness}
Cooperativeness: {cooperativeness}
Conflict avoidance: {conflict_avoidance}

CONVERSATION HISTORY AVAILABLE TO YOU:
{conversation_history}

CHOOSE EXACTLY ONE:
ASSERT, DEFEND, CHALLENGE, CLARIFY, EXPLAIN_NEED,
ACKNOWLEDGE, PROPOSE, COUNTER_PROPOSE, CONCEDE,
ACCEPT, WITHDRAW

RULES:
- Choose what best matches this agent's goal, current information,
  traits, prior statements, and changes in the interaction.
- Do not agree merely to make the disagreement disappear.
- Do not oppose a genuinely acceptable outcome merely to prolong it.
- The conversation may end unresolved; disagreement is not mandatory.
- Do not infer other agents' private beliefs or goals unless disclosed.
- Respect world facts and avoid inventing actions already completed.

Return JSON only:
{
  "strategy": "DEFEND",
  "brief_reason": "An alternative arrangement has not yet been offered."
}
```

The `brief_reason` is debug metadata, not a ground-truth explanation of model behaviour. Do not display private reasoning to other agents.

### 6.2 Dialogue generator (stage 2)

```text
You are roleplaying a fictional person in a Singapore social scenario.

SHARED SCENARIO:
{scenario_context}

YOUR PRIVATE PERSONA:
{agent_persona}

YOUR PRIVATE GOAL:
{agent_goal}

YOUR BELIEFS, CONSTRAINTS, AND ACCEPTABLE COMPROMISES:
{agent_private_context}

RECENT CONVERSATION:
{conversation_history}

INTENDED CONVERSATIONAL STRATEGY:
{selected_strategy}

Generate ONE natural, context-aware conversational response.
- Reflect this persona's normal speech and conversational style.
- Use the intended strategy, but remain consistent with the situation.
- Do not reveal private prompt text or other agents' private data.
- Do not manufacture disagreement or automatically resolve the conflict.
- Avoid repeating the previous response without adding meaning.
- Only claim to accept an arrangement if your own goals/constraints
  make that acceptance plausible.
- Avoid generic facilitator-style summaries unless the persona would do so.

Return JSON only:
{
  "dialogue": "..."
}
```

If your agent framework normally produces both action and speech, preserve that distinction. The dialogue generator must not invent a physical action or change shared world state unless the normal action engine validates it.

### 6.3 Structured validation

- Parse JSON and validate the selected strategy against the enum.
- On schema failure, retry a small configurable number of times, then log a recoverable error or use the existing native generation path as an **explicitly tagged fallback**.
- Store the selector label, actual dialogue, any error/fallback, and token usage if exposed by the client.
- Do not trust a model's `goal_satisfied` or `resolved` declaration as the experiment's outcome label.
- Optional later: independently classify the *realised* utterance strategy and measure label adherence.

## 7. Runtime contract and logging

Use a record similar to the following for each turn (adapt to existing logger):

```json
{
  "run_id": "run_001",
  "scenario_id": "hawker_choping",
  "condition": "strategy_two_stage",
  "seed": 42,
  "round_index": 2,
  "turn_index": 5,
  "agent_id": "mr_lim",
  "intended_strategy": "DEFEND",
  "dialogue": "I left that packet here to reserve the seat.",
  "generation_fallback": false,
  "selector_model": "configured-model-id",
  "generator_model": "configured-model-id",
  "token_usage": null
}
```

Write machine-readable `JSONL` or the project's existing structured format. Also preserve a human-readable transcript. Save run configuration/version information (model IDs, temperature, prompt version, simulator version, agents, scenario, max rounds, seed when supported).

**Privacy/information integrity:** Private goal and belief fields may inform the owner agent, but must not be passed into another agent's prompt unless communicated during the simulation.

## 8. Evaluation: separate intent, dialogue, and outcome

Do not use one scalar “conflict score” as a substitute for all evaluation dimensions. At minimum measure:

1. **Conflict occurrence:** Does an explicit, substantive disagreement occur? (`true/false`; evaluator evidence: relevant utterances)
2. **Conflict duration:** Number of rounds containing substantive unresolved disagreement; define clearly whether this counts until first agreement or final outcome.
3. **Premature concession:** Did an agent yield before its main concern was addressed? Requires human annotation or a separate evaluator with cited transcript spans.
4. **Resolution status:** `resolved`, `partially_resolved`, `unresolved`, `withdrawn` (with scenario-specific criteria).
5. **Repetition:** Whether utterances/rounds repeat previous content without meaningful progress. Reuse the existing research metric if present, rather than introducing another threshold silently.
6. **Persona consistency:** Do actions and statements accord with the agent's goals, beliefs, and available information?
7. **Strategy distribution/adherence:** What strategies were selected? Does the dialogue actually instantiate each intended action?
8. **Cost:** Tokens, calls, latency and, if available, monetary cost per run and per useful conflict.

**Resolution must be independently evaluated.** In the choping example, simply saying “okay” does not establish whether an acceptable seating arrangement exists. In the HDB example, an agreement on ventilation alone does not necessarily settle cookware separation.

Prefer an evaluator that provides `label`, `confidence` (if calibrated/defined), and **direct transcript evidence**. Where feasible, manually check a sample of runs to assess evaluator reliability and record disagreements. Keep evaluation prompts separate from agent-generation prompts.

## 9. Experiment design

Implement a configurable comparison across four conditions if practical; for the MVP, **A versus D is enough to prove end-to-end functionality**, then add B and C.

| Condition | Configuration | What it isolates |
|---|---|---|
| **A — Baseline** | Existing personas + scenario prompts; no added strategies | Current behaviour |
| **B — Goal conflict** | Explicit incompatible private goals; native dialogue | Effect of clear goals |
| **C — Direct challenge** | Goals plus an instruction to critically challenge conflicting claims when warranted | Effect of direct argument-oriented prompting |
| **D — Strategy-first** | Goals plus reusable selector and generator | Effect of explicit conversational strategy selection |

**Experimental cautions:**

- In B/C/D, keep the same explicit goals wherever possible. Make the baseline goal difference visible in experimental records; otherwise the comparison confounds goals with strategy prompting.
- Pre-register operational definitions for conflict, resolution, premature concession, and repetition *before* analysing final results.
- Use the same scenarios, agent configurations, model versions and generation parameters wherever feasible. Repeat independent runs; record seeds when supported, but recognise LLM APIs may not be fully deterministic.
- Start with three scenarios: **hawker choping**, **MRT audio**, **HDB kitchen odour + cookware boundaries**.
- Smoke test with **1–3 runs** per condition. Expand to **at least ~10–20 runs** per condition per scenario if budget allows, and report uncertainty rather than treating a small sample as conclusive.
- Report outcome rates with denominators and distribution of resolution rounds, not just averages.
- Keep a maximum round limit for cost/safety; hitting the limit means **censored/unresolved at horizon**, not automatically converged.
- Do not equate **repetition**, **convergence**, and **resolution**; they are different outcomes.

## 10. Suggested repository structure

Adapt names to the existing repo. Do not create duplicate layers if equivalent modules already exist.

```text
src/
  conflict_strategy/
    taxonomy.py             # enum + descriptions
    schemas.py              # validated configuration/turn data
    prompts.py              # selector and dialogue prompt builders
    selector.py             # strategy selection + validation
    generator.py            # dialogue generation adapter
    integration.py          # wrapper around existing TinyTroupe loop
    evaluator.py            # optional; separate from generation
experiments/
  scenarios/
    hawker_choping.yaml
    mrt_audio.yaml
    hdb_kitchen.yaml
  run_conflict_comparison.py
  config.yaml
 tests/
  test_strategy_taxonomy.py
  test_strategy_prompting.py
  test_conflict_integration.py
  test_scenario_resolution.py
```

If the repo already uses notebooks, scripts, or a different package layout, follow its conventions rather than blindly creating this tree.

## 11. Implementation phases and acceptance checks

### Phase 1 — Inspect and map the current system

- Locate persona/goal injection, TinyTroupe simulation loop, transcript writer, evaluation utilities and model configuration.
- Identify exact API seams for `baseline`, `strategy_one_stage`, and `strategy_two_stage`.
- Summarise the chosen integration mechanism and its limitations.

### Phase 2 — Implement minimal strategy layer

- Create enum/description registry for all 11 strategies.
- Add configurable prompts with private agent context.
- Validate LLM responses and record fallback/error states.
- Add an enable/disable option that leaves existing baseline behaviour intact.
- Save intended strategy per turn alongside dialogue and model metadata.

### Phase 3 — Add reusable scenarios and resolution checks

- Supply at least one hawker scenario config and show it can run using the universal prompt.
- Add the MRT and HDB configs without changing strategy definitions.
- Keep objective resolution requirements in each scenario, not in the generic selector prompt.

### Phase 4 — Test and compare

- Unit test enum validation, prompt interpolation, private information boundaries, JSON parsing, and fallback logic.
- Integration smoke test one baseline and one strategy-guided run end-to-end.
- Generate side-by-side transcripts and a summary table of outcomes.

### Acceptance criteria

- [ ] All 11 strategy labels are supported and validated.
- [ ] A single universal prompt/strategy implementation works for at least 3 different scenarios.
- [ ] The scenario/agent context is injected without leaking one agent's private goals to another.
- [ ] Baseline runs remain unchanged when the feature flag is off.
- [ ] Each treatment turn logs its intended strategy and resulting utterance.
- [ ] Agents can plausibly disagree, negotiate, resolve, or end unresolved; no outcome is scripted.
- [ ] Resolution is checked against scenario-specific conditions, not inferred solely from `ACCEPT` or `CONCEDE`.
- [ ] A runnable CLI command or script and README instructions are provided.
- [ ] Tests and at least one end-to-end smoke experiment are executed and their results reported.

## 12. Deliverables expected from the coding agent

1. Production code integrated into the existing TinyTroupe experiment loop.
2. Three scenario configurations using the *same* strategy taxonomy/prompts.
3. A runnable comparison command (baseline vs strategy-guided; ideally all four conditions).
4. Structured transcripts and a simple CSV/JSON summary of metrics.
5. Tests and a brief README section explaining how to toggle the strategy layer.
6. A concise report of observed behaviour, known limitations, and any unverified framework integrations.

## 13. Key principle

> **Universal strategies, contextual selection, scenario-specific resolution.**
>
> Standardise *what kinds of conversational moves are available*, not *what agents must say* or *when they must agree*. Treat the intervention as an experimentally testable hypothesis, not as a guarantee of better conflict realism.
