# Chope long-horizon boundary report

Experiment: `20261011-223613`  
Model: `openai/gpt-4o-mini`  
Fixed horizon: 3 rounds  
Completed runs: 50  

## Boundary results

- Practical-resolution rate: 58.0%; median round: 1.
- Repetition-onset rate: 0.0%; median round: n/a.
- Saturation rate: 0.0%; median round: n/a.
- Mean forced continuation after resolution: 0.86 rounds.
- Post-saturation simulation tokens: 0 (0.0%).
- Post-saturation simulation cost: $0.000000 (0.0%).
- Runs containing escaped control fragments: 13/50.

## Operational definitions

- An agent utterance repeats when normalized sequence similarity is at least 0.80 relative to the same agent's preceding-round utterance.
- A repeated-round candidate requires mean same-agent similarity of at least 0.70 and at least 50% of comparable agents to repeat.
- Saturation is the First of two consecutive repeated-round candidates strictly after practical resolution.
- These are lexical operationalizations. Manual transcript review remains necessary for paraphrases and genuinely new social developments.
