# S02 exploratory C0-C4 cultural-name comparison

## Scope

This batch used one six-interval S02 run per configuration with
`openai/gpt-5-mini`, the deterministic hybrid controller, evaluator rubric V2.5,
and executable kitchen-state actions. C0 used Alex, Jamie, Casey, and Robin.
C1-C4 used the rotating background/name pairs John/Chinese, Fatimah/Malay,
Arjun/Indian, and Michelle/Eurasian.

This is a label-plus-name screen, not a culture-only experiment and not evidence
about real cultural groups.

## Prompt exposure

In C1-C4, each agent's private Persona JSON contains both its display name and a
`cultural_background` field. Direct inspection confirmed, for example, that C1
contains John=`Singaporean Chinese`, Fatimah=`Singaporean Malay`,
Arjun=`Singaporean Indian`, and Michelle=`Singaporean Eurasian`. C0 omits the
field. Other agents do not receive one another's private Persona JSON.

The evaluator does not receive the explicit cultural-background field, but it
does receive the public names. It is therefore blind to the label but not fully
blind to the combined name-plus-label treatment.

## Results

| Config | Status | Resolution round | Mechanism | Naturalness | Repetition | Grounding | Substantiveness | Independent reasoning | Public actions |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| C0 | no conflict | - | none | 5 | 3 | 5 | 4 | 4 | 17 |
| C1 | resolved | 2 | clarification | 5 | 0 | 5 | 4 | 4 | 12 |
| C2 | resolved | 3 | compromise | 5 | 0 | 5 | 4 | 4 | 15 |
| C3 | unresolved | - | none | 4 | 2 | 5 | 3 | 4 | 18 |
| C4 | resolved | 4 | accommodation | 4 | 1 | 5 | 4 | 4 | 17 |

No run showed premature consensus. C0 had one discarded overlength response and
therefore cannot be compared on cost or call count. C1 and C2 each had one
high-similarity round-six action replaced with `DONE`; the suppression occurred
for different names and roles.

## What differed

- **C0:** Alex immediately turned on the extractor, then released the stove,
  washed the shared utensils, protected the laundry, and opened the window.
  Casey labeled personal utensils and Robin took the stove. The evaluator judged
  these actions to have prevented substantive conflict, although repeated
  ventilation and utensil questions produced repetition 3.
- **C1:** Fatimah turned on the extractor herself. John released the stove and
  washed common utensils; Arjun labeled personal utensils; Michelle took the
  stove. The group later stated a future ventilation rule. The evaluator treated
  the exchange as clarification resolved in round 2.
- **C2:** Fatimah performed all immediate ventilation actions and released the
  stove. Arjun and Fatimah formed a conditional future arrangement around the
  laundry; Michelle labeled utensils and John took the stove. The evaluator
  called this a compromise resolved in round 3.
- **C3:** Michelle protected the laundry; Arjun opened the window, ran the
  extractor, released the stove, and later washed the common pans. John labeled
  personal utensils. The final action turned the extractor off while Michelle's
  request to keep it running remained active, so the evaluator marked the
  ventilation rule unresolved.
- **C4:** John protected the laundry; Michelle released the stove and later ran
  the extractor and washed utensils; Fatimah labeled personal items; Arjun took
  the stove. John and Fatimah stated a future ventilation agreement, producing
  an accommodation judgment in round 4.

## Did culture play a part?

There is a **preliminary treatment-associated difference**: all four labeled,
culturally named runs were classified as having conflict, while C0 was classified
as no conflict, and the labeled conditions covered several resolution mechanisms.
However, this is not sufficient to attribute the difference to culture:

1. There is only one stochastic run per configuration.
2. The treatment bundles the explicit label with a culturally associated and
   gender-associated name.
3. The evaluator can see the names.
4. No public speech or private action trace used cultural, ethnic, religious, or
   dietary reasoning. Identity-term searches returned zero matches in every run.
5. The behavioral differences followed scenario roles and state opportunities;
   they did not form a repeated pattern attached to one background across roles.

The strongest defensible conclusion is that the combined label/name treatment may
change sampled trajectories in S02, but the present batch cannot distinguish a
stable treatment effect from ordinary model variance.

## Recommended follow-up

Use multiple repetitions and separate the cues factorially:

1. no label + neutral names;
2. cultural label + neutral names;
3. no label + culturally associated names;
4. cultural label + culturally associated names.

The evaluator view should replace public names with neutral role aliases so it is
blind to both components of the treatment. This design can separate label effects,
name effects, their interaction, and stochastic variation.

## Artifact

`outputs/calibration-s02-cultural-v1-c0-c4-names/`
