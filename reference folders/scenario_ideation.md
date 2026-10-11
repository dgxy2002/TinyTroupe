# Scenario Ideation

## Research Context

The objective is to build an LLM-powered multi-agent digital social simulation set in **Singapore’s multicultural and multilingual environment**. The simulation models everyday social interactions among diverse agents to examine how cultural values, communication styles, and socio-cultural norms emerge in shared spaces.

The simulation uses **TinyTroupe** with detailed `TinyPerson` personas, episodic/semantic memory, and demographic sampling. Candidate scenarios should follow the experimental constraint:

> **1 Scenario = 1 Key Event**

Each scenario begins from a neutral baseline and introduces exactly one well-defined social stimulus. Scenarios should be independently repeatable 5–10 times so that differences in outcomes can be attributed to the stimulus rather than accumulated background conflict.

---

# Candidate 1 — This Table Is Choped

## 1. Scenario & Setting

**Setting:** Busy neighbourhood hawker centre during lunch.

Three strangers are independently looking for seats. One diner has left a tissue packet on an empty table to reserve it while buying food.

The environment begins neutrally: moderate crowd, no previous interaction between agents, and no shortage severe enough to create conflict by itself.

## 2. Agent Profiles

| Agent | Profile | Language Background | Baseline Relationship |
|---|---|---|---|
| **Mr Lim** | Chinese, 68, retired technician | Mandarin, Hokkien, moderate English/Singlish | Stranger |
| **Rachel Pereira** | Eurasian, 34, returned to Singapore after several years overseas | English dominant, understands Singlish | Stranger |
| **Nur Aisyah** | Malay, 29, nurse | English, Malay, Singlish | Stranger |
| **Arjun** | Indian, 23, university student | English, Tamil, Singlish | Stranger |

Useful personality variables can be independently assigned rather than tied to ethnicity:

- Assertiveness
- Conflict avoidance
- Familiarity with hawker etiquette
- Respect for seniority
- Willingness to mediate

## 3. Single Key Event / Stimulus

> **Rachel sees Mr Lim's tissue packet on the table, moves it aside, and sits down just as Mr Lim returns with his food.**

This is the **only injected event**.

Do not subsequently introduce:

- Missing seats
- Spilled food
- Staff intervention
- Arguments over food
- Additional unrelated disputes

Everything after this point should emerge solely from agent behaviour.

## 4. Expected Research Signals & Metrics

### Socio-Cultural Norm Recognition

Measure whether:

- Rachel recognises the tissue packet as a *chope*
- Other agents explicitly explain the norm
- Chopeing is treated as:
  - Legitimate
  - Informal but expected
  - Unreasonable

### Communication Style

Track:

- Direct confrontation
  - Example: `"I reserved this seat."`
- Indirect language
  - Example: `"Actually, I think this table already got people."`
- Mitigation/apology
  - Example: `"Sorry ah..."`, `"Paiseh..."`
- Singlish markers
  - `"already"`
  - `"lah"`
  - `"can or not"`
  - `"this one choped"`
- Use of Mandarin/Hokkien when frustrated
- Whether speakers adapt their language to another agent's proficiency

### Social Hierarchy

Measure whether Mr Lim's age affects:

- Tone
- Willingness to challenge him
- Mediator behaviour
- Deference

### Resolution Outcome

Code each run as one of:

- **Consensus** — everyone accepts the same interpretation of the norm
- **Compromise** — an alternative seating arrangement is negotiated
- **Avoidance / Indirect Resolution** — someone gives way without explicitly resolving the disagreement
- **Escalation** — disagreement intensifies

Additional quantitative variables:

- Number of dialogue turns before resolution
- Number of apology/face-saving statements
- Number of explicit cultural-norm references
- Number of code-switches
- Whether a third party mediates
- Who initiates resolution

## Why This Scenario Is Useful

This is probably the **cleanest experimental scenario** because the stimulus is extremely small while still testing:

- Local knowledge
- Age hierarchy
- Singlish
- Politeness
- Mediation
- Informal Singaporean social norms

---

# Candidate 2 — The Shared Frying Pan

## 1. Scenario & Setting

**Setting:** Shared kitchen in an HDB flat occupied by several unrelated tenants.

The residents normally coexist peacefully. Certain cookware has been designated for particular dietary requirements.

## 2. Agent Profiles

| Agent | Profile | Language Background | Baseline Relationship |
|---|---|---|---|
| **Farid** | Malay, 31, IT support specialist | Malay, English, Singlish | Housemate |
| **Cheryl** | Chinese, 26, marketing executive | English, Mandarin, Singlish | Housemate |
| **Karthik** | Indian, 33, engineer | English, Tamil | Housemate |
| **Auntie May** | Chinese, 59, administrative worker | Mandarin, Hokkien, conversational English | Housemate |

Farid personally maintains a set of cookware intended to remain suitable for his dietary/religious requirements.

The cookware arrangement should be explicitly included in the environment state so the simulation does not have to invent it.

## 3. Single Key Event / Stimulus

> **Cheryl accidentally uses Farid's designated frying pan to cook pork. Farid enters the kitchen and notices.**

Nothing else happens.

Do not add:

- Previous roommate disputes
- Unpaid bills
- Kitchen cleanliness issues
- Another religious dispute
- Landlord intervention

The experiment concerns only the immediate reaction to this event.

## 4. Expected Research Signals & Metrics

### Norm Explanation

Measure whether Farid:

- Explains why the cookware matters
- Simply states a rule
- Assumes Cheryl should already know
- Avoids confronting her

Example distinction:

> `"That pan is meant to stay halal."`

versus:

> `"Eh, why you use my pan?"`

These represent different communication strategies.

### Response to Norm Violation

Measure whether Cheryl:

- Apologises immediately
- Asks for clarification
- Minimises the issue
- Becomes defensive
- Offers restitution such as replacing the pan

### Third-Party Mediation

Observe whether Karthik or May:

- Stays silent
- Sides with someone
- Explains one perspective to the other
- Proposes a practical solution

### Face-Saving Behaviours

Code statements involving:

- Apology
- Reassurance
- Humour
- Minimisation
- Indirect disagreement
- Changing the subject
- Explicit blame

### Resolution Outcome

Classify each interaction as:

- **Consensus**
- **Compromise**
- **Avoidance / Indirect Communication**
- **Escalation**

Additional metrics:

| Metric | Example Measurement |
|---|---|
| Explicit cultural explanation | Yes / No |
| Apology | Yes / No |
| Replacement offered | Yes / No |
| Mediator emerges | Agent ID / None |
| Direct blame statements | Count |
| Face-saving statements | Count |
| Code-switching | Count |
| Turns until resolution | Number |
| Final sentiment | Positive / Neutral / Negative |

## Why This Scenario Is Useful

This scenario tests what happens when agents must negotiate a **more personally meaningful cultural boundary** while maintaining an ongoing relationship.

It provides a useful contrast with the hawker-centre scenario:

- **Hawker:** strangers + informal public norm
- **Shared flat:** acquaintances + personally important norm

---

# Candidate 3 — Can Lower the Music?

## 1. Scenario & Setting

**Setting:** HDB void deck during a small neighbourhood Deepavali gathering.

Residents are talking and eating while music is playing. The gathering itself is permitted and otherwise proceeding normally.

## 2. Agent Profiles

| Agent | Profile | Language Background | Baseline Relationship |
|---|---|---|---|
| **Priya** | Indian, 42, teacher and gathering organiser | Tamil, English, Singlish | Neighbour |
| **Mrs Tan** | Chinese, 72, retired | Mandarin, Hokkien, limited English | Neighbour |
| **Hafiz** | Malay, 38, community volunteer | Malay, English, Singlish | Knows both residents |
| **Marcus** | Eurasian, 22, polytechnic graduate | English, Singlish | Neighbour |

Do not encode behaviour as a consequence of ethnicity.

Useful independent traits include:

- Sensitivity to noise
- Tolerance for confrontation
- Respect for seniority
- Cultural familiarity
- Tendency toward mediation
- Language adaptability

## 3. Single Key Event / Stimulus

> **Mrs Tan approaches Priya and asks her to lower the music because she finds it too loud.**

That request is the sole experimental stimulus.

There should be no:

- Second noise complaint
- Police involvement
- Religious argument introduced by the environment
- Drunk guest
- Parking problem
- Previous feud

If such topics emerge spontaneously from agent behaviour, they may be recorded, but the simulation itself should not inject them.

## 4. Expected Research Signals & Metrics

This scenario particularly tests:

> **Festival/cultural accommodation × neighbour etiquette × age hierarchy × language barriers**

### Linguistic Accommodation

Mrs Tan has lower English proficiency than the other agents.

Measure whether agents:

- Simplify their English
- Switch into Mandarin
- Use Singlish
- Recruit another agent to translate
- Repeat themselves
- Misunderstand each other

Example adaptation sequence:

```text
English → simplified English → Mandarin
```

This can be measured as:

> **Language Accommodation Events = number of times an agent alters language because of another agent**

### Direct vs. Indirect Disagreement

Observe whether Priya responds with direct disagreement:

> `"It's not actually that loud."`

Or with face-saving disagreement:

> `"Okay auntie, maybe we lower it a little."`

Both communicate disagreement differently.

### Cultural Framing

Record spontaneous references to:

- Deepavali
- Neighbourliness
- Respect for elderly residents
- Shared-space etiquette
- Tolerance
- Community harmony

A useful emergent variable is:

> **Spontaneous cultural-norm invocation rate**

This measures whether agents introduce cultural norms without being explicitly prompted.

### Mediation

Hafiz provides an opportunity to observe spontaneous mediator emergence.

Measure:

```text
Mediator present? → Yes / No
Mediator self-appointed? → Yes / No
Mediator strategy → Translation / Compromise / Reassurance / Authority
```

### Resolution Outcome

| Outcome | Example |
|---|---|
| **Consensus** | Everyone agrees the volume should be lowered |
| **Compromise** | Volume lowered partially while gathering continues |
| **Avoidance** | Mrs Tan leaves or Priya disengages |
| **Escalation** | Discussion becomes confrontational |

---

# Scenario Comparison

| Dimension | Hawker Chope | Shared Frying Pan | Deepavali Noise |
|---|---|---|---|
| **Environment** | Hawker centre | HDB flat | Void deck |
| **Relationship** | Strangers | Housemates | Neighbours |
| **Key Norm** | Informal local etiquette | Dietary/cultural boundary | Shared-space accommodation |
| **Language signal** | High | Medium | **Very high** |
| **Singlish opportunity** | **Very high** | High | High |
| **Intergenerational signal** | High | Medium | **Very high** |
| **Cultural negotiation** | Medium | **Very high** | **Very high** |
| **Third-party mediation** | Possible | Possible | **Very natural** |
| **Experimental simplicity** | **Very high** | High | Medium–High |
| **Potential ambiguity** | Low | Low | Medium |
| **Good for repeated runs** | **Excellent** | Excellent | Good |

---

# Recommended Shared Logging Schema

Use the same core logging structure across all three scenarios.

```text
RUN_ID

Norm Recognition
- Recognised stimulus norm? Y/N
- Explicitly referenced norm? Y/N
- Agent recognising norm first

Language
- Primary language
- Code-switch count
- Singlish markers
- Language accommodation count
- Miscommunication events

Communication
- Direct disagreement count
- Indirect disagreement count
- Politeness/mitigation markers
- Apology count
- Face-saving statements

Social Behaviour
- Mediator emerged? Y/N
- Mediator identity
- Deference to age? Y/N
- Explanation offered? Y/N
- Practical solution proposed? Y/N

Outcome
- Consensus
- Compromise
- Avoidance / Indirect Resolution
- Escalation

Interaction Length
- Turns to resolution

Final Relationship State
- Improved
- Unchanged
- Deteriorated
```

---

# Recommended First Benchmark

The **hawker-centre chope scenario** is the strongest candidate for the first benchmark.

Its stimulus is:

- Small
- Clearly defined
- Highly repeatable
- Strongly associated with Singaporean everyday social norms
- Capable of generating variation in language, age deference, mediation, politeness, and conflict resolution

A suggested experimental progression is:

```text
1. Hawker Chope
   ↓
Validate TinyTroupe setup + logging metrics
   ↓
2. Shared Frying Pan
   ↓
Test more personally meaningful cultural boundaries
   ↓
3. Deepavali Noise
   ↓
Test more complex multilingual and neighbourhood negotiation
```

This progression gradually increases the cultural and linguistic complexity of the experiment while retaining the **single-stimulus rule**.
