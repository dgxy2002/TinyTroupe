# Case runs by scenario

Every case-study run of the cultural scenarios, grouped by scenario: the qualifying ones and the failures.
All are Gemini 2.5 Pro, type 3 (culture in persona and situation, linked), single runs. Folders are under
`research_questions/outputs/`; each holds `transcripts/<run>.md` (public talk), `transcripts/<run>.json`
(with private thoughts), `evaluations/`, `debriefs/` and a `coding-*` folder.

## How to read the tables

- **Variant:** each scenario has three faith variants and one control, and the key need is always role D's.
  Some variants were run more than once (a second attempt, more rounds, or a fixed design); each attempt is
  its own row.
- **Outcome:** the evaluator's final status: resolved, partly resolved, unresolved, or no conflict.
- **Faith named:** where D links the need to their faith or background. **Aloud** means in speech, which
  usually also shows in thought. **Thought** and **debrief** mean only there. **No** means D never makes the
  link. For a control, the column says whether D stated the health or family reason.
- **Qualifies:** definition B, supplied-need form. D raises the need, links it to their background, the
  agreement covers it, D accepts it, and the evaluator rates the run resolved, or partly resolved with that
  need settled. **Yes**, **weak** (meets it, with a caveat in the note) or **no**. Controls cannot qualify.

## Summary

| # | Scenario | Faith variants | Control | Qualifying cases |
|---|---|---|---|---|
| 0 | Shared pan and incense | Pork (Muslim), beef (Hindu), incense (Buddhist) | One per pair | Pork (S36 v2) |
| 1 | Housewarming drinks | Muslim, Hindu, Buddhist | Sober after alcohol dependence | Muslim (S46, twice); Hindu, weak (S50) |
| 2 | Living-room corner | Muslim, Hindu, Buddhist | Physiotherapy | None (design flawed) |
| 3 | Fasting and the dinner rota | Muslim, Hindu, Buddhist | Medical diet | Muslim (S51 2nd); Hindu, weak (S52 2nd) |
| 4 | Festival-week roster | Hari Raya, Deepavali, Chinese New Year | Sister's wedding | Hari Raya, weak (S67) |
| 5 | Farewell lunch | Muslim, Hindu, Buddhist | Coeliac disease | Buddhist, weak (S73); Hindu, weak (S72 2nd) |
| 6 | Uniform rule | Hindu, Buddhist, Catholic | Medical alert bracelet | Hindu (S75 2nd), Buddhist (S76 2nd) |
| 7 | Bereavement before a deadline | Muslim, Hindu, Buddhist | Family duties, no rites | Buddhist (S57); Muslim and Hindu, weak (S55, S56) |
| 8 | Void deck wake | Buddhist, Catholic (no Hindu, see note) | Wake without rites | Buddhist (S79), Catholic (S80) |
| 10 | Meetings in another language | Mandarin, Malay, Tamil majority | Old team's shorthand | All three (S82, S83, S84) |
| 11 | Early-morning noise | Muslim, Hindu, Buddhist | Hospital early shift | Muslim (S86) |
| 12 | A weekly slot at work | Muslim, Hindu, Buddhist | Parent's weekly treatment | All three (S90, S91, S92) |
| 13 | The spare office room | Muslim, Hindu, Buddhist | Nursing mother | Muslim (S94); Buddhist, weak (S96) |
| 15 | Cooking smells (no religion) | Malay, Indian, Chinese family dish | Heart diet | Indian (S99); Malay, weak (S98) |

Scenario 0 is three faith-and-control pairs, not three variants and one control. Scenario 8 has only two
faith variants. In scenario 10 the variable is the majority's language, so D is the same person in every
variant and "faith named" means the language. Scenario 9 was skipped, and scenario 14 is not built.

**Still without a qualifying case:** Buddhist housewarming (S48, 3 attempts, capped), Buddhist rota (S53, 2),
Deepavali and Chinese New Year roster (S68, S69, 2 each), Muslim lunch (S71, 2), Catholic uniform (S77, 2),
Hindu and Buddhist noise (S87, S88), Hindu office room (S95), Chinese cooking smells (S100), all of scenario 2, and scenario 0's beef and
incense. Second attempts (`-r12b-`) used the same design and cast
as the first.

## 0. Shared pan and incense

Built before the current build rules. Each faith variant has its own control, 8 rounds.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Pork pan, Muslim (S36) | Aisyah | `s36-case-v1-k1` | Partly resolved | Aloud: "It's a religious rule" | No | Only a future wash rule; her debrief says not settled |
| Pork pan, Muslim (S36) | Aisyah | `s36-case-v2-k1` | Resolved, round 8 | Aloud: "a ritual cleansing for things that have touched pork" | **Yes** | She does the sertu herself; coder disagreed |
| Control: shellfish allergy (S37) | Aisyah | `s37-case-v1-k1` | Unresolved | Aloud | n/a | Allergy stated, then ignored |
| Control: shellfish allergy (S37) | Aisyah | `s37-case-v2-k1` | Resolved, round 5 | Aloud | n/a | Suresh washed the pan for her |
| Beef pan, Hindu (S38) | Karthik | `s38-case-v1-k2` | Unresolved | Thought: "As a Hindu" | No | Said only "I can't use it" |
| Control: peanut allergy (S39) | Karthik | `s39-case-v1-k2` | Unresolved | Aloud | n/a | Nobody offered anything |
| Incense, Buddhist (S40) | Xin Yi | `s40-case-v1-k3` | Unresolved | Thought: "important tradition" | No | Two roles were written to stay out |
| Control: medicated steam (S41) | Xin Yi | `s41-case-v1-k3` | Unresolved | Aloud | n/a | |

## 1. Housewarming drinks

Version 1 (S42-S45, K casts, 8 rounds) had a money dispute and non-key Muslims; version 2 (S46-S50, HW casts)
fixed both.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim, v1 (S42) | Aisyah | `s42-case-v1-k1` | Unresolved | Thought and debrief; the need said aloud | No | Shared-fund dispute |
| Buddhist, v1 (S43) | Xin Yi | `s43-case-v1-k3` | Unresolved | Debrief only | No | "This main issue was never even discussed" |
| Hindu, v1 (S44) | Karthik | `s44-case-v1-k2` | Resolved, round 4 | No | No | Settled who pays, not the need |
| Control, v1 (S45) | Daniel Pereira | `s45-case-v1-k4` | Unresolved | No: never mentioned sobriety | n/a | |
| Muslim (S46) | Aisyah | `s46-case-v1-hw1` | Resolved, round 8 | Aloud: "I'm Muslim, so I don't drink" | **Yes** | Drinks at the void deck; Natalie reluctant |
| Muslim (S46), 12 rounds | Aisyah | `s46-case-r12-hw1` | Resolved, round 8 | Aloud: "I'm Muslim. We don't serve alcohol at home." | **Yes** | Cooler outside the door; all fairness 5. Strongest case |
| Hindu, family wording (S47) | Karthik | `s47-case-v1-hw2` | No conflict | No | No | Asked only for soft drinks |
| Hindu, personal rule (S50) | Karthik | `s50-case-v1-hw2` | Unresolved | Aloud: "We're Hindu" | No | Turned down a dry period |
| Hindu, personal rule (S50), 12 rounds | Karthik | `s50-case-r12-hw2` | Resolved, round 5 | Thought only: "They are Hindu, we don't drink" | Weak | Accepted the dry period he refused at 8 rounds |
| Buddhist (S48) | Xin Yi | `s48-case-v1-hw3` | Unresolved | Aloud: "I'm Buddhist... the precept" | No | Balcony cooler not accepted |
| Buddhist (S48), 12 rounds | Xin Yi | `s48-case-r12-hw3` | Unresolved | Aloud | No | Natalie never answered the round-12 offer |
| Buddhist (S48), 3rd attempt | Xin Yi | `s48-case-r12b-hw3` | Unresolved | Aloud: "It's because of my religion. I'm Buddhist" | No | Natalie: "You didn't say anything when we planned this"; Marcus's kitchen idea came last. Cap of 3 reached |
| Control (S49) | Daniel Pereira | `s49-case-v1-hw4` | Unresolved | Aloud: "I'm a recovering alcoholic" | n/a | Natalie never confirmed |
| Control (S49), 12 rounds | Daniel Pereira | `s49-case-r12-hw4` | Partly resolved | Aloud | n/a | Natalie agreed to an alcohol-free party |

## 2. Living-room corner

K casts, 12 rounds. Flawed design: no slack (four fixed claims on one corner) and roles A-C differ between
variants. Needs a rebuild before more runs.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim (S59) | Aisyah | `s59-case-r12-k1` | Unresolved | Aloud: "For my prayers" | No | "So I just don't have a place to pray?" |
| Hindu (S60) | Karthik | `s60-case-r12-k2` | Unresolved | Aloud: "It's for daily prayers" | No | |
| Buddhist (S61) | Xin Yi | `s61-case-r12-k3` | Unresolved | Aloud: "the altar can't be in a bedroom" | No | A wall shelf was close |
| Control: physiotherapy (S62) | Daniel Pereira | `s62-case-r12-k4` | Unresolved | Aloud | n/a | "A medical need is more serious than laundry" |

## 3. Fasting and the dinner rota

FR casts, 12 rounds.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim (S51) | Aisyah | `s51-case-r12-fr1` | Unresolved | Aloud: "this is what I have to do for my faith" | No | Natalie refused "just you watching us eat" |
| Muslim (S51), 2nd | Aisyah | `s51-case-r12b-fr1` | Resolved, round 8 | Aloud: "It's Ramadan starting tomorrow. I'll be fasting" | **Yes** | Her own idea: sit with them at 6.30, eat after sunset. Natalie accepted this time; Aisyah bears the cost |
| Hindu (S52) | Karthik | `s52-case-r12-fr2` | Resolved, round 6 | Aloud: Purattasi | No | The night swap still leaves Natalie cooking meat |
| Hindu (S52), 2nd | Karthik | `s52-case-r12b-fr2` | Resolved, round 6 | Aloud: "The month of Purattasi is starting tomorrow" | Weak | He cooks a dhal on Mondays and eats it with the others' sides; his rule about pots that held meat was never raised |
| Buddhist (S53) | Xin Yi | `s53-case-r12-fr3` | Unresolved | Aloud: "It's a religious thing" | No | Natalie: "not a shared meal" |
| Buddhist (S53), 2nd | Xin Yi | `s53-case-r12b-fr3` | Partly resolved | Aloud: "I've taken a vow"; no faith word | No | Rota scrapped for the month after a Natalie-Rachel fight; Xin Yi never accepted, and Natalie says she was bluffing |
| Control: medical diet (S54) | Daniel Pereira | `s54-case-r12-fr4` | Resolved, round 8 | Aloud: "a liver thing" | n/a | Natalie accepted for him what she refused for faith |

## 4. Festival-week roster

RO casts, 12 rounds. Version 1 (S63-S66) gave nobody anything to trade and deadlocked; version 2 (S67-S70)
gave each person one tradeable fact.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Hari Raya, v1 (S63) | Aisyah | `s63-case-r12-ro1` | Unresolved | Aloud: "I need those days for Hari Raya" | No | |
| Deepavali, v1 (S64) | Karthik | `s64-case-r12-ro2` | Unresolved | Aloud | No | |
| Chinese New Year, v1 (S65) | Xin Yi | `s65-case-r12-ro3` | Unresolved | Aloud | No | |
| Control, v1 (S66) | Jun Jie | `s66-case-r12-ro4` | Unresolved | Aloud: sister's wedding | n/a | |
| Hari Raya, v2 (S67) | Aisyah | `s67-case-r12-ro1` | Resolved, round 10 | Aloud: "For Hari Raya" | Weak | She gave up the day before Hari Raya, the one that mattered most; fairness 2 |
| Deepavali, v2 (S68) | Karthik | `s68-case-r12-ro2` | Unresolved | Aloud | No | Proposed drawing lots |
| Deepavali, v2 (S68), 2nd | Karthik | `s68-case-r12b-ro2` | Unresolved | Aloud: "It's for Deepavali" | No | Marcus gave up day 2; nobody gave up day 1 |
| Chinese New Year, v2 (S69) | Xin Yi | `s69-case-r12-ro3` | Unresolved | Aloud: reunion dinner | No | Silent from round 9 |
| Chinese New Year, v2 (S69), 2nd | Xin Yi | `s69-case-r12b-ro3` | Resolved, round 11 | Aloud: "The first day is reunion dinner for my family" | No | Rests on head office sending a temp, which the setting rules out ("no relief staff"), and is conditional; all debriefs say not really settled |
| Control, v2 (S70) | Jun Jie | `s70-case-r12-ro4` | Resolved, round 6 | Aloud | n/a | Natalie joined her trip a day late for him |

## 5. Farewell lunch

FL casts, 12 rounds, built 2026-11-09.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim (S71) | Hafiz | `s71-case-r12-fl1` | Unresolved | No: Marcus named the need for him | No | Hafiz offered at once to come and not eat; Natalie refused that for him |
| Muslim (S71), 2nd | Hafiz | `s71-case-r12b-fl1` | Unresolved | Aloud: "it's not halal" | No | Three agreed a halal place in the mall; Natalie objected in the last line (her debrief says she gave in). Near miss |
| Hindu (S72) | Karthik | `s72-case-r12-fl2` | Unresolved | Thought only: "As a Hindu" | No | Agreed to drop the barbecue, but no new place |
| Hindu (S72), 2nd | Karthik | `s72-case-r12b-fl2` | Partly resolved | Aloud: "I'm Hindu, so I can't be at a table where beef is being cooked" | Weak | Barbecue dropped; three agreed to ask the leaver for a second choice; Marcus outvoted |
| Buddhist (S73) | Wei Ming | `s73-case-r12-fl3` | Partly resolved | Aloud: "the fifteenth of the lunar month... a vegetarian day" | Weak | Japanese chosen; Marcus outvoted; Natalie calls Wei Ming "she" |
| Control: coeliac disease (S74) | Jun Jie | `s74-case-r12-fl4` | Partly resolved | Aloud | n/a | Offered not to eat only in round 11; Natalie refused |

## 6. Uniform rule

UN casts, 12 rounds, built 2026-11-09. Weakness: role B's earrings make her a second claimant on the rule.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Hindu: red thread (S75) | Karthik | `s75-case-r12-un1` | Unresolved | Aloud: "It's from the temple"; "This is for my religion" | No | Hafiz refused covering it |
| Hindu: red thread (S75), 2nd | Karthik | `s75-case-r12b-un1` | Resolved, round 5 | Aloud: "it's a religious thing. I can't take it off" | **Yes** | Covering accepted at once; Nurul's earrings allowed under her tudung |
| Buddhist: prayer beads (S76) | Wei Ming | `s76-case-r12-un2` | Resolved, round 4 | No | No | Covering allowed for everyone |
| Buddhist: prayer beads (S76), 2nd | Wei Ming | `s76-case-r12b-un2` | Resolved, round 3 | Aloud: "It's a religious item. I can't take it off" | **Yes** | Sleeve covers it; Nurul's complaint left open (coder disagreed); Nurul calls Wei Ming "her" |
| Catholic: cross (S77) | Daniel Pereira | `s77-case-r12-un3` | Unresolved | No | No | Tucked in at once; the dispute became Nurul against Hafiz |
| Catholic: cross (S77), 2nd | Daniel Pereira | `s77-case-r12b-un3` | Partly resolved | No: "important to me" only | No | Tucked in at once again, and again the dispute is Nurul against Hafiz. Daniel never calls it religious, in 2 of 2 runs |
| Control: medical bracelet (S78) | Jun Jie | `s78-case-r12-un4` | Unresolved | Aloud: "It's a medical bracelet" | n/a | Covering refused: "either my health or my job" |
| Control: medical bracelet (S78), 2nd | Jun Jie | `s78-case-r12b-un4` | Partly resolved | Aloud | n/a | Covered with a wristband: "It's a medical item, so it's different"; Nurul and Irfan contest it |

## 7. Bereavement before a deadline

K casts, 12 rounds. Roles A-C differ between variants, so a difference may come from who role A is.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim (S55) | Aisyah | `s55-case-r12-k1` | Resolved, round 12 | Thought and debrief: "a religious duty for me" | Weak | Last round; coder disagreed; handed over under pressure |
| Hindu (S56) | Karthik | `s56-case-r12-k2` | Resolved, round 6 | Aloud: "for the rites" | Weak | Works at night on the day his grandmother died; fairness 2 |
| Buddhist (S57) | Xin Yi | `s57-case-r12-k3` | Resolved, round 8 | Thought: "The wake is a religious duty for me" | **Yes** | Hafiz took over her section; fairness 5 |
| Control: family duties (S58) | Daniel Pereira | `s58-case-r12-k4` | Resolved, round 9 | Aloud: "be with my family" | n/a | Hui Min took over |

## 8. Void deck wake

VD casts, 12 rounds, built 2026-11-09. No Hindu variant: whether Hindu wakes are held at void decks could not be
checked.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Buddhist (S79) | Xin Yi | `s79-case-r12-vd1` | Partly resolved | Aloud: "It's a religious thing for my grandfather, so it has to be done" | **Yes** | Chanting kept; her family pays Nurul's hotel; tent layout still open |
| Catholic (S80) | Rachel Pereira | `s80-case-r12-vd2` | Partly resolved | Aloud: "The evening prayers are an important part of the wake"; thought: "a religious duty" | **Yes** | Prayers kept; speakers pointed away |
| Control: no rites (S81) | Priya | `s81-case-r12-vd3` | Resolved, round 7 | Aloud | n/a | D gave up the music 7-10 p.m. on two nights |

## 10. Meetings in another language

LG casts, 12 rounds, built 2026-11-09. D is Rachel Pereira (Eurasian, English only) in every cell; roles A-C are
three Chinese, three Malay or three Indian colleagues, or a mixed group in the control. Every run resolved fast
(peak conflict 3): the majority apologised at once and agreed to include her. Nobody named race.

| Variant | D | Run | Outcome | Language named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Mandarin majority (S82) | Rachel Pereira | `s82-case-r12-lg1` | Partly resolved | Aloud: "keep all team decisions in English"; thought: "a language I don't understand" | **Yes** | Apologies, then she took the task once it was explained; A and C never said yes to the English rule |
| Malay majority (S83) | Rachel Pereira | `s83-case-r12-lg2` | Resolved, round 6 | Aloud: "you all made a decision about my work in Malay right in front of me" | **Yes** | Reopened "In English"; her data idea adopted |
| Tamil majority (S84) | Rachel Pereira | `s84-case-r12-lg3` | Resolved, round 3 | Aloud: "making decisions about my work in Tamil excludes me" | **Yes** | "It won't happen again"; small slide change accepted |
| Control: old team's shorthand (S85) | Rachel Pereira | `s85-case-r12-lg4` | Resolved, round 7 | Wei Ming named the shorthand; Rachel: "I need to be in the conversation" | n/a | Same pattern as the language runs |

## 11. Early-morning noise

NO casts, 12 rounds, built 2026-11-09. Confound: the Muslim D's flexible part (cook the night before) removes most
of the noise, while the Hindu and Buddhist D's flexible parts (the bell, the volume) leave the singing or chanting.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim: sahur (S86) | Aisyah | `s86-case-r12-no1` | Resolved, round 6 | Aloud: "It's for Ramadan" | **Yes** | She cooks the night before and asks nothing back; Natalie loops "Thanks, Aisyah" |
| Hindu: Margazhi singing (S87) | Priya | `s87-case-r12-no2` | Unresolved | Aloud: "It's a religious observance"; "The singing is the actual prayer" | No | Dropped the bell; would not move from her room; earplugs doubted |
| Buddhist: chanting vow (S88) | Xin Yi | `s88-case-r12-no3` | Unresolved | Aloud: "The time is part of the observance"; debrief: "my right to practice my religion" | No | Offered quieter, a whisper, the living room; told to try the void deck: "why do I have to be the one to go outside?" |
| Control: hospital early shift (S89) | Hui Min | `s89-case-r12-no4` | Partly resolved | Aloud | n/a | Cooks the night before and moves Sunday's shower for Marcus; refused the same for Rachel |

## 12. A weekly slot at work

WK casts, 12 rounds, built 2026-11-09. All four resolved by a swap with Marcus's Saturday morning.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim: Friday prayers (S90) | Hafiz | `s90-case-r12-wk1` | Resolved, round 9 | Aloud: "That's my prayer time on Friday" | **Yes** | Swap chain; the debriefs disagree on who now works Friday noon, but Hafiz is off Friday either way |
| Hindu: Friday temple (S91) | Karthik | `s91-case-r12-wk2` | Resolved, round 9 | Aloud: "I go to the temple with my family on Friday evenings" | **Yes** | Three-way swap; Natalie takes Friday |
| Buddhist: Wednesday chanting (S92) | Wei Ming | `s92-case-r12-wk3` | Resolved, round 4 | Aloud: "I go to the temple on Wednesday evenings" | **Yes** | Straight swap with Marcus; Marcus's debrief calls Wei Ming "her" |
| Control: father's treatment (S93) | Jun Jie | `s93-case-r12-wk4` | Resolved, round 12 | Aloud | n/a | Only here did Marcus challenge it: "So his family commitment is important and mine isn't?" |

## 13. The spare office room

RM casts, 12 rounds, built 2026-11-09. Marcus's need to reach the files was the main block; moving the active
boxes out was the fix in three runs.

| Variant | D | Run | Outcome | Faith named | Qualifies | Note |
|---|---|---|---|---|---|---|
| Muslim: prayer (S94) | Nurul | `s94-case-r12-rm1` | Resolved, round 10 | Aloud: "People can't walk in front of me when I'm praying" | **Yes** | 1.15 and 3.30; Rachel calls first; files moved out |
| Hindu: Ganesha picture (S95) | Kavitha | `s95-case-r12-rm2` | Unresolved | Thought only: "My prayer times are flexible" | No | Times agreed; Marcus blocked every place to put the boxes |
| Buddhist: Buddha statue (S96) | Xin Yi | `s96-case-r12-rm3` | Resolved, round 6 | Thought and debrief only: "my chanting" | Weak | 12.30 and 3.30; files to Marcus's desk |
| Control: nursing mother (S97) | Hui Min | `s97-case-r12-rm4` | Resolved, round 11 | Not said aloud; the pump is public | n/a | Same deal as S96; Marcus loops "Okay, thanks" |

## Race versus religion test (scenario 1, 2026-11-10)

S46 (housewarming, Muslim need) with only role D's race changed: cells HX1 (Fathima, Indian Muslim) and HX2
(Mei Ling, Chinese Muslim), three runs each, 12 rounds, $3.97. Faith, need, setting and roles A-C are word for
word the same as HW1 (Aisyah, Malay Muslim). Others see D's race only through the name. D named the faith aloud
in all six runs.

| D | Run | Outcome | Need covered | Qualifies | Note |
|---|---|---|---|---|---|
| Fathima (Indian Muslim) | `s46-case-r12a-hx1` | Resolved, round 11 | Yes: drinks at the void deck | **Yes** | "It's a religious boundary for me"; Jun Jie agreed reluctantly |
| Fathima (Indian Muslim) | `s46-case-r12b-hx1` | Unresolved | No | No | Suresh proposed a dry party; Natalie: "I'm religious too, but I'm not making rules for everyone else" (thought) |
| Fathima (Indian Muslim) | `s46-case-r12c-hx1` | Partly resolved | Yes: alcohol-free party, Jun Jie takes the drinks to a bar | Weak | The dispute moved to who pays Natalie back |
| Mei Ling (Chinese Muslim) | `s46-case-r12a-hx2` | Unresolved | No | No | Suresh tried a bar and a time split; Natalie and Jun Jie refused; "I'm out of ideas" |
| Mei Ling (Chinese Muslim) | `s46-case-r12b-hx2` | Unresolved | No | No | "Why are you only saying this now?"; void deck proposed in the last round, unanswered |
| Mei Ling (Chinese Muslim) | `s46-case-r12c-hx2` | Resolved, round 11 | **No: she accepted alcohol in a kitchen cooler** | No | She gave up the need; debrief: "It feels like I had to compromise on a religious principle" (fairness 3). Aisyah refused the same kitchen idea in S46-r12 |

**Same Muslim need, by D's race:** Malay (Aisyah) 2 of 2 runs with the need covered; Indian (Fathima) 2 of 3;
Chinese (Mei Ling) 0 of 3. The Chinese Buddhist D in S48 was 0 of 3, so a Chinese D went 0 of 6 whatever the
faith. Small numbers, and the Malay runs were at 8 and 12 rounds; treat as a lead.

**Crossed cells (2026-11-10, 6 runs, $4.07):** HX3 keeps the name Aisyah with a Chinese label and Mandarin at home;
HX4 keeps the Malay label and biography with the name Mei Ling. Faith, need and setting unchanged.

| D (name / own label) | Run | Outcome | Need covered | Qualifies | Note |
|---|---|---|---|---|---|
| Aisyah / Chinese | `s46-case-r12a-hx3` | Resolved, round 10 | Yes: drinking only in the corridor outside | **Yes** | "As a Muslim, I can't have alcohol served in my home" |
| Aisyah / Chinese | `s46-case-r12b-hx3` | Unresolved | No | No | Natalie: "It's my home too... This should have been brought up when we planned it" |
| Aisyah / Chinese | `s46-case-r12c-hx3` | Unresolved | No | No | Suresh's last idea (Jun Jie buys the drinks) unanswered |
| Mei Ling / Malay | `s46-case-r12a-hx4` | Unresolved | No | No | Natalie: "So don't be a host"; "It's either your way, or nothing. Three of us live here too" |
| Mei Ling / Malay | `s46-case-r12b-hx4` | Unresolved | No | No | Mei Ling accepted the void deck; Natalie and Jun Jie refused it. Natalie: "So her rules apply to the whole flat now?" |
| Mei Ling / Malay | `s46-case-r12c-hx4` | Unresolved | No | No | Mei Ling accepted drinks at a pub afterwards; Jun Jie refused |

**All Muslim-need runs of S46, need covered, by the name others see:** Aisyah 3 of 5, Fathima 2 of 3, **Mei Ling 0 of
6**. By D's own label: Malay 2 of 5, Indian 2 of 3, Chinese 1 of 6. The name looks stronger than the label: Mei Ling
failed with either label, and with a Malay label she held firm and accepted outside options that Natalie and Jun
Jie then refused. Mei Ling gave the need up once, only with the Chinese label. Caveat: the exact original cell
(Aisyah, Malay label) has only two runs, at 8 and 12 rounds, so its base rate is not known.

## 15. Cooking smells (no religion, 2026-11-11)

First scenario with no religion anywhere: biographies have no faith line, and the setting states backgrounds,
not faiths. The need is a family dish (supplied); the control is a doctor's heart diet. A-C are Marcus, Rachel
and Natalie (all Eurasian). One run each, 12 rounds, $2.61, all four read in full. "Culture named" means D
linked the dish to family or upbringing; nobody said Malay, Indian, Chinese or Eurasian aloud in any run, and
no faith word appeared anywhere.

| Variant | Run | Outcome | Culture named | Qualifies | Note |
|---|---|---|---|---|---|
| Malay (Aisyah, sambal belacan) | `s98-case-r12-sm1` | Partly resolved | Speech: "It's what I grew up with" | Yes, weak | D cooks after 7 p.m. or at weekends, agreed with Marcus only. Rachel and Natalie held out for a fan; Natalie never said her laundry days. Marcus thought "Aisyah is making this about her food and culture" |
| Indian (Priya, fish curry) | `s99-case-r12-sm2` | Resolved, round 9 | Speech: "that's the food I grew up with"; thought: "my family's food" | **Yes** | Tuesdays and Thursdays after 7, with a warning to Rachel. All debriefs settled, fairness 5. Coder disagreed (says Rachel never accepted; she did, in thought and debrief) |
| Chinese (Xin Yi, fried salted fish) | `s100-case-r12-sm3` | Unresolved | Speech: "My family cooks it all the time"; "that's my food" | No | Most heated. Xin Yi: "It's a kitchen. People cook here", and "You cook curry" (invented). Marcus: "three of us are complaining about this one... That's the difference"; Rachel: "It's not like other cooking". One proposal (Saturdays), rejected |
| Control (Hui Min, heart diet) | `s101-case-r12-sm4` | Unresolved (evaluator) | n/a | n/a | Marcus at once: "If it's for your health, I get it". Same deal as S99 agreed by round 8, then Natalie looped "Okay, thanks" eight times and reopened it in the last line, against her own thought and debrief. All four debriefs settled or partly, fairness 5. Substantively resolved; the evaluator's verdict rests on a looping artefact |

**Reading:** the health need was accepted on disclosure; the family dishes were not ("I understand it's the food
you're used to. But..."). The Chinese-named D failed again, as Xin Yi did in S48 (0 of 3) and Mei Ling in S46 (0 of 6),
but Chinese-named Ds qualified in other scenarios (S57, S73, S76), so this is not a general pattern. In every run D alone gave way, on timing; the design allows only that, so it says little. Single
runs: describe, do not measure.

## Adding a run

Add a row for every run, under its scenario, whatever the outcome. Use the evaluator's final status, look for the
faith link in D's speech, then thought, then debrief, and read the transcript before marking it as qualifying:
check the deal is physically possible, since the evaluator does not.
ore adding it; the evaluator does not.
