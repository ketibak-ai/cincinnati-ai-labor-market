# Audit log — Cincinnati AI Labor Market

This file has two parts. **Part I** records every change from 1.0 to 2.1 and why. **Part II** is 1.0's audit of the preliminary draft, unchanged.

---

# Part I — Changes from 1.0 to 2.1

Version 2.0 was an unpublished design stage (13 November 2026). Version 2.1 (16 November
2026) is the first version after 1.0 with results. This part records every correction to a
1.0 number or claim, what was done about each of the reviewer's objections, and what changed
in method.

### Corrections to 1.0

C1–C5 were found at the design stage; C6–C12 came from the 2.1 analysis.

| # | 1.0 said (where) | Correction | Evidence |
|---|---|---|---|
| C1 | "The region's nineteen facilities hold roughly 565 MW" (`archive/v1.0/report.txt:1509`); recorded as existing capacity (`data/local_institutional_sources.csv:20`) | 565+ MW is the Chamber's estimate for **17 existing and 2 planned** facilities, the two planned hyperscalers being the largest. It mixes operating and announced capacity and does not state the MW basis. | Chamber, *Data Centers: A Cincinnati Regional Perspective*, 12 Oct 2026 (`raw/local_institutions/chamber_data_centers_2026.txt:53-55, 103-110`) |
| C2 | "Neither the task force nor a training lab appears in the approved FY2026–2027 budget" (`archive/v1.0/report.txt:1462`) | The approved FY2026–2027 budget includes "MidWest Con – AI Investment – $50,000"; the approved FY2027 update includes "Plans Examination Artificial Intelligence Enhancement", $300,000 (capital). | City of Cincinnati budget documents; CitiCable recording of 4 May 2026 |
| C3 | Fifth Third "has announced no reductions at all" (`README.md:48-50` and the 1.0 site) | Merger-related layoffs followed the Comerica acquisition (1 Feb 2026). Merger-attributed, not AI-attributed; none reported in Cincinnati. | Reporting identified at the design stage; Texas WARN notice not retrieved |
| C4 | Kroger AI attribution "Partly" (`archive/v1.0/report.txt:1008`; `data/ai_adoption_employers.csv:2`) | Coded "technology named, AI not named" on the memo text as reported. "Partly" is retired. | Reporting identified at the design stage |
| C5 | "Thirteen checks" (`README.md:147`; `VERIFICATION.md:64`); a test label calling the LM-AIOE value "observed exposure" | The 1.0 suite runs 16 checks; the label should read language-model AIOE. No number changes. | `python tests/test_study.py` |
| C6 | Language-model exposure 0.0884 for Cincinnati and 0.0931 for the nation (`CALCULATIONS.md` section 4) | **0.0792 and 0.0948.** 1.0 joined the Felten scores by code only; they are published on 2010 occupation codes and the employment data use 2018 codes, so 20% of employment went unmatched. 2.1 carries the scores across with the BLS crosswalk (coverage 97.5%). The conclusion (average exposure) is unchanged; the gap to the nation is 0.016, not 0.005. 1.0's figures remain correct for 1.0's method and its tests still pass. | `scripts/build_industry_exposure.py`; `data/h4_exposure_peers.csv`; `tests/test_study_2_1.py::test_h4_exposure_average` |
| C7 | "The real fragility is slow growth" (`README.md:27-32`) | Growth of 0.735% from Sept 2024 to Sept 2026 equals the nation's (0.723%) and ranks 10th of 20 against the Chamber's peers (median 0.187%). **Withdrawn.** | `data/h9_growth_peers.csv`; `test_h9_growth_not_slow` |
| C8 | 98% of projected openings are replacements: "the most consequential number in this study" | Replacement is 96.3% to 101.3% of openings in every other Ohio metro file, 99.1% for Ohio and 96.6% nationally. Cincinnati's growth share (2.05%) exceeds six of seven other Ohio metros'. A property of the projection method. | `data/h9_projection_growth_share.csv`; `test_h9_replacement_share` |
| C9 | The labor force shrank by about 9,400 | The LAUS fall is entirely between Sept 2025 and Sept 2026 (model-based, revised each March). ACS shows 1,215,870 (2024) and 1,235,990 (2025). Not established. | `data/cincinnati_laus_history.csv`; `data/h9_labor_force_decomposition.csv`; `test_h9_labor_force` |
| C10 | "Cincinnati is buying AI capability rather than building it" | 57.9% of the computing-jobs gap is industry mix; 42.1% is within industries. Restated. Capability ranks: patents 16th, computing R&D 14th, awards 8th of 20. | `data/h6_shift_share.csv` and the three `h6_*` files; `test_h6_shift_share`, `test_h6_capability_ranks` |
| C11 | Exposure rising with pay presented as a Cincinnati finding | Positive in all 33 metros and the nation; Cincinnati's gradient (1.03) is below the nation's (1.20) and below the peers' middle half. | `data/h10_wage_gradient.csv`; `test_h10_gradient_is_national` |
| C12 | "No measurable AI-caused job losses"; the entry-level risk "hard to see in job counts" | Now tested. No narrowing of the entry door in AI-exposed industries in Cincinnati (−0.04 to +0.03, inside the chance range); young workers' hiring fell in every industry group. | `data/h1_ddd.csv`; `test_h1_cincinnati_entry_door` |

Also noted: BLS suppresses most private-sector cells in the Cincinnati MSA-level QCEW file
(19 of 20 sectors in 2024). 1.0's county tables were unaffected because they used county
files.

### The reviewer's objections and what 2.1 did

Verdicts are from the 2.0 design memo (`RESEARCH_DESIGN_MEMO.md`, section 3).

| # | Objection | Verdict | What 2.1 did |
|---|---|---|---|
| 1 | Title promises an effect the paper doesn't find | Partly | Title names what was tested. Key finding 1 states the result of the test, including what it could not detect |
| 2 | Dismisses the Chamber's model output while relying on its own | Valid | Both labeled as model output; the 98% compared with other projection files (C8) |
| 3 | Strongest material buried | Partly | "Numbers in circulation" box; corrections table on page 1 |
| 4 | Distributional results are national patterns | Valid | Tested (C11); said plainly |
| 5 | Rejects 2019 baselines, relies on 2022-base projections | Partly | Projections used only as labeled context; the hiring test uses observed flows |
| 6 | Labor-force decline never decomposed | Valid | Decomposed on the ACS window (C9) |
| 7 | Low computing LQ may be industry mix | Valid | Shift-share run as the reviewer specified (C10) |
| 8 | 98% near-mechanical; +0.7% has no comparator | Valid | Both given comparators (C7, C8) |
| 9 | No research question | Valid | Stated in section 1 |
| 10 | No literature review | Valid | Section 2; every work cited was confirmed to exist |
| 11 | Exposure band moved from 0.50 to 0.40 with no robustness check | Partly | Shares reported at 0.30, 0.40 and 0.50 |
| 12 | Potential-versus-revealed result rests on one index | Valid | Microsoft's applicability score added as a second revealed-use measure; Eloundou et al. as a second potential measure |
| 13 | Reproducibility is the real contribution, and buried | Partly | "How this study is checked" on page 2 |
| 14 | Three news stories buried | Partly | "Numbers in circulation" gives each, with both ratios for the 3,203 figure |
| 15 | The Richardson line | Valid | Name removed from the findings; role described; the recording cited in the design memo; a request for comment drafted, **not sent**; the audio still needs a human check |
| 16 | Kroger "Partly" | Valid | One three-way rule applied to every employer (C4) |
| 17 | Kroger and Fifth Third told in two table rows | Partly | A case box in section 8 |

### What changed in method

- **Comparisons, not levels.** 19 Chamber peers (P1), 25 metros by population (P2) and 10 by
  industry structure (P3), fixed by rule before any value was computed.
- **Pre-registration.** Hypotheses H1–H16 and their decision rules were committed before the
  data they cover were examined. 21 deviations are listed in `PREREGISTRATION.md`.
- **New lenses.** Awareness and participation (events, communities, search interest);
  adoption with a register of AI agents; capability; output per worker; a full data-center
  section.
- **Not completed in 2.1:** WARN notices; employer presence at events; training on offer;
  event censuses for comparison metros; the participation index. Each is stated in the report.
- **Tests.** 24 new checks in `tests/test_study_2_1.py`. The 16 checks for 1.0 are unchanged
  and still pass.

---

# Part II — Audit of the preliminary draft (1.0, unchanged)

The study in this repository began as an independent verification of an earlier draft research
paper and presentation on AI and the Cincinnati labour market. This document records what that
audit found. Every check below was run against the datasets in `data/`, which are extracted from
primary government sources and reproduce from the scripts in `scripts/`.

The draft's own self-assessment was unusually honest and caught several of its problems before
this audit did. Where that is the case it is said so. The conclusions below are not a judgement
of effort; they are a record of which figures can be carried forward and which cannot.

---

## Summary

| | Finding |
|---|---|
| **Verified correct** | Every BLS occupational employment figure in the draft. All eight checked matched the source exactly. |
| **Superseded** | The headline metro employment figure, which came from an older data vintage. |
| **Materially wrong** | The Ohio projections, which are statewide figures used in a regional study. Overstated by a factor of six. |
| **Not what it is called** | The 31.2% "AI exposure" indicator, which measures occupational composition, not exposure. |
| **Correctly labelled** | The national and state-level AI adoption statistics, which the draft did not present as local. |

---

## 1. The occupational figures are correct

Checked against BLS Occupational Employment and Wage Statistics, May 2025, Cincinnati OH–KY–IN
MSA, extracted by series identifier in `scripts/parse_oes.py`.

| Figure in the draft | Claimed | Actual | Verdict |
|---|---|---|---|
| Office and administrative support | 125,530 | 125,530 | Exact |
| — as a share of area employment | 11.4% | 11.40% | Exact |
| Customer service representatives | 19,410 | 19,410 | Exact |
| General office clerks | 16,750 | 16,750 | Exact |
| Management share | 7.6% | 7.59% | Exact |
| Business and financial operations share | 6.6% | 6.64% | Exact |
| Computer and mathematical share | 2.9% | 2.94% | Exact |
| Architecture and engineering share | 2.1% | 2.12% | Exact |
| Legal share | 0.6% | 0.57% | Exact |

Area total employment is 1,101,030. The draft's extraction from BLS is sound, and these figures
carry forward into this study unchanged.

---

## 2. The metro employment figure was a superseded vintage

The draft reported **1,179,300** jobs for August 2026. The CES extract in this repository, taken
from the BLS flat files, gives:

| Series | Aug 2026 | Sep 2026 |
|---|---|---|
| Not seasonally adjusted | 1,181,600 | 1,178,200 (preliminary) |
| Seasonally adjusted | 1,175,100 | 1,175,100 |

1,179,300 matches neither series. It is an earlier vintage of the August estimate, superseded by
revision before the draft was circulated. The draft identified this discrepancy itself and
declined to defend the number, which was the right call.

This study uses September 2026 as its end point and labels it preliminary.

---

## 3. The Ohio projections are statewide, and a regional file existed

This is the most serious finding.

The draft reported **636,978 annual job openings** and **69,054 annual office and administrative
support openings**. Both are **Ohio statewide** figures presented in a study of Greater Cincinnati.

The draft disclosed this, but explained it as a data limitation — that a Cincinnati-specific count
"was not available for this analysis." That explanation does not hold. ODJFS publishes long-term
occupational projections for the Cincinnati area in the same series, as
`LTOP_Cincinnati2032.xlsx`. It is the file this study uses.

| | Draft (Ohio statewide) | Correct (Cincinnati) | Overstatement |
|---|---|---|---|
| Total annual openings | 636,978 | **101,316** | 6.3× |
| Office and admin annual openings | 69,054 | **11,053** | 6.2× |
| Office and admin change to 2032 | −7.2% | **−6.4%** | — |

The error is not one of disclosure but of sourcing: the regional data existed and was not used. A
reader who took 636,978 as a Cincinnati figure would overstate the region's annual hiring
opportunity by more than half a million positions.

**The regional file carries its own trap.** It is titled "Cincinnati Metropolitan Statistical
Area" but covers only the Ohio portion — base employment 907,032 against the metro's 1,101,030.
Every Northern Kentucky and Indiana job is excluded. This study labels all projections
Ohio-portion throughout, and documents the mislabel.

**A point the draft made and this study agrees with:** projected annual openings are not current
vacancies. They include exits from the labour force and transfers between occupations. In the
Cincinnati Ohio portion, growth accounts for 2,074 of the 101,316 — 2.0%.

---

## 4. The 31.2% indicator is not an exposure measure

The draft constructed a figure of 31.2% by summing the Cincinnati employment shares of six
occupational groups: office and administrative support, management, business and financial
operations, computer and mathematical, architecture and engineering, and legal.

**The arithmetic is right.** Those six shares sum to 31.25%, covering 344,100 jobs. The draft also
stated plainly that this was its own constructed indicator rather than a published statistic, and
that it should not be read as a measured exposure rate. That disclosure was correct and necessary.

**The direction is defensible.** Measured against observed AI task exposure, those six groups do
carry higher exposure than the rest of the economy — 0.254 against 0.070, employment-weighted.
Selecting them was not arbitrary.

**But as a ranking it fails.** Measured exposure by major group, Cincinnati MSA:

| Group | Observed exposure | In the 31.2%? |
|---|---|---|
| Computer and mathematical | 0.348 | yes |
| Office and administrative support | 0.328 | yes |
| Business and financial operations | 0.299 | yes |
| **Sales and related** | **0.296** | **no** |
| Legal | 0.203 | yes |
| Educational instruction and library | 0.181 | no |
| Arts, design, entertainment, sports, media | 0.180 | no |
| Management | 0.130 | yes |
| Healthcare practitioners and technical | 0.054 | no |
| **Architecture and engineering** | **0.044** | **yes** |

Architecture and engineering is included at 0.044 — *below* healthcare practitioners, which is
excluded, and barely above construction. Management is included at 0.130, below two excluded
groups. Sales, at 0.296, outranks three of the six groups the indicator does include, and is left
out entirely.

The consequences, counted in jobs:

- **56,730 jobs** inside the six groups score at or below 0.05 — near-zero measured overlap. That
  is 17.3% of the population the indicator calls exposed.
- **20,810 jobs** outside the six groups score above 0.40 — genuinely high exposure, not counted.
- Only **24.4%** of the jobs the indicator labels exposed actually score above 0.40.

**The underlying problem is conceptual.** Selecting whole major groups produces a measure of
occupational composition, not of exposure. It also silently mixes two different things. Architecture
and engineering scores **+0.942 on AIOE**, which measures what AI could in principle do, but
**0.044 on observed exposure**, which measures what AI is actually used for. High potential,
almost no observed use. An indicator built from group membership cannot tell those apart, and the
distinction is the centre of the question being asked.

**What measurement gives instead.** Joining published exposure scores to occupational employment
at six-digit SOC, this study finds Cincinnati's employment-weighted generative-AI exposure is
**0.088 against a national 0.093** — a gap of 0.005 standard deviations. 41.4% of metro employment
sits in occupations with no measured task overlap at all; 10.0% sits above 0.40. The region is
ordinary. No single percentage of "exposed jobs" is reported, because exposure is continuous and
collapsing it to a count is what produced the 31.2% in the first place.

---

## 5. The national and state statistics were handled correctly

The draft cited Brookings national estimates, US Census Bureau business adoption rates (19.8%
of US businesses; 33.9% in finance and insurance) and OhioX survey findings (79% / 57% / 21%).
In its self-assessment it stated that none of these are Cincinnati figures, that the Census data
are national, and that the OhioX survey drew on roughly 270 self-selected leaders statewide rather
than a representative census.

That is the correct treatment and no correction is needed. This study does not use these figures,
preferring employer disclosures that can be tied to named Cincinnati organisations.

The Brookings citations in the draft, including a reported 24.1% figure for Cincinnati STARs in
highly AI-exposed gateway occupations, were not verified in this audit. If that figure is
accurate it is the closest published external benchmark to this study's subject and is worth
checking against the source directly.

---

## 6. What the draft identified as missing, and what now exists

The draft listed five open research questions. Four are now answered in this repository.

| Open question in the draft | Status |
|---|---|
| How many jobs are currently advertised in the metro | **Still open, and not answerable.** The posting source caps its count at 10,000. This study reports no share-of-postings statistic for that reason. |
| Which occupations gained or lost advertised openings | Partly: posting counts by employer and term, October 2026 snapshot. No 12–24 month local series exists. |
| How often local ads request AI skills | Answered: AI-skill postings grew 159% in the year to September 2026, from a small base — roughly 1,008 postings, against 906 mentioning nursing. |
| Which employers are implementing AI, by consistent method | Answered: employer evidence drawn from filings and company releases, with internal memo reporting labelled secondary. |
| Whether employment change can be attributed to AI | Answered in the negative, and deliberately. No regional dataset isolates AI-caused separations. This study attributes nothing it cannot source. |

---

## 7. Method convergence

The draft's closing recommendation was to adopt the Brookings Metro approach: measure occupational
exposure, join it to local employment, and compare metros rather than extrapolate national
findings. That is the method this study uses. Exposure scores are joined to BLS occupational
employment at six-digit SOC, bands are set on the national unweighted distribution so a band means
the same thing in every geography compared, and results are cross-checked against New York Fed
national benchmarks.

Where the two approaches differ is in what gets reported. This study does not produce a single
headline percentage of exposed jobs, because the distribution does not support one.

---

## What carries forward

| From the draft | Disposition |
|---|---|
| BLS occupational employment figures | Carried forward unchanged |
| The projected-openings-are-not-vacancies caveat | Carried forward and made prominent |
| The separation of exposure, hiring demand and displacement | Carried forward; it is the study's organising distinction |
| Metro employment total | Replaced with the current vintage |
| Ohio statewide projections | Replaced with the Cincinnati Ohio-portion file |
| The 31.2% indicator | Not carried forward |
| National AI research used for framing | Retained as national context, never as local measurement |

Two corrections made during this study's own work are documented in `CALCULATIONS.md` rather than
quietly fixed: an occupational misclassification that double-counted national employment by about
58%, and four wrong values in an exposure-band table. Both were caught by reproducibility checks
written for that purpose. The same checks are what make the findings above verifiable rather than
asserted.
