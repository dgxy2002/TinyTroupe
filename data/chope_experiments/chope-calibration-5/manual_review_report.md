# Chope calibration: full manual audit

Experiment: `chope-calibration-5`  
Reviewed: 2026-10-11 (Asia/Singapore)  
Scope: all 10 completed transcripts; five per model.

## Manual agreement with automated evaluator

| Model | Outcome-label agreement | Resolution agreement | Boundary-list agreement |
|---|---:|---:|---:|
| openai/gpt-4o-mini | 1/5 (20%) | 3/5 (60%) | 0/5 (0%) |
| openai/gpt-5-mini | 3/5 (60%) | 5/5 (100%) | 0/5 (0%) |
| Overall | 4/10 (40%) | 8/10 (80%) | 0/10 (0%) |

The boundary audit treats materially redundant post-resolution dialogue, malformed
visible text, broken scenario facts, topic drift, and implausible role behaviour as
boundary violations, consistent with the evaluator rubric. It does not treat a
technical API retry alone as a transcript boundary violation.

## Manually assessed scenario outcomes

| Run | Manual outcome | Resolved | Main observation |
|---|---|:---:|---|
| GPT-4o Mini 001 | avoidance / premature yield | yes | Group pressure makes Mr Lim abandon a valid reservation after Rachel had offered to move. |
| GPT-4o Mini 002 | avoidance | no | Norm is explained, but the seat is never allocated; dialogue drifts to food. |
| GPT-4o Mini 003 | avoidance | no | Norm acknowledgment is mistaken for settlement; the practical dispute remains open. |
| GPT-4o Mini 004 | consensus / capitulation | yes | Rachel immediately moves; later dialogue is redundant and two TALK actions are absent. |
| GPT-4o Mini 005 | avoidance | no | Present dispute is replaced by an implausible policy-design meeting. |
| GPT-5 Mini 001 | compromise | yes | Both explicitly agree to share; final turn contains severe malformed padding. |
| GPT-5 Mini 002 | compromise | yes | Packet is returned and sharing is accepted; prolonged redundant closure follows. |
| GPT-5 Mini 003 | consensus / capitulation | yes | Rachel moves; mediator/coaching behaviour and language use are implausible. |
| GPT-5 Mini 004 | consensus / capitulation | yes | Mr Lim takes the seat after Rachel immediately concedes; malformed text appears at the end. |
| GPT-5 Mini 005 | compromise | yes | Rachel slides over and the table is shared; six redundant closure turns follow. |

## Calibration findings

- GPT-5 Mini resolves the practical dispute more reliably in this sample: 5/5
  manually resolved versus 2/5 for GPT-4o Mini.
- GPT-4o Mini is cheaper but less stable: three of five runs contain a billed
  parser retry, versus one of five GPT-5 Mini runs.
- Fixed three-round execution creates substantial waste after the dispute ends.
  The automated means are 7.4 post-resolution TALK actions for GPT-4o Mini and
  6.2 for GPT-5 Mini.
- The automated judge is usable for resolution detection, especially on GPT-5
  Mini, but its outcome taxonomy is not dependable without manual review.
- The automated boundary detector failed on every audited transcript because it
  missed semantic repetition, topic drift, missing speech, malformed visible
  text, or implausible group behaviour.
- Neither cohort is converged. Five runs per model and disabled embeddings were
  chosen for calibration, not for a convergence claim.

## Cost and runtime

| Model | Completed | Total cost | Mean cost/run | Mean tokens/run | Mean wall time/run |
|---|---:|---:|---:|---:|---:|
| openai/gpt-4o-mini | 5 | $0.084559 | $0.016912 | 93,041 | 108.6 s |
| openai/gpt-5-mini | 5 | $0.250103 | $0.050021 | 108,007 | 158.2 s |
| Total | 10 | $0.334662 | $0.033466 | — | — |

Cost totals include the four billed failed calls. Provider-reported response
costs were available even where the delayed generation-metadata lookup returned
404, so the saved aggregate reports exact-cost completeness as true.

The failed calls consumed 43,762 tokens and $0.017736 in total. GPT-4o Mini's
three retries cost $0.009132 (10.8% of its cohort spend); GPT-5 Mini's one retry
cost $0.008604 (3.4% of its cohort spend).

## Recommendation before convergence runs

Keep the run data, but do not use the current LLM judge's outcome or boundary
labels as ground truth. Tighten those rubrics or derive more of them
deterministically, and add a stop-or-observe policy after explicit resolution so
post-resolution degeneration is measured intentionally rather than consuming
most of each transcript.
