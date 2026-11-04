"""Independently recompute every summary figure in Python and write a Verification sheet.

The workbook's summary sheets hold live Excel formulas. openpyxl writes formulas without
cached values and LibreOffice is not installed in this environment, so the formulas cannot be
evaluated here. This script therefore computes the same quantities directly from the source
CSVs and records them alongside the cell each formula sits in, so the two can be compared the
first time the workbook is opened in Excel.

Run after build_workbook.py:  python -I scripts/verify_workbook.py <base_dir>
"""
import csv
import os
import statistics as st
import sys

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

FONT = "Arial"
H_FILL = PatternFill("solid", fgColor="1F3864")
H_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(name=FONT, bold=True, size=14, color="1F3864")
SUB_FONT = Font(name=FONT, italic=True, size=9, color="595959")
BODY = Font(name=FONT, size=10)


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    if s in ("", "-", "*", "**", "#", "nan", "None"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main(base):
    path = os.path.join(base, "output", "Cincinnati_AI_Labor_Market_Dataset.xlsx")
    occ = list(csv.DictReader(open(os.path.join(base, "data",
                                                "cincinnati_occupation_exposure.csv"),
                                   encoding="utf-8")))
    qcew = list(csv.DictReader(open(os.path.join(base, "data",
                                                 "qcew_cincinnati_counties.csv"),
                                    encoding="utf-8")))

    det = [r for r in occ if r["soc_level"] == "detailed"]
    nat = [r for r in det if r["area"] == "National"]
    cin = [r for r in det if r["area"] == "Cincinnati MSA"]

    def cuts(key, qs=(0.25, 0.5, 0.75)):
        v = sorted(num(r[key]) for r in nat if num(r[key]) is not None)
        return [v[int(len(v) * q)] for q in qs]

    lm_cuts = cuts("aioe_language_modeling")
    lm_med = lm_cuts[1]
    ob_med = st.median([num(r["observed_exposure"]) for r in nat
                        if num(r["observed_exposure"]) is not None])

    def wmean(rows, key):
        s = [(num(r["employment"]), num(r[key])) for r in rows if num(r[key]) is not None]
        w = sum(e for e, _ in s)
        return sum(e * v for e, v in s) / w if w else float("nan")

    def agg(area, soc):
        return next((num(r["employment"]) for r in occ
                     if r["area"] == area and r["soc_code"] == soc), None)

    def lq(area, soc):
        return next((num(r["location_quotient"]) for r in occ
                     if r["area"] == area and r["soc_code"] == soc), None)

    def obs_band(v):
        if v is None:
            return ""
        if v == 0:
            return "0.00 no measured overlap"
        if v <= 0.10:
            return "1 >0.00-0.10"
        if v <= 0.25:
            return "2 >0.10-0.25"
        if v <= 0.40:
            return "3 >0.25-0.40"
        return "4 >0.40"

    def lm_band(v):
        if v is None:
            return ""
        return ("Q1 lowest" if v <= lm_cuts[0] else "Q2" if v <= lm_cuts[1]
                else "Q3" if v <= lm_cuts[2] else "Q4 highest")

    def quad(r):
        lmv, obv = num(r["aioe_language_modeling"]), num(r["observed_exposure"])
        if lmv is None or obv is None:
            return ""
        return (("High exposure / " if lmv > lm_med else "Low exposure / ")
                + ("high use" if obv > ob_med else "low use"))

    emp_in = lambda rows: sum(num(r["employment"]) for r in rows)

    checks = []
    add = lambda sheet, cell, label, val, fmt="{:,.0f}": checks.append(
        dict(sheet=sheet, cell=cell, metric=label,
             expected=(fmt.format(val) if val is not None else "n/a"))
    )

    tot_detail = emp_in(cin)
    add("Summary_KeyFindings", "B5", "Cincinnati MSA total employment (OEWS May 2025)",
        agg("Cincinnati MSA", "00-0000"))
    add("Summary_KeyFindings", "B6", "Cincinnati MSA median annual wage, all occupations",
        next(num(r["annual_median"]) for r in occ
             if r["area"] == "Cincinnati MSA" and r["soc_code"] == "00-0000"), "${:,.0f}")
    add("Summary_KeyFindings", "B7", "Cincinnati MSA mean annual wage, all occupations",
        next(num(r["annual_mean"]) for r in occ
             if r["area"] == "Cincinnati MSA" and r["soc_code"] == "00-0000"), "${:,.0f}")
    add("Summary_KeyFindings", "B8", "Employment in detailed occupations", tot_detail)
    add("Summary_KeyFindings", "B9", "Jobs with ZERO measured AI task overlap",
        emp_in([r for r in cin if obs_band(num(r["observed_exposure"])) == "0.00 no measured overlap"]))
    add("Summary_KeyFindings", "B10", "Jobs with observed AI overlap above 0.40",
        emp_in([r for r in cin if obs_band(num(r["observed_exposure"])) == "4 >0.40"]))
    add("Summary_KeyFindings", "B11", "Jobs in top national LM-AIOE quartile",
        emp_in([r for r in cin if lm_band(num(r["aioe_language_modeling"])) == "Q4 highest"]))
    add("Summary_KeyFindings", "B12", "Jobs both highly exposed and already used with AI",
        emp_in([r for r in cin if quad(r) == "High exposure / high use"]))
    add("Summary_KeyFindings", "B13", "Office and administrative support employment (43-0000)",
        agg("Cincinnati MSA", "43-0000"))
    add("Summary_KeyFindings", "B14", "Computer and mathematical employment (15-0000)",
        agg("Cincinnati MSA", "15-0000"))
    add("Summary_KeyFindings", "B15", "Computer and mathematical location quotient",
        lq("Cincinnati MSA", "15-0000"), "{:.2f}")
    add("Summary_KeyFindings", "B16", "Production occupations location quotient",
        lq("Cincinnati MSA", "51-0000"), "{:.2f}")
    add("Summary_KeyFindings", "B17", "Employment-weighted mean LM-AIOE, Cincinnati",
        wmean(cin, "aioe_language_modeling"), "{:.4f}")
    add("Summary_KeyFindings", "B18", "Employment-weighted mean LM-AIOE, National",
        wmean(nat, "aioe_language_modeling"), "{:.4f}")
    add("Summary_KeyFindings", "B19", "Employment-weighted mean observed exposure, Cincinnati",
        wmean(cin, "observed_exposure"), "{:.4f}")

    # Summary_Exposure Panel A rows begin at row 6
    for i, b in enumerate(["0.00 no measured overlap", "1 >0.00-0.10", "2 >0.10-0.25",
                           "3 >0.25-0.40", "4 >0.40"]):
        g = [r for r in cin if obs_band(num(r["observed_exposure"])) == b]
        add("Summary_Exposure", f"C{6 + i}", f"Panel A employment, observed band {b}", emp_in(g))

    for i, b in enumerate(["Q4 highest", "Q3", "Q2", "Q1 lowest"]):
        g = [r for r in cin if lm_band(num(r["aioe_language_modeling"])) == b]
        add("Summary_Exposure", f"C{15 + i}", f"Panel B employment, LM-AIOE {b}", emp_in(g))

    for i, b in enumerate(["High exposure / high use", "High exposure / low use",
                           "Low exposure / high use", "Low exposure / low use"]):
        g = [r for r in cin if quad(r) == b]
        add("Summary_Exposure", f"C{23 + i}", f"Panel C employment, {b}", emp_in(g))

    # wage quintiles
    cw = sorted([r for r in cin if num(r["annual_median"]) and num(r["employment"])],
                key=lambda r: num(r["annual_median"]))
    tote = sum(num(r["employment"]) for r in cw)
    cum = 0.0
    for r in cw:
        e = num(r["employment"])
        cum += e
        r["_wq"] = f"Q{min(4, int(5 * (cum - e / 2) / tote)) + 1}"
    for i, q in enumerate(["Q1", "Q2", "Q3", "Q4", "Q5"]):
        g = [r for r in cw if r["_wq"] == q]
        add("Summary_WageGradient", f"B{5 + i}", f"Wage quintile {q} employment", emp_in(g))
        add("Summary_WageGradient", f"E{5 + i}", f"Wage quintile {q} weighted LM-AIOE",
            wmean(g, "aioe_language_modeling"), "{:.3f}")
        add("Summary_WageGradient", f"F{5 + i}", f"Wage quintile {q} weighted observed exposure",
            wmean(g, "observed_exposure"), "{:.3f}")

    # Ohio vs Kentucky
    def qsum(year, state, field):
        return sum(num(r[field]) or 0 for r in qcew
                   if r["year"] == year and r["state"] == state and r["agglvl_code"] == "70")
    for i, (lbl, state, field, fmt) in enumerate([
            ("Ohio 4-county covered employment", "OH", "employment", "{:,.0f}"),
            ("Northern Kentucky 3-county covered employment", "KY", "employment", "{:,.0f}"),
            ("Ohio 4-county total annual wages", "OH", "total_annual_wages", "${:,.0f}"),
            ("Northern Kentucky 3-county total annual wages", "KY", "total_annual_wages", "${:,.0f}")]):
        add("Summary_OH_vs_KY", f"B{5 + i}", f"{lbl} 2024", qsum("2024", state, field), fmt)
        add("Summary_OH_vs_KY", f"C{5 + i}", f"{lbl} 2025", qsum("2025", state, field), fmt)

    wb = openpyxl.load_workbook(path)
    if "Verification" in wb.sheetnames:
        del wb["Verification"]
    ws = wb.create_sheet("Verification")
    ws["A1"] = "Verification - summary figures recomputed independently in Python"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = ("The summary sheets contain live Excel formulas, which Excel evaluates when the "
                "workbook is first opened. The values below were computed directly from the source "
                "CSVs by scripts/verify_workbook.py and should match the named cells exactly. "
                "Any disagreement indicates a formula error and should be reported.")
    ws["A2"].font = SUB_FONT
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells("A2:D2")
    ws.row_dimensions[2].height = 42
    for j, (h, w) in enumerate(zip(["Sheet", "Cell", "Metric", "Expected value"],
                                   [26, 10, 62, 22]), 1):
        c = ws.cell(row=4, column=j, value=h)
        c.font = H_FONT
        c.fill = H_FILL
        ws.column_dimensions[chr(64 + j)].width = w
    for i, r in enumerate(checks, 5):
        for j, k in enumerate(["sheet", "cell", "metric", "expected"], 1):
            ws.cell(row=i, column=j, value=r[k]).font = BODY
    ws.freeze_panes = "A5"
    ws.sheet_view.showGridLines = False
    order = [s for s in wb.sheetnames if s != "Verification"]
    order.insert(order.index("National_Benchmarks") + 1, "Verification")
    wb._sheets = [wb[s] for s in order]
    wb.save(path)

    print(f"Verification sheet written with {len(checks)} checks\n")
    print(f"{'sheet':24s} {'cell':6s} {'metric':58s} expected")
    print("-" * 110)
    for c in checks:
        print(f"{c['sheet']:24s} {c['cell']:6s} {c['metric'][:58]:58s} {c['expected']}")


if __name__ == "__main__":
    main(sys.argv[1])
