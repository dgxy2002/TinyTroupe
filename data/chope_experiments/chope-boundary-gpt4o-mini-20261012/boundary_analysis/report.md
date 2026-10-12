# Chope long-horizon boundary report

Experiment: `chope-boundary-gpt4o-mini-20261012`  
Model: `openai/gpt-4o-mini`  
Fixed horizon: 8 rounds  
Completed runs: 15  

## Boundary results

- Practical-resolution rate: 40.0%; median round: 1.
- Topic-drift rate: 33.3%; median onset: 4.
- Repetition-onset rate: 60.0%; median round: 4.
- Saturation rate: 33.3%; median round: 4.
- Earliest detected boundary rate: 40.0%; median round: 3.
- Mean forced continuation after resolution: 2.73 rounds.
- Post-boundary simulation tokens: 895,485 (24.4%).
- Post-boundary simulation cost: $0.097363 (24.6%).
- Post-saturation simulation tokens: 697,923 (19.0%).
- Post-saturation simulation cost: $0.075074 (18.9%).
- Runs containing escaped control fragments: 2/15.

## Operational definitions

- An agent utterance repeats when normalized sequence similarity is at least 0.80 relative to the same agent's preceding-round utterance.
- A repeated-round candidate requires mean same-agent similarity of at least 0.70 and at least 50% of comparable agents to repeat.
- With round embeddings, semantic similarity of at least 0.90 plus a lexical floor of 0.15 also qualifies.
- Topic drift requires two consecutive post-resolution rounds with semantic relevance to round 1 below 0.75.
- Saturation is the First of two consecutive repeated-round candidates strictly after practical resolution.
- These are lexical operationalizations. Manual transcript review remains necessary for paraphrases and genuinely new social developments.

## Manual-audit and validity notes

- A 20% systematic sample (runs 001, 008, and 015) was reviewed against the raw transcripts. Repetition-onset agreement was 3/3.
- Strict practical-resolution agreement was 2/3. In run 008 the human reviewer and the GPT-5 Mini evaluator found resolution in round 2, while the deterministic phrase matcher missed the acceptance wording. This also suppressed that run's automated saturation/boundary result.
- Across the full cohort, deterministic resolution was 40.0% while the final structured evaluator reported 86.7%; seven runs emitted `resolution_source_disagreement`. Treat post-resolution boundary rates as conservative and detector-dependent.
- Run 001 exposes a definition boundary: the agents abandoned an unresolved seat dispute for unrelated food talk, but the metric intentionally did not call this *post-resolution* drift or saturation.
- Seven recoverable length-limit API failures occurred across six runs. All 15 runs completed, so this is an operational reliability limitation rather than attrition.
- The full experiment cost was $0.504408 and took 50 minutes 44 seconds wall-clock time. GPT-4o-mini generated the simulations; GPT-5 Mini was used only for final structured evaluation.
- Across-run cohort convergence was not tested here: `convergence.csv` contains only the n=15 baseline checkpoint. This experiment measures within-run repetition, drift, and post-resolution saturation over an 8-round fixed horizon.

See [manual_audit.md](manual_audit.md) for the reviewed cases and [manual_review.csv](manual_review.csv) for the audit sheet.
