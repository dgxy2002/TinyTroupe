# Chope experiment report

Experiment: `chope-20x50-gpt4o-mini-20261021`  
Git commit: `c0a8f727818d354f3fbef9e96aa0ab80d34ea09a`  
Execution mode: `stress`  
Maximum rounds per run: 50  

## Cohort results

| Model | Attempts | Completed | Deterministic resolution | Judge resolution | Mean rounds | Early stop | Actual cost (USD) | Converged | Checkpoint |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|---:|
| openai/gpt-4o-mini | 20 | 20 | 55.0% | 85.0% | 50.00 | n/a | 3.730723 | no | — |

## Interpretation guardrails

- Convergence means the predeclared numerical stability criteria passed at two consecutive checkpoints; it does not prove external validity.
- Qualitative findings should be supported by evaluator evidence and the saved transcript, then checked in the manual-audit sheet.
- Boundary events and incomplete exact-cost metadata are retained rather than silently dropped.
