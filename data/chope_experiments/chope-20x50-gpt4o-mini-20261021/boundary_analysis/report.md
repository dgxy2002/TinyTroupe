# Chope resolution and repetition report

Experiment: `chope-20x50-gpt4o-mini-20261021`  
Model: `openai/gpt-4o-mini`  
Fixed horizon: 50 rounds  
Completed runs: 20  

## Main results

- Resolved: 17/20 (85.0%); median first-resolution round: 2.
- Repetitive: 20/20 (100.0%); median first-repetition round: 3.5.
- Simulation tokens: 32,479,027.
- Simulation cost: $3.502086.

## Category summary

| Final category | Runs | Share |
|---|---:|---:|
| Resolved + repetitive | 17 | 85.0% |
| Resolved + not repetitive | 0 | 0.0% |
| Unresolved + repetitive | 3 | 15.0% |
|    | 0 | 0.0% |

Unresolved by round 50: 3/20.  
No repetition detected by round 50: 0/20.

## Operational definitions

- Resolution: The structured evaluator's first accepted practical-resolution turn, converted to its simulation round.
- An agent utterance repeats when normalized sequence similarity is at least 0.80 relative to the same agent's preceding-round utterance.
- A repeated-round candidate requires mean same-agent similarity of at least 0.70 and at least 50% of comparable agents to repeat.
- With round embeddings, semantic similarity of at least 0.90 plus a lexical floor of 0.15 also qualifies.
- Repetition onset is the first of 2 consecutive repeated-round candidates.
- Manual transcript review remains necessary for ambiguous cases.
