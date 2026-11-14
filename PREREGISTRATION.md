# Pre-registration — Cincinnati AI Labor Market 2.0

**Status: DRAFT for the check-in.** Written 13 November 2026, before any new data values for
2.0 were downloaded or computed. It is committed to the local `v2.0` branch so the timestamp
can be checked against the analysis commits that follow. After the author's decisions at the
check-in, any change is recorded in the **Amendments** section at the bottom with its date and
reason. Changes made after a data value has been seen are marked as such.

The purpose is simple. 1.0 drew its conclusions after seeing its data. 2.0 states in advance
what evidence would support or overturn each conclusion, which series would show it, and when
it will be checked, so the result cannot be fitted to the hypothesis afterwards.

---

## 0. What had been seen before this was written

Honesty about contamination matters more than a claim of purity.

1. **All of 1.0's values** (README.md, CALCULATIONS.md, the 1.0 report). Several hypotheses
   below re-test those values, so they were known.
2. **Release metadata only** (which vintages exist, file names, period coverage). Checking
   which releases exist was permitted and is not a data value.
3. **Values seen in web-search snippets on 13 November 2026, before this file was written:**
   - Cleveland Fed SORCE survey (Fourth District firms): 74% of respondents used AI for
     business tasks in March 2026 and 81% in September 2026; in March, 8% said AI use raised
     staffing and 4% said it lowered it.
   - Census BTOS, as reported secondhand: national business AI use "rose from 17% to 25%" over
     some ten-month window; Denver and Phoenix "around 36%". Cincinnati is not among the 25
     metros BTOS publishes (verified from the file's list of metro names, without values).
   - No QWI, QCEW, CES, LAUS, BEA, patent, HERD, IPEDS, postings or data-center value for 2.0
     had been seen.

Hypotheses H5 (adoption) were written knowing the SORCE figures above. They are therefore
treated as descriptive, not as confirmatory tests.

---

## 1. Geography (one definition, used everywhere)

**Greater Cincinnati = the Cincinnati, OH-KY-IN Metropolitan Statistical Area, CBSA 17140**,
OMB 2023 delineation, 15 counties: Brown, Butler, Clermont, Hamilton, Warren (OH); Boone,
Bracken, Campbell, Gallatin, Grant, Kenton, Pendleton (KY); Dearborn, Franklin, Ohio (IN).

- Where a source publishes the MSA directly (OEWS, CES, LAUS, QCEW area C1714, BEA), that
  series is used.
- Where a source publishes by state part (QWI metro files), the Ohio, Kentucky and Indiana
  parts are summed. The combined series ends at the **earliest** of the three states' last
  quarters. No state part is extrapolated.
- Where a source is published only for a different area, it is labelled with that area every
  time it appears: ODJFS "Cincinnati MSA" projections = **Ohio counties only**; AEI, BTOS =
  **state**; SORCE and the Beige Book = **Fourth Federal Reserve District**.
- 1.0's "core seven counties" table is retired as a geography; county detail appears only as
  county detail.

## 2. Peer-selection rule (written before any peer value was computed)

Three peer sets, fixed now:

| Set | Rule | Members |
|---|---|---|
| **P1 (primary)** | The 19 peer metros the Cincinnati Regional Chamber uses in *State of the Region 2026* (15 Oct 2026, p. 6). Chosen because it was fixed by a regional institution before this study and is the comparison regional readers already use. | Atlanta, Austin, Baltimore, Charlotte, Cleveland, Columbus, Dayton, Denver, Detroit, Indianapolis, Kansas City, Louisville, Milwaukee, Minneapolis, Nashville, Pittsburgh, Raleigh, St. Louis, Tampa |
| **P2 (size rule)** | All MSAs whose July 2025 Census population estimate is between 0.6× and 1.4× Cincinnati's. | Determined mechanically from the Vintage 2025 file |
| **P3 (structure rule)** | The 10 MSAs among the 60 most populous with the lowest Duncan dissimilarity index to Cincinnati's 2025 QCEW private employment shares across 2-digit NAICS sectors. | Determined mechanically |

Named benchmarks, reported separately and never pooled with peers: **United States**,
**Ohio**, and **Columbus** (in-state; the required data-center comparator, with New Albany /
Licking County shown as its own row).

Reporting rule: for every comparative statistic, report Cincinnati's value, its rank within
P1, and the P1 median and interquartile range. A Cincinnati difference is called **robust**
only if Cincinnati falls outside the peer interquartile range in the same direction in at
least two of P1, P2 and P3. Otherwise it is described as within the normal range of peers.

The reviewer's statement that "Columbus is 14 points higher" is treated as an untested guess.

---

## 3. Research questions

- **RQ1 Adoption.** How widely and how fast are firms in the region using AI, compared with
  Ohio, Kentucky, Indiana, the nation and peers?
- **RQ2 Capability.** Is the region building AI capability or buying it, once its industry
  mix is accounted for?
- **RQ3 Labor market (central).** Since late 2022, has hiring of early-career workers into
  AI-exposed industries fallen relative to experienced workers, by more than in less-exposed
  industries, by more than in peer metros, and by more than the 2022–23 interest-rate shock
  explains?
- **RQ4 Output.** Are AI-exposed industries in the region producing more per worker than
  less-exposed industries since 2022?
- **RQ5 Infrastructure.** What AI-related physical investment (data centers) is coming, with
  how many permanent jobs per MW, what effect on electricity rates, at what public cost, and
  does it create AI-related work here?
- **RQ6 Re-test of 1.0.** Do 1.0's six main claims survive when tested by comparison rather
  than by level?

## 4. Definitions fixed in advance

- **Early-career** = QWI age group A03 (22–24). Secondary: A04 (25–34). **Experienced** =
  A05+A06 (35–54).
- **Pre-period** = 2018Q1–2019Q4 (primary). Sensitivity: 2022Q1–2022Q4. Quarters
  2020Q1–2021Q4 are excluded from all estimates. **Post-period** = 2023Q1 to the last quarter
  available for the combined MSA. ChatGPT's release (30 Nov 2022) dates the break.
- **Industry AI exposure** = employment-weighted mean occupational exposure within each
  NAICS 3-digit industry, using **national OEWS May 2022 industry staffing patterns** (the last
  reference period before ChatGPT, so the classification cannot respond to the outcome).
  Occupational exposure measures, each run separately:
  1. Felten, Raj & Seamans language-model AIOE (primary, continuity with 1.0);
  2. Eloundou et al. (2024) GPT exposure, β measure;
  3. Anthropic Economic Index observed exposure (revealed use);
  4. Microsoft Research AI applicability score (Tomlinson et al. 2025), a second revealed-use
     measure — subject to confirming the file is public and joinable at SOC level.
  **Exposed** = top tercile of industries (national employment-weighted); **less exposed** =
  bottom tercile. Sensitivity: quartiles.
- **Interest-rate-sensitive placebo industries** = construction (NAICS 23) and durable-goods
  manufacturing (NAICS 33): high rate sensitivity, low AI exposure. Fixed by convention from
  the monetary-transmission literature, not chosen from the data.
- **Rate-and-tech exclusion set** = information (51), finance and insurance (52), real estate
  (53): the sectors hit hardest by the 2022–23 tightening and the tech correction.

---

## 5. Hypotheses, tests and decision rules

### H1 — The narrowing entry door (1.0's central risk). Confirmatory.

**Statement.** In the Cincinnati MSA, the early-career share of new hires fell after 2022 in
AI-exposed industries relative to less-exposed industries.

**Series.** Census LEHD Quarterly Workforce Indicators, sex-by-age metro files by NAICS
3-digit, private ownership (`qwi_[st]_sa_f_gm_n3_op_u`), Ohio, Kentucky and Indiana parts of
CBSA 17140. Primary outcome **HirN** (new hires). Secondary: **HirAS** (stable hires),
**Emp** (beginning-of-quarter employment, the Brynjolfsson–Chandar–Chen headcount analogue)
and **EarnHirNS** (monthly earnings of new stable hires). Cells flagged as suppressed are
dropped, never imputed.

**Estimate.** The triple difference, using four-quarter averages to remove seasonality:

```
DDD = { [ln H(young, exposed) − ln H(old, exposed)] − [ln H(young, less) − ln H(old, less)] }post
    − { same }pre
```

**Decision rule.**
- **Supports a narrowing entry door** if all of: DDD ≤ −0.05; DDD lies below the 10th
  percentile of a 1,000-draw permutation distribution in which industries are randomly
  assigned to the exposed and less-exposed groups; and the same sign appears with at least two
  of the exposure measures.
- **Cincinnati-specific** only if, in addition, Cincinnati's DDD is in the bottom quartile of
  peers in at least two of P1–P3. Otherwise the finding is described as a national or
  peer-wide pattern observed here.
- **Contradicts** 1.0's risk if DDD ≥ 0, or if DDD is inside the 10th–90th permutation band.
- **Practically large** if DDD ≤ −0.10 (about a 10% relative decline).

**Interest-rate threat (addressed explicitly).** The 2022–23 rate rises hit finance and tech,
the most exposed industries, as generative AI arrived. Four checks, all reported:
1. Re-estimate excluding NAICS 51, 52 and 53. If DDD falls by more than half toward zero, the
   result is described as not separable from the rate shock.
2. Placebo: estimate the same young-minus-old change in NAICS 23 and 33 against the
   less-exposed group. If the placebo change is at least as negative as the exposed-group
   change, the result is attributed to the cycle, not AI.
3. Timing: the rate shock peaked in 2023 and policy rates began falling in September 2024. A
   gap that is largest in 2023 and narrows by 2025 is read as more consistent with rates; one
   that widens through 2025 as more consistent with AI. This is labelled inference.
4. Peers: the rate shock was national, so Cincinnati-minus-peer differences net it out, except
   through industry mix, which P3 addresses.

**What will be said either way.** Even a result that passes every rule shows a pattern
consistent with AI substitution for entry-level work, not proof of it. Attribution language
is limited to "consistent with" unless an employer's own statement attributes hiring changes
to AI.

### H2 — Early-career employment (headcount version). Secondary.
Same design as H1 with **Emp** as the outcome, indexed to the pre-period. Same decision rules.

### H3 — New-hire earnings. Secondary, descriptive.
If AI reduces demand for early-career work, both hires and new-hire earnings for 22–24 fall
relative to 35–54 in exposed industries. Falling hires with rising earnings would point to
supply, not demand.

### H4 — Exposure level relative to peers (re-test of 1.0 claim 1).
Cincinnati's employment-weighted exposure on each of the four measures is described as
**average** if it lies inside the P1 interquartile range on at least three of four; otherwise
**above** or **below**. Robustness of 1.0's band table: report shares above 0.30, 0.40 and
0.50 observed exposure and the top national decile. The 0.40 cut is retained only as the
continuity measure (it matches the NY Fed benchmark); conclusions must hold at every cut.

### H5 — Adoption. Descriptive (see section 0).
BTOS AI-use rate for Ohio, Kentucky and Indiana against the nation, latest period and change
since the first AI question (September 2023). SORCE Fourth District results. AEI state usage.
AI mentions in 10-K filings of Cincinnati-headquartered public companies, 2021–2026, counted
by a fixed phrase list (`artificial intelligence`, `generative AI`, `machine learning`,
`large language model`), using SEC full-text search. No metro-level AI usage figure is
reported from any of these; a test enforces this.

### H6 — Buying or building (re-test of 1.0 claim 4). Confirmatory.
**Shift-share.** Expected computer and mathematical employment = Σ over NAICS 4-digit
industries of (MSA QCEW 2025 employment × national OEWS May 2025 share of SOC 15-0000 in that
industry). Split the gap between actual (OEWS May 2025) and national-rate employment into an
**industry-mix** component and a **within-industry** component.

**Decision rule.** "Buying rather than building" is retained only if (a) the within-industry
component is at least half of the gap, **and** (b) Cincinnati ranks in the bottom half of P1
on at least two of three per-capita capability measures: AI patents by inventor location
(USPTO AIPD with PatentsView), computer and information sciences R&D (NSF HERD), and
completions in computing, data science and statistics (IPEDS). If (a) fails, the claim is
restated as "the region's industry mix employs fewer computing workers". If (b) fails, the
claim is withdrawn. Consultancy and staffing firms advertising AI roles is reported as
description, not as evidence for the claim.

### H7 — Output per worker. Descriptive only.
BEA real GDP by industry for the MSA divided by QCEW employment in the same industries, 2019,
2022, 2023 and 2024 (last available). Exposed (51, 52, 54, 55) against less-exposed sectors,
and against peers. With two post years and BEA's suppression of small industries, no
attribution is attempted.

### H8 — Data centers (test of 1.0 claim 5, not a defence of it). Confirmatory.
1.0 said data centers are not a jobs story. That finding is **overturned** if any of these
holds on primary records (abatement agreements, tax-credit authority approvals, company
filings, county records, QCEW):
- **DC1.** Permanent on-site full-time-equivalent jobs average at least **0.5 per MW** of IT
  load (more than three times the Chamber's 0.15) across at least three operating or
  under-construction facilities in the region, or in Columbus/New Albany.
- **DC2.** QCEW NAICS 518210 employment in the MSA's published counties rose by at least
  **1,000** between 2022 and the latest annual or quarterly figure. Where QCEW suppresses the
  county cell, the result is reported as **not testable**, and nothing is estimated around the
  suppression.
- **DC3.** Permanent jobs committed in signed agreements for regional facilities total at
  least **0.1% of MSA employment** (about 1,100). Commitments are reported as commitments, not
  as jobs.

The finding is **qualified, not overturned**, if construction employment tied to data-center
projects by primary sources exceeds 1,000 concurrent workers: that is a temporary construction
story and is reported as one.

Rules that apply to every data-center number: operating, under construction and announced
capacity are kept in separate columns and never summed; every MW figure says whether it is
an interconnection request, facility capacity or IT load, and comparisons use one basis;
job comparisons use permanent, on-site, full-time-equivalent jobs; industry trackers and
broker reports are labelled private.

Electricity is descriptive: data-center load in PJM's Duke Energy Ohio/Kentucky zone (DEOK)
from PJM's load forecast; household and small-business rate effects only where a primary
source (PJM Independent Market Monitor, PUCO or utility filings) attributes them.

### H9 — Slow growth (re-test of 1.0 claim 2).
- **Comparator.** Total nonfarm, September 2024 to September 2026, same-month NSA, for
  Cincinnati, each P1 peer and the US. "Slow" only if Cincinnati is in the bottom quartile of
  P1.
- **Labor-force decline.** Decompose the change into population ageing and participation:
  expected labor force = Σ over age groups of (Census Vintage 2025 MSA population × the
  base-year MSA participation rate from ACS 1-year). Presented on its own ACS window and never
  spliced onto the LAUS months.
- **98% replacement share.** Compare Cincinnati's 2.0% growth share of projected openings with
  the other seven Ohio MSA files of the same ODJFS vintage, Ohio statewide, and the BLS
  national projections. If Cincinnati is within one percentage point of the Ohio-MSA median,
  the share is described as a feature of the projection method, not a regional fragility.

### H10 — Exposure rises with pay: national pattern or local finding?
Compute the same wage-quintile gradient for the nation and each P1 peer. If Cincinnati's top-
minus-bottom gradient lies inside the P1 interquartile range, the report says plainly that
this is a national pattern visible in Cincinnati, not a Cincinnati finding.

### H11 — Attributed displacement (re-test of 1.0 claim 6).
WARN notices for the MSA's counties in Ohio, Kentucky and Indiana, 2022 to November 2026, and
employer statements about workforce reductions, coded by one rule applied to every case,
including Kroger, P&G and Fifth Third:
- **AI named** — the employer's own statement names AI as a reason for the reduction;
- **technology named, AI not named**;
- **neither**.
"Partly" is retired. Media framing is recorded separately and never used for the code.

---

## 6. Data, vintages and when each test is run

| Lens | Series | Last data point available on 13 Nov 2026 | Released |
|---|---|---|---|
| Labor | QWI Ohio | 2026Q1 (all-firm files; firm-age and firm-size files to 2025Q4) | R2026Q4, 12 Nov 2026 |
| Labor | QWI Indiana | 2026Q1 (all-firm files; firm-age and firm-size files to 2025Q4) | R2026Q4, 5 Nov 2026 |
| Labor | QWI Kentucky | 2025Q4 (firm-age and firm-size files to 2025Q3) — so the combined MSA ends 2025Q4 | R2026Q3, 6 Aug 2026 |
| Labor | CES / LAUS metro | September 2026 (preliminary) | Oct metro release scheduled 2 Dec 2026, outside the window |
| Labor | QCEW county | 2026Q1 | 2026Q2 not yet published (checked: API returns 404) |
| Labor | OEWS metro | May 2025 | Spring 2026 |
| Adoption | BTOS | 2026 period 22 (state; no Cincinnati metro) | Updated 5 Nov 2026 |
| Adoption | AEI | April–May 2026 usage (state) | Release of 26 Jun 2026; no newer release on 13 Nov 2026 |
| Adoption | SORCE (Fourth District) | September 2026 survey | 14 Oct 2026 |
| Capability | NSF HERD | FY2024 | FY2025 scheduled 24 Nov 2026, inside the window |
| Capability | USPTO AIPD | Patents and publications through 2023 | 2023 update |
| Projections | ODJFS Cincinnati (Ohio portion) | 2022–2032 | June 2025; Ohio says 2024–2034 is being incorporated, no metro file posted |

QWI measures that need the following quarter (stable hires HirAS, EarnHirNS) end one quarter
earlier than the file's last quarter; the last quarter of each state file is often noisier
and is reported with its status flags.

To be completed after the check-in: IPEDS, PatentsView, BEA, WARN, PJM, Indeed (if used).
Every series and its last real data point goes into the vintage table in the report and in
`CALCULATIONS.md`. Nothing is extrapolated to fill a gap.

**When tests run.** Once, after the check-in decisions, on the data available on the day of
download, with the data window closing on 30 November 2026. A series released after the
download but before 30 November (HERD FY2025, the November Beige Book) is added only if it
arrives before the analysis freeze, and the addition is logged here. Leading indicators for
later monitoring (each QWI release, OEWS May 2026 in spring 2027, BEA 2025 GDP in December
2026, the CES benchmark in March 2027) are listed in the report's outlook and not used in 2.0.

## 7. What will be reported regardless of outcome

Every test above is reported, including nulls and results that contradict 1.0 or the author's
stated optimism. The headline findings are chosen by the decision rules here, not by which
results are most interesting.

---

## 8. Extension for 2.1: awareness and participation, and the agent register

**Added 14 November 2026** on the local branch `v2.1`, under the 2.1 prompt (`PROMPT_2.1.md`).
The project is named "Cincinnati AI Labor Market 2.1" from this point; "2.0" above refers to
the unpublished design stage. Sections 1–7 are unchanged and still govern H1–H11.

### 8.0 What had been seen before this section was written

Web searches on 14 November 2026, made while writing the 2.1 prompt, returned these values.
They are disclosed so the reader can judge which tests they could have shaped.

- **Cincinnati only.** A community group's newsletters list monthly meetings through 2026 and
  state membership of "over 1,400", then "over 1,700", then "over 2,000" (spring 2026).
  Attendance claims for an annual June event: "nearly 1,500" (2024, one news item), "1,100
  over 3 days" (2025, a recap), "over 1,000 attendees, 175 speakers, 150 volunteers" (year
  unclear). A statewide summit: "375+ attendees" (2024) and "300+" projected (2025).
- **Existence only.** That named groups, chapters and events exist in Cincinnati, Columbus,
  Dayton and Louisville; the number of months with Internet Archive snapshots for five sites
  (16, 14, 11, 8, 1) and none for a sixth.
- **Agent register.** Product and programme names in search snippets (one Cincinnati vendor's
  agent product; small local agent vendors). The eight rows of `data/ai_adoption_employers.csv`
  were known from 1.0.
- **Not seen:** any event count for any metro; any peer-metro membership or attendance figure;
  any Google Trends value; any count of postings naming AI tools; any state or metro adoption
  rate beyond those in section 0.

Consequence: every statement about Cincinnati's **level** of activity is descriptive. The
confirmatory test (H12) is **comparative**, and no comparison value had been seen.

### 8.1 Research questions added

- **RQ7 Awareness and participation.** How much public AI convening is there in Greater
  Cincinnati compared with peer metros, how regular and how broad is it, are employers part of
  it, and is it related to firms' adoption of AI?
- **RQ8 Agents at work.** In which business functions do the region's large employers state
  that AI agents are in production, at what scale, and what do they say it does to jobs?

### 8.2 Definitions fixed in advance

- **Terms.** *Awareness and participation* is never called adoption. *AI agent* = a system
  that carries out a multi-step task by itself using tools or other software, with human
  review of the result at most. *AI assistant* = drafts or suggests while a person performs
  each step. Coding follows what the source describes, not the label the company uses.
- **Event (inclusion rule).** (a) AI is the stated main subject; (b) open to people outside the
  host organization; (c) held in person in the metro, or virtual or hybrid and run by an
  organizer based in the metro. Company-internal training is excluded. A multi-day conference
  is one event. An event enters the census only with a live or archived dated page behind it.
- **Window.** 1 December 2023 – 30 November 2026, reported as three 12-month years ending
  30 November.
- **Per-capita base.** Residents aged 18–64, Census Vintage 2025 county characteristics,
  summed to each CBSA.
- **Like-for-like measures (all 19 P1 metros plus Cincinnati, collected on one day each):**
  - **L1 Platform listings.** Count of events returned on Eventbrite, Luma and Meetup for the
    metro's principal city, dated within the 60 days after the collection day, matching any of
    `AI`, `artificial intelligence`, `generative AI`, `machine learning`, `LLM`, `ChatGPT`,
    `agents`, de-duplicated and screened by the inclusion rule. Per 100,000.
  - **L2 Chapter meetings.** Meetings held in the last 12 months by local chapters of national
    AI community organizations that run a standard format, where each chapter publishes a
    dated event list. A metro with no chapter scores zero and is flagged. Count, and per
    100,000.
  - **L3 Search interest.** Google Trends interest by media market (DMA) over the last 12
    months for the topics `ChatGPT`, `Claude`, `Microsoft Copilot` and `Gemini` and the
    searches `AI course`, `AI training` and `AI jobs`; the metro's score is the mean across the
    seven terms of its DMA value. Labelled a private platform's sampled index.
- **Full census subset.** All P1 metros in Ohio (Cleveland, Columbus, Dayton) and the nearest
  P1 metro in each of Indiana, Kentucky and Pennsylvania (Indianapolis, Louisville,
  Pittsburgh). Subject to the author's decision at the 2.1 check-in. Dayton is reported in its
  own row because its labor market adjoins Cincinnati's.
- **Census measures A1–A9** as defined in `PROMPT_2.1.md`, Step 3. Back-years are rebuilt only
  from records fixed at the time (newsletter issues, archived snapshots, dated news). A
  metro-year enters a trend comparison only if at least one recurring series can be rebuilt
  for it; otherwise it is reported as not recoverable.
- **Agent register scope.** (1) Public companies headquartered in CBSA 17140; (2) the 25
  largest employers in the metro from the most recent published regional ranking, named in the
  methods; (3) AI vendors and service firms based in the metro. **Source grades:** 1 = company's
  own record; 2 = named executive on the record; 3 = vendor case study; 4 = third-party
  description of what a company could do. Only grades 1 and 2 support a finding.
- **Postings naming AI tools.** Phrase queries on CareerOneStop (NLx), 25-mile radius of each
  principal city, same day for all metros, for: `AI agent`, `agentic`, `LangChain`,
  `Copilot Studio`, `Agentforce`, `Model Context Protocol`, `prompt engineering`, `ChatGPT`,
  `Claude`, `Copilot`, `Gemini`, `OpenAI`, `large language model`, `retrieval-augmented`.
  Reported per 100,000 residents aged 18–64 because the tool caps displayed totals at 10,000,
  so a share of all postings cannot be computed.

### 8.3 Hypotheses, tests and decision rules

**H12 — Convening relative to peers. Confirmatory.** For each of L1, L2 and L3, report
Cincinnati's value, its rank in P1, and the P1 median and interquartile range. Cincinnati is
described as **above its peers** only if it lies above the P1 interquartile range on at least
two of the three; **below** if under it on at least two; otherwise **within the normal range of
peers**. P2 and P3 are not collected for this lens, and the report says so.

**H13 — Breadth. Descriptive, with conventions fixed now.** From the Cincinnati census, last
12 months: participation is described as **reaching beyond technologists** if at least half of
events are aimed at an audience other than "technical"; employers are described as **in the
room** if at least 10 of the 25 largest employers appear at least once as host, sponsor or
speaker's employer in the three-year window. Both thresholds are conventions, labelled as such.
The same two statistics are shown for the six-metro subset.

**H14 — Is awareness related to adoption? Exploratory.** Across the 20 metros, Spearman rank
correlation between each of L1–L3 and postings naming AI tools per 100,000, with an exact
permutation p-value. Described as **related** only if ρ ≥ 0.4 with p < 0.10 on at least two of
the three; otherwise "no relationship detectable with 20 metros". Shown as scatters. No
regression. Within Cincinnati: the count of employers appearing in both the event census (A6)
and the agent register at grades 1–2, out of each list's total.

**H15 — Does awareness lead? Descriptive only.** Monthly Cincinnati event counts against any
monthly metro series of AI-related postings. If no such monthly series exists in a public
source, this is reported as **not testable**, and "early indicator" is used in the report only
as a description of sequence in principle, not as a finding.

**H16 — Agents at work. Descriptive.** Reported whatever the result: in-scope employers by
group; how many have grade 1–2 evidence of an agent **in production**, of one announced or in
pilot, of assistants only, and of nothing; functions; every quantified claim with its source;
every grade 1–2 statement linking agents to headcount, quoted. The sentence "AI agents are in
production at large Greater Cincinnati employers" is used only if at least three in-scope
employers have grade 1–2 evidence of an agent, as defined in 8.2, in production. No disclosure
is reported as no disclosure, never as no use.

**AI Participation Index.** Computed only after H12–H14 are reported. Components A1, A3, A4,
A5, A6 (six-metro subset plus Cincinnati) and L3, each standardized across the metros, equal
weights. Published only if Cincinnati's rank moves by no more than two places when each
component is dropped in turn; otherwise the components are reported alone. Labelled a
constructed summary. Subject to the author's decision.

### 8.4 What this lens will not be used for

No attendance or membership figure is summed across groups. No organizer-reported figure
appears without its source. No event measure is offered as evidence of a change in employment,
hiring or output. Organizations are named; attendees are not.

---

## Amendments

| Date | Change | Reason | Made before or after seeing data? |
|---|---|---|---|
| 13 Nov 2026 | **Add H2b**: occupation-based entry-door test using ACS 1-year PUMS for the PUMAs that make up CBSA 17140. Outcome: employment of ages 22–25 relative to 35–54 in occupations in the top tercile of exposure (same four measures, national 2022 OEWS employment weights) vs the bottom tercile; pre-period 2018–2019 pooled, post-period 2023–2025 pooled (2020–2022 excluded); same peers. Secondary to H1 because ACS measures employment, not hires, and metro samples are small; reported with replicate-weight standard errors. | QWI has industries, not occupations; ACS adds the occupational dimension that the Brynjolfsson–Chandar–Chen design uses. | **Before.** No ACS value had been seen. |
| 13 Nov 2026 | Noted, no change to hypotheses: after the commit of this file, web searches for the design memo surfaced statewide data-center job figures (Weldon Cooper Center via news: about 22,300 short-term and 4,500 permanent Ohio jobs as of 2024; a study of 1,584 data centers reported at about 2.7 non-construction local jobs per MW of eventual capacity) and that the Chamber's 565 MW counts 17 existing and 2 planned facilities. | Disclosure. H8's thresholds were fixed before these were seen. | After the commit; H8 unchanged. |
| 14 Nov 2026 | **Add section 8** (RQ7–RQ8, H12–H16, definitions for the event census, like-for-like measures, the agent register and the AI Participation Index). Project renamed 2.1; work moves to branch `v2.1`. | The author's 2.1 prompt adds a sixth lens (awareness and participation) and a register of AI agents in local workflows. | **Mixed, disclosed in 8.0.** Cincinnati membership, meeting-schedule and attendance claims had been seen in search snippets; no peer-metro value, event count, search-interest value or AI-tool postings count had been seen. H12 is comparative for that reason; Cincinnati level statements are descriptive. |
