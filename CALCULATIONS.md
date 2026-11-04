# How every number was produced

This document traces each published figure back to its source and shows the arithmetic. Run
`python -I scripts/trace_numbers.py .` to regenerate every number here from the data files;
`output/number_trace.txt` is the saved output of that run.

Three rules govern everything below.

1. **Published values are never recomputed.** Where an agency publishes a number (total
   employment, a median wage, a projected opening count), it is read from the source file and
   used as-is. The arithmetic in this study is confined to weighting, shares and ratios.
2. **Derived figures are labelled.** Exactly one headline number — the implied total of AI job
   postings — is arithmetic on top of someone else's published numbers, and it is called a
   calculation everywhere it appears.
3. **Coverage is always stated.** No percentage appears without its denominator.

---

## 1. Acquiring the sources

### 1.1 Occupational employment and wages (BLS OEWS)

The published HTML tables were not used. Instead the study reads the BLS time-series flat file,
because its series identifiers are deterministic and the extraction is therefore exactly
reproducible.

```
https://download.bls.gov/pub/time.series/oe/oe.data.0.Current     (331 MB)
https://download.bls.gov/pub/time.series/oe/oe.occupation          (SOC code -> title)
https://download.bls.gov/pub/time.series/oe/oe.area                (area codes)
https://download.bls.gov/pub/time.series/oe/oe.datatype            (datatype codes)
```

A series id is 25 characters, built as:

```
OE | U | areatype(1) | area(7) | industry(6) | occupation(6) | datatype(2)
```

So Cincinnati total employment across all industries and occupations is
`OEUM001714000000000000001`:

| Field | Value | Meaning |
|---|---|---|
| survey | `OE` | Occupational Employment and Wage Statistics |
| seasonal | `U` | not seasonally adjusted |
| areatype | `M` | metropolitan area |
| area | `0017140` | Cincinnati, OH-KY-IN |
| industry | `000000` | cross-industry |
| occupation | `000000` | all occupations |
| datatype | `01` | employment |

The 331 MB file was streamed and filtered in one pass to the four areas used, never stored whole:

```bash
curl -sL "https://download.bls.gov/pub/time.series/oe/oe.data.0.Current" \
 | grep -E '^OEU[NSM](0000000|3900000|2100000|0017140)' > raw/oes/oes_filtered.txt
```

Datatype codes used: `01` employment, `04` annual mean wage, `13` annual median wage,
`11`/`12`/`14`/`15` the 10th/25th/75th/90th percentiles, `16` employment per 1,000 jobs,
`17` location quotient.

Only cross-industry series (`industry = 000000`) are retained. BLS does not publish
industry-by-occupation detail for metropolitan areas.

### 1.2 Why there are no Kentucky-portion occupational figures

OEWS publishes one area record for this metro — `39 | 0017140 | M | Cincinnati, OH-KY-IN`. There
is no Kentucky-portion cut. That is why every occupational and wage figure in the study covers
the whole tri-state metro and cannot be split by state, and why the Ohio/Kentucky comparison is
built from county QCEW data instead.

### 1.3 County employment and wages (BLS QCEW)

One file per county from the QCEW open-data API:

```
https://data.bls.gov/cew/data/api/{year}/a/area/{fips}.csv
```

Counties: Hamilton `39061`, Butler `39017`, Clermont `39025`, Warren `39165` (Ohio); Boone
`21015`, Kenton `21117`, Campbell `21037` (Kentucky). Years 2024 and 2025, annual averages.

Aggregation levels retained: `70` county total across all ownerships, `71` county by ownership,
`74` private sector by NAICS. Industry titles come from
`https://data.bls.gov/cew/doc/titles/industry/industry_titles.csv`.

QCEW counts jobs covered by unemployment insurance and excludes most self-employment, which is
why its totals sit below OEWS and CES.

### 1.4 Industry employment and unemployment (BLS CES and LAUS)

```
https://download.bls.gov/pub/time.series/sm/sm.data.36.Ohio   -> filtered to area 17140
https://download.bls.gov/pub/time.series/la/la.data.42.Ohio   -> filtered to MT3917140
```

CES series layout is `SM | seasonal | state(2) | area(5) | industry(8) | datatype(2)`; datatype
`01` is all employees in thousands. This yields 52 industry series back to January 1990. Only
total nonfarm is seasonally adjusted at metro level, so **all industry comparisons use the same
calendar month across years** (September) rather than seasonally adjusted figures.

LAUS measure codes: `03` unemployment rate, `04` unemployment, `05` employment, `06` labour force.

### 1.5 Exposure measures

| Measure | Source | What it is |
|---|---|---|
| AIOE | `github.com/AIOE-Data/AIOE`, Appendix A | Felten, Raj & Seamans (2021). Occupational exposure to 10 AI applications via O*NET abilities. Standardised across occupations: mean 0, sd 1. |
| LM-AIOE | same repo, `Language Modeling AIOE and AIIE.xlsx` | Felten, Raj & Seamans (2023). The language-model-specific variant — the one relevant to generative AI. |
| IG-AIOE | same repo, `Image Generation AIOE and AIIE.xlsx` | Image-generation variant. |
| Observed exposure | `huggingface.co/datasets/Anthropic/EconomicIndex`, `labor_market_impacts/job_exposure.csv` | Share of an occupation's O*NET tasks that actually appear in real AI usage. 0 to 1. |

The first three are *potential* exposure, computed without reference to any firm. The fourth is
*revealed* exposure, measured from observed usage. Keeping them separate is the point: an
occupation can score high on the first and zero on the fourth.

### 1.6 State AI usage

`release_2026_06_26/data/aei_claude_ai_2026-06-26.csv` (219 MB), filtered to `geo_id` in
`{US-OH, US-KY, USA}`. Geography levels are global, country and subregion; **subregion means US
state, not metro**. There is no Cincinnati cut, which is why these figures are never presented
as Cincinnati's.

### 1.7 Job postings

Two independent sources, deliberately not combined:

- **Bipartisan Policy Center Skills Data Dashboard** (Lightcast data, updated 9 October 2026) for
  metro growth rates. The dashboard itself returned HTTP 403, so the metro table came via a
  third-party reproduction and is labelled secondary throughout.
- **CareerOneStop Job Finder** (US DOL / National Labor Exchange), queried directly on
  30 October 2026 with quoted phrases, Cincinnati OH, 25-mile radius.

---

## 2. Classifying occupations, and the bug this caught

SOC codes encode their own aggregation level:

| Pattern | Level | Example |
|---|---|---|
| `XX-0000` | major group | 43-0000 Office and Administrative Support |
| `XX-X000` | minor group | 43-1000 Supervisors of Office Workers |
| `XX-XXX0` | broad occupation | 15-1250 Software and Web Developers |
| `XX-XXXX` (last digit non-zero) | **detailed occupation** | 15-1252 Software Developers |

**The first version of this analysis got this wrong.** It tested `endswith("00")` for broad
occupations, which misses codes ending in a single zero such as `15-1250`. Those were classified
as detailed and counted alongside the detailed occupations nested inside them. National detailed
employment summed to 234,970,310 against a published total of 155,495,730 — an overcount of about
58%, caused entirely by double counting.

The corrected rule tests, in order: `0000` major, `000` minor, `0` broad, else detailed. The
check that it is now right is that detailed occupations sum to slightly *under* the published
total, the gap being occupations suppressed for disclosure:

| Area | Detailed occupations | Sum of detailed | Published total | Coverage |
|---|---|---|---|---|
| Cincinnati MSA | 638 | 1,056,940 | 1,101,030 | 96.0% |
| Ohio | 758 | 5,294,860 | 5,550,180 | 95.4% |
| Kentucky | 681 | 1,898,000 | 2,000,360 | 94.9% |
| National | 823 | 148,807,680 | 155,495,730 | 95.7% |

**Every employment-weighted statistic in the study uses detailed occupations only.** Including
aggregates would count the same jobs two or three times.

---

## 3. Joining exposure to employment

Exposure measures are joined to OEWS on the six-digit SOC code. AIOE is keyed to the 2010 SOC
revision while OEWS May 2025 uses the 2018 revision, so some occupations have no match.

**Match rate is reported as a share of employment, not a share of occupations**, because
unmatched occupations are systematically smaller and an occupation-count match rate would
flatter the coverage:

```
match rate = SUM(employment where score exists) / SUM(employment over all detailed occupations)
```

| Area | AIOE | Observed exposure |
|---|---|---|
| Cincinnati MSA | 82.9% (876,090 / 1,056,940) | 95.4% (1,008,490 / 1,056,940) |
| Ohio | 82.7% | 95.4% |
| Kentucky | 85.0% | 95.5% |
| National | 82.7% | 94.4% |

So roughly one Cincinnati job in six is absent from the AIOE results. Those results describe 83%
of metro employment, not all of it, and the paper says so wherever they appear.

---

## 4. The headline exposure figure

```
employment-weighted exposure = SUM(emp_i x score_i) / SUM(emp_i)
```

summed over detailed occupations **where the score exists**. Occupations with no score are
excluded from both numerator and denominator. Treating a missing score as zero would be wrong:
zero is a meaningful value on these scales (the average occupation for AIOE, no measured task
overlap for observed exposure), so substituting it would bias every regional average toward the
middle.

| Area | AIOE | LM-AIOE | IG-AIOE | Observed |
|---|---|---|---|---|
| Cincinnati MSA | 0.0320 | 0.0884 | −0.1570 | 0.1267 |
| Ohio | 0.0104 | 0.0656 | −0.1699 | 0.1230 |
| Kentucky | −0.0633 | −0.0033 | −0.2527 | 0.1182 |
| National | 0.0325 | 0.0931 | −0.1606 | 0.1305 |

The headline gap is one subtraction:

```
0.0884 − 0.0931 = −0.0047       Cincinnati LM-AIOE minus national
```

AIOE is standardised across occupations, so these units are standard deviations and zero is the
average occupation. A gap of 0.005 standard deviations is the basis for the claim that
Cincinnati's exposure is ordinary.

---

## 5. Thresholds: why they are set nationally and unweighted

Every band in the study is cut on the **national, unweighted distribution of occupations**. Two
choices are doing work here.

*National* means a band labelled "top quartile" means the same thing in Cincinnati, Ohio,
Kentucky and the nation, so the geographies are comparable. Cutting each geography at its own
quartiles would guarantee 25% of employment in each band everywhere and measure nothing.

*Unweighted* means each occupation counts once when the cut points are found, so the thresholds
describe the technology, not the labour market. Weighting the thresholds by employment would
make them move with the thing being measured.

Cut points, from 673 occupations with an LM-AIOE score:

```
Q1/Q2 boundary   −0.9230
median           −0.1205
Q3/Q4 boundary   +0.9571
```

For observed exposure the median is **0.0000**, because 410 of 755 nationally scored occupations
— 54.3% — have no measured AI task overlap at all. Quartiles are therefore meaningless on that
axis and fixed bands are used instead. This is also why the quadrant analysis says "some use"
rather than "high use": the split is between occupations AI has touched and occupations it has
not.

---

## 6. The distribution tables

### 6.1 Employment by observed-exposure band

```
band employment = SUM(emp_i) for occupations whose score falls in the band
band share      = band employment / 1,008,490        (the covered total, not 1,101,030)
band wage       = SUM(emp_i x median_wage_i) / SUM(emp_i)   within the band
```

| Band | Occupations | Employment | Share | Employment-weighted median wage |
|---|---|---|---|---|
| None measured (0.00) | 297 | 417,870 | 41.4% | $50,964 |
| 0.00 to 0.10 | 131 | 230,970 | 22.9% | $73,333 |
| 0.10 to 0.25 | 87 | 127,660 | 12.7% | $83,964 |
| 0.25 to 0.40 | 47 | 131,160 | 13.0% | $69,113 |
| Above 0.40 | 30 | 100,830 | 10.0% | $59,383 |
| **Total covered** | **592** | **1,008,490** | **100%** | |

> **Correction, 4 November 2026.** The first published version of this table gave 57 and 20
> occupations in the last two bands, with wages of $66,159 and $62,210. Those four values were
> wrong — they were carried over from an earlier run that used a 0.50 cut point rather than 0.40.
> Employment and share figures were correct throughout. The research paper and the executive
> briefing have both been corrected. The error was caught by `scripts/trace_numbers.py`, which
> recomputes every published figure from the data; the workbook was never affected because its
> summary sheets compute these counts with live `COUNTIFS` formulas rather than stored values.

The "employment-weighted median wage" needs a word of caution: it is the average of occupational
*medians*, weighted by employment. It is not the median wage of workers in the band, which would
need the underlying wage distribution and is not published.

### 6.2 The four quadrants

Axes split at the national medians: LM-AIOE at −0.1205, observed exposure at 0.000.

| Quadrant | Occupations | Employment | Share of 872,030 | Median wage |
|---|---|---|---|---|
| High exposure, some use | 208 | 460,970 | 52.9% | $72,095 |
| High exposure, no measured use | 78 | 47,150 | 5.4% | $66,261 |
| Low exposure, some use | 44 | 79,080 | 9.1% | $51,467 |
| Low exposure, no measured use | 190 | 284,830 | 32.7% | $50,721 |

The denominator is 872,030, not 1,056,940: an occupation enters only if **both** measures exist.

### 6.3 Wage quintiles

Occupations are sorted by median annual wage and cut at equal **cumulative employment**, not
equal occupation counts. The assignment rule places an occupation by its midpoint in the
cumulative distribution, so a single large occupation cannot straddle a boundary:

```
running total += employment_i
quintile_i = floor( 5 x (running_total − employment_i / 2) / total_employment )
```

| Quintile | Wage range | Employment | LM-AIOE | Observed |
|---|---|---|---|---|
| Q1 | $27,400–$36,530 | 211,570 | −0.311 | 0.071 |
| Q2 | $36,650–$46,410 | 207,880 | −0.364 | 0.083 |
| Q3 | $46,470–$61,540 | 214,210 | −0.163 | 0.152 |
| Q4 | $61,570–$82,330 | 212,180 | +0.521 | 0.194 |
| Q5 | $82,820–$551,320 | 209,840 | +0.703 | 0.134 |

Quintiles hold 207,880 to 214,210 jobs — close to equal, with the small spread an unavoidable
consequence of occupations being indivisible.

---

## 7. Projections and the 98% figure

Read directly from `LTOP_Cincinnati2032.xlsx`, row `00-0000`:

```
2022 employment     907,032
2032 employment     927,769
change              927,769 − 907,032 = +20,737  =  +2.29%

annual openings     2,074 growth + 43,731 exits + 55,511 transfers = 101,316
growth share        2,074 / 101,316      =  2.0%
replacement share   99,242 / 101,316     = 98.0%
```

Three warnings travel with these numbers.

**They are projected average annual openings, not current vacancies.** Nothing in this study
reports a Cincinnati vacancy count, because JOLTS produces no metropolitan estimates.

**They cover Ohio counties only.** Ohio LMI states on its own projections page that, for
employment projections, the Cincinnati MSA and the Southwest Ohio JobsOhio region are identical.
The file is titled "Cincinnati Metropolitan Statistical Area" but excludes every Northern
Kentucky and Indiana job. The 907,032 base against the OEWS metro total of 1,101,030 is the
visible symptom.

**They do not model AI.** The projections were produced in June 2025 from a 2022 base with no AI
assumptions. Where the paper observes that projected declines correlate with exposure, that is
offered as context — these occupations were already contracting — not as a causal finding.

### 7.1 Openings by exposure tercile

The 483 detailed occupations present in both the projections and the exposure join are sorted by
LM-AIOE and split into three equal-count groups:

| Tercile | Annual openings | Share of 77,397 | Net change 2022–32 | Growth-driven share |
|---|---|---|---|---|
| Top third (most exposed) | 24,856 | 32.1% | +2.09% | 2.3% |
| Middle third | 27,870 | 36.0% | +0.61% | 0.5% |
| Bottom third | 24,671 | 31.9% | +2.52% | 2.2% |

---

## 8. County arithmetic

Average pay is not published per county group; it is computed:

```
average annual pay = SUM(total_annual_wages) / SUM(employment)
```

| Year | Group | Employment | Total wages | Average pay |
|---|---|---|---|---|
| 2024 | Ohio four-county | 841,640 | $60,749,171,120 | $72,180 |
| 2024 | Northern Kentucky three-county | 209,322 | $13,288,402,536 | $63,483 |
| 2025 | Ohio four-county | 843,262 | $62,503,571,751 | $74,121 |
| 2025 | Northern Kentucky three-county | 212,943 | $13,748,420,859 | $64,564 |
| 2025 | Seven-county total | 1,056,205 | $76,251,992,610 | $72,194 |

Growth rates:

```
Ohio four-county     (843,262 − 841,640) / 841,640 = +0.19%
Northern Kentucky    (212,943 − 209,322) / 209,322 = +1.73%
```

The "nine times faster" claim is 1.73 / 0.19 = 9.1.

---

## 9. Industry and labour-force figures

**Baseline.** The study's analytical window begins in 2024. A 2019 baseline runs through the
pandemic collapse and the recovery that followed, so a "change since 2019" is mostly a measure of
that round trip. Generative AI reached broad enterprise deployment in 2023–24, so September 2024
is the last clean pre-period. Both baselines are reported side by side wherever the choice changes
the reading, because for two series it changes the sign.

CES levels are published in thousands and multiplied by 1,000 for presentation. All comparisons are
September to September. BLS publishes a seasonally adjusted metro series only for total nonfarm, so
an adjusted industry panel does not exist; comparing like months cancels seasonality without needing
adjustment. `scripts/rebase_2024.py` recomputes the whole panel and writes
`data/cincinnati_rebased_2024.csv`.

```
change vs 2024 = (Sept 2026 − Sept 2024) / Sept 2024
change vs 2019 = (Sept 2026 − Sept 2019) / Sept 2019
```

| Series | Sept 2024 | Sept 2026 | vs 2024 | vs 2019 |
|---|---|---|---|---|
| Total nonfarm | 1,169,600 | 1,178,200 | **+0.7%** | +4.7% |
| Federal government | 15,700 | 13,500 | −14.0% | −5.6% |
| Transportation and warehousing | 62,300 | 59,300 | −4.8% | **+17.0%** |
| Information | 13,700 | 13,100 | −4.4% | −3.0% |
| Credit intermediation¹ | 24,500 | 23,500 | −4.1% | **−13.9%** |
| Finance and insurance | 63,300 | 62,000 | −2.1% | +3.5% |
| Professional, scientific and technical | 67,100 | 68,100 | +1.5% | +6.7% |
| Manufacturing | 121,200 | 123,300 | +1.7% | +2.2% |
| Health care and social assistance | 164,400 | 171,600 | +4.4% | +12.2% |
| Specialty trade contractors | 37,200 | 39,100 | +5.1% | +17.8% |

Seven of the seventeen sectors in the published panel reverse direction between the two baselines:
transportation and warehousing, trade and transportation, insurance carriers, financial activities,
government, other services and employment services. Transportation swings furthest, reading as the
metro's fastest-growing sector against 2019 and a shrinking one against 2024, because the pandemic
logistics surge peaked and unwound inside the 2019 window.

Credit intermediation does **not** change sign — it falls on both baselines — but its magnitude
collapses from 13.9% to 4.1%. That case matters for this study specifically: the −13.9% figure has
been cited as evidence of AI displacement in banking, and re-baselining shows that roughly
seven-tenths of it predates the technology.

```
total nonfarm   (1,178,200 − 1,169,600) / 1,169,600 = +0.735%  → +0.7%, or 8,600 jobs
banking 2024    (23,500 − 24,500) / 24,500          = −4.08%   → −4.1%
banking 2019    (23,500 − 27,300) / 27,300          = −13.92%  → −13.9%
share predating 2024 = (27,300 − 24,500) / (27,300 − 23,500) = 73.7%
```

¹ Full CES series name: "Credit Intermediation and Related Activities including Monetary
Authorities - Central Bank". Shortened to "banking" in presentation only.

**What is not re-based.** Three inputs have one vintage each and cannot be put on a 2024 footing:
OEWS occupational employment and wages (May 2025), the ODJFS projections (base year 2022, horizon
2032) and the Anthropic Economic Index (April and May 2026). Each is labelled single-vintage where
it appears. No 2024 figure was constructed for them by interpolation or any other means.

The staffing figure is measured from its own peak rather than from 2019, and the paper says so:

```
(29,800 − 39,700) / 39,700 = −24.9%      September 2022 peak to September 2026
```

LAUS values are published levels; the rate is published too and reconciles to
`unemployment / labour force` within rounding (3.56% rounds to the published 3.6%).

```
                     Sept 2024    Sept 2026     change
unemployment rate         4.1%         3.6%    −0.5 pp
labour force         1,187,924    1,178,550     −9,374
employment           1,138,786    1,136,625     −2,161
unemployed              49,138       41,925     −7,213
```

Both employment and the labour force fell while the rate fell. That is the basis for the claim
that the rate improved for the wrong reason: the denominator shrank faster than the numerator.

**A gap in the extract.** October 2025 is absent from the LAUS series as downloaded, so 2025 has
eleven monthly observations and no annual average is computed for it. Every comparison in this
study is September to September and is unaffected.

---

## 10. The one derived posting figure

The Bipartisan Policy Center publishes a growth rate and a count of postings added, but no metro
total. The paper reports an implied total and labels it a calculation:

```
implied prior-year base = 619 / 1.59 = 389
implied current total   = 389 + 619  = 1,008
```

This assumes the published rate and the published count describe the same universe and period.
It is the only figure in the study built on that kind of assumption, and it is never presented as
a published number.

The direct posting counts are a separate source and are not combined with it:

| Query (quoted phrase) | Postings |
|---|---|
| "artificial intelligence" | 177 |
| "data analytics" | 170 |
| "machine learning" | 95 |
| "data scientist" | 79 |
| "generative AI" | 64 |
| "large language model" | 17 |
| "robotic process automation" | 6 |
| "prompt engineering" | 4 |
| nurse (non-AI benchmark) | 906 |

**No share-of-postings statistic is computed from this source.** The platform caps its display at
10,000, confirmed by comparing a 25-mile radius (returning exactly 10,000) against a 5-mile
radius (returning 8,782). Without a trustworthy denominator, a share would be invented. The
counts also contain visible false positives — nine wireless retail sales advertisements appeared
under "artificial intelligence" — so they are reported as indicative.

---

## 11. State AI usage, and what the 1.00 means

These values are read directly; no arithmetic is applied.

| Measure, May 2026 | Ohio | Kentucky |
|---|---|---|
| AI Usage Index | 0.59 | 0.39 |
| Work-related share of use | 40.0% | 40.0% |
| Automation (delegating) | 50.8% | 53.0% |
| Augmentation (collaborating) | 49.2% | 47.0% |

The index is a share of usage divided by a share of working-age population. **State indices are
computed within the United States**, so the US average is 1.00 by construction — that is a
definitional anchor, not a published figure. Anthropic separately publishes an index of 3.87 for
the United States itself, which measures the country against the world and is not comparable
with the state values. The paper now states this explicitly.

---

## 12. What this study does not compute

Deliberate omissions, each because the data would not support the figure:

- **A Cincinnati job-vacancy count.** JOLTS has no metropolitan estimates.
- **An AI-skill share of Cincinnati postings.** No trustworthy denominator exists.
- **A Northern Kentucky occupational exposure score.** OEWS publishes no such geography.
- **A Cincinnati AI usage index.** The Economic Index stops at state level.
- **Any attribution of employment change to AI.** Exposure measures task overlap. Whether overlap
  becomes job loss is the open question, and no dataset used here can close it.

The national benchmarks quoted for comparison (8% of postings economy-wide, 11% in manufacturing,
2.6% from the Stanford AI Index) use three different definitions of an AI skill. They are
reported separately and never combined into a single series.

---

## 13. Reproducing the analysis

```bash
python -I scripts/parse_oes.py        raw/oes  data/oes_may2025_cincinnati_panel.csv
python -I scripts/build_exposure.py   .
python -I scripts/parse_projections.py .
python -I scripts/parse_ces_laus.py   .
python -I scripts/build_qcew_aei.py   .
python -I scripts/analyze_exposure.py .
python -I scripts/build_workbook.py   .
python -I scripts/verify_workbook.py  .
python -I scripts/trace_numbers.py    .
```

The last two are the checks. `verify_workbook.py` recomputes the workbook's 51 summary figures in
Python and writes them to a Verification sheet beside the live Excel formulas, so the two can be
compared cell by cell. `trace_numbers.py` regenerates every figure in this document.

A note on that verification: the workbook's summary sheets contain live Excel formulas, which
openpyxl writes without cached values. The usual check is to recalculate with LibreOffice, which
was not installed on the machine this was built on, so the Python recomputation stands in for it.
Excel computes the formulas on first open.
