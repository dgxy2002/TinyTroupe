# Chope long-horizon boundary report

Experiment: `chope-boundary-calibration-20261012`  
Model: `openai/gpt-4o-mini`  
Fixed horizon: 8 rounds  
Completed runs: 1  

## Boundary results

- Practical-resolution rate: 100.0%; median round: 1.
- Topic-drift rate: 100.0%; median onset: 4.
- Repetition-onset rate: 100.0%; median round: 6.
- Saturation rate: 100.0%; median round: 6.
- Earliest detected boundary rate: 100.0%; median round: 4.
- Mean forced continuation after resolution: 7.00 rounds.
- Post-boundary simulation tokens: 127,420 (53.7%).
- Post-boundary simulation cost: $0.013353 (51.6%).
- Post-saturation simulation tokens: 64,556 (27.2%).
- Post-saturation simulation cost: $0.006798 (26.3%).
- Runs containing escaped control fragments: 0/1.

## Operational definitions

- An agent utterance repeats when normalized sequence similarity is at least 0.80 relative to the same agent's preceding-round utterance.
- A repeated-round candidate requires mean same-agent similarity of at least 0.70 and at least 50% of comparable agents to repeat.
- With round embeddings, semantic similarity of at least 0.90 plus a lexical floor of 0.15 also qualifies.
- Topic drift requires two consecutive post-resolution rounds with semantic relevance to round 1 below 0.75.
- Saturation is the First of two consecutive repeated-round candidates strictly after practical resolution.
- These are lexical operationalizations. Manual transcript review remains necessary for paraphrases and genuinely new social developments.
