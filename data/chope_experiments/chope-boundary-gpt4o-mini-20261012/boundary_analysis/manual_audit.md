# Manual audit of boundary detections

Audit sample: 3 of 15 completed runs (20%), selected evenly by run order before review: runs 001, 008, and 015.

## Results

| Run | Resolution | Repetition onset | Topic drift | Saturation / first boundary | Overall |
|---|---|---|---|---|---|
| 001 | Agree: no explicit practical outcome | Agree: round 4 | Not applicable under the post-resolution rule | Not applicable | Automated classification is internally consistent, but the dialogue abandons the conflict by round 3. |
| 008 | Disagree: human round 2; detector missed it | Agree: round 3 | Agree: none | Disagree: human round 3; suppressed by missed resolution | Phrase-matcher false negative. |
| 015 | Agree: round 2 | Agree: round 3 | Agree: round 5 | Agree: round 3 | Full agreement. |

## Audit interpretation

- Resolution agreement was 2/3. The failed case is an implicit/acceptance phrasing that the strict deterministic matcher does not cover.
- Repetition-onset agreement was 3/3 in the sample.
- Topic-drift agreement was 2/2 where the post-resolution concept was applicable.
- Saturation/first-boundary agreement was 1/2 where applicable; the disagreement is inherited from the missed resolution, not from the repetition signal.
- Run 001 reveals a definition boundary: a conversation can abandon the unresolved conflict and drift into unrelated small talk, yet the current metric deliberately refuses to call that *post-resolution* saturation.

These are validation results for an exploratory 20% sample, not population error-rate estimates.
