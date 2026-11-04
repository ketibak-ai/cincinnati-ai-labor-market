# Audit of the preliminary draft

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
