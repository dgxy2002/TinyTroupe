# Chope experiment report

Experiment: `chope-boundary-calibration-20261012`  
Git commit: `a4bcf6a724974a0a0a7375be34f17ba1c21d6685`  
Execution mode: `stress`  
Maximum rounds per run: 8  

## Cohort results

| Model | Attempts | Completed | Deterministic resolution | Judge resolution | Mean rounds | Early stop | Actual cost (USD) | Converged | Checkpoint |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|---:|
| openai/gpt-4o-mini | 1 | 1 | 0.0% | 100.0% | 8.00 | n/a | 0.033026 | no | — |

## Interpretation guardrails

- Convergence means the predeclared numerical stability criteria passed at two consecutive checkpoints; it does not prove external validity.
- Qualitative findings should be supported by evaluator evidence and the saved transcript, then checked in the manual-audit sheet.
- Boundary events and incomplete exact-cost metadata are retained rather than silently dropped.
