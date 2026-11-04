# How this study is checked

Most regional economic analysis cannot be checked at all. A number appears in a slide, nobody
can trace it, and an error survives because finding it would take longer than believing it.

This study is built so that every published figure can be recomputed from public data by someone
who does not trust it. That design has already paid for itself twice: both errors described at the
bottom of this page were found by the checks, not by a reader.

---

## The five layers

| Layer | What it answers | Where |
|---|---|---|
| 1. Provenance | Where did this number come from? | `CALCULATIONS.md` |
| 2. Reproduction | Does the pipeline rebuild it from raw files? | `scripts/` |
| 3. Trace | What is the arithmetic, line by line? | `scripts/trace_numbers.py` |
| 4. Regression | Does what we published still match the data? | `tests/test_study.py` |
| 5. External | Do the results agree with independent research? | cross-checks below |

Layers 1–3 let a reader follow the work. Layer 4 is the one that fails loudly when something
moves. Layer 5 is the one that catches a method that is internally consistent and still wrong.

---

## Layer 1 — provenance

`CALCULATIONS.md` has thirteen sections and documents every figure: the download command, the BLS
series identifier, the filter, the formula, and the rounding. Series identifiers are constructed
deterministically rather than copied from a web form:

```
OES series =  OE + U + areatype(1) + area(7) + industry(6) + occupation(6) + datatype(2)
```

Anyone can rebuild the same identifier and pull the same file. Nothing says "according to BLS"
without saying which table, which period and which cut.

## Layer 2 — reproduction

Nine scripts run in order and rebuild every derived dataset from the raw extracts. `README.md`
lists them with the command line for each. Three large source files are gitignored; section 1 of
`CALCULATIONS.md` gives the exact commands that regenerate them.

The point is not convenience. It is that a reader who distrusts a number can delete `data/` and
rebuild it.

## Layer 3 — the trace

`scripts/trace_numbers.py` prints every published figure with the arithmetic that produces it:

```
  Cincinnati observed exposure          0.088   SUM(emp x score) / SUM(emp), missing excluded
  total nonfarm jobs added              8,600   (1,178.2 - 1,169.6) x 1,000
  share of banking fall predating 2024  73.7%   (27.3 - 24.5) / (27.3 - 23.5)
```

Saved output lives in `output/number_trace.txt`. This is the layer that caught the exposure-band
error: the trace disagreed with the published table, and the table was wrong.

## Layer 4 — the regression tests

`tests/test_study.py` recomputes thirteen published findings from `data/` and asserts each still
matches. Unlike the trace, it does not need a human to read it — it exits non-zero and names what
moved.

```
python tests/test_study.py
```

Two of the thirteen exist because the work got those things wrong once:

- `test_soc_levels_partition` guards the occupational misclassification that double-counted
  national employment by about 58%. It asserts detailed occupations never sum above the published
  total.
- `test_exposure_band_table` guards the four wrong values in the exposure-band table, and pins the
  two definitions that caused the confusion: "none measured" is a measured **zero**, not a missing
  value, and the band wage is an employment-weighted **mean of occupational medians**.

Several tests assert a *direction* rather than a value, so they survive a data refresh but still
catch an inversion — that exposure rises with pay, that both employment and the labour force fell,
that no metro-level AI usage figure is ever claimed.

**The suite is mutation-tested.** Flipping the sign on banking fails two checks; shifting one
occupation's employment by 5,000 fails four. A suite that cannot fail proves nothing.

## Layer 5 — external cross-checks

Internal consistency is not accuracy. Three independent checks:

| Check | Independent source | This study | Verdict |
|---|---|---|---|
| Share of workers in zero-exposure occupations | NY Fed, ~40% nationally | 41.4% | consistent |
| Share above 0.40 exposure | NY Fed, under 10% nationally | 10.0% | consistent |
| Fifth Third AI code generation | 2025 annual report (primary) | ~30% | verified against filing |

The Fifth Third figure is worth noting. Secondary coverage reported "nearly 60%" of developers
using AI daily; the primary filing says 56%. The study cites the filing. A number that is easy to
repeat is not the same as a number that is true.

---

## What the checks cannot do

Being honest about the limits of verification is part of verification.

- **They cannot validate the exposure indices.** AIOE and observed exposure measure task overlap.
  Whether overlap becomes job loss is unestablished, and no test here changes that.
- **They cannot detect a wrong source.** If BLS publishes a revision, the tests pass against the
  old file until it is refreshed.
- **They cannot check the employer evidence.** Company statements are read and cited by hand.
- **They cannot run the workbook's formulas.** `verify_workbook.py` recomputes 51 summary figures
  in Python because LibreOffice was unavailable to recalculate the live Excel formulas. The
  workbook's own formulas have not been executed by a spreadsheet engine.
- **One known inconsistency.** The workbook's industry sheet is still baselined to 2019 while the
  paper, deck and site use 2024. The authoritative 2024 figures are in `output/number_trace.txt`
  and `CALCULATIONS.md` section 9.

---

## The two errors, and how each was found

**The SOC misclassification.** Occupational codes were classified by testing whether they end in
two zeros. That rule accepts broad codes like `11-3010`, which are containers for the detailed
codes beneath them, so detailed employment was counted twice. National detailed employment summed
to 234,970,310 against a published 155,495,730 — about 58% too high.

Found by a coverage check: the sum should approach the published total from below and could not
exceed it. Fixed with an ordered rule testing four zeros, then three, then one. Coverage became
96.0% for the nation and 95.4% for Cincinnati.

**The exposure-band table.** Four values in the published table were carried over from an earlier
run that used a 0.50 cut point: 57 and 20 occupations at $66,159 and $62,210, where the correct
figures are 47 and 30 at $69,113 and $59,383. Employment and shares were right, which is why it
survived a read-through.

Found by `trace_numbers.py` recomputing the table and disagreeing with it.

Both are documented in `CALCULATIONS.md` rather than quietly corrected, and both now have a test.
Most published regional analysis contains errors of exactly this kind that nobody ever finds.
