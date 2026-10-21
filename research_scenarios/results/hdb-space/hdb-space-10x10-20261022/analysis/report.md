# hdb-space resolution and repetition report

Experiment: `hdb-space-10x10-20261022`  
Model: `openai/gpt-4o-mini`  
Fixed horizon: 10 rounds  
Completed runs: 10/10  

## Main results

- Resolved: 5/10 (50.0%); median first-resolution round: 3.
- Repetitive: 5/10 (50.0%); median repetition-onset round: 5.
- Total tokens (simulation, evaluation, and embeddings): 3,178,540.
- Total recorded cost: $0.405889; exact cost metadata complete: true.

## Category summary

| Final category | Runs | Share |
|---|---:|---:|
| Resolved + repetitive | 2 | 20.0% |
| Resolved + not repetitive | 3 | 30.0% |
| Unresolved + repetitive | 3 | 30.0% |
| Unresolved + not repetitive | 2 | 20.0% |

## Scenario outcomes

| Outcome | Runs |
|---|---:|
| compromise | 4 |
| consensus | 1 |
| unresolved | 5 |

## Operational definitions

- Resolution: The scenario-specific structured evaluator finds mutually accepted consensus or compromise; the first accepted turn is converted to a round.
- Lexical repetition: mean same-agent similarity >= 0.70, with at least 50% of comparable agents individually >= 0.80.
- Semantic repetition: adjacent-round embedding similarity >= 0.90, plus mean lexical similarity >= 0.15. This can detect the same broad topic expressed using different words.
- Repetition onset: the first of 2 consecutive rounds meeting either repetition rule.
- A run can resolve and later repeat; these are separate measurements. Manual transcript review remains necessary for ambiguous cases.
