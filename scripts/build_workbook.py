"""Assemble the reproducible research workbook for the Greater Cincinnati AI labour-market study.

Raw-data sheets hold source values exactly as published. Summary sheets contain live Excel
formulas that reference those raw sheets, so the workbook recalculates if an input changes.

Run: python -I scripts/build_workbook.py <base_dir>
"""
import csv
import os
import statistics as st
import sys

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT = "Arial"
H_FILL = PatternFill("solid", fgColor="1F3864")
H_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(name=FONT, bold=True, size=14, color="1F3864")
SUB_FONT = Font(name=FONT, italic=True, size=9, color="595959")
BODY = Font(name=FONT, size=10)
BOLD = Font(name=FONT, size=10, bold=True)
NOTE_FILL = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def read_csv(base, name):
    with open(os.path.join(base, "data", name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def write_table(ws, rows, headers=None, start=1, numeric_cols=None, widths=None,
                number_formats=None, freeze=True, autofilter=True):
    if not rows:
        return start
    headers = headers or list(rows[0].keys())
    numeric_cols = numeric_cols or set()
    number_formats = number_formats or {}
    for j, h in enumerate(headers, 1):
        c = ws.cell(row=start, column=j, value=h)
        c.font = H_FONT
        c.fill = H_FILL
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BOX
    for i, r in enumerate(rows, start + 1):
        for j, h in enumerate(headers, 1):
            v = r.get(h)
            if h in numeric_cols:
                v = num(v)
            c = ws.cell(row=i, column=j, value=v)
            c.font = BODY
            if h in number_formats:
                c.number_format = number_formats[h]
    ws.row_dimensions[start].height = 30
    for j, h in enumerate(headers, 1):
        w = (widths or {}).get(h)
        if w is None:
            vals = [len(str(r.get(h, "") or "")) for r in rows[:300]]
            w = min(46, max(10, max([len(h)] + vals) + 2))
        ws.column_dimensions[get_column_letter(j)].width = w
    if freeze:
        ws.freeze_panes = ws.cell(row=start + 1, column=1)
    if autofilter:
        ws.auto_filter.ref = f"A{start}:{get_column_letter(len(headers))}{start + len(rows)}"
    return start + len(rows) + 1


def titled(ws, title, subtitle):
    ws["A1"] = title
    ws["A1"].font = TITLE_FONT
    ws["A2"] = subtitle
    ws["A2"].font = SUB_FONT
    ws["A2"].alignment = Alignment(wrap_text=False)
    return 4


def hdr_row(ws, row, labels, widths=None):
    for j, h in enumerate(labels, 1):
        c = ws.cell(row=row, column=j, value=h)
        c.font = H_FONT
        c.fill = H_FILL
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BOX
        if widths and j - 1 < len(widths):
            ws.column_dimensions[get_column_letter(j)].width = widths[j - 1]
    ws.row_dimensions[row].height = 30
    return row + 1


def note(ws, row, text):
    c = ws.cell(row=row, column=1, value=text)
    c.font = SUB_FONT
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
    ws.row_dimensions[row].height = 28
    return row + 2


def main(base):
    wb = openpyxl.Workbook()

    occ = read_csv(base, "cincinnati_occupation_exposure.csv")
    panel = read_csv(base, "oes_may2025_cincinnati_panel.csv")
    qcew = read_csv(base, "qcew_cincinnati_counties.csv")
    ces = read_csv(base, "cincinnati_ces_history.csv")
    laus = read_csv(base, "cincinnati_laus_history.csv")
    proj = read_csv(base, "cincinnati_oh_projections_2022_2032.csv")
    posts = read_csv(base, "job_postings_cincinnati_oct2026.csv")
    pemp = read_csv(base, "job_postings_employers_oct2026.csv")
    bpc = read_csv(base, "bpc_metro_ai_postings.csv")
    emp_ev = read_csv(base, "ai_adoption_employers.csv")
    aei_o = read_csv(base, "aei_state_overall.csv")
    aei_s = read_csv(base, "aei_state_soc_major_groups.csv")

    # Thresholds, quadrants and wage quintiles are defined over DETAILED occupations only;
    # including SOC aggregates would double-count employment.
    nat = [r for r in occ if r["area"] == "National" and r["soc_level"] == "detailed"]
    cin = [r for r in occ if r["area"] == "Cincinnati MSA" and r["soc_level"] == "detailed"]

    def cuts(key, qs=(0.25, 0.5, 0.75)):
        v = sorted(num(r[key]) for r in nat if num(r[key]) is not None)
        return [v[int(len(v) * q)] for q in qs]

    lm_cuts = cuts("aioe_language_modeling")
    lm_med = lm_cuts[1]
    ob_med = st.median([num(r["observed_exposure"]) for r in nat
                        if num(r["observed_exposure"]) is not None])

    OBS_BANDS = ["0.00 no measured overlap", "1 >0.00-0.10", "2 >0.10-0.25",
                 "3 >0.25-0.40", "4 >0.40"]
    LM_BANDS = ["Q1 lowest", "Q2", "Q3", "Q4 highest"]
    QUADS = ["High exposure / high use", "High exposure / low use",
             "Low exposure / high use", "Low exposure / low use"]

    def band_obs(v):
        if v is None:
            return ""
        if v == 0:
            return OBS_BANDS[0]
        if v <= 0.10:
            return OBS_BANDS[1]
        if v <= 0.25:
            return OBS_BANDS[2]
        if v <= 0.40:
            return OBS_BANDS[3]
        return OBS_BANDS[4]

    def band_lm(v):
        if v is None:
            return ""
        return (LM_BANDS[0] if v <= lm_cuts[0] else LM_BANDS[1] if v <= lm_cuts[1]
                else LM_BANDS[2] if v <= lm_cuts[2] else LM_BANDS[3])

    cw = sorted([r for r in cin if num(r["annual_median"]) and num(r["employment"])],
                key=lambda r: num(r["annual_median"]))
    tote = sum(num(r["employment"]) for r in cw)
    cum = 0.0
    wq = {}
    for r in cw:
        e = num(r["employment"])
        cum += e
        wq[(r["area"], r["soc_code"])] = f"Q{min(4, int(5 * (cum - e / 2) / tote)) + 1}"

    for r in occ:
        lmv, obv = num(r["aioe_language_modeling"]), num(r["observed_exposure"])
        r["lm_quartile_national"] = band_lm(lmv)
        r["observed_exposure_band"] = band_obs(obv)
        r["quadrant"] = ""
        if lmv is not None and obv is not None:
            r["quadrant"] = (("High exposure / " if lmv > lm_med else "Low exposure / ")
                             + ("high use" if obv > ob_med else "low use"))
        r["wage_quintile_cincinnati"] = wq.get((r["area"], r["soc_code"]), "")

    # ================= README =================
    ws = wb.active
    ws.title = "README"
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 112
    ws["A1"] = "Greater Cincinnati AI and Labour Market Study - Reproducible Dataset"
    ws["A1"].font = TITLE_FONT
    readme = [
        ("Compiled", "30 October 2026"),
        ("Purpose", "Underlying data for the study of how AI adoption is affecting employment, "
                    "occupational demand and workforce requirements in Greater Cincinnati."),
        ("", ""),
        ("GEOGRAPHY DEFINITIONS", "Three different geographies appear here and they are NOT interchangeable."),
        ("Cincinnati MSA (full)", "Cincinnati, OH-KY-IN Metropolitan Statistical Area. BLS area 17140 / "
                                  "QCEW C1714. Spans Ohio, Kentucky and Indiana. Used for OEWS, CES, LAUS."),
        ("Core 7 counties", "Hamilton, Butler, Clermont, Warren (OH) plus Boone, Kenton, Campbell (KY). "
                            "Used for QCEW so the Ohio and Kentucky portions report separately. NOT the whole MSA."),
        ("ODJFS 'Cincinnati MSA'", "CAUTION. Ohio's projections file is labelled 'Cincinnati Metropolitan "
                                   "Statistical Area' but Ohio LMI states it is identical to the Southwest Ohio "
                                   "JobsOhio region, i.e. OHIO COUNTIES ONLY. Northern Kentucky and Indiana are "
                                   "excluded. Its 2022 base of 907,032 sits well below the 1,101,030 OEWS MSA total."),
        ("", ""),
        ("CRITICAL CAVEATS", ""),
        ("Projected openings", "ODJFS 'annual openings' are projected average annual openings (growth + exits + "
                               "transfers) across 2022-2032. They are NOT current job vacancies."),
        ("Exposure is not displacement", "AIOE and observed-exposure scores measure potential or observed overlap "
                                         "between an occupation's tasks and AI capability. They do not measure job loss."),
        ("State is not metro", "Anthropic Economic Index AI-usage data are published for US states (Ohio, Kentucky), "
                               "not the Cincinnati MSA. Do not present them as Cincinnati figures."),
        ("Postings are not vacancies", "Posting counts measure advertised demand on the platforms sampled. They "
                                       "undercount unadvertised hiring and can double-count one vacancy advertised by "
                                       "several staffing firms. The CareerOneStop total is display-capped at 10,000."),
        ("SOC vintage mismatch", "AIOE is keyed to 2010 SOC; OEWS May 2025 uses 2018 SOC. Matching is on 6-digit code "
                                 "and covers 82.9% of Cincinnati detailed-occupation employment."),
        ("QCEW coverage", "QCEW counts jobs covered by unemployment insurance and excludes most self-employment, so it "
                          "runs below OEWS and CES totals."),
        ("", ""),
        ("FORMULA CELLS", "Summary sheets hold live Excel formulas. They were written "
                          "programmatically and carry no cached values, so Excel computes them the first "
                          "time the workbook is opened; until then some readers show them as blank. The "
                          "Verification sheet lists the same figures recomputed independently in Python so "
                          "the formulas can be checked cell by cell."),
        ("", ""),
        ("SHEET GUIDE", ""),
        ("Sources", "Every dataset with agency, URL, vintage and reference period."),
        ("Summary_*", "Formula-driven tables that recalculate from the raw sheets."),
        ("OEWS_*", "May 2025 occupational employment and wages with AI-exposure measures joined."),
        ("QCEW_Counties", "County industry employment and wages, 2024 and 2025, Ohio vs Kentucky."),
        ("CES_History", "Monthly industry employment for the MSA, 1990 to September 2026."),
        ("LAUS_History", "Monthly labour force and unemployment for the MSA, 1990 to September 2026."),
        ("Projections_OH_Cincinnati", "ODJFS 2022-2032 occupational projections, Ohio portion only."),
        ("JobPostings_*", "Point-in-time posting counts collected 30 October 2026."),
        ("AI_Adoption_Employers", "Evidence on named regional employers, separating documented AI deployment from "
                                  "AI-attributed job cuts."),
        ("AEI_State_*", "Measured AI usage by state from the Anthropic Economic Index."),
        ("National_Benchmarks", "National reference points for comparison."),
        ("Verification", "Summary figures recomputed in Python, with the cell each should match."),
    ]
    r = 3
    for k, v in readme:
        ws.cell(row=r, column=1, value=k).font = BOLD if k else BODY
        c = ws.cell(row=r, column=2, value=v)
        c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if k == "CRITICAL CAVEATS" or k.startswith("ODJFS"):
            ws.cell(row=r, column=1).fill = NOTE_FILL
            c.fill = NOTE_FILL
        ws.row_dimensions[r].height = 30 if v and len(str(v)) > 110 else 15
        r += 1

    # ================= Sources =================
    ws = wb.create_sheet("Sources")
    nxt = titled(ws, "Data sources", "Every figure in the study traces to one of these. Retrieved 30 October 2026.")
    sources = [
        dict(dataset="OEWS - Occupational Employment and Wage Statistics", agency="BLS",
             geography="Cincinnati MSA 17140; Ohio; Kentucky; National", vintage="May 2025",
             period="May 2025 reference period",
             url="https://download.bls.gov/pub/time.series/oe/oe.data.0.Current",
             notes="Flat file. Series ID = OE+U+areatype+area(7)+industry(6)+occupation(6)+datatype(2)."),
        dict(dataset="QCEW - Quarterly Census of Employment and Wages", agency="BLS",
             geography="7 core counties; Cincinnati MSA C1714", vintage="2024 and 2025 annual averages",
             period="Calendar years 2024 and 2025",
             url="https://data.bls.gov/cew/data/api/2025/a/area/39061.csv",
             notes="One file per county FIPS. UI-covered employment only."),
        dict(dataset="CES - State and Metro Area Employment", agency="BLS",
             geography="Cincinnati MSA 17140", vintage="through September 2026 (preliminary)",
             period="Monthly, January 1990 - September 2026",
             url="https://download.bls.gov/pub/time.series/sm/sm.data.36.Ohio",
             notes="52 industry series. Industry detail is not seasonally adjusted."),
        dict(dataset="LAUS - Local Area Unemployment Statistics", agency="BLS",
             geography="Cincinnati MSA 17140", vintage="through September 2026 (preliminary)",
             period="Monthly, January 1990 - September 2026",
             url="https://download.bls.gov/pub/time.series/la/la.data.42.Ohio",
             notes="Not seasonally adjusted."),
        dict(dataset="Long-term occupational projections",
             agency="Ohio Dept. of Job and Family Services, Bureau of LMI",
             geography="Ohio portion of the Cincinnati MSA (= Southwest Ohio JobsOhio region)",
             vintage="Published June 2025", period="2022-2032 horizon; wages May 2023",
             url="https://ohiolmi.com/_docs/PROJ/MSA/LTOP_Cincinnati2032.xlsx",
             notes="EXCLUDES Northern Kentucky and Indiana. Openings are projected, not vacancies."),
        dict(dataset="AIOE - AI Occupational Exposure",
             agency="Felten, Raj & Seamans (2021), Strategic Management Journal 42(12):2195-2217",
             geography="By 6-digit SOC (US)", vintage="2021", period="n/a",
             url="https://github.com/AIOE-Data/AIOE",
             notes="Standardised across occupations (mean 0, sd 1). Theoretical exposure of O*NET abilities to 10 AI applications."),
        dict(dataset="AIOE - Language Modeling and Image Generation variants",
             agency="Felten, Raj & Seamans (2023)", geography="By 6-digit SOC (US)", vintage="2023",
             period="n/a", url="https://github.com/AIOE-Data/AIOE",
             notes="Generative-AI-specific. LM-AIOE is the measure most relevant to large language models."),
        dict(dataset="Anthropic Economic Index - observed job exposure", agency="Anthropic",
             geography="By SOC (US)", vintage="2026", period="n/a",
             url="https://huggingface.co/datasets/Anthropic/EconomicIndex",
             notes="labor_market_impacts/job_exposure.csv. Share of an occupation's tasks observed in actual AI usage, 0-1. CC-BY."),
        dict(dataset="Anthropic Economic Index - state usage metrics", agency="Anthropic",
             geography="US states (Ohio, Kentucky) and national", vintage="Release 2026-06-26",
             period="April and May 2026",
             url="https://huggingface.co/datasets/Anthropic/EconomicIndex",
             notes="Usage index = share of usage divided by share of working-age (15-64) population. 1.0 = proportional. No metro data."),
        dict(dataset="Skills Data Dashboard - AI job postings by metro",
             agency="Bipartisan Policy Center, using Lightcast data",
             geography="50 largest-posting metros incl. Cincinnati OH-KY-IN",
             vintage="Updated 9 October 2026", period="Year to September 2026",
             url="https://bipartisanpolicy.org/skills-data-dashboard/",
             notes="Accessed via a third-party reproduction; the dashboard returned HTTP 403. Treat as secondary."),
        dict(dataset="Job Finder postings census",
             agency="CareerOneStop (US DOL) / National Labor Exchange",
             geography="Cincinnati OH, 25-mile and 5-mile radius", vintage="Retrieved 30 October 2026",
             period="Point in time", url="https://www.careeronestop.org/Toolkit/Jobs/find-jobs.aspx",
             notes="Full-text keyword matching with observable false positives. Total display-capped at 10,000."),
        dict(dataset="Do Job Postings Show Early Labor-Market Effects of AI?",
             agency="Audoly, Guerin & Topa, Federal Reserve Bank of New York", geography="National",
             vintage="14 May 2026", period="2018-2025 quarterly; January 2026 vacancy snapshot",
             url="https://libertystreeteconomics.newyorkfed.org/2026/05/do-job-postings-show-early-labor-market-effects-of-ai/",
             notes="Benchmark: ~40% of US workers in occupations with zero measured exposure; <10% at exposure >=0.4."),
        dict(dataset="AI on the Factory Floor: Evidence from Manufacturing Job Postings",
             agency="Tito, M.D., FEDS Notes, Federal Reserve Board", geography="National",
             vintage="30 September 2026", period="through July 2026",
             url="https://www.federalreserve.gov/econres/notes/feds-notes/ai-on-the-factory-floor-evidence-from-manufacturing-job-postings-20260930.html",
             notes="11% of manufacturing postings require AI skills vs 8% economy-wide. No regional breakdown."),
        dict(dataset="Fifth Third Bancorp FY2025 Annual Report and Form 10-K",
             agency="Fifth Third Bancorp / SEC EDGAR", geography="Company", vintage="FY2025",
             period="Q4 2025 metrics",
             url="https://www.sec.gov/Archives/edgar/data/35527/000003552726000124/a2025annualreport.pdf",
             notes="Primary source for the 30% AI-generated code and 56% daily-usage figures."),
        dict(dataset="Kroger AI strategy release", agency="The Kroger Co.", geography="Company",
             vintage="22 September 2026", period="n/a",
             url="https://ir.kroger.com/news/news-details/2026/Kroger-Details-AI-Strategy-Built-on-Decades-Retail-Expertise-at-GroceryShop-2026/default.aspx",
             notes="Company framing. Pair with October 2026 reporting of the 3,000-role reduction."),
    ]
    write_table(ws, sources, ["dataset", "agency", "geography", "vintage", "period", "url", "notes"],
                start=nxt,
                widths={"dataset": 44, "agency": 36, "geography": 32, "vintage": 24,
                        "period": 30, "url": 54, "notes": 58})

    # ================= OEWS_Occupations (written early so formulas can target it) =======
    wso = wb.create_sheet("OEWS_Occupations")
    nxt_o = titled(wso, "OEWS May 2025 occupational employment and wages with AI-exposure measures",
                   "Cincinnati MSA, Ohio, Kentucky and National. AIOE is standardised (mean 0, sd 1) across "
                   "occupations; observed_exposure runs 0-1. Helper columns drive the summary sheets.")
    ohdr = ["area", "soc_code", "occupation", "soc_level", "employment", "annual_mean",
            "annual_median", "location_quotient", "emp_per_1000", "aioe",
            "aioe_language_modeling", "aioe_image_generation", "lm_quartile_national",
            "observed_exposure_band", "quadrant", "observed_exposure",
            "wage_quintile_cincinnati"]
    write_table(wso, occ, ohdr, start=nxt_o,
                numeric_cols={"employment", "annual_mean", "annual_median", "location_quotient",
                              "emp_per_1000", "aioe", "aioe_language_modeling",
                              "aioe_image_generation", "observed_exposure"},
                number_formats={"employment": "#,##0", "annual_mean": "$#,##0",
                                "annual_median": "$#,##0", "location_quotient": "0.00",
                                "emp_per_1000": "#,##0.0", "aioe": "0.000",
                                "aioe_language_modeling": "0.000",
                                "aioe_image_generation": "0.000", "observed_exposure": "0.000"},
                widths={"occupation": 46, "quadrant": 26, "observed_exposure_band": 22,
                        "lm_quartile_national": 18, "wage_quintile_cincinnati": 18})

    O = "OEWS_Occupations"
    d0 = nxt_o + 1
    d1 = nxt_o + len(occ)
    col = {h: get_column_letter(i) for i, h in enumerate(ohdr, 1)}

    def rng(h):
        return f"{O}!${col[h]}${d0}:${col[h]}${d1}"

    AREA, LVL, EMP = rng("area"), rng("soc_level"), rng("employment")
    MED, LQ, SOC = rng("annual_median"), rng("location_quotient"), rng("soc_code")
    AIOE, LMA, OBS = rng("aioe"), rng("aioe_language_modeling"), rng("observed_exposure")
    OBAND, LMQ, QUAD, WQ = rng("observed_exposure_band"), rng("lm_quartile_national"), rng("quadrant"), rng("wage_quintile_cincinnati")

    # move OEWS sheet after the summaries later via sheet ordering

    # ================= Summary_KeyFindings =================
    ws = wb.create_sheet("Summary_KeyFindings")
    nxt = titled(ws, "Key findings - headline figures",
                 "Column B holds live formulas referencing OEWS_Occupations. Column D gives source and interpretation.")
    for c, w in zip("ABCD", (64, 16, 4, 58)):
        ws.column_dimensions[c].width = w
    nxt = hdr_row(ws, nxt, ["Finding", "Value", "", "Source / interpretation"])
    findings = [
        ("Cincinnati MSA total employment (OEWS, May 2025)",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{LVL},"total")', "#,##0",
         "BLS OEWS May 2025, all occupations"),
        ("Cincinnati MSA median annual wage, all occupations",
         f'=SUMIFS({MED},{AREA},"Cincinnati MSA",{LVL},"total")', "$#,##0",
         "BLS OEWS May 2025"),
        ("Cincinnati MSA mean annual wage, all occupations",
         f'=SUMIFS({rng("annual_mean")},{AREA},"Cincinnati MSA",{LVL},"total")', "$#,##0",
         "Mean exceeds median, as expected in a right-skewed wage distribution"),
        ("Employment in detailed occupations used for the exposure analysis",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{LVL},"detailed")', "#,##0",
         "OEWS detailed occupations with published employment"),
        ("Jobs in occupations with ZERO measured AI task overlap",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{OBAND},"{OBS_BANDS[0]}")', "#,##0",
         "Anthropic observed exposure = 0. NY Fed finds ~40% nationally."),
        ("Jobs in occupations with observed AI overlap above 0.40",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{OBAND},"{OBS_BANDS[4]}")', "#,##0",
         "NY Fed finds <10% of US workers above 0.40"),
        ("Jobs in the top national quartile of generative-AI exposure (LM-AIOE)",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{LMQ},"{LM_BANDS[3]}")', "#,##0",
         "Felten/Raj/Seamans language-modeling AIOE; thresholds set on the national occupation distribution"),
        ("Jobs both highly exposed AND already used with AI",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{QUAD},"{QUADS[0]}")', "#,##0",
         "Quadrant analysis; national medians split each axis"),
        ("Office and administrative support employment (largest major group)",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{SOC},"43-0000")', "#,##0",
         "OEWS major group 43-0000"),
        ("Computer and mathematical occupations employment",
         f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{SOC},"15-0000")', "#,##0",
         "OEWS major group 15-0000"),
        ("Computer and mathematical location quotient",
         f'=SUMIFS({LQ},{AREA},"Cincinnati MSA",{SOC},"15-0000")', "0.00",
         "1.00 = national average. Below 1.00 means the metro is UNDER-represented in computing occupations."),
        ("Production occupations location quotient",
         f'=SUMIFS({LQ},{AREA},"Cincinnati MSA",{SOC},"51-0000")', "0.00",
         "Manufacturing concentration"),
        ("Employment-weighted mean LM-AIOE, Cincinnati MSA",
         f'=SUMPRODUCT(({AREA}="Cincinnati MSA")*({LVL}="detailed")*{EMP}*IF(ISNUMBER({LMA}),{LMA},0))'
         f'/SUMPRODUCT(({AREA}="Cincinnati MSA")*({LVL}="detailed")*{EMP}*ISNUMBER({LMA}))', "0.0000",
         "Generative-AI exposure of the local occupation mix"),
        ("Employment-weighted mean LM-AIOE, National",
         f'=SUMPRODUCT(({AREA}="National")*({LVL}="detailed")*{EMP}*IF(ISNUMBER({LMA}),{LMA},0))'
         f'/SUMPRODUCT(({AREA}="National")*({LVL}="detailed")*{EMP}*ISNUMBER({LMA}))', "0.0000",
         "Comparison point. Cincinnati sits essentially at the national average."),
        ("Employment-weighted mean observed exposure, Cincinnati MSA",
         f'=SUMPRODUCT(({AREA}="Cincinnati MSA")*({LVL}="detailed")*{EMP}*IF(ISNUMBER({OBS}),{OBS},0))'
         f'/SUMPRODUCT(({AREA}="Cincinnati MSA")*({LVL}="detailed")*{EMP}*ISNUMBER({OBS}))', "0.0000",
         "Actual observed AI task overlap, employment-weighted"),
    ]
    for label, formula, fmt, src in findings:
        ws.cell(row=nxt, column=1, value=label).font = BODY
        c = ws.cell(row=nxt, column=2, value=formula)
        c.font = BOLD
        c.number_format = fmt
        s = ws.cell(row=nxt, column=4, value=src)
        s.font = BODY
        s.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[nxt].height = 26
        nxt += 1

    # ================= Summary_Exposure =================
    ws = wb.create_sheet("Summary_Exposure")
    nxt = titled(ws, "Cincinnati MSA employment by AI-exposure band",
                 "All values are live SUMIFS / SUMPRODUCT formulas over OEWS_Occupations.")
    ws.cell(row=nxt, column=1, value="Panel A. Observed AI task exposure (Anthropic Economic Index)").font = BOLD
    nxt += 1
    nxt = hdr_row(ws, nxt, ["Observed exposure band", "Occupations", "Employment",
                            "Share of covered employment", "Employment-weighted median wage"],
                  [30, 14, 14, 16, 18])
    first_a = nxt
    for b in OBS_BANDS:
        ws.cell(row=nxt, column=1, value=b).font = BODY
        ws.cell(row=nxt, column=2,
                value=f'=COUNTIFS({AREA},"Cincinnati MSA",{OBAND},"{b}")').number_format = "#,##0"
        ws.cell(row=nxt, column=3,
                value=f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{OBAND},"{b}")').number_format = "#,##0"
        ws.cell(row=nxt, column=4, value=f"=IFERROR(C{nxt}/$C${first_a + len(OBS_BANDS)},\"\")").number_format = "0.0%"
        ws.cell(row=nxt, column=5, value=(
            f'=IFERROR(SUMPRODUCT(({AREA}="Cincinnati MSA")*({OBAND}="{b}")*{EMP}*IF(ISNUMBER({MED}),{MED},0))'
            f'/SUMPRODUCT(({AREA}="Cincinnati MSA")*({OBAND}="{b}")*{EMP}*ISNUMBER({MED})),"")')).number_format = "$#,##0"
        for j in range(1, 6):
            ws.cell(row=nxt, column=j).font = BODY
        nxt += 1
    ws.cell(row=nxt, column=1, value="Total covered").font = BOLD
    ws.cell(row=nxt, column=2, value=f"=SUM(B{first_a}:B{nxt - 1})").number_format = "#,##0"
    ws.cell(row=nxt, column=3, value=f"=SUM(C{first_a}:C{nxt - 1})").number_format = "#,##0"
    ws.cell(row=nxt, column=4, value=f"=IFERROR(C{nxt}/$C${nxt},\"\")").number_format = "0.0%"
    for j in range(1, 5):
        ws.cell(row=nxt, column=j).font = BOLD
    nxt += 2

    ws.cell(row=nxt, column=1, value="Panel B. Generative-AI exposure quartile (LM-AIOE, national thresholds)").font = BOLD
    nxt += 1
    nxt = hdr_row(ws, nxt, ["LM-AIOE quartile", "Occupations", "Employment",
                            "Share of covered employment", "Employment-weighted median wage"])
    first_b = nxt
    for b in LM_BANDS[::-1]:
        ws.cell(row=nxt, column=1, value=b).font = BODY
        ws.cell(row=nxt, column=2,
                value=f'=COUNTIFS({AREA},"Cincinnati MSA",{LMQ},"{b}")').number_format = "#,##0"
        ws.cell(row=nxt, column=3,
                value=f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{LMQ},"{b}")').number_format = "#,##0"
        ws.cell(row=nxt, column=4, value=f"=IFERROR(C{nxt}/$C${first_b + len(LM_BANDS)},\"\")").number_format = "0.0%"
        ws.cell(row=nxt, column=5, value=(
            f'=IFERROR(SUMPRODUCT(({AREA}="Cincinnati MSA")*({LMQ}="{b}")*{EMP}*IF(ISNUMBER({MED}),{MED},0))'
            f'/SUMPRODUCT(({AREA}="Cincinnati MSA")*({LMQ}="{b}")*{EMP}*ISNUMBER({MED})),"")')).number_format = "$#,##0"
        for j in range(1, 6):
            ws.cell(row=nxt, column=j).font = BODY
        nxt += 1
    ws.cell(row=nxt, column=1, value="Total covered").font = BOLD
    ws.cell(row=nxt, column=2, value=f"=SUM(B{first_b}:B{nxt - 1})").number_format = "#,##0"
    ws.cell(row=nxt, column=3, value=f"=SUM(C{first_b}:C{nxt - 1})").number_format = "#,##0"
    for j in range(1, 4):
        ws.cell(row=nxt, column=j).font = BOLD
    nxt += 2

    ws.cell(row=nxt, column=1, value="Panel C. Exposure versus observed use - four quadrants").font = BOLD
    nxt += 1
    nxt = hdr_row(ws, nxt, ["Quadrant", "Occupations", "Employment",
                            "Share of covered employment", "Employment-weighted median wage"])
    first_c = nxt
    for b in QUADS:
        ws.cell(row=nxt, column=1, value=b).font = BODY
        ws.cell(row=nxt, column=2,
                value=f'=COUNTIFS({AREA},"Cincinnati MSA",{QUAD},"{b}")').number_format = "#,##0"
        ws.cell(row=nxt, column=3,
                value=f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{QUAD},"{b}")').number_format = "#,##0"
        ws.cell(row=nxt, column=4, value=f"=IFERROR(C{nxt}/$C${first_c + len(QUADS)},\"\")").number_format = "0.0%"
        ws.cell(row=nxt, column=5, value=(
            f'=IFERROR(SUMPRODUCT(({AREA}="Cincinnati MSA")*({QUAD}="{b}")*{EMP}*IF(ISNUMBER({MED}),{MED},0))'
            f'/SUMPRODUCT(({AREA}="Cincinnati MSA")*({QUAD}="{b}")*{EMP}*ISNUMBER({MED})),"")')).number_format = "$#,##0"
        for j in range(1, 6):
            ws.cell(row=nxt, column=j).font = BODY
        nxt += 1
    ws.cell(row=nxt, column=1, value="Total covered").font = BOLD
    ws.cell(row=nxt, column=2, value=f"=SUM(B{first_c}:B{nxt - 1})").number_format = "#,##0"
    ws.cell(row=nxt, column=3, value=f"=SUM(C{first_c}:C{nxt - 1})").number_format = "#,##0"
    for j in range(1, 4):
        ws.cell(row=nxt, column=j).font = BOLD
    nxt += 2
    nxt = note(ws, nxt, f"Thresholds, set on the national UNWEIGHTED distribution of occupations so that a band means "
                        f"the same thing in every geography: LM-AIOE quartile cuts {lm_cuts[0]:.4f} / {lm_cuts[1]:.4f} / "
                        f"{lm_cuts[2]:.4f}; quadrant split at the national LM-AIOE median {lm_med:.4f} and observed-exposure "
                        f"median {ob_med:.4f}. 54% of national occupations have observed exposure of exactly zero, which is "
                        f"why observed exposure is reported in fixed bands rather than quartiles.")

    # ================= Summary_WageGradient =================
    ws = wb.create_sheet("Summary_WageGradient")
    nxt = titled(ws, "AI exposure across the Cincinnati wage distribution",
                 "Occupations ranked by median annual wage, then split into five equal-employment quintiles.")
    nxt = hdr_row(ws, nxt, ["Wage quintile", "Employment", "Lowest median wage", "Highest median wage",
                            "Employment-weighted LM-AIOE", "Employment-weighted observed exposure"],
                  [16, 14, 18, 18, 22, 24])
    for q in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        ws.cell(row=nxt, column=1, value=f"{q}{' (lowest paid)' if q == 'Q1' else ' (highest paid)' if q == 'Q5' else ''}").font = BODY
        ws.cell(row=nxt, column=2,
                value=f'=SUMIFS({EMP},{AREA},"Cincinnati MSA",{WQ},"{q}")').number_format = "#,##0"
        ws.cell(row=nxt, column=3,
                value=f'=_xlfn.MINIFS({MED},{AREA},"Cincinnati MSA",{WQ},"{q}")').number_format = "$#,##0"
        ws.cell(row=nxt, column=4,
                value=f'=_xlfn.MAXIFS({MED},{AREA},"Cincinnati MSA",{WQ},"{q}")').number_format = "$#,##0"
        ws.cell(row=nxt, column=5, value=(
            f'=IFERROR(SUMPRODUCT(({AREA}="Cincinnati MSA")*({WQ}="{q}")*{EMP}*IF(ISNUMBER({LMA}),{LMA},0))'
            f'/SUMPRODUCT(({AREA}="Cincinnati MSA")*({WQ}="{q}")*{EMP}*ISNUMBER({LMA})),"")')).number_format = "0.000"
        ws.cell(row=nxt, column=6, value=(
            f'=IFERROR(SUMPRODUCT(({AREA}="Cincinnati MSA")*({WQ}="{q}")*{EMP}*IF(ISNUMBER({OBS}),{OBS},0))'
            f'/SUMPRODUCT(({AREA}="Cincinnati MSA")*({WQ}="{q}")*{EMP}*ISNUMBER({OBS})),"")')).number_format = "0.000"
        for j in range(1, 7):
            ws.cell(row=nxt, column=j).font = BODY
        nxt += 1
    nxt += 1
    nxt = note(ws, nxt, "MINIFS is used rather than MIN(IF(...)) because it avoids array entry. Quintile assignment is "
                        "precomputed in column Q of OEWS_Occupations by cumulative employment share, so each quintile "
                        "holds roughly one fifth of covered Cincinnati employment.")

    # ================= Summary_Geography =================
    ws = wb.create_sheet("Summary_OH_vs_KY")
    nxt = titled(ws, "Ohio portion versus Northern Kentucky portion",
                 "QCEW annual averages for the seven core counties. Formulas reference QCEW_Counties.")
    nxt = hdr_row(ws, nxt, ["Measure", "2024", "2025", "Change", "Percent change"],
                  [44, 16, 16, 14, 14])
    q0 = 5
    q1 = 4 + len(qcew)
    QY = f"QCEW_Counties!$A${q0}:$A${q1}"
    QST = f"QCEW_Counties!$D${q0}:$D${q1}"
    QAG = f"QCEW_Counties!$F${q0}:$F${q1}"
    QEM = f"QCEW_Counties!$K${q0}:$K${q1}"
    QWG = f"QCEW_Counties!$L${q0}:$L${q1}"
    rows_geo = [
        ("Ohio 4-county covered employment", "OH", QEM, "#,##0"),
        ("Northern Kentucky 3-county covered employment", "KY", QEM, "#,##0"),
        ("Ohio 4-county total annual wages ($)", "OH", QWG, "$#,##0"),
        ("Northern Kentucky 3-county total annual wages ($)", "KY", QWG, "$#,##0"),
    ]
    start_geo = nxt
    for label, state, rngcol, fmt in rows_geo:
        ws.cell(row=nxt, column=1, value=label).font = BODY
        for k, yr in enumerate(("2024", "2025")):
            ws.cell(row=nxt, column=2 + k,
                    value=f'=SUMIFS({rngcol},{QY},"{yr}",{QST},"{state}",{QAG},70)').number_format = fmt
        ws.cell(row=nxt, column=4, value=f"=C{nxt}-B{nxt}").number_format = fmt
        ws.cell(row=nxt, column=5, value=f"=IFERROR(C{nxt}/B{nxt}-1,\"\")").number_format = "0.00%"
        for j in range(1, 6):
            ws.cell(row=nxt, column=j).font = BODY
        nxt += 1
    ws.cell(row=nxt, column=1, value="Seven-county total employment").font = BOLD
    ws.cell(row=nxt, column=2, value=f"=B{start_geo}+B{start_geo + 1}").number_format = "#,##0"
    ws.cell(row=nxt, column=3, value=f"=C{start_geo}+C{start_geo + 1}").number_format = "#,##0"
    ws.cell(row=nxt, column=4, value=f"=C{nxt}-B{nxt}").number_format = "#,##0"
    ws.cell(row=nxt, column=5, value=f"=IFERROR(C{nxt}/B{nxt}-1,\"\")").number_format = "0.00%"
    for j in range(1, 6):
        ws.cell(row=nxt, column=j).font = BOLD
    nxt += 1
    ws.cell(row=nxt, column=1, value="Ohio portion average annual pay").font = BODY
    ws.cell(row=nxt, column=2, value=f"=IFERROR(B{start_geo + 2}/B{start_geo},\"\")").number_format = "$#,##0"
    ws.cell(row=nxt, column=3, value=f"=IFERROR(C{start_geo + 2}/C{start_geo},\"\")").number_format = "$#,##0"
    nxt += 1
    ws.cell(row=nxt, column=1, value="Northern Kentucky average annual pay").font = BODY
    ws.cell(row=nxt, column=2, value=f"=IFERROR(B{start_geo + 3}/B{start_geo + 1},\"\")").number_format = "$#,##0"
    ws.cell(row=nxt, column=3, value=f"=IFERROR(C{start_geo + 3}/C{start_geo + 1},\"\")").number_format = "$#,##0"
    nxt += 2
    nxt = note(ws, nxt, "QCEW covers jobs insured for unemployment compensation and excludes most self-employment, so "
                        "these totals run below the OEWS and CES counts for the full 15-county MSA. The seven counties "
                        "here are the region's core, not the entire MSA.")

    # ================= raw sheets =================
    ws = wb.create_sheet("OEWS_MajorGroups")
    nxt = titled(ws, "OEWS May 2025 major occupational groups",
                 "Employment, location quotient and wages for Cincinnati MSA, Ohio, Kentucky and National.")
    majors = [r for r in panel if r["soc_level"] in ("major", "total")]
    write_table(ws, majors,
                ["area", "soc_code", "occupation", "soc_level", "employment", "emp_per_1000",
                 "location_quotient", "annual_mean", "annual_median", "annual_p10", "annual_p90"],
                start=nxt,
                numeric_cols={"employment", "emp_per_1000", "location_quotient", "annual_mean",
                              "annual_median", "annual_p10", "annual_p90"},
                number_formats={"employment": "#,##0", "emp_per_1000": "#,##0.0",
                                "location_quotient": "0.00", "annual_mean": "$#,##0",
                                "annual_median": "$#,##0", "annual_p10": "$#,##0",
                                "annual_p90": "$#,##0"},
                widths={"occupation": 48})

    ws = wb.create_sheet("QCEW_Counties")
    nxt = titled(ws, "QCEW county employment and wages, 2024 and 2025 annual averages",
                 "Seven core Greater Cincinnati counties. agglvl 70 = county total; 71 = by ownership; 74 = private NAICS sector.")
    assert nxt == 4
    write_table(ws, qcew, list(qcew[0].keys()), start=nxt,
                numeric_cols={"establishments", "employment", "total_annual_wages",
                              "avg_weekly_wage", "avg_annual_pay",
                              "location_quotient_employment", "emp_chg_yoy", "emp_pct_chg_yoy",
                              "agglvl_code"},
                number_formats={"establishments": "#,##0", "employment": "#,##0",
                                "total_annual_wages": "$#,##0", "avg_weekly_wage": "$#,##0",
                                "avg_annual_pay": "$#,##0",
                                "location_quotient_employment": "0.00",
                                "emp_chg_yoy": "#,##0", "emp_pct_chg_yoy": "0.0"},
                widths={"industry_title": 44, "portion": 26, "ownership": 22})

    ws = wb.create_sheet("CES_History")
    nxt = titled(ws, "Cincinnati MSA industry employment, monthly 1990 - September 2026",
                 "Thousands of jobs. seasonal U = not seasonally adjusted, S = seasonally adjusted "
                 "(total nonfarm only). September 2026 is preliminary.")
    write_table(ws, ces, ["seasonal", "industry_code", "industry_name", "year", "month",
                          "employment_thousands"], start=nxt,
                numeric_cols={"year", "month", "employment_thousands"},
                number_formats={"employment_thousands": "#,##0.0"},
                widths={"industry_name": 54})

    ws = wb.create_sheet("LAUS_History")
    nxt = titled(ws, "Cincinnati MSA labour force and unemployment, monthly 1990 - September 2026",
                 "Not seasonally adjusted. September 2026 is preliminary.")
    write_table(ws, laus, ["year", "month", "labor_force", "employment", "unemployment",
                           "unemployment_rate"], start=nxt,
                numeric_cols={"year", "month", "labor_force", "employment", "unemployment",
                              "unemployment_rate"},
                number_formats={"labor_force": "#,##0", "employment": "#,##0",
                                "unemployment": "#,##0", "unemployment_rate": "0.0"})

    ws = wb.create_sheet("Projections_OH_Cincinnati")
    nxt = titled(ws, "ODJFS occupational projections 2022-2032 - OHIO PORTION of the Cincinnati MSA only",
                 "Northern Kentucky and Indiana are EXCLUDED. 'open_total' is projected average annual "
                 "openings (growth + exits + transfers), NOT current vacancies.")
    for r in proj:
        soc = r["soc_code"]
        r["exposure_lm_aioe"] = ""
        r["observed_exposure"] = ""
        m = next((c for c in cin if c["soc_code"] == soc), None)
        if m:
            r["exposure_lm_aioe"] = m["aioe_language_modeling"]
            r["observed_exposure"] = m["observed_exposure"]
    write_table(ws, proj, ["soc_code", "occupation", "emp_2022", "emp_2032", "chg", "pct_chg",
                           "open_growth", "open_exits", "open_transfers", "open_total",
                           "exposure_lm_aioe", "observed_exposure", "median_wage_may2023_raw"],
                start=nxt,
                numeric_cols={"emp_2022", "emp_2032", "chg", "pct_chg", "open_growth",
                              "open_exits", "open_transfers", "open_total", "exposure_lm_aioe",
                              "observed_exposure"},
                number_formats={"emp_2022": "#,##0", "emp_2032": "#,##0", "chg": "#,##0",
                                "pct_chg": "0.0%", "open_growth": "#,##0", "open_exits": "#,##0",
                                "open_transfers": "#,##0", "open_total": "#,##0",
                                "exposure_lm_aioe": "0.000", "observed_exposure": "0.000"},
                widths={"occupation": 50})

    ws = wb.create_sheet("JobPostings_Cincinnati")
    nxt = titled(ws, "Job postings matching AI and adjacent terms, Cincinnati, 30 October 2026",
                 "Source: CareerOneStop Job Finder (National Labor Exchange). Point-in-time counts, "
                 "full-text keyword matching. These are advertised postings, NOT vacancies.")
    write_table(ws, posts, list(posts[0].keys()), start=nxt, numeric_cols={"postings"},
                number_formats={"postings": "#,##0"},
                widths={"source": 34, "geography": 28, "query": 30, "notes": 60})

    ws = wb.create_sheet("JobPostings_Employers")
    nxt = titled(ws, "Employers advertising the most AI-related roles in Cincinnati",
                 "Top five advertisers per query, from the CareerOneStop employer facet, 30 October 2026.")
    write_table(ws, pemp, list(pemp[0].keys()), start=nxt, numeric_cols={"rank", "postings"},
                number_formats={"postings": "#,##0"},
                widths={"employer_type": 36, "query": 28})

    ws = wb.create_sheet("BPC_Metro_AI_Postings")
    nxt = titled(ws, "Growth in AI-skill job postings by metro area, year to September 2026",
                 "Bipartisan Policy Center Skills Data Dashboard using Lightcast data, updated 9 October 2026. "
                 "Selected rows from the 50 metros with the most postings.")
    for r in bpc:
        g = num(r["ai_posting_growth_1yr_pct"])
        a = num(r["ai_postings_added"])
        r["implied_base_postings"] = round(a / (g / 100)) if g else ""
        r["implied_current_postings"] = round(a / (g / 100) + a) if g else ""
    write_table(ws, bpc, ["rank", "metro", "ai_posting_growth_1yr_pct", "ai_postings_added",
                          "other_postings_change_pct", "implied_base_postings",
                          "implied_current_postings"], start=nxt,
                numeric_cols={"rank", "ai_posting_growth_1yr_pct", "ai_postings_added",
                              "other_postings_change_pct", "implied_base_postings",
                              "implied_current_postings"},
                number_formats={"ai_postings_added": "#,##0", "implied_base_postings": "#,##0",
                                "implied_current_postings": "#,##0"},
                widths={"metro": 48})
    nxt += len(bpc) + 1
    note(ws, nxt + len(bpc) + 2,
         "implied_base_postings and implied_current_postings are OUR CALCULATION, not published figures: "
         "base = added / growth rate, current = base + added. They assume the published growth rate and the "
         "count added refer to the same universe and period. The dashboard does not publish metro-level totals.")

    ws = wb.create_sheet("AI_Adoption_Employers")
    nxt = titled(ws, "AI adoption among major Greater Cincinnati employers",
                 "Separates documented AI deployment from workforce actions, and records whether the employer "
                 "itself attributed the workforce action to AI.")
    write_table(ws, emp_ev, list(emp_ev[0].keys()), start=nxt,
                widths={"employer": 34, "sector": 26, "cincinnati_role": 40,
                        "ai_deployment_evidence": 60, "quantified_metrics": 54,
                        "workforce_action": 50, "ai_attributed_by_company": 60,
                        "analyst_caveat": 58, "source": 56, "evidence_type": 36,
                        "source_tier": 30})

    ws = wb.create_sheet("AEI_State_Overall")
    nxt = titled(ws, "Measured AI usage by state - Anthropic Economic Index, April and May 2026",
                 "STATE-LEVEL, not Cincinnati. usage_per_capita_index of 1.0 means usage proportional to "
                 "working-age population; for states the comparison is within the United States.")
    write_table(ws, aei_o, ["geography", "geo_id", "geo_level", "month", "metric_id", "value"],
                start=nxt, numeric_cols={"value"}, number_formats={"value": "0.00"},
                widths={"metric_id": 44})

    ws = wb.create_sheet("AEI_State_SOC")
    nxt = titled(ws, "Share of Claude usage by SOC major group and state, April and May 2026",
                 "Percent of the geography's usage falling in each occupational group. STATE-LEVEL, not Cincinnati.")
    write_table(ws, aei_s, ["geography", "geo_id", "month", "node_name", "node_external_id", "value"],
                start=nxt, numeric_cols={"value"}, number_formats={"value": "0.00"},
                widths={"node_name": 50})

    # ================= National_Benchmarks =================
    ws = wb.create_sheet("National_Benchmarks")
    nxt = titled(ws, "National benchmarks for comparison",
                 "Use these to judge whether Cincinnati is ahead of, behind or in line with the nation.")
    bench = [
        dict(measure="Share of US workers in occupations with zero measured AI exposure", value="~40%",
             geography="National", period="January 2026 vacancy snapshot",
             source="NY Fed, Audoly/Guerin/Topa, 14 May 2026",
             cincinnati_comparison="41.4% of covered Cincinnati employment - essentially identical"),
        dict(measure="Share of US workers in occupations with exposure of 0.40 or more", value="<10%",
             geography="National", period="January 2026",
             source="NY Fed, Audoly/Guerin/Topa, 14 May 2026",
             cincinnati_comparison="See Summary_Exposure Panel A, band '4 >0.40'"),
        dict(measure="Share of US online job postings requiring at least one AI skill", value="8%",
             geography="National", period="through July 2026",
             source="Tito, FEDS Notes, 30 September 2026 (Acemoglu et al. method)",
             cincinnati_comparison="Not directly comparable - different AI-skill definition from the BPC/Lightcast series"),
        dict(measure="Share of US manufacturing postings requiring at least one AI skill", value="11%",
             geography="National", period="through July 2026",
             source="Tito, FEDS Notes, 30 September 2026",
             cincinnati_comparison="Relevant to Cincinnati's production location quotient of 1.24"),
        dict(measure="Share of US manufacturing postings requiring generative-AI skills", value="<1%",
             geography="National", period="through July 2026",
             source="Tito, FEDS Notes, 30 September 2026",
             cincinnati_comparison="Generative AI is essentially absent from production-occupation postings"),
        dict(measure="AI-skill wage premium in manufacturing postings", value="~70% above average manufacturing posted wage",
             geography="National", period="sample average",
             source="Tito, FEDS Notes, 30 September 2026",
             cincinnati_comparison="Volatile; based on a small number of AI postings"),
        dict(measure="AI-skill wage premium in production-occupation postings", value="~30% since 2023",
             geography="National", period="2023 onward",
             source="Tito, FEDS Notes, 30 September 2026",
             cincinnati_comparison="Applies to SOC 51-0000, where Cincinnati is over-represented"),
        dict(measure="Share of US online job postings requesting at least one AI skill", value="2.6%",
             geography="National", period="2025",
             source="Stanford AI Index 2026 (Lightcast)",
             cincinnati_comparison="Different definition again; shows how sensitive the share is to method"),
        dict(measure="Anthropic AI Usage Index", value="1.00 = US average",
             geography="US states", period="May 2026",
             source="Anthropic Economic Index, release 2026-06-26",
             cincinnati_comparison="Ohio 0.59, Kentucky 0.39 - both well below the US average"),
        dict(measure="Automation share of AI collaboration patterns", value="49.6% US",
             geography="National and states", period="May 2026",
             source="Anthropic Economic Index, release 2026-06-26",
             cincinnati_comparison="Ohio 50.8%, Kentucky 53.0% - both skew slightly more toward delegation"),
        dict(measure="Growth in US job postings requesting AI skills", value="+111% year to September 2026",
             geography="National", period="September 2025 to September 2026",
             source="Bipartisan Policy Center Skills Data Dashboard (Lightcast)",
             cincinnati_comparison="Cincinnati +159%, 4th fastest of the 50 largest-posting metros"),
    ]
    write_table(ws, bench, ["measure", "value", "geography", "period", "source",
                            "cincinnati_comparison"], start=nxt,
                widths={"measure": 58, "value": 36, "geography": 20, "period": 28,
                        "source": 46, "cincinnati_comparison": 60})

    order = ["README", "Sources", "Summary_KeyFindings", "Summary_Exposure",
             "Summary_WageGradient", "Summary_OH_vs_KY", "National_Benchmarks",
             "OEWS_MajorGroups", "OEWS_Occupations", "QCEW_Counties", "CES_History",
             "LAUS_History", "Projections_OH_Cincinnati", "JobPostings_Cincinnati",
             "JobPostings_Employers", "BPC_Metro_AI_Postings", "AI_Adoption_Employers",
             "AEI_State_Overall", "AEI_State_SOC"]
    wb._sheets = [wb[s] for s in order if s in wb.sheetnames]
    for s in wb.worksheets:
        s.sheet_view.showGridLines = False

    os.makedirs(os.path.join(base, "output"), exist_ok=True)
    out = os.path.join(base, "output", "Cincinnati_AI_Labor_Market_Dataset.xlsx")
    wb.save(out)
    print("saved", out)
    print("sheets:", len(wb.sheetnames))


if __name__ == "__main__":
    main(sys.argv[1])
