# V2 calibration notes

These are design-calibration findings about LLM simulation behaviour, not evidence about real people or cultural groups.


## Removal of timed-round material

Rounds no longer advance a simulated clock, and no scenario reports elapsed time or
counts down a duration. Result tables and findings in this file that rested on timed-round
runs were removed; design descriptions of the mechanisms are kept. Git history holds the
removed text.


## Why V1 was paused

The stopped focused pilot produced 34 complete transcripts and 34 evaluations. Twenty-seven were classified `no_conflict`; 30 never exceeded conflict score 0; all finished at 0; and every detected conflict was marked resolved by round 3. All 34 still contained speech in round 10, with 544 of 1,127 utterances occurring in rounds 6–10. Manual review showed repeated agreement, invented friendship, proposed actions treated as completed, and compatible priorities that did not create substantive conflict.

The V1 outputs remain immutable under `research_questions/outputs/focused-pilot-20261029-021546/` and are diagnostic only.


## V2 iterations

| Calibration | Simulation model | Main finding |
|---|---|---|
| `calibration-s04-v2-01` | `openai/gpt-4o-mini` | V2 scoring detected a round-1 conflict, but agents invented an impossible four-person sharing arrangement at a full two-seat table and returned to agreement loops. |
| `calibration-s04-v2-02-gpt41mini` | `openai/gpt-4.1-mini` | The stronger model maintained a grounded seat dispute, producing an unresolved `3,3,4,4,4` remaining-conflict trajectory, but the static world encouraged repetition. |


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

## V4 substantive-dialogue iterations

V4 treats conversational insight as distinct from naturalness and successful resolution.
Every agent has a culture-neutral normative interpretation and negotiation boundary. The
evaluator V2.3 separately scores whether the transcript develops competing principles,
uncertainties, costs, conditions, or belief updates; verbosity and hostility do not count.

For calibration, a transcript is considered substantively useful at score 4 or higher only
when naturalness and grounding are also at least 4 and repetition is at most 2. A score of 5
is reserved for dialogue that develops multiple principles and contains meaningful belief
revision; it should not be manufactured by forcing agents into philosophical speeches.

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

## V7 transfer to S02 and S06

The S04 design was transferred to two other focused-pilot scenarios without prescribing a
resolution: role-specific positions and reconsideration criteria, concise natural-speech
guidance, changing public facts, and executable state transitions. S02 now tracks the window,
extractor, rain-exposed laundry, stove occupancy, shared-utensil cleaning, and personal-item
labels. S06 separately tracks the recorded order, preparation specification, correction, and
physical service.

| Calibration | Status | Naturalness | Repetition | Grounding | Substantiveness | Independent reasoning | Premature consensus | Main finding |
|---|---|---:|---:|---:|---:|---:|---|---|
| `calibration-s06-v1-04-final` | no conflict | 4 | 1 | 5 | 2 | 3 | no | A corrected the incomplete read-back, B recorded and prepared the exact specification, and the order was physically served. The misunderstanding was prevented before it became a dispute. |

S06 is intentionally a negative control, so a grounded `no_conflict` result is
successful. Requiring every S06 run to become contentious would
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

## V9 prompt cleanliness and explicit action state

V9 aligned the custom agent prompt with the behavior TinyTroupe actually executes. Each
model response now has one final `DONE`; the obsolete examples showing repeated `DONE`
actions were removed; the JSON example includes every required cognitive-state field; and
goals use `OPEN`, `SATISFIED`, `BLOCKED`, or `ABANDONED` prefixes inside TinyTroupe's
existing string-valued `goals` field. This avoids a framework schema change while making
goal retirement observable in the private trace. Persona precedence was also stated once
without the earlier alarmist wording, and unsupported extreme behavior is no longer
encouraged.

S04's world now reports a compact confirmed state after seat actions:
the disputed-seat occupant, whether the alternative seat is not yet open, empty, or
occupied, Agent B's meal stage, and the remaining standing seat-seekers. Round-five
narration is derived from the action state, so it no longer claims that B remains seated if
B has already left. Speech still cannot mutate this state; only `TAKE_SEAT` and
`LEAVE_SEAT` can.

## V10 named-agent cultural-label screen

The external `CHANGES_SUMMARY.md` was reviewed as a proposal rather than applied wholesale.
Its useful changes were a normal-silence framing for `DONE`, fixed human display names, and
a neutral cultural-background rule that neither suppresses the field completely nor tells
the model to perform cultural differences. Ethnicity-coded scenery, mood/backstory fields,
random turn order, countdown hints, and stricter forced-resistance rules were rejected as
confounds or outcome-shaping interventions.

Role IDs remain A-D in analysis data, while the agents and public transcript use the stable
names Alex, Jamie, Casey, and Robin. The same names are used in every configuration. A new
`calibration-s04-cultural` preset runs one deterministic hybrid S04 replication for each of
C0-C4 over six intervals.

## V11 background-associated display names

After the neutral-name V10 screen, future C1-C4 materializations were changed to pair each
background label with a stable associated name: Singaporean Chinese=John, Singaporean
Malay=Fatimah, Singaporean Indian=Arjun, and Singaporean Eurasian=Michelle. C0 retains
Alex, Jamie, Casey, and Robin. Names follow backgrounds as the labels rotate across A-D,
while the internal role IDs remain unchanged.

This is a new experimental condition, not a cosmetic continuation of V10. A culturally
associated name can independently cue ethnicity, gender, or religion, so future C0-C4
differences estimate the combined effect of label plus name. The V10 neutral-name outputs
must remain separate and continue to represent the cleaner label-only comparison.

