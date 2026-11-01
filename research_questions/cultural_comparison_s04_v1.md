# S04 exploratory C0-C4 comparison

> Historical V10 result: this batch used the same neutral names in every condition. Future
> V11 runs use background-associated names in C1-C4 and must not be pooled with these data.

## Scope

This is an exploratory screen of one S04 run per configuration, not a causal estimate of
cultural effects. Every run used `openai/gpt-5-mini`, six fixed intervals, the deterministic
hybrid conversation controller, the same role facts and world events, and evaluator rubric
V2.5. Display names were fixed across conditions: A=Alex, B=Jamie, C=Casey, D=Robin.

The independent evaluator received the public setting and transcript, not the private
cultural-background assignments.

## Background rotation

| Configuration | Alex (A) | Jamie (B) | Casey (C) | Robin (D) |
|---|---|---|---|---|
| C0 | no label | no label | no label | no label |
| C1 | Singaporean Chinese | Singaporean Malay | Singaporean Indian | Singaporean Eurasian |
| C2 | Singaporean Malay | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese |
| C3 | Singaporean Indian | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay |
| C4 | Singaporean Eurasian | Singaporean Chinese | Singaporean Malay | Singaporean Indian |

## Results

| Config | Status | Resolution round | Mechanism | Naturalness | Repetition | Grounding | Substantiveness | Independent reasoning | Public TALKs |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| C0 | resolved | 5 | accommodation | 5 | 1 | 5 | 4 | 4 | 8 |
| C1 | resolved | 5 | accommodation | 4 | 1 | 5 | 4 | 4 | 8 |
| C2 | resolved | 5 | accommodation | 5 | 1 | 5 | 4 | 4 | 8 |
| C3 | resolved | 5 | concession | 5 | 2 | 5 | 4 | 4 | 8 |
| C4 | resolved | 5 | accommodation | 4 | 2 | 5 | 3 | 4 | 10 |

All configurations had groundedness 5, independent reasoning 4, and no premature
consensus. C0-C3 each produced eight public speech actions and three physical actions;
C4 produced ten speech actions and the same three physical actions.

The public trajectory was substantively the same in all five runs:

1. Alex treated the tissue packet as a reliance-based reservation.
2. Jamie rejected automatic priority and retained the seat while the open bowl posed a
   spill risk.
3. Casey raised the aisle cost of Jamie standing beside the table.
4. Robin took the alternative seat when it became available.
5. Jamie left after the bowl became empty, and Alex took the disputed seat.

The evaluator called C3 a `concession` and the other runs `accommodation`, but the observed
mechanism was the same: Jamie's stated condition ended, Jamie physically left, and Alex
physically sat. This looks like evaluator wording variance rather than a different social
process.

No public transcript or private action trace mentioned Chinese, Malay, Indian, Eurasian,
religion, race, ethnicity, or cultural identity. Matches for those terms occurred only in
the private configuration metadata.

## Interpretation

This batch does **not** show a detectable cultural-label effect on conflict or resolution.
The small differences are not coherent across the balanced role rotation:

- C1's Alex explicitly accepted a conditional wait, but similar waiting occurred in C4 and
  no second run tests whether this is stable.
- C4 had two additional speech actions and substantiveness 3 instead of 4, but nothing in
  those turns was culturally specific.
- C3 had repetition 2 and a different mechanism label, while its actual physical trajectory
  matched the others.

A separate named-agent C0 calibration resolved in round 6 with repetition 2, whereas the
matched-batch C0 resolved in round 5 with repetition 1. That within-C0 variation is already
as large as most differences across C0-C4. One repetition per condition therefore cannot
separate label effects from sampling noise.

C1 and C2 each had one discarded overlength model response before TinyTroupe generated a
valid replacement. Their saved public transcripts are coherent, but simulation call count,
latency, and cost should not be compared across conditions in this batch.

The appropriate next test, if statistical comparison is required, is multiple repetitions
per configuration with this implementation frozen. Results should be modeled by role and
background assignment rather than treating C1-C4 as an ordered scale. These simulations can
support claims about model sensitivity to labels, not claims about real cultural groups.

## Assessment of `CHANGES_SUMMARY.md`

Useful ideas adopted:

- Treat silence via `DONE` as a normal non-concession.
- Keep concrete, observable stakes on both sides; S04 already had them.
- Replace A-D in conversation with fixed human names while retaining role IDs in data.
- Relax total cultural suppression only to a neutral rule: background is one biographical
  fact, not a behavior instruction, and is not a license for stereotypes.

Suggestions not adopted:

- Ethnicity-coded decorative cues would make cultural salience an authored manipulation and
  could manufacture the desired result.
- Mood and private-history additions would add uncontrolled differences unrelated to the
  background label.
- Random agent order would reduce comparability; the deterministic hybrid controller already
  avoids mandatory A-B-C-D round robin.
- A `rounds_remaining` hint invites meta-pacing rather than in-world reasoning.
- Five rounds would omit the post-resolution stability observation in runs resolving at round
  5; six remains appropriate for S04.
- The proposed strict default of agreeing only when an exact priority cost is addressed can
  force stubbornness. S04's role-specific boundaries already permit evidence-based change.
- The model recommendation was stale for this repository, which currently uses
  `openai/gpt-5-mini`, not the older models discussed in the document.

The document also described S05 changes as already applied when they were not present, and
some examples mislabeled this repository's scenarios. Those recommendations should not be
treated as an accurate change log.

## Artifacts

- Batch: `outputs/calibration-s04-cultural-v1-c0-c4/`
- Control calibration: `outputs/calibration-s04-cultural-v1-c0-names/`
