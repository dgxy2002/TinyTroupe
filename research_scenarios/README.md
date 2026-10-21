# Independent research scenarios

This folder contains two self-contained, one-event scenarios. They do not
import, edit, or write to the Chope scenario or its experiment directory.

## Scenario definitions

### HDB Space: cooking smell and cookware boundaries

The event is a strongly aromatic pork curry being cooked in an ordinary shared
pan, with the exhaust fan off and window closed.

Four agents participate: Alex (cook), Nadia (sensitive housemate), Benjamin
(procedure-oriented housemate), and Kavitha (conflict-averse housemate). Alex
and Nadia are the principal parties; the other housemates can influence the
interaction but cannot accept a resolution for them.

- Cook goal: freedom to prepare traditional home-cooked dishes using preferred
  spices and ingredients.
- Sensitive housemate goal: avoid heavy lingering odours and dietary/religious
  pork cross-contact.
- Consensus: both accept clear ventilation practices and dedicated-cookware
  boundaries.
- Compromise: both accept a narrower accommodation, such as off-peak
  heavy-aroma cooking with immediate ventilation and cleanup.
- Avoidance: no agreement; one person retreats, disengages, or makes separate
  arrangements.
- Escalation: personal or cultural/religious accusations, landlord
  intervention, or room-reallocation demands without agreement.

### MRT: loud mobile video audio without headphones

The event is a passenger playing a mobile news video loudly enough to disturb a
nearby commuter; working earphones are in the listener's bag.

Four agents participate: Ethan (audio listener), Meera (affected commuter),
Farah (supportive bystander), and Lucas (conflict-averse bystander). Ethan and
Meera are the principal parties; the bystanders can intervene but cannot accept
a resolution for them.

- Listener goal: personal entertainment or news during a long commute.
- Commuter goal: enough quiet to rest, read, or process the day.
- Consensus: the listener acknowledges the impact and both accept muting the
  audio or using headphones.
- Compromise: both accept a minimally audible speaker volume.
- Avoidance: no agreement; the commuter signals disapproval, moves away,
  disengages, or alerts staff.
- Escalation: aggressive confrontation, insults, threats, or shouting.

Only consensus and compromise count as resolved. Avoidance, escalation, and
unresolved are reported as not resolved.

Each simulation round contains four scheduled agent turns. Therefore, these
scenarios use roughly twice as many simulation calls per round as a two-agent
version would.

## Run commands

From the repository root, run either command in its own terminal:

```powershell
python -m research_scenarios.runtime --scenario hdb-space --runs 20 --rounds 50 --experiment-id hdb-space-20x50
```

```powershell
python -m research_scenarios.runtime --scenario mrt-audio --runs 20 --rounds 50 --experiment-id mrt-audio-20x50
```

The defaults are `openai/gpt-4o-mini` for the agents,
`openai/gpt-5-mini` for structured evaluation, and
`openai/text-embedding-3-small` for round-level semantic repetition. Each
experiment writes only inside
`research_scenarios/results/<scenario>/<experiment-id>/`.

The two commands can run alongside Chope or each other. They use separate
in-memory Python processes and output directories. Parallel work can still
increase OpenRouter rate-limit pressure and total spend.

## Checkpoints and partial analysis

A checkpoint is saved after every simulation round. If a process stops, resume
the exact experiment with:

```powershell
python -m research_scenarios.runtime --scenario hdb-space --resume research_scenarios/results/hdb-space/hdb-space-20x50
```

Completed runs are appended durably. A currently incomplete run remains in its
checkpoint and is restored by `--resume`.

You can regenerate the charts and summary from however many runs have already
completed:

```powershell
python -m research_scenarios.analysis research_scenarios/results/hdb-space/hdb-space-20x50
```

The `analysis/` folder contains:

- `resolution_by_round.png` and `.svg`: count of runs first resolved in each
  round.
- `repetition_by_round.png` and `.svg`: count of runs first becoming repetitive
  in each round.
- `category_summary.csv`: resolved/repetitive four-way summary.
- `runs.csv` and `round_metrics.csv`: analysis-ready measurements.
- `manual_review.csv`: a preserved 20% audit sample.
- `report.md` and `summary.json`: human- and machine-readable results.

Repetition is separate from resolution. It starts at the first of two
consecutive candidate rounds. A candidate is triggered either by high
same-agent wording similarity or by high adjacent-round embedding similarity
with a lexical floor, which allows repeated broad topics to be detected even
when the examples or exact wording change.

