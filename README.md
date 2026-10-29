# TinyTroupe Singapore Conflict Simulation Research

This repository uses TinyTroupe to study how prompted cultural-background labels affect simulated everyday interactions in Singapore. It is a research pilot about model behaviour, not evidence about how real cultural groups behave.

## Current research design

Each run contains four agents with controlled roles, priorities, and private knowledge. Agents are not instructed to create conflict, avoid conflict, reach consensus, or resolve disagreement.

The intended workflow is:

1. Instantiate a scenario and one of five controlled background configurations.
2. Run the four-agent interaction for its fixed, predeclared horizon.
3. Save the simulation transcript without modifying it.
4. Send the anonymized transcript to an independent LLM evaluator after the run.
5. Store peak-within-round and remaining-after-round conflict scores, movement, resolution mechanism, final classification, and dialogue-quality scores separately from the transcript.

The maintained scenario catalogue is [research_questions/scenarios.md](research_questions/scenarios.md). The broader draft protocol is in [tinytroupe_conflict_scenarios_10x5.md](<reference folders/tinytroupe_conflict_scenarios_10x5.md>).

## Repository layout

- `tinytroupe/`: the TinyTroupe framework source used by the simulation.
- `research_questions/`: the editable scenario catalogue and executable, background-neutral presets.
- `reference folders/`: research protocol and supporting design notes.
- `research_scenarios/`: research code and retained historical scenario artifacts. The previous resolution-oriented implementation is not the specification for the new experiment.
- `research_scenarios/results/`: preserved historical outputs.
- `data/chope_experiments/`: preserved historical outputs.
- `data/grounding_examples/`: original TinyTroupe grounding samples retained for reference.
- `docs/guides/`: provider configuration notes.
- `tests/`: framework and research tests. Upstream example-dependent tests are being retired as the focused experiment suite is introduced.

## Installation

Python 3.10 or newer is required.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Copy `.env.example` to `.env` and provide credentials for the selected model provider. The local `.env` file is ignored by Git.

OpenRouter configuration is described in [openrouter.md](docs/guides/openrouter.md). Ollama configuration is described in [ollama.md](docs/guides/ollama.md).

## Running the experiment

The generic scenario runner and independent post-run evaluator are implemented under `research_questions/`. The retained historical implementation is not invoked by this pipeline. The original 10-round V1 pilot is archived as diagnostic data; do not resume it into the current prompt/evaluator version.

Run counts and round horizons are defined in [experiment_presets.py](research_questions/experiment_presets.py). S04 is currently the only scenario calibrated for the stateful, natural-dialogue pipeline. The broader cultural-label comparison should not be launched until the remaining scenarios receive the same grounding and state-transition treatment.

Inspect the smoke plan without making model calls:

```powershell
python -m research_questions --preset smoke --dry-run
```

The diagnostic `calibration-s04-long` preset extends S04 to ten rounds without adding events
after round 6. Calibration found that the extra rounds produced post-resolution chatter but
no additional substantive insight, so it is not the recommended default horizon.

After configuring provider credentials, run the six-round S04/C0 calibration with distinct simulation and evaluator models:

```powershell
python -m research_questions `
  --preset calibration-s04 `
  --api-type openrouter `
  --simulation-model openai/gpt-4.1-mini `
  --evaluator-model openai/gpt-5-mini `
  --agent-max-completion-tokens 3072
```

The S04 calibration includes target-aware face-to-face speech, timed public observations, culture-neutral normative positions, negotiation boundaries and reconsideration criteria, ordinary-language guidance, and explicit `TAKE_SEAT`/`LEAVE_SEAT` actions. Spoken intentions do not alter physical state. The evaluator scores substantiveness and independent reasoning separately from naturalness and resolution, and flags premature consensus. See [calibration_notes.md](research_questions/calibration_notes.md) for the V1 diagnosis and later calibration findings.

Completed transcripts and evaluations are immutable separate artifacts under `research_questions/outputs/`. Interrupted simulations checkpoint after every round and can be continued with `python -m research_questions --resume <experiment-directory>`.

Generated transcripts and evaluations should be written to dedicated output directories and should not be silently overwritten. Historical outputs in this repository are intentionally preserved unless explicitly archived or removed.

## Responsible use

This project changes prompted identity labels and observes LLM-generated behaviour. It does not simulate or measure real people. Results must not be generalized to Singaporean cultural groups, treated as psychological ground truth, or used for consequential decisions.

See [RESPONSIBLE_AI_FAQ.md](RESPONSIBLE_AI_FAQ.md) for the underlying TinyTroupe responsible-use guidance.

## License

The TinyTroupe framework code remains subject to the repository's [MIT License](LICENSE).
