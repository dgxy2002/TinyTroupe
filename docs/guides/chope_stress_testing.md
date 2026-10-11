# Chope scenario stress testing

The Chope benchmark runs one independent hawker-centre event repeatedly. Each
run creates four fresh agents and gives them asymmetric observations of Rachel
moving Mr Lim's tissue packet. Runs never share memory or world state.

The default `outcome` execution mode checks for an explicit practical settlement
after each four-agent round and stops early when one is found. The detector is
deterministic and conservative: apologies, norm acknowledgement, conditional
offers, mediator suggestions, and generic claims that the issue is settled are
not sufficient. Its trigger and evidence are saved in every run record.

Use `--execution-mode stress` to force all configured rounds. Fixed-horizon mode
is intended for measuring post-resolution repetition and dialogue degeneration,
not for the primary cost-efficient outcome comparison.

```powershell
# Primary settlement/convergence experiment (also the default)
python examples/chope_stress_test.py --execution-mode outcome

# Fixed-horizon boundary experiment
python examples/chope_stress_test.py --execution-mode stress
```

## Run the experiment

Configure OpenRouter in `.env`, then inspect the command before spending API
credits:

```powershell
python examples/chope_stress_test.py --help
```

The default experiment compares `openai/gpt-4o-mini` with
`openai/gpt-5-mini`. It performs one excluded pilot per model, starts with 10
main runs, and adds batches of five until the model passes two consecutive
convergence checkpoints or reaches 30 runs.

Agent action calls are capped at 4,096 completion tokens to bound malformed or
runaway structured responses. The structured evaluator uses its own 6,000-token
allowance. Override the action cap only when investigating truncation with
`--agent-max-completion-tokens`.

For a cheap structural smoke test, use one model, skip the pilot and
embeddings, and disable adaptive expansion:

```powershell
python examples/chope_stress_test.py `
  --models openai/gpt-4o-mini `
  --pilot-runs 0 `
  --min-runs 1 `
  --batch-size 1 `
  --max-runs 1 `
  --no-adaptive `
  --no-embeddings
```

That smoke command executes one evaluator call. It runs the full 12-turn
simulation when `--execution-mode stress` is supplied; in the default outcome
mode it may stop after four or eight turns. Unit tests do not make network calls.

Resume an interrupted experiment with the same model list:

```powershell
python examples/chope_stress_test.py `
  --resume data/chope_experiments/20261010-120000 `
  --models openai/gpt-4o-mini openai/gpt-5-mini
```

## What is measured

The harness combines deterministic transcript counts with one structured
LLM-as-judge evaluation per completed run. The primary measures are outcome,
conflict and resolution rates, turns to resolution, norm recognition,
mediation, immediate capitulation, perspective diversity, persona adherence,
communication markers, failures, token counts, latency, and exact OpenRouter
cost where metadata is available.

Primary outcome and resolution convergence use the deterministic explicit
settlement signal. The LLM judge remains available for secondary qualitative
constructs such as mediation and persona adherence. Detector-versus-judge
resolution or outcome disagreements are saved as boundary events rather than
silently choosing the judge as ground truth.

Do not mix execution modes in one convergence series. Outcome mode measures
settlement behavior and cost efficiently; stress mode measures what happens when
agents are forced to continue after settlement.

Convergence compares each cumulative checkpoint with the preceding checkpoint:

| Signal | Passing threshold |
|---|---:|
| Outcome-distribution total variation distance | <= 0.10 |
| Largest core binary-rate change | <= 0.10 |
| Largest continuous standardized mean difference | <= 0.20 |
| Transcript-centroid cosine distance | <= 0.05 |

All enabled criteria must pass twice consecutively. This operationalizes
stability; it does not establish external validity or show that the simulated
behavior represents Singaporeans outside the authored setup.

## Result files

Every experiment is stored under `data/chope_experiments/<experiment_id>/`:

- `manifest.json`: configuration, controls, Git commit, thresholds, and persona hashes.
- `runs.jsonl`: one complete metric/resource record per main run.
- `transcripts/`: full JSON audit records and readable Markdown transcripts.
- `round_metrics.csv`: calls, tokens, cost, and latency by simulation round.
- `embeddings.jsonl`: transcript embeddings used for semantic convergence.
- `convergence.csv`: every model/checkpoint and every pass/fail criterion.
- `boundary_events.jsonl`: run failures, evaluator violations, and incomplete exact-cost records.
- `manual_review.csv`: deterministic 20% audit sample for a human reviewer.
- `summary.json` and `report.md`: aggregate results and showcase-ready overview.

Simulation, evaluator, embedding, and total resource use are stored separately.
Do not silently treat a zero cost as exact: consult `exact_cost_complete` and
the boundary log.
