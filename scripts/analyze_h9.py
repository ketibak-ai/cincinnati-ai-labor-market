"""H9: re-test of 1.0's "slow growth" claim, three parts.

(a) Comparator. Total nonfarm, September 2024 to September 2026, same-month, not seasonally
    adjusted, for Cincinnati, each P1 peer and the US. "Slow" only if Cincinnati is in the
    bottom quartile of P1.
(b) The 98% replacement share. Growth share of projected annual openings for Cincinnati's
    ODJFS file against the other seven Ohio MSA files of the same vintage, Ohio statewide and
    the BLS national projections. If Cincinnati is within one percentage point of the
    Ohio-MSA median, the share is a feature of the projection method.
(c) Labor force. ACS 1-year, Cincinnati MSA (table B23001): change in the civilian labor
    force aged 16+ split into population size, age mix and participation. Population by age
    is from Census Vintage 2025 county estimates summed to the 15 counties; participation
    rates by age are from ACS. Shown on its own window (2024 to 2025; 2023 to 2025 beside it)
    and never spliced onto the monthly LAUS series.

Outputs: data/h9_growth_peers.csv, data/h9_projection_growth_share.csv,
         data/h9_labor_force_decomposition.csv, output/h9_trace.txt
"""
import os

import numpy as np
import openpyxl
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
CIN = 17140
peers = pd.read_csv(P("data", "peer_sets.csv"))
nm = dict(zip(peers.CBSA, peers.short)); nm[0] = "United States"

# ---------- (a)
d = pd.read_csv(P("data", "ces_total_nonfarm_peers.csv"))
a = d[(d.year == 2024) & (d.month == 9)].set_index("cbsa").value_thousands
b = d[(d.year == 2026) & (d.month == 9)].set_index("cbsa").value_thousands
G = pd.DataFrame({"sep_2024_thousands": a, "sep_2026_thousands": b})
G["change_thousands"] = (G.sep_2026_thousands - G.sep_2024_thousands).round(1)
G["growth_pct"] = (G.sep_2026_thousands / G.sep_2024_thousands - 1) * 100
G["area"] = G.index.map(nm)
G = G.sort_values("growth_pct").reset_index()
G.to_csv(P("data", "h9_growth_peers.csv"), index=False)
pg = G[~G.cbsa.isin([0, CIN])].growth_pct
cin_g = float(G.loc[G.cbsa == CIN, "growth_pct"].iloc[0])

# ---------- (b)
rows = []
for n in ["Cincinnati", "Akron", "Canton", "Cleveland", "Columbus", "Dayton", "Toledo", "Youngstown"]:
    wb = openpyxl.load_workbook(P("raw", "proj", f"LTOP_{n}2032.xlsx"), read_only=True, data_only=True)
    for row in wb["Occupational Detail"].iter_rows(min_row=5, values_only=True):
        if row[0] == "00-0000":
            rows.append(dict(area=f"{n} (ODJFS MSA file, Ohio counties)", source="ODJFS 2022-2032", base_emp=row[2],
                             growth_openings=row[6], exits=row[7], transfers=row[8], total_openings=row[9]))
            break
wb = openpyxl.load_workbook(P("raw", "proj", "OccOH32.xlsx"), read_only=True, data_only=True)
for row in wb["Occupational Detail"].iter_rows(min_row=3, values_only=True):
    if row[0] == "00-0000":
        rows.append(dict(area="Ohio", source="ODJFS 2022-2032", base_emp=row[2], growth_openings=row[6],
                         exits=row[7], transfers=row[8], total_openings=row[9]))
        break
wb = openpyxl.load_workbook(P("raw", "proj", "bls_occupation_2024_34.xlsx"), read_only=True, data_only=True)
t110 = [r for r in wb["Table 1.10"].iter_rows(values_only=True) if r[1] == "00-0000"][0]
t12 = [r for r in wb["Table 1.2"].iter_rows(values_only=True) if r[1] == "00-0000"][0]
rows.append(dict(area="United States", source="BLS 2025-2035", base_emp=t110[3] * 1000, growth_openings=t110[5] * 100,
                 exits=t110[10] * 1000, transfers=t110[11] * 1000, total_openings=t12[10] * 1000))
S = pd.DataFrame(rows)
S["growth_share_pct"] = S.growth_openings / S.total_openings * 100
S["replacement_share_pct"] = 100 - S.growth_share_pct
S.to_csv(P("data", "h9_projection_growth_share.csv"), index=False)
oh = S[S.area.str.contains("ODJFS MSA")]
cin_share = float(oh.loc[oh.area.str.startswith("Cincinnati"), "growth_share_pct"].iloc[0])
med = float(oh[~oh.area.str.startswith("Cincinnati")].growth_share_pct.median())
med_all = float(oh.growth_share_pct.median())

# ---------- (c)
# B23001: sex by age by employment status, population 16+. For each sex and age group the
# table gives total and "in labor force". Column offsets below follow the Census table shell.
AGES = ["16-19", "20-21", "22-24", "25-29", "30-34", "35-44", "45-54", "55-59", "60-61", "62-64", "65-69", "70-74", "75+"]
TOT_M = [3, 10, 17, 24, 31, 38, 45, 52, 59, 66, 73, 78, 83]
TOT_F = [89, 96, 103, 110, 117, 124, 131, 138, 145, 152, 159, 164, 169]
BROAD = {"16-19": "16-19", "20-21": "20-24", "22-24": "20-24", "25-29": "25-34", "30-34": "25-34", "35-44": "35-44",
         "45-54": "45-54", "55-59": "55-64", "60-61": "55-64", "62-64": "55-64", "65-69": "65+", "70-74": "65+", "75+": "65+"}


def acs(year):
    f = P("raw", "acs", f"acsdt1y{year}-b23001.dat")
    head = open(f, encoding="utf-8").readline().strip().split("|")
    for line in open(f, encoding="utf-8"):
        if line.startswith("310M") and "US17140|" in line:
            v = dict(zip(head, line.strip().split("|")))
            break
    e = lambda k: float(v[f"B23001_E{k:03d}"])
    pop, lf = {}, {}
    for age, m, fe in zip(AGES, TOT_M, TOT_F):
        g = BROAD[age]
        pop[g] = pop.get(g, 0) + e(m) + e(fe)
        lf[g] = lf.get(g, 0) + e(m + 1) + e(fe + 1)     # "In labor force" follows each age total
    return pd.Series(pop), pd.Series(lf), e(1)

cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
fips = set(cty.loc[cty.CBSA == CIN, "STCOU"])
cc = pd.read_csv(P("raw", "census", "cc-est2025-agesex-all.csv"), encoding="latin-1", dtype={"STATE": str, "COUNTY": str})
cc["fips"] = cc.STATE.str.zfill(2) + cc.COUNTY.str.zfill(3)
cc = cc[cc.fips.isin(fips)]
assert cc.fips.nunique() == 15


def census_pop(year):
    yr = {2020: 2, 2021: 3, 2022: 4, 2023: 5, 2024: 6, 2025: 7}[year]     # YEAR code: 2 = 7/1/2020 ... 7 = 7/1/2025
    s = cc[cc.YEAR == yr].sum(numeric_only=True)
    g = {"20-24": s.AGE2024_TOT, "25-34": s.AGE2529_TOT + s.AGE3034_TOT, "35-44": s.AGE3539_TOT + s.AGE4044_TOT,
         "45-54": s.AGE4549_TOT + s.AGE5054_TOT, "55-64": s.AGE5559_TOT + s.AGE6064_TOT, "65+": s.AGE65PLUS_TOT}
    g["16-19"] = s.AGE16PLUS_TOT - sum(g.values())
    return pd.Series(g), s.POPESTIMATE

dec = []
for y0, y1 in ((2024, 2025), (2023, 2025)):
    p0a, l0, _ = acs(y0); p1a, l1, _ = acs(y1)
    r0, r1 = l0 / p0a, l1 / p1a
    P0, tot0 = census_pop(y0); P1, tot1 = census_pop(y1)
    idx = r0.index
    lf0, lf1 = (P0[idx] * r0).sum(), (P1[idx] * r1).sum()
    size = (P1[idx].sum() / P0[idx].sum() - 1) * lf0                       # 16+ population growth at fixed age mix and rates
    ageing = (P1[idx] * r0).sum() - lf0 - size                              # change in age mix at base-year rates
    particip = (P1[idx] * (r1 - r0)).sum()                                  # change in rates at end-year population
    dec.append(dict(window=f"{y0}-{y1}", lf_start=lf0, lf_end=lf1, change=lf1 - lf0, population_size=size,
                    age_mix=ageing, participation=particip,
                    pop16_start=P0[idx].sum(), pop16_end=P1[idx].sum(), pop65_share_start=P0["65+"] / P0[idx].sum(),
                    pop65_share_end=P1["65+"] / P1[idx].sum(), lfpr_start=lf0 / P0[idx].sum(), lfpr_end=lf1 / P1[idx].sum(),
                    acs_lf_start=l0.sum(), acs_lf_end=l1.sum(),
                    **{f"lfpr_{g}_start": r0[g] for g in idx}, **{f"lfpr_{g}_end": r1[g] for g in idx}))
D = pd.DataFrame(dec)
D.to_csv(P("data", "h9_labor_force_decomposition.csv"), index=False)

with open(P("output", "h9_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a)
        print(*a, file=fh)

    w("(a) Total nonfarm, Sept 2024 -> Sept 2026 (NSA; Sept 2026 preliminary)")
    w(G[["area", "sep_2024_thousands", "sep_2026_thousands", "change_thousands", "growth_pct"]].round(2).to_string(index=False))
    w(f"P1 q25 {pg.quantile(.25):+.3f}%  median {pg.median():+.3f}%  q75 {pg.quantile(.75):+.3f}% | Cincinnati {cin_g:+.3f}% "
      f"| rank {int((pg > cin_g).sum()) + 1} of 20 (1 = fastest) | bottom quartile: {bool(cin_g < pg.quantile(.25))}")
    w("\n(b) Growth share of projected annual openings")
    w(S[["area", "source", "base_emp", "growth_openings", "total_openings", "growth_share_pct", "replacement_share_pct"]].round(2).to_string(index=False))
    w(f"Cincinnati {cin_share:.2f}% | median of the other seven Ohio MSA files {med:.2f}% | difference {cin_share - med:+.2f} points "
      f"| within one point: {bool(abs(cin_share - med) <= 1)} | median of all eight {med_all:.2f}%")
    w("\n(c) Labor force decomposition, Cincinnati MSA (Census population by age x ACS participation by age)")
    w(D[["window", "lf_start", "lf_end", "change", "population_size", "age_mix", "participation", "lfpr_start", "lfpr_end",
         "pop65_share_start", "pop65_share_end", "acs_lf_start", "acs_lf_end"]].round(4).to_string(index=False))
    w("Participation by age (start -> end):")
    for _, r in D.iterrows():
        w(" ", r.window, {g: (round(r[f'lfpr_{g}_start'], 3), round(r[f'lfpr_{g}_end'], 3)) for g in ["16-19", "20-24", "25-34", "35-44", "45-54", "55-64", "65+"]})
