# Chope experiment report

Experiment: `20261011-223613`  
Git commit: `a4bcf6a724974a0a0a7375be34f17ba1c21d6685`  
Execution mode: `stress`  
Maximum rounds per run: 3  

## Cohort results

| Model | Attempts | Completed | Deterministic resolution | Judge resolution | Mean rounds | Early stop | Actual cost (USD) | Converged | Checkpoint |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|---:|
| openai/gpt-4o-mini | 30 | 30 | 33.3% | 100.0% | 3.00 | n/a | 0.443751 | yes | 30 |
| openai/gpt-5-mini | 20 | 20 | 30.0% | 100.0% | 3.00 | n/a | 0.970098 | yes | 20 |

## Interpretation guardrails

- Convergence means the predeclared numerical stability criteria passed at two consecutive checkpoints; it does not prove external validity.
- Qualitative findings should be supported by evaluator evidence and the saved transcript, then checked in the manual-audit sheet.
- Boundary events and incomplete exact-cost metadata are retained rather than silently dropped.
