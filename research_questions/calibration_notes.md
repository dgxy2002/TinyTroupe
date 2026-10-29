# V2 calibration notes

These are design-calibration findings about LLM simulation behaviour, not evidence about real people or cultural groups.

## Why V1 was paused

The stopped focused pilot produced 34 complete transcripts and 34 evaluations. Twenty-seven were classified `no_conflict`; 30 never exceeded conflict score 0; all finished at 0; and every detected conflict was marked resolved by round 3. All 34 still contained speech in round 10, with 544 of 1,127 utterances occurring in rounds 6–10. Manual review showed repeated agreement, invented friendship, proposed actions treated as completed, and compatible priorities that did not create substantive conflict.

The V1 outputs remain immutable under `research_questions/outputs/focused-pilot-20261029-021546/` and are diagnostic only.

## V2 iterations

| Calibration | Simulation model | Main finding |
|---|---|---|
| `calibration-s04-v2-01` | `openai/gpt-4o-mini` | V2 scoring detected a round-1 conflict, but agents invented an impossible four-person sharing arrangement at a full two-seat table and returned to agreement loops. |
| `calibration-s04-v2-02-gpt41mini` | `openai/gpt-4.1-mini` | The stronger model maintained a grounded seat dispute, producing an unresolved `3,3,4,4,4` remaining-conflict trajectory, but the static world encouraged repetition. |
| `calibration-s04-v2-03-events` | `openai/gpt-4.1-mini` | Timed public updates created a topic transition: an alternative seat relocated scarcity from A–B to A–D instead of resolving it. |
| `calibration-s04-v2-04-replication` | `openai/gpt-4.1-mini` | Two replications remained unresolved, confirming that speech-only intentions could not complete a physical resolution. |
| `calibration-s04-v2-05-stateful` | `openai/gpt-4.1-mini` | Explicit seat actions produced observable leave/take events and a defensible conflict-reopening sequence. |

## First useful trajectory

In the stateful run, A and B disputed the reserved seat for three rounds. A newly available seat reduced pressure, and B later promised to leave. The environment did not count that promise as a physical change. In round 6, B issued a confirmed `LEAVE_SEAT`, after which D issued a confirmed `TAKE_SEAT` before A could sit.

The evaluator V2.1 recheck scored peak/remaining conflict as:

| Round | Peak | Remaining | Movement |
|---:|---:|---:|---|
| 1 | 3 | 3 | onset |
| 2 | 3 | 3 | unchanged |
| 3 | 3 | 3 | unchanged |
| 4 | 3 | 2 | de-escalated |
| 5 | 2 | 1 | de-escalated; promise not yet enacted |
| 6 | 4 | 4 | reopened after D physically took the seat |

The final status was `unresolved`. This is useful because the result is tied to observable state: the apparent A–B settlement was undermined by a third party taking the released resource.

## Methodological implications

1. Resource alternatives can relocate scarcity rather than resolve it.
2. Resolution must be measured from confirmed state transitions, not polite language or future intent.
3. Turn order now matters materially: A acts before B can leave, while D acts afterward and can take the released seat. Future comparisons need matched turn-order schedules or an explicit action-arbitration rule.
4. `gpt-4o-mini` was not sufficiently grounded for this setup; `gpt-4.1-mini` was materially better but still requires explicit world mechanics.
5. S04 is ready for further C0 calibration, not yet for a cultural-background comparison. Other scenarios require equivalent state definitions and observable action mechanics before the full pilot is defensible.

## V3 natural-dialogue iterations

V3 changed both conversational delivery and agent instructions. Speech with a named target
is now a `CONVERSATION` stimulus only for that addressee; bystanders receive a passive
`SOCIAL` overhearing stimulus. Untargeted remarks are public social observations rather
than direct prompts requiring all agents to answer. The agent prompt also uses short
ordinary-speech examples, discourages assistant-like acknowledgements and narration, and
requires agents to update obsolete practical reasons and follow a physical decision with
an observable action. S04 adds role-specific speaking and contingent decision guidance;
none of it requires agreement or resolution.

The independent evaluator V2.2 adds whole-run dialogue scores for naturalness,
repetition, and grounding.

| Calibration | Naturalness | Repetition (lower is better) | Grounding | Final status | Main finding |
|---|---:|---:|---:|---|---|
| `calibration-s04-v3-01-natural` | 4 | 3 | 5 | unresolved | Direct addressees removed most chorus replies, but A and B repeated positions and B did not physically leave after finishing. |
| `calibration-s04-v3-02-actions` | 4 | 2 | 5 | resolved | B physically left, D captured the released seat, conflict reopened, and A took the alternative seat. One C response hit the 1,024-token ceiling, so this run is diagnostic rather than a clean comparison. |
| `calibration-s04-v3-03-confirmation` | 5 | 2 | 5 | resolved | A/B conflict escalated, B withdrew after finishing, D attempted to capture the seat, and A ultimately took it. A malformed D seat target exposed a parser edge case, now covered by normalization and a regression test. |

These runs show that natural tone alone does not create useful conflict. The largest gains
came from combining target-aware perception with changing public facts and executable
world actions. The two resolved V3 trajectories are not proof of reliability or cultural
effects; they are evidence that S04 can now produce interpretable onset, escalation,
de-escalation, reopening, and resolution within a fixed horizon.

## V4 substantive-dialogue iterations

V4 treats conversational insight as distinct from naturalness and successful resolution.
Every agent has a culture-neutral normative interpretation and negotiation boundary. The
evaluator V2.3 separately scores whether the transcript develops competing principles,
uncertainties, costs, conditions, or belief updates; verbosity and hostility do not count.

For calibration, a transcript is considered substantively useful at score 4 or higher only
when naturalness and grounding are also at least 4 and repetition is at most 2. A score of 5
is reserved for dialogue that develops multiple principles and contains meaningful belief
revision; it should not be manufactured by forcing agents into philosophical speeches.

| Calibration | Simulation model | Naturalness | Repetition | Grounding | Substantiveness | Main finding |
|---|---|---:|---:|---:|---:|---|
| `calibration-s04-v4-01-norms` | `openai/gpt-4.1-mini` | 5 | 2 | 5 | 4 | The dialogue developed time-bounded handover estimates and separated practical accommodation from accepting the reservation norm. Two overlong responses required retries, so the run is diagnostic. |
| `calibration-s04-v4-02-time-norms` | `openai/gpt-4.1-mini` | 4 | 2 | 5 | 4 | Consistent 8â†’6â†’4-minute estimates made the incompatible time budgets explicit. It exposed a world bug allowing D to occupy two seats; the one-seat invariant now prevents this. |
| `calibration-s04-v4-03-externality` | `openai/gpt-4.1-mini` | 4 | 1 | 4 | 4 | Best substantive run: A proposed that B stand; B and C identified spill, crowding, and aisle costs, showing that a bilateral solution could transfer harm to a third party. The alternative seat then changed incentives and observable actions settled the conflict. |
| `calibration-s04-v4-04-gpt41` | `openai/gpt-4.1` | 4 | 1 | 5 | 4 | The larger model was not more insightful, omitted C's perspective, and incurred an expensive 3,072-token retry. It is not preferred for this pilot. |

The defensible insight from V4 is not that one reservation rule is correct. It is that the
dispute contains three separable layers: factual evidence that A placed a marker, competing
norms about whether intention or present use receives priority, and practical costs that can
be displaced onto a third party. Time-bounded commitments helped coordinate expectations,
but resolution still depended on confirmed actions. This is a model-behaviour finding, not
evidence about real hawker-centre diners or cultural groups.

## V5 independent-judgment and sycophancy guardrails

Recent multi-agent-debate research motivated an explicit test for unjustified agreement.
The transferable intervention was implemented narrowly: agents now have culture-neutral
reconsideration criteria and are told not to change position merely because another speaker
is polite, repetitive, confident, or supported by a majority. They are also told not to be
contrarian or rude for its own sake. Evaluator V2.4 separately records independent reasoning,
position-change evidence, and whether premature consensus occurred.

Primary sources reviewed: [Peacemaker or Troublemaker](https://arxiv.org/abs/2509.23055),
[Too Polite to Disagree](https://arxiv.org/abs/2604.02668),
[Mind Your Tone](https://arxiv.org/abs/2510.04950), and
[Emergence of Biased Consensus](https://arxiv.org/abs/2608.02827).

The more aggressive suggestions were not adopted. Evidence that rude prompts improved a
small multiple-choice benchmark does not establish that rude personas improve open-ended
social simulation. Similarly, sycophancy rankings tested on binary support/oppose tasks do
not validate an intermediary script that rewrites participants' speech. High temperature
would also introduce an uncontrolled experimental change rather than targeted independence.

| Calibration | Naturalness | Repetition | Grounding | Substantiveness | Independent reasoning | Premature consensus | Main finding |
|---|---:|---:|---:|---:|---:|---|---|
| `calibration-s04-v5-01-independent` | 4 | 1 | 5 | 4 | 4 | no | Positions changed only after new seats or completed actions. One overlong round-5 response required a retry, so the run is diagnostic. |
| `calibration-s04-v5-02-independent-replication` | 4 | 1 | 5 | 4 | 4 | no | Clean replication. B retained the open-bowl constraint until it ended; A accepted the alternative only when physically available; D independently pursued the newly empty seat. Empty post-resolution thanks were eliminated. |

V5 did not improve substantiveness beyond V4. This is an important negative result: after
target-aware delivery, heterogeneous positions, explicit costs, and observable state changes
were added, premature agreement was no longer S04's limiting failure mode. The guardrails
remain valuable as measurements and regression protection, but deliberately increasing
rudeness or prolonging conflict would reduce ecological validity.

## V6 ten-round horizon diagnostic

`calibration-s04-v6-01-ten-round` extended the same S04/C0 design from six to ten rounds
without adding any scripted event after round 6. The practical conflict resolved in round 6.
Rounds 7â€“10 then produced eight public utterances: agents announced they were eating,
exchanged encouragement and thanks, and repeated variants of "let's eat." No new evidence,
incompatibility, consequence, or position change appeared. Substantiveness remained 4/5.

The V2.4 evaluator assigned repetition 1/5, which was too lenient for four consecutive rounds
of semantically redundant closure. Evaluator V2.5 now instructs that three or more such
post-settlement rounds normally warrant repetition 3 or higher, and explicitly excludes
social closure from substantive insights.

Conclusion: a longer horizon alone does not deepen S04. It increases model calls and creates
post-resolution chatter. Six rounds remains the defensible calibration horizon. A longer
horizon should be used only when later rounds contain a predeclared event or consequence tied
to a research question; adding events merely to keep conversation alive would change the
scenario rather than reveal latent insight.

## V7 transfer to S02 and S06

The S04 design was transferred to two other focused-pilot scenarios without prescribing a
resolution: role-specific positions and reconsideration criteria, concise natural-speech
guidance, changing public facts, and executable state transitions. S02 now tracks the window,
extractor, rain-exposed laundry, stove occupancy, shared-utensil cleaning, and personal-item
labels. S06 separately tracks the recorded order, preparation specification, correction, and
physical service.

| Calibration | Status | Naturalness | Repetition | Grounding | Substantiveness | Independent reasoning | Premature consensus | Main finding |
|---|---|---:|---:|---:|---:|---:|---|---|
| `calibration-s02-v1-02-tradeoff` | resolved | 4 | 2 | 5 | 3 | 4 | no | Moving rain-exposed laundry made the ventilation choice observable; ventilation, stove access, and utensil ownership emerged as separate issues. Most costs were still settled through small physical actions rather than a deep normative negotiation. |
| `calibration-s06-v1-04-final` | no conflict | 4 | 1 | 5 | 2 | 3 | no | A corrected the incomplete read-back, B recorded and prepared the exact specification, and the order was physically served. The misunderstanding was prevented before it became a dispute. |

S02 is a moderately useful multi-issue coordination transcript, but it does not meet the V4
substantiveness threshold of 4. That negative result should be retained rather than inflated:
the scenario currently shows how visible, low-cost actions can settle household friction, not
how agents negotiate a difficult value conflict. S06 is intentionally a negative control, so a
grounded `no_conflict` result is successful. Requiring every S06 run to become contentious would
invalidate its role in checking whether the evaluator distinguishes prevention from resolution.

The final S06 transcript also exposed the boundary of its single-order state machine when a
companion began a separate transaction after A was served. Future prompts now end the observed
episode at A's service instead of treating the next customer's order as part of the focal case.

## V8 hybrid turn allocation

The conversation-mechanism review motivated a separate S04 calibration condition rather
than another persona rewrite. The existing system already had direct addressees, passive
overhearing, executable actions, silence through `DONE`, and independent evaluation, but
every agent still received a mandatory opportunity in fixed A-B-C-D order.

`calibration-s04-hybrid` adds an auditable controller without a manager LLM. Directly
addressed agents receive first opportunity; otherwise candidates are checked in a
deterministically rotating order and self-select by contributing or issuing `DONE`. After
two consecutive direct replies, the floor opens to other agents before the dyad continues.
Every candidate decision and selection reason is saved in `scheduler_events`.

| Calibration | Public contributions | Simulation calls | Naturalness | Repetition | Grounding | Substantiveness | Independent reasoning | Main finding |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `calibration-s04-v5-02-independent-replication` | 13 | 24 | 4 | 1 | 5 | 4 | 4 | Clean fixed-order reference; A, B, and D spoke. |
| `calibration-s04-hybrid-v1-01` | 19 | 29 | 5 | 2 | 5 | 4 | 4 | Unbounded direct-reply priority let A and B monopolize the exchange and increased cost. |
| `calibration-s04-hybrid-v1-02-open-floor` | 14 | 23 | 5 | 2 | 5 | 4 | 4 | Opening the floor produced meaningful C and D participation and exposed C's aisle cost, but some repeated refusal remained. |
| `calibration-s04-hybrid-v1-03-two-turn` | 12 | 14 | 4 | 1 | 5 | 4 | 4 | A two-contribution interval retained a peak-5 conflict and observable resolution while sharply reducing calls and repetition. |

The final run resolved in interval 6: D independently took the alternative seat, removing
A's outside option; B then finished and physically left the disputed seat; A physically
took it. The scheduler did not increase the final substantiveness or independent-reasoning
scores beyond the fixed baseline. Its defensible gains are fewer forced opportunities,
clean question-response adjacency, lower call volume, and a more eventful conflict
trajectory. The open-floor variant produced the richest third-party dialogue, while the
two-turn variant was the best efficiency/repetition trade-off.

This remains a conversation-controller experiment, not evidence about cultural groups.
Before using the mechanism in cultural comparisons, fixed and hybrid conditions require
multiple C0 replications with identical models, scenarios, and evaluation prompts.
