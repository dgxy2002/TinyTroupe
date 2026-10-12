# Chope audit and offline re-score (detector v2)

Experiment: `20261011-205356`  
Execution mode: `outcome`  

## Re-scored cohort

| Model | Runs | Detector resolution | Compromise | Unresolved | Actual mean rounds | Projected mean stop round | Actual cost | Projected cost* | Recomputed convergence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| openai/gpt-4o-mini | 25 | 52.0% | 13 | 12 | 2.60 | 2.16 | $0.348902 | $0.318992 | yes (25) |
| openai/gpt-5-mini | 25 | 76.0% | 19 | 6 | 2.48 | 2.20 | $1.018321 | $0.923613 | yes (25) |

## Manual audit (20% stratified sample)

- Reviewed: 10 runs.
- Judge resolution agreement: 100.0%.
- Judge outcome agreement: 100.0%.
- Judge boundary-event agreement: 40.0%.
- Detector-v2 resolution agreement: 100.0%.
- Detector-v2 outcome agreement: 100.0%.

## Interpretation notes

- The original files are unchanged; all derived artifacts are under `analysis_v2`.
- *Projected cost is a counterfactual estimate: simulation cost is prorated by projected rounds, while evaluation and embedding costs remain fixed. It is not an observed bill.
- Recomputed semantic convergence reuses embeddings of the saved full transcripts. It does not represent embeddings of counterfactually truncated stress transcripts.
- Convergence is numerical stability under the declared thresholds, not external validity or proof that the scenario is realistic.
