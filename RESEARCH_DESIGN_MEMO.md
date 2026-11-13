# Cincinnati AI Labor Market 2.0 — research design memo

**For:** KetiB (author) · **Date:** 13 November 2026 · **Status:** check-in draft; nothing
pushed or published.

Repository state: tag `v1.0` created on commit d4a1d36; work is on the local branch `v2.0`.
The draft pre-registration is committed (`PREREGISTRATION.md`, commit 934e679, 16:22 ET) before
any 2.0 data value was downloaded. A plain-text copy of the 1.0 report is in
`archive/v1.0/report.txt` so 1.0 can be cited by line. The 1.0 test suite passes: 16 of 16
checks.

---

## 1. The short version

1. **1.0's arithmetic is sound; its inferences are under-tested.** Every number I re-ran
   reproduces. The weakness is design: 1.0 measured levels, compared Cincinnati only with the
   nation, had no research question, and ran no test that could have detected an AI effect. Its
   "no measurable AI job losses" is an absence of a test, not a null result.
2. **2.0 is built around one confirmatory test** of 1.0's central risk: did the entry door to
   AI-exposed work narrow for 22–24-year-olds after late 2022, relative to experienced workers,
   relative to less-exposed industries, and relative to peer metros? The data exist and are
   current (Census QWI, released 5 and 12 November 2026; the three-state metro series ends
   2025 Q4). The 2022–23 interest-rate shock is handled with four pre-specified checks.
3. **Five corrections to 1.0 surfaced in this design phase alone** (section 2.3): the Chamber's
   565 MW includes two *planned* hyperscale sites; the City budget *does* contain AI lines; Fifth
   Third *has* announced merger-related cuts since 1.0's sources; Kroger's memo, as reported,
   names "technology", not AI; and two repo documents miscount the test suite.
4. **Two data limits change the plan.** Census BTOS publishes metro AI-use estimates only for
   the 25 largest metros, and Cincinnati is not one of them. BEA stopped publishing metro-area
   GDP with its February 2026 release, so the output lens must be built from the 15 counties.
5. **The reviewer is mostly right.** Of 17 objections: 10 VALID, 7 PARTLY, 0 WRONG (section 3).
6. **Five decisions are yours** (section 9). My recommendations: a neutral title that states the
   question, not a result; use Indeed only as a labelled, timely secondary indicator; take the
   Richardson name out of the findings, cite the City's own recording, and offer a right of
   reply; keep the June 2026 AEI (nothing newer exists) and the 2022–2032 metro projections (no
   newer metro file exists); show both baselines in the workbook's industry sheet.

---

## 2. Assessment of 1.0

### 2.1 What holds

| 1.0 claim | Status | Why it holds, and what 2.0 must still do |
|---|---|---|
| Exposure is average (LM-AIOE 0.088 vs 0.093) | Holds as arithmetic | Reproduces (`tests/test_study.py:106-118`). But "average" was judged only against the nation (`archive/v1.0/report.txt:589`). 2.0 tests it against peers and three more exposure measures (pre-registration H4). |
| ODJFS "Cincinnati MSA" projections exclude KY and IN | Holds | 907,032 base vs 1,101,030 metro (`CALCULATIONS.md:343-347`). A genuine, checkable public-data finding. |
| 2019 baselines overstate change; banking's −13.9% mostly predates generative AI | Holds | 73.7% of the fall predates Sept 2024 (`CALCULATIONS.md:437-441`). |
| Kroger, P&G, Fifth Third attribution read from primary documents | Mostly holds | Method is right; two rows need updating (2.3). |
| Chamber's 3,203 is modelled, not a payroll | Holds | The Chamber's own caveats say so (`archive/v1.0/report.txt:1507`). But 1.0 applied a stricter standard to that model than to its own projections (objection 2). |
| Reproducibility | Holds, and is a real asset | 16 regression tests pass; two past errors are documented. |

### 2.2 What does not hold, or is not yet supported

- **"The real fragility is slow growth."** The +0.7% figure has no comparator anywhere in the
  repo: `data/cincinnati_ces_history.csv` holds only area 17140. The 98% replacement share is
  likely close to a property of the projection method: in the BLS separations method,
  replacement openings dominate by construction, and my recollection — not yet checked — is
  that the national growth share is in the low single digits too. H9 recomputes it from source. The
  labour-force fall was never split into ageing and participation. The claim may survive; it
  has not been tested.
- **"Exposure rises with pay."** True in Cincinnati, but 1.0 never computed the national
  gradient. With an occupational mix within 0.005 SD of the nation's, this is very likely a
  national pattern carrying a local label (H10).
- **"Buying, not building."** Rests on a location quotient (0.87) that can be produced by
  industry mix alone, and on which firms advertise AI roles. No shift-share; no capability
  measures (patents, R&D, graduates). It is a hypothesis, not a finding (H6).
- **"Data centers are not a jobs story."** Rests on the Chamber's 0.15 FTE/MW staffing
  assumption, which the Chamber adapted from an Oklahoma State study
  (`data/local_institutional_sources.csv:14`). 1.0 counted no facility's actual jobs and made no
  Columbus comparison per MW. Not wrong, untested (H8).
- **"No measurable AI-caused job losses; the risk is fewer entry-level hires."** The first half
  is an absence of evidence that 1.0 itself flags (`archive/v1.0/report.txt:1780`). The second
  half is explicitly a hypothesis (`archive/v1.0/report.txt:1309`). 2.0 tests it (H1–H3).

### 2.3 Corrections to 1.0 found during this design phase

Each will go into `AUDIT.md` and the corrections box at the top of the 2.0 report.

| # | 1.0 said | What the record shows | Source (type) |
|---|---|---|---|
| C1 | "The region's nineteen facilities hold roughly 565 MW of capacity" (`archive/v1.0/report.txt:1509`); recorded as "existing regional data centre capacity" (`data/local_institutional_sources.csv:20`) | The Chamber's figure is **17 existing + 2 planned** facilities, and "the two largest facilities are planned hyperscalers". 565 MW therefore adds announced to operating capacity, and the MW basis is not stated. The Chamber's sources are Datacentermap.com and Cushman & Wakefield. | Chamber, *Data Centers: A Cincinnati Regional Perspective*, 12 Oct 2026, pp. 2–3 (advocacy; underlying sources private) |
| C2 | "Neither the task force nor a training lab appears in the approved FY2026–2027 budget" (`archive/v1.0/report.txt:1462`; `data/local_institutional_sources.csv:31`) | The approved FY2026–2027 budget lists **"MidWest Con – AI Investment – $50,000"** (one-time special-event funding; MidWest Con is the task-force chair's conference). The approved FY2027 update funds **"Plans Examination Artificial Intelligence Enhancement", $300,000** (capital). In the 4 May 2026 meeting a council member says "the ask was more than $200,000, we were only able to get you $200,000" (CitiCable recording, ≈1:14:38), which suggests an earlier allocation I have not yet located. The "not in the budget" statement is at best incomplete. | City of Cincinnati, Approved FY2026–2027 Biennial Budget, Vol. I, pp. 31 and 140; Approved FY2027 Budget Update, Capital Exhibit 3; CitiCable video (government) |
| C3 | Fifth Third "has announced no reductions at all" (`docs/index.html:303`; README.md:49-50) | Fifth Third closed its acquisition of Comerica on 1 Feb 2026; Comerica filed a Texas WARN notice for 184 jobs in Frisco, and the CEO confirmed Michigan layoffs. These are merger-attributed, not AI-attributed, and none reported so far is in Cincinnati. The AI-and-no-cuts contrast needs restating. | Banking Dive; Comerica WARN notice to Texas (journalism; government record to be retrieved) |
| C4 | Kroger: AI attribution "Partly" (`archive/v1.0/report.txt:1008`; `data/ai_adoption_employers.csv:2`) | As reported, the memo says "Technology is reshaping what's possible … we must adapt and take advantage of technology." Fast Company reports that it "does not specify artificial intelligence as the technology". Under one coding rule this is **"technology named, AI not named"**, pending the full memo text. The "AI job cuts" framing is the media's. | Fortune, 14 Oct 2026, quoting Business Insider; Fast Company (journalism) |
| C5 | "Thirteen checks" (`README.md:147`; `VERIFICATION.md:64`) | The suite runs **16** checks. Also, `tests/test_study.py:116-117` labels the LM-AIOE result "observed exposure", which is a different measure. Labels only; no number changes. | Repository |

Also logged, not a correction: 1.0's posting comparison of 472 vs 9,025 data-center postings
(`archive/v1.0/report.txt:1509`) is Lightcast data relayed by the Chamber. 1.0 called it "a
measured figure". It is a private-vendor count and will be labelled so.

### 2.4 What is missing

A research question; a literature review; any peer comparison; any design that compares
exposed with less-exposed work, young with experienced workers, or before with after late
2022; a robustness check on the exposure bands; a second revealed-use measure; a shift-share;
a labour-force decomposition; capability measures; an output lens; a data-center section with
operating, under-construction and announced capacity kept apart; and an outlook kept separate
from findings.

---

## 3. The reviewer's objections

The reviewer did not see the code. Verdicts use evidence from the repo and the archived report.

| # | Objection | Verdict | Evidence and reasoning | What 2.0 does |
|---|---|---|---|---|
| 1 | Title promises an effect the paper doesn't find; a null result that never says so | **PARTLY** | The framing promises "how AI adoption is affecting employment" (`README.md:3-4`; `docs/index.html:7`), and none of the seven executive findings states the absence of an effect (`archive/v1.0/report.txt:11-25`). It appears only at line 1597 and in the "honest summary" (1617-1621). But "null result" overstates it: 1.0 ran no test that could have found an effect, so it has absence of evidence, which it says once (line 1780). | States the research question and the test up front; reports the result as a result, with what the design could and could not detect. |
| 2 | Dismisses the Chamber's 3,203 as model output while relying on its own model output (101,316 openings; 98%) | **VALID** | 1.0 calls 2.0% "the most consequential number in this study" (`report.txt:1085`) and builds the "real vulnerability" on it (`report.txt:15`; `README.md:27-32`), while saying of the Chamber that "a modelled total is not a payroll" (`report.txt:1507`). Both are model outputs. The models differ in transparency (ODJFS publishes a BLS-standard method; the Chamber applies a revenue-driven input-output multiplier), but the asymmetry in treatment is real. | Treats both as models, labels both, and tests the 98% against other projection files (H9). |
| 3 | The strongest material (31.2%, 6.3×, 3,203, D-minus) is buried in section 9 | **PARTLY** | The section number does not match any 1.0 product. The report does not contain the 31.2% or 6.3× material at all; it is only in `AUDIT.md:66-152` and site section 10 (`docs/index.html:392-446`). The 3,203 and D-minus items sit in report section 15 of 20 (`report.txt:1452-1511`) and site section 8 (`docs/index.html:307-369`). The substance — late and scattered — is right. | A box early in the report, "Numbers in circulation", with the provenance of each. |
| 4 | With the mix within 0.005 SD of the nation, the distributional results are national patterns with a local label | **VALID** | 1.0 computes the wage gradient for Cincinnati only (`CALCULATIONS.md:300-317`) and presents band shares that match the NY Fed's national figures as validation (`VERIFICATION.md:94-95`; `report.txt:672`), then calls the gradient a reversal of "every previous automation wave" (`report.txt:680`). Equal means do not force equal distributions, so this needs a test, but 1.0 gives no evidence the pattern is local. | H10: same gradient for the nation and each peer; say plainly if it is national. |
| 5 | Rejects 2019 baselines but relies on 2022-base projections that assume no AI | **PARTLY** | The uses differ: 2019 was rejected for measuring change (`README.md:7-12`); the projections are used for a share. 1.0 also discloses that projections "do not model AI" (`CALCULATIONS.md:347-351`; `report.txt:1279`). But a 2022 base is the post-pandemic hiring peak, and 1.0 puts its headline weight on it. The tension is real. | Uses projections only as labelled context, never as a finding; the hiring test uses observed QWI flows with a 2018–19 pre-period. |
| 6 | Labor-force decline (−9,400) never split into ageing vs participation | **VALID** | No decomposition anywhere (`CALCULATIONS.md:460-469`; `report.txt:86`, 158). LAUS metro labour force is also model-based and revised each March. | H9 decomposition with Census population by age and ACS participation, on its own window. |
| 7 | The 0.87 computing LQ may reflect industry mix; needs a shift-share using national staffing patterns on local QCEW industry mix | **VALID** | No shift-share exists. 1.0 notes OEWS has no metro industry detail (`CALCULATIONS.md:64-65`) but then reads the LQ as behaviour (`report.txt:982`; `README.md:34-38`). The REDI cross-check (`report.txt:1468-1470`) confirms the level, not the cause. | H6 shift-share exactly as the reviewer describes, plus patents, R&D and graduates. |
| 8 | 98% replacement share is near-mechanical; +0.7% has no comparator | **VALID** | No comparator for either (only area 17140 in `data/cincinnati_ces_history.csv`; 98% compared with nothing at `report.txt:1128`). Replacement dominates projected openings by construction in the BLS method. | H9: peers for +0.7%; other Ohio MSA files, Ohio and the US for the 98%. |
| 9 | No research question | **VALID** | None stated in the report, README or site. | Six research questions (section 4). |
| 10 | No literature review | **VALID** | 1.0 cites the NY Fed, a FEDS Note, BPC and Felten et al. only (`report.txt:1883-1932`). | Short review (section 5), every work confirmed to exist. |
| 11 | Exposure band cut moved from 0.50 to 0.40 after seeing the data, with no robustness check | **PARTLY** | The move is real (`CALCULATIONS.md:275-281`) and no sensitivity table exists. But 0.40 matches the NY Fed's published benchmark ("0.40 or above"; `scripts/build_workbook.py:321`, 402-404), which is an external anchor, not a specification search. The 0.50 run predates the repository (0.40 is in the first commit, a62c4d2), so the order cannot be audited from git. | H4: report 0.30, 0.40, 0.50 and the top decile; conclusions must hold at all. |
| 12 | Potential-vs-revealed result rests only on the Anthropic Economic Index | **VALID** | AEI is the only revealed-use measure (`CALCULATIONS.md:113-116`; `report.txt:686`, 1772). | Adds Microsoft Research's AI applicability score (Tomlinson et al. 2025) as a second revealed-use measure, and Eloundou et al. as a second potential measure. |
| 13 | The reproducibility work is the real contribution, and it is buried | **PARTLY** | Buried: yes, methodology is section 18 of 20 and the tests are never mentioned in the findings. "The real contribution": a judgement. Reproducibility makes findings checkable; it is not itself a finding. | A "How this study is checked" box on page 2; pre-registration and tests linked from the key findings. |
| 14 | Three news stories are buried (ODJFS mislabel; D-minus from someone seeking $200,000; Chamber figure vs its own table, 30× vs ~84×) | **PARTLY** | The ODJFS mislabel is not buried: report section 2 (`report.txt:76`) and site section 2 (`docs/index.html:84-86`). The other two are late (above). On the ratio, both numbers are right and measure different things: (3,203 ÷ 2.89) ÷ 37.5 = 29.6× compares modelled *direct* jobs with on-site staff (`tests/test_study.py:364-384`); 3,203 ÷ 37.5 ≈ 85× (≈84× if on-site staff is rounded to 38) compares modelled *total* jobs (direct, indirect and induced) with on-site staff. Like-for-like is the first. | The box in row 3, showing both ratios with their definitions. The D-minus item is handled under row 15. |
| 15 | The Richardson line names a private citizen with no primary-record link and no right of reply | **VALID** | Named at `report.txt:1458` and `docs/index.html:324`; the D-minus and $200,000 framing at `report.txt:1462` and `docs/index.html:337`; recorded as a "secondary" source (`data/local_institutional_sources.csv:32`). Neither the CityBeat article nor the City's recording appears in the 1.0 sources (`report.txt:1934-1976`). The record also complicates 1.0's account (correction C2), and the meeting captions are garbled at the grade itself, so the exact words need checking against the audio. | Section 9.3. |
| 16 | Kroger "Partly": either the source cites AI or it doesn't | **VALID** | `report.txt:1008`; `data/ai_adoption_employers.csv:2`. | One three-code rule applied to every employer and WARN notice (H11); see C4. |
| 17 | Kroger's cuts vs Fifth Third's 30% AI code with no cuts is the human story, told in two table rows | **PARTLY** | The report gives each its own subsection (`report.txt:1055-1069`); the site reduces it to rows and one sentence (`docs/index.html:290-303`). The contrast was never drawn as the central case, and it now needs restating because of C3. | A case-study box: two of the region's largest employers, two strategies, with each company's own words and the coding rule applied. |

Tally: **VALID 10** (2, 4, 6, 7, 8, 9, 10, 12, 15, 16); **PARTLY 7** (1, 3, 5, 11, 13, 14,
17); **WRONG 0**.

---

## 4. Research questions and hypotheses

Full statements, decision rules and the interest-rate checks are in `PREREGISTRATION.md`.

| RQ | Question | Hypotheses (decision rule in the pre-registration) |
|---|---|---|
| RQ1 Adoption | How widely and how fast are firms here using AI, compared with the states, nation and peers? | H5 (descriptive; written after seeing two survey figures, disclosed) |
| RQ2 Capability | Is the region building AI capability or buying it, once industry mix is accounted for? | H6 (shift-share plus capability ranks) |
| RQ3 Labor market (central) | Since late 2022, has the entry door to AI-exposed work narrowed for young workers here, beyond peers and beyond the rate shock? | H1 (confirmatory), H2, H3 |
| RQ4 Output | Are exposed industries producing more per worker? | H7 (descriptive) |
| RQ5 Infrastructure | What AI-related physical investment is coming, with how many permanent jobs per MW, what rate effect and what public cost? | H8 (confirmatory test of 1.0's finding) |
| RQ6 1.0 re-test | Do 1.0's six claims survive comparison? | H4, H9, H10, H11 |

One addition made after the pre-registration was committed, before any data was seen, and
logged in its Amendments table: **H2b**, an occupation-based version of the entry-door test
using ACS 1-year microdata (PUMS) for the metro's PUMAs, 2018–19 vs 2023–25. QWI has industries,
not occupations; ACS has occupations but only employment, not hires, and small samples. Running
both is the closest a public-data study can get to the Brynjolfsson–Chandar–Chen design.

---

## 5. Measurement framework and identification

### 5.1 Framework

I keep your five lenses and order them as a chain: **adoption** (are firms using AI?) →
**labour market** and **output** (what changes for workers and productivity?), with
**capability** (who builds it) and **infrastructure** (what physical investment arrives) as the
two conditions around that chain. Exposure is treated as a measurement input that feeds every
lens, not as a lens of its own, because it says what AI *could* touch, not what it did. The
three-way separation 1.0 introduced — potential exposure, observed use, attributed displacement
— is kept as a rule that applies across all five.

### 5.2 Data by lens, with the last data point available today

Source types: G = government, A = academic, I = industry or advocacy, J = journalism,
P = private vendor, C = commentary.

| Lens | Series | Geography | Last data point (13 Nov 2026) | Released | Type |
|---|---|---|---|---|---|
| Adoption | Census BTOS AI use | OH, KY, IN, US (no Cincinnati: only the 25 largest metros) | 2026 period 22 | 5 Nov 2026 | G |
| Adoption | Anthropic Economic Index | State | Apr–May 2026 usage | 26 Jun 2026 (no newer release) | I |
| Adoption | Cleveland Fed SORCE AI questions | Fourth District | Sept 2026 survey | 14 Oct 2026 | G |
| Adoption | Beige Book, Cleveland District | Fourth District | 14 Oct 2026 edition; next 25 Nov 2026 (inside window) | — | G |
| Adoption | 10-K AI disclosures, Cincinnati-HQ companies | Firm | Latest filings | Live (SEC EDGAR) | G (filings) |
| Adoption | AI postings: Indeed (if approved), BPC/Lightcast, CareerOneStop | Metro | Indeed daily to Nov 2026 | — | P / P / G |
| Capability | USPTO AI Patent Dataset + PatentsView inventor location | Inventor county/metro | Patents through 2023 | AIPD 2023 update | G |
| Capability | NSF HERD | Institution | FY2024; FY2025 due 24 Nov 2026 (inside window) | 23 Dec 2025 | G |
| Capability | IPEDS completions (CIP 11, 30.70, 27.05, 14.09) | Institution | To confirm (2023–24 final expected) | — | G |
| Capability | Venture funding | Metro/state | To source | — | P |
| Labor | Census QWI hires, earnings by age × industry | State parts of CBSA 17140 | OH, IN 2026 Q1; KY 2025 Q4 → metro 2025 Q4 | OH 12 Nov; IN 5 Nov; KY 6 Aug 2026 | G |
| Labor | ACS 1-year PUMS (H2b) | PUMAs ≈ MSA | 2025 | Sept 2026 | G |
| Labor | OEWS | MSA | May 2025 | Spring 2026 | G |
| Labor | CES, LAUS | MSA | Sept 2026 (preliminary); Oct metro release 2 Dec 2026, outside window | — | G |
| Labor | QCEW | County / MSA | 2026 Q1 (Q2 not yet posted: API 404) | — | G |
| Labor | WARN notices | OH, KY, IN | Live to Nov 2026 | — | G |
| Output | BEA GDP by county and industry, summed to the MSA | 15 counties | 2024 | 5 Feb 2026 (BEA discontinued metro GDP with this release; 2025 data due 2 Dec 2026, outside window) | G |
| Infrastructure | PJM load forecast (DEOK zone) | Utility zone | 2026 forecast | Jan 2026 | I (grid operator) |
| Infrastructure | PUCO dockets (Duke Energy Ohio large-load tariff, filed Dec 2025; rate case) | Utility | Live | — | G |
| Infrastructure | QCEW NAICS 518210 | County | 2026 Q1; county cells often suppressed — reported as not testable where so | — | G |
| Infrastructure | Abatement and tax-credit records; county and city legislation | Local / state | Live | — | G |
| Infrastructure | Chamber facility counts (Datacentermap, Cushman & Wakefield underneath) | Metro | July 2026 | 12 Oct 2026 | I / P |

### 5.3 Identification

The core design compares four differences at once: exposed vs less-exposed industries,
22–24-year-olds vs 35–54-year-olds, 2018–19 vs 2023–25, and Cincinnati vs its peers. Industry
exposure is fixed from national 2022 staffing patterns, so it cannot respond to the outcome.
A permutation test (industries randomly reassigned to exposed and less-exposed groups) gives
the range of results chance alone would produce.

**The interest-rate threat.** The 2022–23 rate rises hit finance and tech hardest — the most
exposed industries — exactly when generative AI arrived. Four checks, each with a rule written
in advance: drop information, finance and real estate and see if the result survives; run the
same test on construction and durable manufacturing, which are rate-sensitive but barely
exposed (if they show the same pattern, it is the cycle); read the timing (a gap largest in 2023
and narrowing after rate cuts began in September 2024 points to rates; one widening through
2025 points to AI); and compare with peers, which share the national rate shock.

**What the design can and cannot attribute.** Even a result that passes every check shows a
pattern *consistent with* AI substituting for entry-level work. It cannot rule out other forces
that hit young workers in exposed industries at the same time (offshoring of entry roles,
remote-work shifts, a graduate-supply bulge). The report will say so in those words. Only an
employer's own statement attributes a job change to AI.

---

## 6. Interpretive lenses and skeptics

These go only in the outlook section, which is separate from the findings. Each is used as a
question that a specific finding answers, not as decoration.

| Thinker | Specific piece (existence confirmed) | Position, accurately stated | The question for Cincinnati | Finding that answers it |
|---|---|---|---|---|
| Noah Smith | "Plentiful, high-paying jobs in the age of AI", *Noahpinion*, 17 Mar 2024 (C) | Comparative advantage can keep humans in well-paid work even where AI is better at a task — *if* something constrains the total amount of AI, such as compute or energy. He later stressed the conditional: it is a possibility, not a guarantee. | Where is the region's comparative advantage when routine cognitive work gets cheap, and which local jobs does AI complement? | Exposure by occupation × observed use (complement vs automate split, AEI and Microsoft); manufacturing and engineering LQs; health care growth. Energy as the binding limit links to the data-center section. |
| Ezra Klein & Derek Thompson | *Abundance*, Avid Reader Press, 18 Mar 2025 (C) | Growth is limited by the capacity to build — housing, energy, transmission — and by the capacity of public institutions. | Can the region build fast enough (power, housing for young workers, permitting, state and city capacity) to capture AI-driven growth? | PJM/DEOK load and rate record; local moratoria and zoning overlays; data-center policy chronology. |
| Ezra Klein (risk side) | To confirm before citing: candidate *Ezra Klein Show* episodes in 2025–26 on AI and labour/government. I will cite only an episode or column I have opened. | Klein has argued AI may pose risks to workers and to institutions' capacity to respond. Exact wording to be taken from the confirmed source. | Are public institutions here ready for disruption to entry-level work? | Exponential-gap indicators below; the entry-door result. |
| Azeem Azhar | *The Exponential Age*, 2021 (UK: *Exponential*) (C) | Technologies improve and cheapen exponentially; institutions adapt linearly; the divergence is the "exponential gap". | How fast is adoption moving here, and where is the gap between firm adoption and workers', schools' and governments' readiness? | Adoption change (BTOS states, SORCE) vs training and curriculum measures (IPEDS, AI Ready Ohio counts), and the City's AI policy status. |
| Daron Acemoglu (skeptic) | "The Simple Macroeconomics of AI", NBER WP 32487 (May 2024); *Economic Policy* 40(121), 2025 (A) | Total factor productivity gains of no more than about 0.66% over ten years; possibly under 0.53%. | Is there any sign of an output-per-worker gain in exposed industries? | H7 output lens (descriptive). |
| David Autor (skeptic) | "Applying AI to Rebuild Middle Class Jobs", NBER WP 32140, Feb 2024 (A) | AI *could* restore middle-skill work by extending expertise to workers without elite credentials — a possibility contingent on how it is deployed, not a forecast. | Is local deployment extending expertise (health care, technicians) or replacing it? | Complement vs automate split by occupation; employer deployment evidence (Children's, UC Health, GE Aerospace). |

**Literature to be reviewed (existence confirmed so far):** Brynjolfsson, Chandar & Chen,
"Canaries in the Coal Mine?" (Stanford Digital Economy Lab; Aug 2025, revised Aug 2026 with ADP
data through June 2026 — I will cite the latest version and its own figures); Lichtinger &
Hosseini, "Generative AI as Seniority-Biased Technological Change" (SSRN 5425555, 2025);
Eloundou, Manning, Mishkin & Rock, "GPTs are GPTs" (arXiv 2303.10130; published in *Science*,
2024 — journal page to confirm); Tomlinson, Jaffe, Wang, Counts & Suri, "Working with AI"
(arXiv 2507.07935, Microsoft Research; data on GitHub); Felten, Raj & Seamans (2021, 2023);
Audoly, Guerin & Topa (NY Fed, May 2026); Muro & Methkupally, Brookings, "Mapping the AI
economy" (July 2025; secondary coverage puts Cincinnati among "Focused Movers"). **Still to
confirm before citing:** Acemoglu & Restrepo (2019 JEP; 2020 JPE); Webb (2020); Humlum &
Vestergaard (2025); Kinder et al., Brookings (2024); the October 2026 study of 1,584 data
centers reported by Fortune and *The Conversation*.

---

## 7. OhioX and Marketplace

Both are used as the brief requires: OhioX figures are traced to method and labelled advocacy;
Marketplace is cited by story and date for reporting and voices, with any number traced to its
primary source.

| Item | Date | Type | What it offers | Where it fits | To do |
|---|---|---|---|---|---|
| OhioX, *2026 State of AI Report* | 2026 | I | Self-selected survey of "more than 270" Ohio leaders; headline shares 79% / 57% / 21% (the figures the preliminary draft cited, `AUDIT.md:158-162`) | Adoption, as statewide advocacy context only | Read the method; label non-representative |
| OhioX, *State of AI_2025 – Mapping Ohio's AI Opportunity* | 2025 | I | "Over 600 tech leaders"; sponsored by Foundry for AI by Rackspace | Same; change between the two editions cannot be read as a trend (different samples) | Same |
| OhioX hub essays and op-ed (e.g., "The cognitive rust belt is here"; Columbus Dispatch op-ed on preparing students) | 2025–26 | C / I | Policy positions on AI skills | Outlook (exponential gap) | Confirm dates |
| OhioX on data centers | — | — | **Not found** in two searches (general, and restricted to ohiox.org). I am not claiming it does not exist. | Infrastructure policy | Search the HB 646 witness lists and OhioX policy pages |
| Marketplace, "Ohio data center boom shows Big Tech planting seeds in Middle America" | 10 Feb 2025 | J | Interview on New Albany and JobsOhio-negotiated deals | Data centers: Columbus comparator; public money | Read in full |
| Marketplace, "How data center construction is affecting the labor market" (and episode "The data center job boom") | 11 Aug 2026 | J | National reporting on construction labour demand and wages | Data centers: temporary vs permanent jobs | Trace any figure to primary |
| Marketplace, "More data centers plan to build their own natural gas plants for power" | 4 Feb 2026 | J | Bring-your-own-power trend | Electricity; links to Acton's and HB 646's on-site power conditions | Read |
| Marketplace, "As AI changes entry-level jobs, how can we prep young people?" (and episode "When AI disrupts entry-level work, will we be ready?") | 6 Jul 2026 | J | Researchers and workers on entry-level effects | Entry-door section; outlook | Read; trace numbers |
| Marketplace, "The tough job market for new college grads probably isn't all due to AI" | 30 Jun 2025 | J | The cyclical-vs-AI argument | Rate-shock threat | Read |
| Marketplace, "As AI spreads, entry-level economics jobs are shifting" | 2 Feb 2026 | J | Occupation-level reporting | Entry-door section | Read |
| Marketplace, "One college senior's take on the slowing labor market and the emergence of AI" | 21 Apr 2026 | J | Worker voice | Entry-door section | Read |
| Marketplace, "AI is pushing young people toward the trades" | 16 Dec 2025 | J | Supply response | Comparative-advantage discussion | Read |
| Marketplace on Cincinnati specifically | — | — | **None found on AI or data centers.** A site-restricted search for "Cincinnati" returned only the 2012–15 Oyler School series. | — | Search Kroger, P&G, Fifth Third, GE Aerospace and Marketplace Tech before writing |

---

## 8. Data-center section: plan and leads

### 8.1 Status of the leads you gave me

| Lead | Status | Source (type) |
|---|---|---|
| 565 MW / 19 facilities vs 3,000+ MW Columbus | **Corrected (C1):** 17 existing + 2 planned; the Chamber's Columbus figure is "3,150+" MW; MW basis unstated | Chamber, 12 Oct 2026 (I; underlying P) |
| 472 vs 9,025 data-center postings | Confirmed as Chamber-relayed Lightcast counts, July 2025–July 2026 | Chamber (I; underlying P) |
| Acton won on 3 Nov 2026; takes office Jan 2027 | **Confirmed** (AP call); inauguration date to confirm | AP via Ohio Capital Journal; WAMC (J) |
| Acton: data centers tied to good jobs and own energy; review JobsOhio | **Confirmed in substance.** "Conditional moratorium" on new data centers unless conditions on costs, union labour, transparency, environment and community benefit agreements are met; running mate on bring-your-own-power; clawbacks for unmet job promises; campaign pledge of a "top-to-bottom review of JobsOhio" | WYSU, 27 Jul 2026 (J); actonforgovernor.com (C, campaign) |
| HB 646 caps abatements at 50%, ends megaproject grant | **Partly confirmed.** Substitute HB 646 (June 2026) cuts the sales-tax exemption from 100% to 50% (75% for brownfields or off-grid power), caps local property-tax abatements at 50%, and per one report ends megaproject-grant access; creates a PUCO data-center rate class. It stalled before summer recess. Current status to check. | Route Fifty; WYSU; WCPO (J); bill text to read (G) |
| Separate proposal: surety bond = 10 years of salaries | **Appears to be inside Sub. HB 646**, not separate (one report: a bond equal to the average salary of all workers over ten years). Bill text to confirm. | Route Fifty (J) |
| SB 103 (enacted) covers data centers' effect on electricity rates | **Partly wrong.** SB 103 (136th GA) was signed 19 Dec 2025 and took effect 20 Mar 2026, but it concerns **natural-gas** alternative rate plans; a trade report says it shifts gas cost risk to large loads, including data centers. It is not an electricity-rate law. Bill text to confirm. | ohiohouse.gov status page (G); Environment+Energy Leader (J) |
| $1.6B tax-break dispute stalled broader regulation | **Confirmed.** Ohio Taxation reported about $1.57B in 2025 data-center sales-tax exemptions against a $136M estimate; the dispute stalled the June package; DeWine paused new exemptions on 28 May 2026 | E&E News; Signal Ohio; Fox19 (J); Ohio Dept. of Taxation (G, to retrieve) |
| OCC: few permanent jobs once built | **Confirmed** | OCC fact sheet and 27 May 2026 testimony (G) |
| City AI task force; $200,000 request not voted | **Confirmed with complications (C2)** | CitiCable recording; CityBeat, 5 May 2026; City budget books |
| Indeed metro postings index, Feb 2020 = 100 | **Confirmed:** `metro_job_postings_us.csv` (metros ≥ 500k), seasonally adjusted, % change since 1 Feb 2020; GitHub states CC BY 4.0 while FRED marks it "pre-approval required" | Indeed Hiring Lab (P) |

### 8.2 What the section will contain

Facilities table with **operating / under construction / announced** in separate columns, each
row sourced, MW basis stated. Already identified: Prologis "Project Mila" in Trenton (15-year,
75% abatement approved July 2026; Trenton voters' Issue 17 limits new facilities above 25 MW);
the AWS-linked Butler County proposal (status disputed in reporting); a Logistix power request
in Hamilton (paused); Warren County's six-month moratorium; the City of Cincinnati's Interim
Development Control Overlay No. 89 for data centers (extended to 11 Feb 2027). Just outside the
region and sharing its labour market or grid: the reported OpenAI facility in Pike County, and
Columbus/New Albany (AEP zone) as the required comparator. Jobs per MW split into temporary
construction and permanent on-site FTE. Electricity: DEOK load from PJM; Duke Energy Ohio's
large-load tariff (filed December 2025) and rate case; AEP Ohio's approved tariff as the
template. Public money: Ohio Tax Credit Authority exemptions and local abatements, granted and
proposed. Policy as of November 2026. The verdict on 1.0's finding follows the pre-registered
rule (H8), whichever way it goes.

---

## 9. Decisions that are yours

### 9.1 Title — three options, each with "2.0"

1. **Cincinnati AI Labor Market 2.0: Early Evidence on Adoption, Hiring and Investment in
   Greater Cincinnati** *(recommended)* — describes what was tested, so it stays honest whatever
   the hiring test finds; meets objection 1.
2. Cincinnati AI Labor Market 2.0: Is AI Narrowing the Entry Door to Professional Work in
   Greater Cincinnati? — leads with the central question; strong for journalists; risks reading
   as a yes if the answer is no.
3. Cincinnati AI Labor Market 2.0: Exposure, Adoption and the Data Center Boom in a
   Slow-Growth Metro — foregrounds the policy fight; "slow-growth" pre-judges a claim 2.0 is
   re-testing, so I would only use it if H9 confirms it.

I suggest fixing the frame now and allowing a one-line, finding-based subtitle to be added once
the results are in (Brookings Metro usually titles by finding).

### 9.2 Indeed postings

**Recommendation: use it, narrowly.** Official series end in September 2026 (CES) and 2025 Q4
(QWI); Indeed is the only public metro series that runs to November 2026, and the outlook needs
a leading indicator. Rules: labelled private; shown only as change since February 2020 and
since November 2022, never as a level; total postings only (Indeed publishes no metro AI-postings
or occupation series); used in the outlook and one robustness chart, never for a headline
finding or for attribution. Redistribution: Hiring Lab's GitHub says CC BY 4.0, FRED says
pre-approval; I would commit the download script and cite, not commit the file, until you
confirm the licence. Alternative if you prefer a pure government-data study: leave it out and
state the official series' last points.

### 9.3 The Richardson line

**Recommendation:** take the name out of the findings. The analytical point — that the only
public "grade" of the City's AI readiness was an on-the-spot verbal answer to a council
member's question, with no method — does not need a name. Describe the role ("the task force's
chair, presenting to the committee"), link the City's own recording with a timestamp, drop the
"the person grading the city was the person asking it for at least $200,000" construction, fix
the budget statement (C2), and offer a right of reply before publication. Sending the request is
an outward action, so it waits for your approval; the draft is below. Two further cautions: the
meeting captions are garbled exactly at the grade ("B MINUS. D OR B? >> D."), with the council
member then restating "a D minus", so someone should check the audio before the grade is quoted;
and the $200,000 history needs one more record (the earlier allocation the council member
mentions).

**Primary-record citation (draft):**
> City of Cincinnati, Economic and Cultural Opportunity Committee, meeting of 4 May 2026. Video
> recording, CitiCable (Office of the Clerk of Council). Internet Archive item `34260501-eco`,
> https://archive.org/details/34260501-eco, presentation from ≈0:36:34; funding exchange
> ≈1:14:20–1:15:30; grade exchange ≈1:15:30–1:17:30. Linked from the Clerk of Council's
> Council Meeting Videos page, https://www.cincinnati-oh.gov/council/council-meeting-videos/.
> Secondary: Noah Jones, "Cincinnati given low score for AI preparedness, but city could still
> catch up", *CityBeat*, 5 May 2026.

**Draft request for comment (not sent):**
> Subject: Request for comment — Cincinnati AI Labor Market 2.0
>
> Dear Mr. Richardson,
>
> I am preparing version 2.0 of an independent research study, *Cincinnati AI Labor Market*,
> on how AI is affecting the regional economy and workforce. Version 1.0 (November 2026)
> referred to your 4 May 2026 presentation to the City's Economic and Cultural Opportunity
> Committee. I want to make sure 2.0 describes it accurately and to give you the chance to
> respond.
>
> The draft would say, citing the City's video recording: (1) that you presented as chair of
> the City's regional AI task force; (2) that, asked by Councilmember Walsh to grade the City
> from A to F on its willingness to embrace AI, you gave a grade reported as D-minus, and that
> the grade was an informal assessment rather than the result of an index or survey; and
> (3) that the presentation sought at least $200,000 in City funding for the task force's work
> and a proposed AI training lab.
>
> Is any of this inaccurate or incomplete? In particular: what grade did you give, what did
> you mean it to measure, and what City funding has the task force or Disruption Now received
> to date, and for what? Any response you send by [date] will be reflected in the report, and
> I can include a short statement from you if you wish.
>
> Thank you,
> KetiB, [AFFILIATION]

### 9.4 Newer AEI release or projections round?

- **AEI: no newer release exists.** The Hugging Face dataset's latest usage release is
  `release_2026_06_26`; the only addition since (30 Sept 2026) is a separate `robot_exposure`
  dataset. Recommendation: keep June 2026. The robot-exposure file is outside generative AI and I
  would not add it without your say-so.
- **Projections: no newer metro round exists.** Ohio LMI says statewide 2024–2034 projections
  are being incorporated (O*NET already shows Ohio 2024–2034 figures from Projections Central),
  but the only Cincinnati-area files posted are 2022–2032; `LTOP_Cincinnati2034.xlsx` returns
  404. Recommendation: keep 2022–2032 for the metro, and use the statewide and national
  2024–2034 rounds only in the "is 98% mechanical?" comparison (H9), labelled.

### 9.5 The workbook's industry sheet (kept on 2019 by your choice)

**Recommendation: show both baselines, 2024 first.** The paper, deck and site use 2024;
`VERIFICATION.md:116-118` records the inconsistency. Putting the 2019 column beside the 2024
one keeps what you wanted to preserve and removes the inconsistency. Alternatives: switch to
2024 only, or keep 2019 only and label the sheet as differing from the paper.

---

## 10. Report outline (Brookings Metro style)

0. Title, byline [KetiB, AFFILIATION]; **corrections to 1.0** box
1. **Key findings** (one sentence and one number each)
2. Introduction: the research question, why it matters, what 2.0 adds; one geography; box
   "How to read this report" (potential exposure, observed use and attributed displacement kept
   apart; source-type labels); box "How this study is checked"
3. What the research says (short literature review)
4. The regional economy in comparison (growth vs peers; labour-force decomposition; the 98%)
5. Exposure: Greater Cincinnati against its peers (four measures; band robustness; is the wage
   gradient national?)
6. Adoption: are local firms using AI? (states, district, filings, postings)
7. Capability: building or buying? (shift-share; patents; R&D; graduates)
8. Hiring and the entry door (QWI test; event-time chart; rate-shock checks; peers; ACS
   occupation version; new-hire earnings; WARN and employer attribution; Kroger–Fifth Third case
   box)
9. Output per worker (descriptive)
10. Data centers and AI infrastructure (facilities by status; jobs per MW; Columbus; electricity;
    public money; policy as of November 2026; link to AI work; verdict on 1.0's finding)
11. What the evidence can and cannot attribute to AI (claims table)
12. Box: Numbers in circulation (ODJFS "Cincinnati MSA"; 3,203 vs the Chamber's own table, 30×
    and 85× defined; 565 MW; the D-minus)
13. **Outlook** (separate from findings): the interpretive lenses and skeptics; bull case; bear
    case; leading indicators with thresholds and release dates
14. **Policy implications** (separate): workforce boards; employers; city and county; state
    legislators on data-center bills; universities and JobsOhio
15. Methods appendix: vintage table; peer rule; exposure construction; test specifications;
    shift-share; decomposition; data-center definitions; coding rules; deviations from the
    pre-registration
16. Endnotes; sources grouped by type

Every chart carries a source line. The deck (about 20 slides with speaker notes) follows the
same order. The site becomes 2.0, with 1.0 moved to `docs/v1.0/` and linked from an archive
page.

---

## 11. After the check-in

Order of work: amend the pre-registration with your decisions → acquisition scripts and raw
pulls (QWI for Cincinnati and the 19 peers' states; QCEW; OEWS national industry staffing;
BTOS; ACS PUMS; WARN; BEA county; patents; HERD; IPEDS) → tests for every new number → run the
pre-registered analyses once → report → deck → site and archive → `AUDIT.md`, `CALCULATIONS.md`
vintage table → stop for approval to push and publish.

Known risks: QWI noise and suppression in small age-by-industry cells (mitigated by 3-digit
NAICS and four-quarter averages); QCEW 518210 county suppression (reported as not testable);
BTOS has no Cincinnati metro (state only, said plainly); BEA metro discontinued (county build,
with suppressed industries listed); I cannot watch video, so the grade quotation needs a human
check of the audio.
