# Research: How Researchers Make Multiple LLM Agents Converse

## Main finding

Researchers generally do not make multiple LLMs converse simply by connecting one model's output to another indefinitely. Instead, they build a **multi-agent conversation system** that controls:

- **Who speaks** and in what order
- **What each agent knows** about the situation and other agents
- **How agents react** to messages and environmental events
- **When a conversation ends**, including when conflicts resolve or dialogue becomes repetitive

For a Singapore multicultural social simulation using **TinyTroupe**, the most relevant approaches come from research on *generative agents, social simulation, multi-party dialogue, and conversational turn-taking*.

## 1. Six approaches to multi-agent conversation

| Approach | How the conversation works | Research / framework |
|---|---|---|
| **Fixed turn-taking** | Agents take turns in a predetermined order, responding to conversation history. | SOTOPIA |
| **Shared environment** | Agents act within a simulated world, receiving and reacting to one another's messages. | TinyTroupe, Concordia |
| **LLM-selected speaker** | A separate LLM decides who should speak next based on the conversation. | AutoGen |
| **Event-triggered conversation** | Agents initiate conversations when events, observations, or encounters make interaction appropriate. | Generative Agents |
| **Self-selection** | Agents decide whether they want to speak; a mechanism chooses among interested speakers. | Nonomura & Mori (2025) |
| **Asynchronous conversation** | Agents independently decide when to participate rather than waiting for assigned turns. | Time to Talk (2025) |

These approaches are **not mutually exclusive**. A system can combine a shared environment, private agent personas, event triggers, and self-selection.

## 2. How the research implements conversation

### A. SOTOPIA — fixed turn-taking with individual goals

**Research:** Zhou et al., ICLR 2024  
**Links:** [Research paper](https://proceedings.iclr.cc/paper_files/paper/2024/hash/b3075b88e583a0e98d8b24338a613060-Abstract-Conference.html) · [GitHub](https://github.com/sotopia-lab/sotopia)

SOTOPIA simulates social situations where agents have different goals, personalities, and information. Its original research experiments use two agents taking turns. Rather than generating dialogue alone, each agent chooses an action type:

1. `speak` — say something
2. `non-verbal communication` — nod, gesture, or express emotion
3. `action` — do something in the environment
4. `none` — remain inactive
5. `leave` — exit the interaction

In a hawker-centre seat-reservation scenario, Mr Lim might want to retain his reserved seat, while Rachel wants somewhere to eat. Neither agent needs to be instructed to compromise.

Agents receive their individual profiles and goals, observe the interaction history, and decide what to do next. The framework supports evaluation of social-goal achievement and interaction quality.

**Relevance:** Very high for studying *open-ended conflict resolution*, where the interaction should not be scripted to produce agreement.

### B. TinyTroupe — agents communicating inside a shared world

**Framework:** Microsoft TinyTroupe  
**Link:** [Official GitHub repository](https://github.com/microsoft/TinyTroupe)

TinyTroupe uses two central abstractions:

- `TinyPerson`: an individual agent with an identity and behavioural specifications.
- `TinyWorld`: the environment where agents encounter stimuli and interact.

Example based on the framework's usage pattern:

```python
world = TinyWorld("Chat Room", [lisa, oscar])
world.make_everyone_accessible()

lisa.listen("Talk to Oscar to know more about him")

world.run(4)
```

Agents receive stimuli, generate actions such as `TALK`, and can communicate with other accessible agents. The environment handles message delivery and simulation steps.

**Important:** `world.run(4)` specifies simulation steps; it does not necessarily mean exactly four individual utterances.

**Relevance:** This is closest to the existing research setup. It is possible to preserve TinyTroupe for agent personas and interactions while experimenting with how speakers are selected and when conversations end.

### C. AutoGen — an LLM chooses who speaks next

**Framework:** Microsoft AutoGen, `SelectorGroupChat`  
**Link:** [Official documentation](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html)

AutoGen's `SelectorGroupChat` uses a language model to decide which agent should speak next, based on the conversation and agent descriptions.

```text
Conversation history + agent descriptions
                    |
                    v
           Speaker-selection LLM
                    |
                    v
       Selected agent generates reply
                    |
                    v
          Update shared conversation
                    |
                    +----> Repeat
```

For example, after Mr Lim and Rachel disagree, the selector may choose Nur Aisyah as the next speaker because her role as a mediator is contextually relevant.

The system also supports custom speaker-selection logic and termination conditions.

**Relevance:** Useful for three- or four-agent simulations where fixed speaker order feels unnatural. However, the selector itself introduces a separate LLM decision that can influence outcomes, so it should be treated as an experimental variable.

### D. Generative Agents — social encounters trigger conversations

**Research:** Park et al., UIST 2023  
**Link:** [Generative Agents: Interactive Simulacra of Human Behavior](https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/)

The *Generative Agents* study simulates 25 agents in a virtual town. Agents:

- Observe their environment
- Store experiences in memory
- Retrieve relevant memories
- Reflect on events
- Plan actions and interact with others

Conversations can arise when agents encounter one another. Those interactions can influence later behaviour and events. The paper demonstrates social behaviours such as spreading invitations, forming acquaintances, and coordinating attendance.

**Relevance:** Especially useful for the longer-term goal of simulating HDB estates, hawker centres, and MRT environments in which conversations emerge from day-to-day situations rather than a fixed starting prompt.

### E. Who Speaks Next? — agents decide whether they want to speak

**Research:** Nonomura & Mori, *Frontiers in Artificial Intelligence*, June 2025  
**Link:** [Full paper](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1582287/full)

The paper investigates conversational turn-taking in multi-agent LLM systems, inspired by human group discussions.

Each agent uses an LLM to decide whether to **speak** or **listen**, with a speaking-importance score from **0 to 9**. If several agents want to speak, the mechanism selects the agent with the highest score. The system also accounts for directed questions, giving the addressed agent an opportunity to respond.

Example:

- Rachel directly asks Mr Lim why the tissue packet should reserve the table; Mr Lim is the natural next respondent.
- Rachel makes a general remark about fairness; a nearby bystander might decide to participate.
- A bystander who does not feel a need to intervene can stay silent.

The authors compared random equal participation, self-selection alone, and self-selection combined with speaker designation. In their murder-mystery experiments, the combined approach reduced conversational breakdowns.

**Relevance:** Particularly strong for studying *who intervenes, who remains silent, and how participation affects conflict resolution*. This is a promising approach for the Singapore multicultural simulation.

### F. Time to Talk — decide *when* to speak separately from *what* to say

**Research:** Eckhaus, Berger & Stanovsky, *Findings of EMNLP 2025*  
**Links:** [Research paper](https://aclanthology.org/2025.findings-emnlp.608/) · [Project and code](https://niveck.github.io/Time-to-Talk/)

The study separates two functions:

1. **Scheduler:** decides when an agent should communicate.
2. **Generator:** decides what an agent says.

The researchers evaluated asynchronous participation using online Mafia games with humans and LLM agents. Agent participation timing resembled human timing patterns, although differences remained in the generated language.

**Relevance:** Useful for studying hesitation, conflict avoidance, spontaneous intervention, and other temporal aspects of social participation.

## 3. Recommended architecture for the TinyTroupe simulation

Rather than replacing TinyTroupe, start with a **hybrid conversation controller** on top of it:

- **TinyTroupe:** manages personas, observations, actions, and shared context.
- **Conversation scheduler:** decides who is eligible and willing to speak.
- **Speaker generation:** produces the selected agent's utterance or action.
- **External evaluator:** independently scores conflict resolution, repetition, coherence, and participation.

```text
       Scenario + Shared Environment
         (e.g. hawker centre)
                    |
                    v
         Independent Agent States
      +-------------+-------------+
      |             |             |
   Mr Lim         Rachel      Nur Aisyah
   keep seat      find seat    seek fairness
      |             |             |
      +-------------+-------------+
                    |
                    v
          Individual Decisions
         speak / listen / act / leave
                    |
                    v
        Conversation Scheduler
  (direct reply priority + self-selection)
                    |
                    v
       Selected Agent's Response
                    |
                    v
        Update Shared World State
                    |
                    v
        Independent Evaluation
   resolution / repetition / coherence
                    |
             Continue or stop
```

**Key principle: separate simulation from evaluation.** Agents should not be instructed to reach a compromise simply because resolution is an evaluation metric. Instead, give them individual goals and behavioural constraints, then use a separate evaluator to detect what happened.

### Example: Custom agent decision prompt

The following is an **illustrative custom design**, not a built-in TinyTroupe API.

```text
You are Rachel, a diner at a busy Singapore hawker centre.

Private goal:
Find a place to eat without accepting unfair treatment.

Personality:
Independent, moderately assertive, and willing to
consider reasonable explanations.

Current observation:
Mr Lim has explained that he reserved the table
with a tissue packet. A bystander is listening.

Based on your goal, personality, and the conversation:
- Decide whether to speak, listen, act, or leave.
- You may disagree, change your mind, or remain silent.
- You are not required to resolve the disagreement.
- Do not assume access to other agents' private goals.

Return a structured decision with:
- action
- urgency (0-9)
- addressee (if any)
- message (if speaking)
```

Example structured response:

```json
{
  "action": "speak",
  "urgency": 7,
  "addressee": "Mr Lim",
  "message": "I understand that's the custom, but can we share the table instead?"
}
```

## 4. Proposed experiment: Compare conversation mechanisms

Keep the **scenario, personas, base LLM, generation settings, and evaluation criteria** constant. Change only the mechanism for assigning speaking turns.

| Condition | Who decides the next speaker? | Research question |
|---|---|---|
| **A — Baseline** | Fixed round-robin order | How does the existing setup perform? |
| **B — LLM selector** | Separate conversation-management model | Does contextual selection improve coherence? |
| **C — Self-selection** | Agents independently express interest in speaking | Does voluntary participation change social dynamics? |
| **D — Hybrid** | Direct-reply priority plus self-selection | Does a more human-like turn-taking mechanism improve outcomes? |

A reasonable **pilot design** is 10 independent runs per condition per scenario, followed by additional replication based on observed variability. Apply the same maximum-turn or maximum-event budget for comparable runs; report actual conversation lengths separately.

### Suggested evaluation metrics

| Metric | Measurement |
|---|---|
| **Resolution rate** | Share of runs where the underlying practical issue is resolved |
| **Turns to resolution** | Number of conversational turns until resolution, conditional on resolution |
| **Repetition onset** | First point where subsequent contributions stop introducing meaningful content |
| **Conversational coherence** | Whether each utterance responds appropriately to preceding messages |
| **Participation balance** | Distribution of speaking turns and silence across agents |
| **Persona consistency** | Whether decisions align with assigned goals, traits, and known information |
| **Cultural plausibility** | Human evaluation of whether conversations are credible in Singaporean contexts |
| **Token cost** | Tokens consumed per run and per meaningful interaction |

**Related evaluation research:** [Computational Analysis of Conversation Dynamics through Participant Responsivity (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1798/), which studies responsiveness between conversational turns. This can complement similarity-based repetition measures.

### Connection to the existing simulation experiments

The October 22 presentation reported:

- **HDB shared-space scenario, 10 runs × 5 rounds:** 40% resolved, 60% unresolved and not repetitive.
- **MRT scenario, 10 runs × 5 rounds:** 100% resolved, with 20% later classified as repetitive within the observation window.

The difference suggests that **conversation length and difficulty vary by scenario**. A conflict requiring multiple agreements (e.g. ventilation practices *and* cookware boundaries) should not be assumed to require the same interaction budget as an easily addressed inconvenience (e.g. loud phone audio).

**Source:** *Research Presentation — Crafting Scenarios Around Conflict & Resolution (TinyTroupe)*, October 22, pages 7, 9 and 10.

This also reinforces the need to distinguish:

- **Resolution:** practical agreement or changed behaviour addresses the issue.
- **Repetition:** dialogue becomes semantically repetitive.
- **Convergence:** a separately defined condition, such as repetition *after* resolution.

An unresolved disagreement can become repetitive; repetition alone should not be equated with successful conflict resolution.

## 5. Further reading

### DialogLab (UIST 2025)

[DialogLab: Authoring, Simulating, and Testing Dynamic Group Conversations in Hybrid Human-AI Conversations](https://research.google/pubs/dialoglab-authoring-simulating-and-testing-dynamic-group-conversations-in-hybrid-human-ai-conversations-2/)

Explores combining scripted conversation structures, dynamic groups, turn-taking rules, and improvisation. Useful for creating repeatable but not fully scripted simulation scenes.

### CAMEL (NeurIPS 2023)

[CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society](https://proceedings.neurips.cc/paper/2023/hash/a3621ee907def47c1b952ade25c67698-Abstract-Conference.html)

Introduces role-playing and inception prompting for autonomous agent interactions. More relevant to cooperative, goal-oriented agents than spontaneous social encounters, but informative for prompting techniques.

### Survey of LLM social simulation (2024)

[From Individual to Society: Survey of LLM Social Simulation](https://arxiv.org/abs/2412.03563)

Reviews individual-, scenario-, and society-level simulation work, including architectural and evaluation considerations. Useful for structuring a literature review.

## 6. Recommendation and potential research question

**Recommended next step:** Compare **fixed round-robin turn-taking** with **self-selection plus direct-reply priority** within TinyTroupe before moving to a full asynchronous simulation. This is a bounded change that allows the conversation mechanism itself to become the independent variable.

**Potential research question:**

> How do different conversational turn-taking mechanisms influence interaction coherence, participation patterns, conflict resolution, and repetition in LLM-based multicultural social simulations?

This extends the work beyond asking *how many rounds agents take to converge* to examining **how the conversation mechanism shapes the social behaviour being simulated**.

---

## Primary references

1. [SOTOPIA — ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/b3075b88e583a0e98d8b24338a613060-Abstract-Conference.html)
2. [TinyTroupe — Microsoft GitHub](https://github.com/microsoft/TinyTroupe)
3. [AutoGen SelectorGroupChat — Microsoft documentation](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html)
4. [Generative Agents — Park et al., UIST 2023](https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/)
5. [Who Speaks Next? — Nonomura & Mori, 2025](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1582287/full)
6. [Time to Talk — Eckhaus et al., EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.608/)
7. [DialogLab — UIST 2025](https://research.google/pubs/dialoglab-authoring-simulating-and-testing-dynamic-group-conversations-in-hybrid-human-ai-conversations-2/)
8. [CAMEL — NeurIPS 2023](https://proceedings.neurips.cc/paper/2023/hash/a3621ee907def47c1b952ade25c67698-Abstract-Conference.html)
9. [From Individual to Society: Survey of LLM Social Simulation](https://arxiv.org/abs/2412.03563)
10. [Computational Analysis of Conversation Dynamics through Participant Responsivity — EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1798/)
