# Chope experiment report

Experiment: `20261011-205356`  
Git commit: `a4bcf6a724974a0a0a7375be34f17ba1c21d6685`  
Execution mode: `outcome`  
Maximum rounds per run: 3  

## Cohort results

| Model | Attempts | Completed | Deterministic resolution | Judge resolution | Mean rounds | Early stop | Actual cost (USD) | Converged | Checkpoint |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|---:|
| openai/gpt-4o-mini | 25 | 25 | 20.0% | 96.0% | 2.60 | 20.0% | 0.348902 | yes | 25 |
| openai/gpt-5-mini | 25 | 25 | 48.0% | 96.0% | 2.48 | 48.0% | 1.018321 | yes | 25 |

## Interpretation guardrails

- Convergence means the predeclared numerical stability criteria passed at two consecutive checkpoints; it does not prove external validity.
- Qualitative findings should be supported by evaluator evidence and the saved transcript, then checked in the manual-audit sheet.
- Boundary events and incomplete exact-cost metadata are retained rather than silently dropped.
