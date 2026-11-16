"""Build the 2.1 dataset workbook: output/Cincinnati_AI_Labor_Market_2.1_Dataset.xlsx
(also copied to docs/ for the site). The 1.0 workbook is left exactly as published.

One sheet per 2.1 data table, a README sheet that lists them, a key-findings sheet, and the
industry sheet with BOTH baselines, 2024 first (the author's decision at the check-in).
"""
import os
import shutil

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("output", "Cincinnati_AI_Labor_Market_2.1_Dataset.xlsx")

SHEETS = [  # (sheet name, data file, what it holds, source type)
    ("Peer_Sets", "peer_sets.csv", "The three pre-registered peer sets (P1 Chamber, P2 population, P3 industry structure)", "Government; advocacy (P1 list)"),
    ("H1_Hiring_Test", "h1_ddd.csv", "Entry-door test for every metro, outcome, age group and exposure measure", "Government (Census QWI)"),
    ("H1_Rate_Checks", "h1_rate_checks.csv", "Interest-rate checks: result without information, finance and real estate; placebo industries", "Government (Census QWI)"),
    ("H1_Event_Time", "h1_event_time.csv", "Yearly gap relative to 2018-19, by metro and measure", "Government (Census QWI)"),
    ("H1_Hires_By_Age", "h1_hires_by_age_group_cincinnati.csv", "Greater Cincinnati new hires by age and industry exposure group, 2018-19 and 2023-25", "Government (Census QWI)"),
    ("H2b_ACS_Occupations", "h2b_acs.csv", "Occupation-based version of the test from ACS microdata, with standard errors", "Government (ACS PUMS)"),
    ("H3_New_Hire_Earnings", "h3_earnings.csv", "Earnings of new stable hires, young against experienced", "Government (Census QWI)"),
    ("H4_Exposure_Peers", "h4_exposure_peers.csv", "Employment-weighted AI exposure on four measures, every metro and the US", "Government; academic; industry"),
    ("H4_Exposure_Bands", "h4_bands.csv", "Share of employment above three observed-exposure cut points", "Government; industry"),
    ("H10_Wage_Gradient", "h10_wage_gradient.csv", "Exposure in the top and bottom wage fifths", "Government; academic; industry"),
    ("Industry_Exposure", "industry_exposure_naics3.csv", "Exposure and group of each 3-digit industry, from 2022 national staffing patterns", "Government; academic; industry"),
    ("H5_BTOS_AI_Use", "btos_ai_use.csv", "Business AI use: nation, states and the 25 published metros (no Cincinnati estimate exists)", "Government (Census BTOS)"),
    ("H5_Annual_Reports", "h5_10k_ai_mentions.csv", "Annual reports of nine Cincinnati-based companies that mention artificial intelligence", "Government (SEC EDGAR)"),
    ("H6_Shift_Share", "h6_shift_share.csv", "Computing jobs: actual, expected from industry mix, and the two-part gap", "Government (OEWS, QCEW)"),
    ("H6_AI_Patents", "h6_ai_patents.csv", "AI patents 2019-23 by inventor metro", "Government (USPTO)"),
    ("H6_Computing_RD", "h6_herd_computing_rd.csv", "University R&D in computer and information sciences, FY2024", "Government (NSF HERD)"),
    ("H6_Computing_Awards", "h6_ipeds_completions.csv", "Computing and data degrees and certificates, 2023-24", "Government (IPEDS)"),
    ("H7_Output_Per_Worker", "h7_output_per_worker.csv", "Real GDP per worker, exposed sectors and the rest, by metro and year", "Government (BEA, QCEW)"),
    ("H7_Growth_Table", "h7_growth_table.csv", "Change in output per worker 2019-22 and 2022-24", "Government (BEA, QCEW)"),
    ("H8_DataCenter_Evidence", "h8_data_center_evidence.csv", "Every data-center figure used, with its definition and source type", "Mixed: each row labelled"),
    ("H8_DataCenter_Jobs", "h8_qcew_518210_counties.csv", "Data-processing and hosting employment by county, Cincinnati and Columbus", "Government (QCEW)"),
    ("H9_Growth_Peers", "h9_growth_peers.csv", "Total nonfarm employment, Sept 2024 and Sept 2026", "Government (BLS CES)"),
    ("H9_Projections", "h9_projection_growth_share.csv", "Growth share of projected openings: Ohio metros, Ohio, US", "Government (ODJFS, BLS) - model output"),
    ("H9_Labor_Force", "h9_labor_force_decomposition.csv", "Labor-force change split into population, age mix and participation", "Government (ACS, Census)"),
    ("Awareness_20_Metros", "awareness_like_for_like.csv", "Three like-for-like awareness measures and postings naming AI tools", "Private platform; organizer-reported; government (postings)"),
    ("Awareness_Listings", "l1_platform_events.csv", "Every event kept by the platform search, 20 metros", "Private platform"),
    ("Awareness_Chapters", "l2_chapter_meetings.csv", "Chapter meetings in the last 12 months", "Organizer-reported"),
    ("AI_Events_Cincinnati", "ai_events.csv", "The Cincinnati event census, Dec 2023 - Nov 2026", "Organizer-reported; private platform"),
    ("AI_Community_Groups", "ai_community_groups.csv", "Stated membership, as attributed text", "Organizer-reported"),
    ("AI_Attendance_Claims", "ai_event_attendance_claims.csv", "Attendance claims, each with who reported it; never summed", "Organizer-reported; journalism"),
    ("AI_Agent_Register", "ai_agent_register.csv", "What large employers say they do with AI and AI agents, source graded", "Company records; journalism"),
    ("AI_Agent_No_Statement", "ai_agent_register_no_disclosure.csv", "Large employers with no statement found (not evidence of no use)", "-"),
]
KEY = [
    ("Entry-door test, Cincinnati (four measures)", "+0.010, +0.014, +0.029, -0.044", "log points; inside the chance range on all four", "H1_Hiring_Test"),
    ("Entry-door test, median of Chamber peers", "-0.022, -0.077, -0.056, -0.161", "log points", "H1_Hiring_Test"),
    ("New hires of ages 22-24, most / middle / least exposed industries", "-8.9% / -16.1% / -11.3%", "2023-25 against 2018-19", "H1_Hires_By_Age"),
    ("Language-model exposure, Cincinnati and US", "0.079 and 0.095", "standard-deviation units", "H4_Exposure_Peers"),
    ("Businesses using AI: OH, KY, IN, US", "22.2%, 23.2%, 20.2%, 23.7%", "mean of six periods to 18 Oct 2026; no metro figure exists", "H5_BTOS_AI_Use"),
    ("Annual reports naming AI (of nine companies)", "1, 2, 1, 4, 8, 9", "fiscal years 2020 to 2025", "H5_Annual_Reports"),
    ("Computing-jobs gap", "-4,906 = -2,839 industry mix + -2,066 within industry", "jobs", "H6_Shift_Share"),
    ("AI patents per 100,000 residents", "44.3 (rank 16 of 20)", "2019-23", "H6_AI_Patents"),
    ("University computing R&D per resident", "$2.80 (rank 14 of 20)", "FY2024", "H6_Computing_RD"),
    ("Computing and data awards per 100,000 residents", "130 (rank 8 of 20)", "2023-24", "H6_Computing_Awards"),
    ("Output per worker, exposed sectors, 2022-24", "+2.35% (US +5.44%)", "real GDP per private worker", "H7_Growth_Table"),
    ("Data-center industry jobs, six published counties", "1,576 to 1,977 (+401)", "2022 to 2025", "H8_DataCenter_Jobs"),
    ("Data-center load under contract, Duke Energy Ohio", "250 MW (a further 1,080 MW not under contract)", "filed 29 Sept 2026", "H8_DataCenter_Evidence"),
    ("Trenton project commitment", "120 jobs for 250 MW (0.48 per MW)", "developer's estimate in the abatement agreement", "H8_DataCenter_Evidence"),
    ("Job growth, Sept 2024 - Sept 2026", "+0.735% (US +0.723%; rank 10 of 20)", "total nonfarm", "H9_Growth_Peers"),
    ("Growth share of projected openings", "Cincinnati 2.05%; other Ohio metros -1.3% to 3.7%; US 3.39%", "model output", "H9_Projections"),
    ("AI events listed, per 100,000 adults", "0.36 (rank 15 of 20)", "next 60 days from 14 Nov 2026", "Awareness_20_Metros"),
    ("Chapter meetings, per 100,000 adults", "0.07 (rank 10 of 20)", "last 12 months; one national organization", "Awareness_20_Metros"),
    ("Search interest index", "30.7 (rank 17 of 20)", "three terms, last 12 months", "Awareness_20_Metros"),
    ("CincyAI for Humans meetings", "35 held of 36 scheduled", "Dec 2023 - 14 Nov 2026", "AI_Events_Cincinnati"),
    ("Employers with an AI system in production on the record", "8", "read, grade 1-2 sources", "AI_Agent_Register"),
    ("Employers with a verified AI agent in production", "1 (a vendor)", "the three-employer rule is not met", "AI_Agent_Register"),
]


def style(ws, widths=None):
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A5F")
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    for i, col in enumerate(ws.columns, 1):
        w = widths[i - 1] if widths and i <= len(widths) else min(46, max(10, max(len(str(c.value)) if c.value is not None else 0 for c in col[:60]) + 2))
        ws.column_dimensions[get_column_letter(i)].width = w

with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    readme = pd.DataFrame([("README", "This sheet", "-", "-"), ("Key_Findings_2_1", "The headline numbers and the sheet each comes from", "-", "-"),
                           ("Industry_Both_Baselines", "Industry employment with the 2024 baseline first and the 2019 baseline beside it", "Government (BLS CES)", "-")] +
                          [(n, d, s, f) for n, f, d, s in SHEETS], columns=["Sheet", "What it holds", "Source type", "Data file in data/"])
    top = pd.DataFrame([["Cincinnati AI Labor Market 2.1 - dataset workbook"], ["Built 16 November 2026 by scripts/build_workbook_2_1.py from the files in data/."],
                        ["Every figure is covered by tests/test_study_2_1.py. The 1.0 workbook is separate and unchanged."],
                        ["Greater Cincinnati = Cincinnati, OH-KY-IN MSA (CBSA 17140), 15 counties, unless a sheet says otherwise."], [""]])
    top.to_excel(xw, sheet_name="README", index=False, header=False)
    readme.to_excel(xw, sheet_name="README", index=False, startrow=6)
    pd.DataFrame(KEY, columns=["Finding", "Value", "Unit or note", "Sheet"]).to_excel(xw, sheet_name="Key_Findings_2_1", index=False)
    ind = pd.read_csv(P("data", "cincinnati_rebased_2024.csv"))
    ind["jobs_change_from_2019_thousands"] = (ind.sep_2026 - ind.sep_2019).round(1)
    ind = ind[["industry", "sep_2024", "sep_2026", "jobs_change_from_2024_thousands", "pct_change_from_2024", "sep_2019",
               "jobs_change_from_2019_thousands", "pct_change_from_2019"]].sort_values("pct_change_from_2024")
    ind.columns = ["Industry", "Sept 2024 (thousands)", "Sept 2026 (thousands)", "Change from 2024 (thousands)", "Change from 2024 (%)",
                   "Sept 2019 (thousands)", "Change from 2019 (thousands)", "Change from 2019 (%)"]
    ind.to_excel(xw, sheet_name="Industry_Both_Baselines", index=False)
    for name, f, _, _ in SHEETS:
        d = pd.read_csv(P("data", f))
        if name == "H5_BTOS_AI_Use":
            d = d[d.area.isin(["United States", "OH", "KY", "IN"]) | (d.geo == "MSA")]
        d.to_excel(xw, sheet_name=name[:31], index=False)
    wb = xw.book
    ws = wb["README"]; ws["A1"].font = Font(bold=True, size=14)
    for c in ws[7]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A5F")
    for col, w in zip("ABCD", (26, 92, 44, 44)):
        ws.column_dimensions[col].width = w
    style(wb["Key_Findings_2_1"], [58, 56, 54, 26])
    style(wb["Industry_Both_Baselines"], [58, 16, 16, 16, 14, 16, 16, 14])
    for name, *_ in SHEETS:
        style(wb[name[:31]])
shutil.copyfile(OUT, P("docs", "Cincinnati_AI_Labor_Market_2.1_Dataset.xlsx"))
import openpyxl
wb = openpyxl.load_workbook(OUT, read_only=True)
print(len(wb.sheetnames), "sheets;", os.path.getsize(OUT) // 1024, "KB")
