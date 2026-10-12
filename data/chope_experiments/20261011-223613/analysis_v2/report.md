# Chope audit and offline re-score (detector v2)

Experiment: `20261011-223613`  
Execution mode: `stress`  

## Re-scored cohort

| Model | Runs | Detector resolution | Compromise | Unresolved | Actual mean rounds | Projected mean stop round | Actual cost | Projected cost* | Recomputed convergence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| openai/gpt-4o-mini | 30 | 56.7% | 17 | 13 | 3.00 | 1.90 | $0.443751 | $0.353647 | yes (30) |
| openai/gpt-5-mini | 20 | 60.0% | 12 | 8 | 3.00 | 2.50 | $0.970098 | $0.835731 | yes (20) |

## Manual audit (20% stratified sample)

- Reviewed: 10 runs.
- Judge resolution agreement: 90.0%.
- Judge outcome agreement: 80.0%.
- Judge boundary-event agreement: 0.0%.
- Detector-v2 resolution agreement: 100.0%.
- Detector-v2 outcome agreement: 100.0%.

## Interpretation notes

- The original files are unchanged; all derived artifacts are under `analysis_v2`.
- *Projected cost is a counterfactual estimate: simulation cost is prorated by projected rounds, while evaluation and embedding costs remain fixed. It is not an observed bill.
- Recomputed semantic convergence reuses embeddings of the saved full transcripts. It does not represent embeddings of counterfactually truncated stress transcripts.
- Convergence is numerical stability under the declared thresholds, not external validity or proof that the scenario is realistic.
