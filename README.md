# AI and the Greater Cincinnati Labor Market

An independent study of how AI adoption is affecting employment, occupational demand and
workforce requirements in the Cincinnati OH–KY–IN metropolitan area. Every figure traces to a
public source, and the analysis reproduces from the scripts in this repository.

**Analytical window: 2024 onward.** Historical comparisons are baselined to September 2024, not
2019. A 2019 baseline runs through the pandemic collapse and recovery, so any "change since 2019"
conflates that shock with the generative-AI period. Three inputs have no 2024 edition and are not
re-based: occupational employment and wages (OEWS, single vintage May 2025), the ODJFS projections
(fixed base year 2022, horizon 2032), and observed AI usage (Anthropic Economic Index, April–May
2026). They are labelled single-vintage wherever they appear.

**Reference periods:** industry employment and unemployment September 2024 – September 2026
(preliminary); county employment and wages 2024–2025 annual averages; occupational employment and
wages May 2025; projections 2022–2032; job postings collected 30 October 2026.

---

## Headline findings

**Cincinnati's AI exposure is average, not elevated.** Weighting every occupation by its May 2025
employment, the metro's generative-AI exposure score is 0.088 against a national 0.093 — a gap of
0.005 standard deviations. Claims that the region is unusually threatened, or unusually safe, are
not supported by its occupational mix.

**The real vulnerability is the thinness of job creation.** Cincinnati added 8,600 jobs between
September 2024 and September 2026 — growth of 0.7% across two years on a base of 1.18 million —
while the labour force shrank by about 9,400. Looking forward, of 101,316 projected average annual
openings just 2,074 — 2.0% — come from growth; the other 98.0% exist only because workers leave.
Observed and projected data agree: a technology that slows hiring is far more damaging in an
economy with no growth cushion.

**The region is under-represented in the occupations where AI work concentrates.** Computer and
mathematical occupations carry a location quotient of 0.87. The largest advertisers of AI roles in
the metro are Deloitte, Kelly Services, PwC, Eliassen Group and Accenture; among major regional
employers only GE Aerospace appears near the top. Cincinnati is buying AI capability rather than
building it.

**Exposure rises with pay, inverting the older automation story.** Generative-AI exposure is
negative across the bottom three wage quintiles and reaches +0.703 standard deviations in the top.
The most exposed Cincinnati occupations are accountants, HR specialists, market research analysts
and financial managers — not production workers.

**Deployment is broad; attributed displacement is narrow.** Kroger announced roughly 3,000
corporate role eliminations in October 2026, but the CEO memo cites organisational layers and
never states how many roles AI replaces. Procter & Gamble's larger reduction of up to 7,000
non-manufacturing roles is attributed to cost, tariffs and consumer uncertainty. Fifth Third
generates about 30% of new code with AI and has announced no reductions at all — its CEO argues
that AI is *not* what is driving current productivity gains.

---

## What this study deliberately does not claim

- That AI has caused measurable job losses in Greater Cincinnati
- That P&G's 7,000-role reduction is an AI story
- That the fall in metro banking employment reflects AI (−13.9% from 2019 but only −4.1% from 2024,
  so most of it predates generative AI)
- That any sector decline since 2024 is an AI effect — federal employment, logistics and banking
  each have visible non-AI causes, and professional services and management of companies have grown
- That entry-level hiring has collapsed because of AI
- Any current Cincinnati job-vacancy count — JOLTS has no metropolitan estimates
- Any Northern-Kentucky-specific occupational exposure figure

---

## A geography warning

Four different geographies are called "Cincinnati" in official data, and they differ by about
194,000 jobs.

| Geography | Coverage | Employment |
|---|---|---|
| Cincinnati OH–KY–IN MSA | Full metro, three states | 1,101,030 |
| MSA covered employment | Same area, UI-insured jobs | 1,096,580 |
| Core seven counties | 4 Ohio + 3 Northern Kentucky | 1,056,205 |
| **ODJFS "Cincinnati MSA"** | **Ohio counties only** | **907,032** |

Ohio publishes occupational projections titled "Cincinnati Metropolitan Statistical Area" that in
fact cover only the Southwest Ohio JobsOhio region. They exclude every Northern Kentucky and
Indiana job. Projections in this study are labelled Ohio-portion throughout.

---

## Repository layout

```
CALCULATIONS.md    How every published number was produced, with formulas
scripts/           The pipeline, in run order
data/              Derived analysis-ready datasets (CSV), incl. cincinnati_rebased_2024.csv
raw/               Source extracts as downloaded (large files gitignored)
output/            The reproducible workbook and the number trace
```

### Scripts, in run order

| Script | What it does |
|---|---|
| `parse_oes.py` | Parses the BLS OEWS flat-file extract into a tidy occupational panel |
| `build_exposure.py` | Joins AIOE and observed-exposure measures to OEWS on six-digit SOC |
| `parse_projections.py` | Parses ODJFS 2022–2032 projections and joins exposure |
| `parse_ces_laus.py` | Parses Cincinnati industry employment and unemployment history |
| `build_qcew_aei.py` | Builds county employment/wages and state AI-usage datasets |
| `analyze_exposure.py` | Distributional analysis: bands, quadrants, wage gradient |
| `build_workbook.py` | Assembles the 20-sheet Excel workbook with live formulas |
| `verify_workbook.py` | Recomputes 51 summary figures in Python into a Verification sheet |
| `rebase_2024.py` | Re-bases industry, unemployment and county series to 2024 and prints the trace |
| `trace_numbers.py` | Re-derives every published figure, printing each formula |

```bash
python -I scripts/parse_oes.py raw/oes data/oes_may2025_cincinnati_panel.csv
python -I scripts/build_exposure.py .
python -I scripts/parse_projections.py .
python -I scripts/parse_ces_laus.py .
python -I scripts/build_qcew_aei.py .
python -I scripts/analyze_exposure.py .
python -I scripts/build_workbook.py .
python -I scripts/rebase_2024.py .
python -I scripts/verify_workbook.py .
python -I scripts/trace_numbers.py .
```

Requires Python 3 with `openpyxl`. The three large source extracts are gitignored; section 1 of
`CALCULATIONS.md` gives the exact commands that produce them.

---

## Method in brief

Occupational employment is extracted from BLS flat files by deterministic series identifier,
classified to SOC aggregation level, and restricted to **detailed occupations**, which cover
96.0% of published Cincinnati employment. Published exposure measures are joined on six-digit
SOC, covering 82.9% of that employment for AIOE and 95.4% for observed exposure.

All exposure bands are set on the **national unweighted distribution of occupations**, so a band
means the same thing in every geography compared. Employment-weighted statistics exclude
occupations with no score from both numerator and denominator rather than treating them as zero.

Employer figures come from filings and company releases where available, with reporting of
internal memos labelled secondary. The single derived headline figure — an implied total of AI job
postings — is labelled a calculation wherever it appears.

Two corrections made during the work are documented rather than quietly fixed: an occupational
misclassification that double-counted national employment by about 58%, and four wrong values in
an exposure-band table. Both are described in `CALCULATIONS.md`.

---

## Sources

### Government data

| Source | Agency | Period |
|---|---|---|
| [Occupational Employment and Wage Statistics](https://download.bls.gov/pub/time.series/oe/) | BLS | May 2025 |
| [Quarterly Census of Employment and Wages](https://data.bls.gov/cew/data/api/2025/a/area/39061.csv) | BLS | 2024–2025 annual |
| [State and Metro Area Employment](https://download.bls.gov/pub/time.series/sm/) | BLS | Monthly, 1990 to Sept 2026 |
| [Local Area Unemployment Statistics](https://download.bls.gov/pub/time.series/la/) | BLS | Monthly, 1990 to Sept 2026 |
| [Long-term occupational projections](https://ohiolmi.com/_docs/PROJ/MSA/LTOP_Cincinnati2032.xlsx) | ODJFS | 2022–2032 |
| [CareerOneStop Job Finder](https://www.careeronestop.org/Toolkit/Jobs/find-jobs.aspx) | US DOL / National Labor Exchange | 30 Oct 2026 |

### Research and measurement

| Source | Authors |
|---|---|
| [AIOE dataset](https://github.com/AIOE-Data/AIOE) | Felten, Raj & Seamans, *Strategic Management Journal* 42(12):2195–2217 (2021), and the 2023 generative-AI variants |
| [Anthropic Economic Index](https://huggingface.co/datasets/Anthropic/EconomicIndex) | Anthropic, release 26 June 2026 (CC-BY) |
| [Do Job Postings Show Early Labor-Market Effects of AI?](https://libertystreeteconomics.newyorkfed.org/2026/05/do-job-postings-show-early-labor-market-effects-of-ai/) | Audoly, Guerin & Topa, Federal Reserve Bank of New York, 14 May 2026 |
| [AI on the Factory Floor](https://www.federalreserve.gov/econres/notes/feds-notes/ai-on-the-factory-floor-evidence-from-manufacturing-job-postings-20260930.html) | Tito, FEDS Notes, Federal Reserve Board, 30 Sept 2026 |
| [Skills Data Dashboard](https://bipartisanpolicy.org/skills-data-dashboard/) | Bipartisan Policy Center, using Lightcast |

### Required citation

If you use the AIOE data in `raw/aioe/`, cite:

> Felten E, Raj M, Seamans R (2021) Occupational, industry, and geographic exposure to artificial
> intelligence: A novel dataset and its potential uses. *Strategic Management Journal*
> 42(12):2195–2217.

Anthropic Economic Index data are released CC-BY. BLS and ODJFS data are US government works.
Fifth Third's annual report is not redistributed here; read it from
[SEC EDGAR](https://www.sec.gov/Archives/edgar/data/35527/000003552726000124/a2025annualreport.pdf).

---

## Limitations

Exposure indices measure task overlap, not outcomes. AIOE covers 82.9% of Cincinnati
detailed-occupation employment, and the unmatched sixth is not random — it concentrates in
occupations whose SOC codes changed between the 2010 and 2018 revisions. Observed exposure
reflects usage of one AI system. State AI-usage figures are not metro figures. Projections predate
generative AI and do not model it. Posting counts are not vacancies, and the keyword census
contains visible false positives.

The most valuable missing input is metro job-posting microdata with experience requirements, which
would allow a direct test of whether entry-level hiring in exposed occupations has weakened
locally.
