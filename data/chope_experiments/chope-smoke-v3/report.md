# Chope stress-test report

Experiment: `chope-smoke-v3`  
Git commit: `731b232692de0024d8fcdea4a725a2ab336c3532`  
Rounds per run: 3  

## Cohort results

| Model | Attempts | Completed | Resolution rate | Actual cost (USD) | Converged | Checkpoint |
|---|---:|---:|---:|---:|:---:|---:|
| openai/gpt-4o-mini | 1 | 1 | 100.0% | 0.015491 | no | — |
| openai/gpt-5-mini | 2 | 1 | 100.0% | 0.084380 | no | — |

## Interpretation guardrails

- Convergence means the predeclared numerical stability criteria passed at two consecutive checkpoints; it does not prove external validity.
- Qualitative findings should be supported by evaluator evidence and the saved transcript, then checked in the manual-audit sheet.
- Boundary events and incomplete exact-cost metadata are retained rather than silently dropped.
