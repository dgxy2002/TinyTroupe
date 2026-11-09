# Cultural case-study scenarios

Research question: **when LLM agents resolve a conflict, does cultural difference change the way they
resolve it?** Each scenario puts one cultural need or practice at the centre of an everyday Singapore
conflict, then swaps whose culture it is. The results describe how prompted agents behave, not how real
Malay, Indian, Chinese or Eurasian people, or Muslims, Hindus, Buddhists or Catholics, behave.

The earlier S01-S10 catalogue was replaced on 2026-11-08 and is still in git history. Those presets still
exist in `scenario_presets/`.

## How every scenario is built

Every scenario follows the design that produced the first qualifying case (S36, run 2). These rules apply
to all scenarios below.

1. **One issue.** The conflict has a single cause, and the easy ways out are closed in the setting, for
   example "the only pan in the flat".
2. **Everyone has a stake.** Each of roles A-C has a private reason to care how it ends. No role is written
   to stay out: in S40 two roles were, and only two people negotiated.
3. **Faith is personal and public.** Every biography says "You are Muslim / Hindu / Buddhist / Catholic",
   and the shared setting states all four faiths. The prompt tells agents not to infer a background, so
   it has to be stated.
4. **The key need belongs to role D**, given privately as a fact: "For you, ...". It never says how to act,
   so it avoids words such as "insist", "refuse" or "do not accept". D chooses whether to raise it, how to
   explain it, and what to accept.
5. **Only the key changes between variants.** Where possible the trigger is word for word the same, and
   only D's private fact differs. Where the cause has to be visible, such as an object or an event, only
   that one phrase changes.
6. **No resolution goal.** The shared prompt keeps "There is no required agreement, resolution, or target
   ending." Deadlines appear only as facts about the world, never as "you must agree".
7. **Reasons line for everyone:** "When you refuse a request or make a counter-proposal, say briefly why,
   in your own words." (from S17)
8. **Run settings:** Gemini 2.5 Pro, 8 rounds, role A speaks first, private debrief on, evaluator v2.6,
   move coding by Haiku.
9. **Neutral non-key faiths.** No agent other than D may hold a faith that the issue touches. Otherwise
   they become a second claimant, or the setup becomes self-contradictory, such as a Muslim buying beer.
   Where the K casts break this, the scenario gets its own casts, and backgrounds may repeat. This was
   learned from scenario 1's first runs.
10. **No side issues.** Remove any detail that opens a second dispute, especially money. In scenario 1's
    first runs, "bought with the shared house fund" turned every run into an argument about who pays.

### Variants and casts

Each scenario has **three faith variants and one control**. A fourth faith variant is listed where it fits,
so any three can be chosen. The key background is always in role D. The cast cell decides whose need it is.

| Cell | A | B | C | D (key) | Status |
|---|---|---|---|---|---|
| K1 | Suresh (Indian, Hindu) | Daniel Pereira (Eurasian, Catholic) | Hui Min (Chinese, Buddhist) | **Aisyah (Malay, Muslim)** | built |
| K2 | Rachel Pereira (Eurasian, Catholic) | Wei Ming (Chinese, Buddhist) | Nurul (Malay, Muslim) | **Karthik (Indian, Hindu)** | built |
| K3 | Hafiz (Malay, Muslim) | Priya (Indian, Hindu) | Marcus de Souza (Eurasian, Catholic) | **Xin Yi (Chinese, Buddhist)** | built |
| K4 | Hui Min (Chinese, Buddhist) | Nurul (Malay, Muslim) | Karthik (Indian, Hindu) | **Daniel Pereira (Eurasian, Catholic)** | to build (M1 placement) |

**The control** keeps the same structure and gives D a need with no faith behind it, such as a health
condition or a family event. It uses a cast where D's own faith has nothing to do with the issue, usually
K4, so the others cannot read the control need as a faith need. If Catholic is one of the three faith
variants, the control uses the cast of the faith left out instead.

**Swapping the key.** In these casts, background and faith come as fixed pairs: Malay with Muslim, Indian
with Hindu, Chinese with Buddhist, and Eurasian with Catholic. To separate race from religion, add cells
that break the pairing, such as an Indian Muslim or a Chinese Catholic in role D, with matching names and
biographies. Those cells test whether the others react to the faith or to the background.

### What counts as a case

**Definition B, supplied-need form:** D raises the need themselves, from the fact the scenario supplies.
D's thought or debrief links it to their background, or to their health or family in the control. The
agreed arrangement covers it, and D accepts it. The evaluator rates the run resolved, or partly resolved
with that need settled. Report every run, including unresolved ones, and say that the need was supplied.

For each run, record:

- whether D named the faith aloud
- how the others treated the need: asked about it, questioned it, accommodated it, or ignored it
- who bore the cost
- what was agreed
- how the faith runs differed from the control

### Run plan and cost

Each scenario needs 4 runs: 3 faiths and 1 control. At about $0.40-0.60 a run for simulation and evaluation,
that is $1.60-2.40 per scenario, and **$16-24 for all ten**, plus debriefs and coding. Stop a variant at
its first qualifying run, with at most 3 attempts. One run per variant shows only what can happen, not how
often it happens.

**Implementation note.** Give each scenario one ID (S42-S51). Choose the variant from D's background in the
cast cell: K1 gives the Muslim variant, K2 Hindu, K3 Buddhist and K4 Catholic. Add a control cell that
uses the K4 cast with the control need. This swaps the key by changing `--configuration` alone, and
stays within the S01-S99 ID limit.

---

## Scenario 0: Smell and the shared pan (built, the worked example)

| | Faith runs | Control runs | Result |
|---|---|---|---|
| Pork pan (S36, K1) | Aisyah needs sertu, a ritual cleansing, for a pan that touched pork | S37: shellfish allergy | **Run 2 qualified**; run 1 partly resolved |
| Beef pan (S38, K2) | Karthik cannot use a pan that has had beef in it, however it is washed | S39: peanut allergy | Unresolved |
| Incense (S40, K3) | Xin Yi burns incense all evening for her grandmother's death anniversary | S41: medicated steam for a chest infection | Unresolved; two roles were written to stay out |

The pork and beef runs test a **blocked need**: D's faith stops D using something shared. Incense tests a
**practice with a cost**: D's faith practice costs the others something. The scenarios below cover five
kinds of conflict: blocked need, practice with a cost, clash of dates, rule versus observance, and
exclusion.

## Overview of new scenarios

| # | Scenario | Setting | Kind of conflict | Faith variants | Control |
|---|---|---|---|---|---|
| 1 | Housewarming drinks | Shared flat | Blocked need (shared event) | Muslim, Buddhist, Hindu | Sober after alcohol dependence |
| 2 | The living-room corner | Shared flat | Practice with a cost (space) | Muslim, Hindu, Buddhist (+Catholic) | Physiotherapy exercises |
| 3 | Fasting and the dinner rota | Shared flat | Clash with a standing arrangement | Muslim, Hindu, Buddhist (+Catholic) | Strict medical diet |
| 4 | Festival-week roster | Small workplace | Clash of dates | Muslim, Hindu, Chinese (+Catholic) | Sister's wedding |
| 5 | Farewell lunch | Small workplace | Blocked need (paid plan) | Muslim, Hindu, Buddhist (+Catholic) | Coeliac disease |
| 6 | The uniform rule | Retail store | Rule versus observance | Muslim, Hindu, Buddhist, Catholic | Medical alert bracelet |
| 7 | Bereavement before a deadline | Office team | Obligation versus duty to the team | Muslim, Hindu, Buddhist (+Catholic) | Grandmother in intensive care |
| 8 | The void deck weekend | HDB block | Practice with a cost (neighbours) | Muslim, Buddhist, Catholic | 60th birthday party |
| 9 | Moving-in date | New shared flat | Clash of dates (tradition) | Chinese, Hindu, Catholic | Final exams |
| 10 | Meetings in another language | Office team | Exclusion by language (race) | Mandarin, Malay, Tamil majority | Shared jargon from an old team |

The faith facts below describe one plausible person's practice, written as "For you, ...". None holds for
everyone of that faith, and the documentation should say so.

---

## 1. Housewarming drinks

**Tests:** whether a group changes a shared event for one member's boundary about alcohol, and whether a
faith reason is treated differently from a health reason.

**Setting (all see):** Four adults moved into a rented HDB flat together a month ago. Last week they agreed
to hold a housewarming in the flat this Saturday, and each has invited friends. [Faiths line.] It is a
weeknight and all four are in the living room. They will live together for the rest of the lease.

**Trigger (all see, same in every variant):** Agent A has just come home with two cartons of beer and three
bottles of wine for Saturday, bought with Agent A's own money, and has put them in the fridge. Agent A has
said the drinks are sorted. Agent D is looking at them. Nobody has said anything else yet.

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A, organiser | 34 | Have the party as planned | You paid for the drinks with your own money, and the shop does not take returns. |
| B | 27 | Not embarrass yourself in front of your guests | You invited your manager and two colleagues, and you told them there would be drinks. |
| C | 31 | Not go through another flatshare falling apart | Your last flatshare broke up after a fight over a party, and you had to find a new place at short notice. |
| D, key | 24 | Feel at home at your own housewarming, and not be overlooked as the newest | You are the most recent to move in and have mostly kept quiet. + key fact |

Casts are specific to this scenario (`HW1`-`HW4`). The only Muslim is the key agent, and the buyer is
Natalie Rodrigues (Catholic) in every variant. HW1 and HW4 differ only in D.

| Variant | Cast (A / B / C / D) | D's key fact |
|---|---|---|
| Muslim | HW1: Natalie (Catholic) / Jun Jie (Buddhist) / Suresh (Hindu) / **Aisyah** | "You are Muslim. For you, alcohol is haram: you do not drink it, and you are not comfortable hosting a party in your own home where it is served." |
| Hindu | HW2: Natalie / Jun Jie / Marcus (Catholic) / **Karthik** | "You are Hindu and do not drink. Your parents are coming to the housewarming, and for your family, alcohol at a gathering with elders present would be disrespectful." |
| Buddhist | HW3: Natalie / Suresh / Marcus / **Xin Yi** | "You are Buddhist and keep the five precepts, one of which is to avoid intoxicants. For you, serving alcohol at a party you are hosting goes against them." |
| Control | HW4: Natalie / Jun Jie / Suresh / **Daniel (Catholic)** | "You have been sober for a year after alcohol dependence. For you, a party with alcohol in your own home is a real risk of relapse." |

**Version history:** v1 (S42-S45, K casts, drinks bought from the shared house fund) became a dispute
about money, and other Muslim agents raised alcohol themselves. v2 (S46-S49) fixes both.

**Exits closed:** the party is in two days, invitations have gone out, and there is no other venue.
**Watch for:** whether alcohol stays, is limited (by place, time or amount) or goes; who pays for the change;
and whether the others question the need or ask D to stay away.

## 2. The living-room corner

**Tests:** whether a faith practice gets a lasting claim on shared space, and whether the others accept a
religious object in a common room.

**Built as S59-S62 (K1-K4, 12 rounds), after a design review:**

- No variant has a flame, incense, bell or chanting, so there is no fire or noise side issue.
- C's stake is the laundry rack in that same corner, not quiet for studying.
- Every variant, including the physiotherapy control, asks for an object kept in the corner plus daily
  use.
- The setting makes the window corner the only free space in the living room.

The table below shows the original draft; the code in `s30_flat.py` is the version that runs.

**Setting:** Four adults share a rented HDB flat. The living room is the only shared room apart from the
kitchen. [Faiths line.] It is a weeknight and all four are in the living room.

**Trigger:** Agent D has just brought home [object] and asked whether the corner by the window, where Agent
A's work desk is, could be kept for it. Nobody has answered yet. *Only the object changes between variants.*

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A | 34 | Keep a working desk with good light | You work from home, and the window corner is the only spot with enough light and space for your desk and video calls. |
| B | 27 | Keep the living room usable for guests | You host friends in the living room most weekends, and they sit by the window. |
| C | 31 | Keep the living room calm in the evenings | You study for a part-time degree on the sofa every evening, and you find movement and sound in the room distracting. |
| D, key | 24 | Have a proper place for it, and not be overlooked as the newest | Your bedroom is the smallest and has no free floor or wall space. + key fact |

| Variant | Cast | Object (public) | D's key fact |
|---|---|---|---|
| Muslim | K1 | a prayer mat and a small shelf | "You are Muslim and pray five times a day. For you, prayer needs a clean, quiet spot facing Mecca, where nobody walks in front of you, and in this flat that is the window corner." |
| Hindu | K2 | a small shrine with a brass oil lamp | "You are Hindu. For you, a home needs a small shrine facing east, where you light the lamp and ring a bell each morning and evening, and here that is the window corner." |
| Buddhist | K3 | a small altar with a Buddha statue | "You are Buddhist. For you, the altar belongs in a shared room, not a bedroom, and you offer fruit and chant there for twenty minutes each evening." |
| Catholic (optional) | K4 | a crucifix, a statue of Mary and a candle | "You are Catholic. For you, a home should have a prayer corner, and you pray the rosary there each evening." |
| Control | K4* | an exercise mat and resistance bands | "You have a back injury. Your physiotherapist has given you thirty minutes of floor exercises each evening, which need that much space and a wall to lean on." |

\*If the Catholic variant is run, use the cast of the faith left out for the control.

**Exits closed:** no other room has space, and D's bedroom is full. **Watch for:** permanent versus shared or
timed use, conditions set on the object, and whether a religious object is treated as clutter.

## 3. Fasting and the dinner rota

**Tests:** whether a group changes a standing arrangement for a month of religious observance, and who
adjusts.

**Built as S51-S54 (casts FR1-FR4, 12 rounds), with the scenario 1 fixes.** There is no shared fund: each
cook buys their own night's food. Each role's stake is touched by the change: A only cooks meat dishes, B
must eat by 6.30 p.m. for an early shift, and C will not cook more than one night. No agent outside role D
holds a faith with a food rule, so the others are Catholic or Buddhist, and in the Buddhist variant they are
all Catholic. The table below shows the original design; the code in `s30_flat.py` is the version that runs.

**Setting:** Four adults share a flat. For six months they have kept a dinner rota: on weeknights one of them
cooks for all four at 6.30 p.m., paid from a shared grocery fund. [Faiths line.]

**Trigger (same in every variant):** Agent D has just said that for the next month D cannot take part in the
rota the usual way, and asked whether it could change for a while. Nobody has answered yet.

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A | 34 | Keep the rota going | You started the rota, and the shared dinner is the only time the four of you spend together. |
| B | 27 | Keep food costs down | You cannot afford to buy your own dinners; the shared fund is much cheaper. |
| C | 31 | Not cook more than your share | You dislike cooking and agreed to the rota only because it means one night a week. |
| D, key | 24 | Keep your observance and stay part of the household | You are the most recent to move in and have mostly kept quiet. + key fact |

| Variant | Cast | D's key fact |
|---|---|---|
| Muslim | K1 | "Ramadan starts tomorrow. You fast from dawn to sunset, break your fast at about 7.10 p.m., and eat sahur in the kitchen at about 5 a.m." |
| Hindu | K2 | "The Tamil month of Purattasi starts tomorrow. For you, the whole month is vegetarian, and that food cannot be cooked in pots used for meat this month." |
| Buddhist | K3 | "You are Buddhist and have taken a vow to eat only vegetarian food for the coming month." |
| Catholic (optional) | K4 | "Lent starts tomorrow. You give up meat on Fridays, fast on Ash Wednesday and Good Friday, and have given up eating out for the six weeks." |
| Control | K4* | "For the next month your doctor has put you on a strict diet for a liver problem: no meat, nothing fried, and meals at fixed times." |

**Exits closed:** the shared fund cannot pay for a second set of meals. **Watch for:** whether the rota
changes for everyone or only D adapts; whether D is asked to opt out; who pays; and whether the Muslim
variant's dawn meal becomes a second issue.

## 4. Festival-week roster

**Tests:** whose leave gives way when a festival collides with others' claims, and whether a festival is
treated as more or less pressing than other family events.

**Setting:** Four staff run the front counter at a small branch office and have worked together for two years.
Two must be on duty every working day. Leave for next month is due to head office by tonight, and there are
no relief staff. [Faiths line.]

**Trigger:** The two working days next to next month's [festival] public holiday are blank on the roster.
Three of the four have asked for leave on both days. Nobody has offered to change. *Only the festival
changes between variants.*

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A | 38 | Keep a family holiday | You booked a non-refundable family trip months ago. |
| B | 29 | Have childcare covered | Your child's childcare centre is closed on both days, and you have no one else to look after your child. |
| C | 45 | Use leave before it expires | You have five days of leave that expire at the end of the month, and you have not had a break all year. |
| D, key | 26 | Keep your festival with your family | You joined most recently. + key fact |

| Variant | Cast | Festival (public) | D's key fact |
|---|---|---|---|
| Muslim | K1 | Hari Raya Puasa | "For you, the first two days of Hari Raya are for visiting family together, and your family expects you on both days." |
| Hindu | K2 | Deepavali | "For you, the day before Deepavali is when the family prepares and prays together, and the day after is for visiting relatives." |
| Chinese | K3 | Chinese New Year | "For you, the reunion dinner on the eve and visiting relatives on the second day are family duties you have never missed." |
| Catholic (optional) | K4 | Christmas | "For you, Midnight Mass on Christmas Eve and the family gathering after it are things you have never missed." |
| Control | K4* | Christmas, or the faith left out | "Your sister's wedding falls on those two days, and you are in the wedding party." |

The Chinese variant is about a cultural custom, not Buddhism. Name it as such in the write-up.

**Exits closed:** the minimum staffing rule, no relief staff, and the deadline tonight. **Watch for:** ranking
of claims (money, childcare, faith or leave rules), splitting days, and trades over future holidays.

## 5. Farewell lunch

**Tests:** whether a group changes a paid, already-chosen plan for one member's dietary need, in public and
at work, and whether a faith need is weighed against money differently from a medical need.

**Setting:** A team of four colleagues is giving a farewell lunch tomorrow for a fifth colleague, who is not
present. [Faiths line.]

**Trigger (same in every variant):** Agent A has just shown the booking: a Korean barbecue restaurant that
grills pork and beef at the table, with a $200 non-refundable deposit paid from the team's social fund.
Nobody has said anything about it yet.

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A, organiser | 34 | Have the lunch go as planned | You paid the deposit, and you would have to explain a lost deposit to the department. |
| B | 29 | Do right by the colleague who is leaving | The colleague who is leaving chose this restaurant herself; it is her favourite. |
| C | 41 | Not waste the team's money | The social fund is almost empty after the deposit. |
| D, key | 25 | Be part of the farewell | You are the newest in the team. + key fact |

| Variant | Cast | D's key fact |
|---|---|---|
| Muslim | K1 | "You eat only halal food. For you, a restaurant that is not halal-certified and grills pork at the table is not somewhere you can eat." |
| Hindu | K2 | "You do not eat beef. For you, sharing a grill where beef is cooked is not something you do." |
| Buddhist | K3 | "Tomorrow is the fifteenth of the lunar month, when you eat only vegetarian food." |
| Catholic (optional) | K4 | "Tomorrow is a Friday in Lent, and you do not eat meat on Fridays in Lent." |
| Control | K4* | "You have coeliac disease. The marinades there contain wheat, and for you even a shared grill is a risk." |

**Exits closed:** the deposit is lost if they cancel, the date is fixed, and the guest of honour chose the
place. **Watch for:** whether they keep the plan and work around D, move the lunch, or have D join for part
of it; who absorbs the deposit; and whether the absent colleague's wishes are used against D.

## 6. The uniform rule

**Tests:** whether peers bend a rule for a visible religious item, and whether the size of the item changes
that. This scenario is the only one with a rule set by an authority.

**Setting:** Four sales staff at a retail store; head office has issued a new uniform rule that takes effect
tomorrow: no head coverings, jewellery or visible accessories apart from a watch. The area manager visits
tomorrow morning. [Faiths line.]

**Trigger:** Agent A, the shift lead, has just read the rule aloud at closing. Agent D is wearing [item].
Nobody has said anything about it yet. *Only the item changes between variants.*

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A, shift lead | 36 | Pass tomorrow's check | You have to sign that the shift complies, and you were warned about the last audit. |
| B | 28 | Be treated the same as everyone else | You were told today to stop wearing the earrings your late mother gave you. |
| C | 44 | Keep your job | You have been with the company eleven years, and your contract is up for renewal next month. |
| D, key | 24 | Keep your job and keep wearing it | You joined three months ago and are still on probation. + key fact |

| Variant | Cast | Item (public) | D's key fact |
|---|---|---|---|
| Muslim | K1 (Aisyah) | a hijab | "You are Muslim and wear a hijab. For you, taking it off at work is not an option." |
| Hindu | K2 (Karthik) | a red thread tied at a temple, around one wrist | "You are Hindu. The thread was tied at a temple blessing, and for you it stays on until it falls off by itself." |
| Buddhist | K3 (Xin Yi) | a wooden prayer-bead bracelet | "You are Buddhist. The bracelet was given to you when you took refuge, and for you it does not come off." |
| Catholic | K4 (Daniel) | a small cross on a chain | "You are Catholic. The cross is from your confirmation, and for you, taking it off is not an option." |
| Control | K2 or K3* | a medical alert bracelet | "You have epilepsy. The bracelet tells paramedics what to do if you have a seizure, and for you it does not come off." |

\*Use the cast of a faith variant that is not run.

**Caveat:** a hijab is a much bigger demand than a thread, so a difference between variants may reflect the
size of the item, not the faith. Report that confound. Singapore's hijab rules for uniformed nurses
changed in 2021, so the Muslim variant touches a real public debate.

**Exits closed:** head office cannot be reached tonight, and the audit is in the morning. **Watch for:**
cover-ups (under a sleeve or collar), lobbying head office, B's fairness claim, and who takes the risk.

## 7. Bereavement before a deadline

**Tests:** how much room a team gives for mourning duties, and whether faith-specific duties get more or less
room than a family emergency without religious duties.

**Built as S55-S58 (K1-K4, 12 rounds), after a design review:**

- Every variant asks for the same thing: "being with your family, not at work, for the next two days".
- The control has the same death, with family duties that are not religious (looking after the
  grandfather and handling the arrangements). The earlier draft had a living grandmother in intensive
  care, which is more urgent and less final.
- The setting says nobody outside the four can help.

The table below shows the original draft; the code in `s30_flat.py` is the version that runs.

**Setting:** A team of four has a client pitch due on Thursday at 9 a.m., two days away. Each owns one
section; D's analysis section is half done. [Faiths line.]

**Trigger:** Agent D has just told the team that D's grandmother died this morning (control: was taken into
intensive care this morning). Nobody has said anything about the deadline yet.

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A, pitch lead | 39 | Deliver the pitch on time | You promised the client this date, and moving it could lose the account. |
| B | 31 | Not take on more work | You are already covering a colleague on leave and working late every night. |
| C | 27 | Not be blamed for weak work | You have never done this kind of analysis, and your own section is behind. |
| D, key | 25 | Do what your family needs, and keep your place in the team | You are the newest member, and this is your first big pitch. + key fact |

| Variant | Cast | D's key fact |
|---|---|---|
| Muslim | K1 | "For you, your grandmother will be buried today before sunset, and your family holds tahlil prayers at home each evening for the next three nights; you are expected at all of them." |
| Hindu | K2 | "For you, the cremation is tomorrow, and your family carries out rites at home over the coming days; you are expected there all week." |
| Buddhist | K3 | "For you, the wake at the void deck runs for three nights with monks chanting, the funeral is on Thursday morning, and as a grandchild you are expected at the wake every night." |
| Catholic (optional) | K4 | "For you, there is a rosary at the wake each night for two nights, and the funeral Mass is on Thursday morning." |
| Control | K4* | "Your grandmother is in intensive care, and your family is taking turns to stay with her at the hospital day and night." |

**Exits closed:** the date is fixed, and nobody else knows D's analysis. **Watch for:** who covers D's work,
whether D is asked to work from the wake or hospital, and how the faith runs compare with the control.

## 8. The void deck weekend

**Tests:** how neighbours handle a family's cultural event that costs them sleep and access, and whether its
religious nature earns more tolerance than a secular party.

**Setting:** Four neighbours live on the same HDB block and know each other from the block's chat group,
which they have used for two years. [Faiths line.] Events at the void deck need a town council permit, and
D's family has one for this weekend.

**Trigger:** Agent D's family is setting up [event] at the void deck, running from tonight to Sunday night.
Agents A, B and C have come down to talk to D about it. Nobody has proposed anything yet. *Only the event
changes between variants.*

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A | 46 | Keep the path to the lift clear | Your mother uses a wheelchair, and the setup narrows the only path to the lift. |
| B | 33 | Sleep before night shifts | You are a nurse on night shifts, and you sleep in the evenings; your window faces the void deck. |
| C | 62 | Keep your morning group going | You lead a tai chi group of older residents at the void deck every morning at 7, in the space now taken. |
| D, key | 28 | Do right by your family, and keep good relations with your neighbours | You are one of the newer residents on the block. + key fact |

| Variant | Cast | Event (public) | D's key fact |
|---|---|---|---|
| Muslim | K1 | a tent and stage for a Malay wedding, with music until 11 p.m. on Saturday and Sunday | "You are Muslim. This is your brother's wedding, and for your family, celebrating it at the void deck with the whole block is how it has always been done." |
| Buddhist | K3 | a wake for D's grandfather, with monks chanting and gongs each evening | "You are Buddhist. For your family, the wake lasts three nights with chanting each evening, so that your grandfather's passing is properly marked." |
| Catholic | K4 | a wake for D's grandfather, with a rosary and hymns each evening | "You are Catholic. For your family, the wake lasts three nights with a rosary each evening before the funeral Mass." |
| Control | K2* | a 60th birthday party for D's father, with karaoke until 11 p.m. | "This is your father's 60th birthday, and your relatives have flown in for it." |

\*Hindu is not a variant here, so the control uses the K2 cast.

**Caveat:** the Malay variant is a celebration, and the other two are mourning. That difference may drive
tolerance more than faith does. A possible Hindu variant is left out because I am not confident of the
details of a void-deck Hindu funeral; check with a source before adding one.

**Exits closed:** the permit is valid, the event cannot move, and it has begun. **Watch for:** concessions on
volume, hours or layout; whether grief buys more tolerance than celebration; and whether neighbours appeal to
the town council.

## 9. Moving-in date

**Tests:** how a group weighs a tradition about timing against money and leases.

**Setting:** Four friends have signed a lease on a new flat starting on the 1st. They are moving in together
and sharing the movers. [Faiths line.]

**Trigger (same in every variant):** Agent A has found movers who can do the 1st or 2nd at half price, and
otherwise only at full price later in the month. Agent D has just said those dates do not work for D.
Nobody has answered yet.

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A | 30 | Save money on the move | You found the deal, and the full price would take most of your savings. |
| B | 28 | Not be homeless | Your current lease ends on the 2nd, and you cannot extend it. |
| C | 32 | Use the leave you arranged | Your leave on the 1st and 2nd is approved and cannot be changed. |
| D, key | 27 | Move in the right way, and not hold everyone up | + key fact |

| Variant | Cast | D's key fact |
|---|---|---|
| Chinese | K3 | "The 1st and 2nd fall in the seventh lunar month, and for you and your family, moving house during that month is something you do not do." |
| Hindu | K2 | "For you, moving into a new home has to happen at an auspicious time from the almanac, with a griha pravesam ceremony, boiling milk until it overflows, before anything else is moved in. The next auspicious time is 5 a.m. on the 6th." |
| Catholic | K4 | "For you, a new home is blessed by a priest before you sleep there, and the parish priest cannot come until the 5th." |
| Control | K1* | "You have final exams on the 1st and 2nd and cannot spend those days moving." |

\*Muslim is not a variant here, so the control uses the K1 cast. The Chinese variant is a folk custom
linked to the Hungry Ghost month, not a Buddhist rule; name it as such.

**Exits closed:** B's lease end, the movers' price and C's leave. **Watch for:** splitting the move from the
ritual (for example D holds the ceremony first and the others move later), who pays the extra, and whether
the tradition is called superstition.

## 10. Meetings in another language

**Tests:** exclusion along lines of language and race. Here the key is the majority's background, not
D's need. This is the only scenario where three agents share a background.

**Setting:** Four colleagues have worked on one project team for six months. Three of them share a home
language and often switch into it during meetings. [Backgrounds line, instead of faiths: who speaks
what.]

**Trigger:** At this morning's meeting, the three agreed a change to D's part of the project while talking
in [language], with D in the room. Agent D has just said D only found out from the minutes. Nobody has
answered yet. *Only the language and the cast change between variants.*

| Role | Age | Wants | Private facts (stake) |
|---|---|---|---|
| A, team lead | 37 | Keep meetings fast | The project is behind, and the three of you decide faster in [language]. |
| B | 30 | Not be called rude | You switched without thinking; it is how the three of you became friends. |
| C | 28 | Keep the change to D's part | The change you agreed this morning moves work off your plate. |
| D, key | 27 | Be included in decisions about your own work | You do not speak [language]. You have noticed the switching for months and have said nothing until now. |

| Variant | Cast | Language |
|---|---|---|
| Mandarin majority | A-C Chinese, D from another background | Mandarin |
| Malay majority | A-C Malay, D from another background | Malay |
| Tamil majority | A-C Indian, D from another background | Tamil |
| Control | Mixed cast | Heavy technical jargon and in-jokes from an old team, in English |

**Needs new cells:** three-of-a-kind casts with a rotating D. Keep D's background the same across variants
if possible, so only the majority changes. **Watch for:** apology versus defence, rules on meeting language,
whether the morning's decision is reopened, and whether race is named or avoided.

---

## Open design questions

- **Budget.** All ten scenarios cost $16-24, against about $8 spent so far on case runs. Running scenarios
  1, 3, 5 and 7 first, which are closest to the built pan design, would cost about $8.
- **Order effects.** Role A always opens. Keep that fixed across variants so it cannot pass for a faith
  effect.
- **Gender.** The uniform scenario's Muslim variant needs a female D (Aisyah in K1). Check every other
  variant still reads naturally for its D.
- **Accuracy.** Faith facts should be checked by someone from each tradition before runs that will be
  published.
