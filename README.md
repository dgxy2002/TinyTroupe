# TinyTroupe Singapore Conflict Simulation Research

This repository uses TinyTroupe to study how prompted cultural-background labels affect simulated everyday interactions in Singapore. It is a research pilot about model behaviour, not evidence about how real cultural groups behave.

## Current research design

Each run contains four agents with controlled roles, priorities, and private knowledge. Agents are not instructed to create conflict, avoid conflict, reach consensus, or resolve disagreement.

The intended workflow is:

1. Instantiate a scenario and one of five controlled background configurations.
2. Run the four-agent interaction for ten complete rounds.
3. Save the simulation transcript without modifying it.
4. Send the anonymized transcript to an independent LLM evaluator after the run.
5. Store round-level conflict scores and the final classification separately from the transcript.

The draft protocol and scenario bank are in [tinytroupe_conflict_scenarios_10x5.md](<reference folders/tinytroupe_conflict_scenarios_10x5.md>).

## Repository layout

- `tinytroupe/`: the TinyTroupe framework source used by the simulation.
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

## Development status

The repository is being reorganized around the post-run evaluation design. The generic 10-scenario × 5-configuration runner and evaluator have not yet replaced the retained historical implementation.

Generated transcripts and evaluations should be written to dedicated output directories and should not be silently overwritten. Historical outputs in this repository are intentionally preserved unless explicitly archived or removed.

## Responsible use

This project changes prompted identity labels and observes LLM-generated behaviour. It does not simulate or measure real people. Results must not be generalized to Singaporean cultural groups, treated as psychological ground truth, or used for consequential decisions.

See [RESPONSIBLE_AI_FAQ.md](RESPONSIBLE_AI_FAQ.md) for the underlying TinyTroupe responsible-use guidance.

## License

The TinyTroupe framework code remains subject to the repository's [MIT License](LICENSE).
