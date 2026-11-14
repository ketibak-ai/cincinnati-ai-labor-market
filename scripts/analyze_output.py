"""H7 (descriptive only): real output per worker in AI-exposed sectors against the rest.

BEA stopped publishing metro-area GDP in February 2026, so the metro is built from its
counties: BEA CAGDP9 (real GDP by county and industry, thousands of chained 2017 dollars)
divided by QCEW private employment in the same sectors and counties.

Exposed sectors: information (51), finance and insurance (52), professional, scientific and
technical services (54), management of companies (55). Comparison: all other private industry.

A county enters a metro's figures only if all four sector values and the private total are
published by both BEA and QCEW in every year used (2019, 2022, 2023, 2024). The share of the
metro's private employment that survives is reported. Chained-dollar values are not strictly
additive across counties or sectors, so sums are approximations. No attribution is attempted.

Outputs: data/h7_output_per_worker.csv, output/h7_trace.txt
"""
import io
import os
import zipfile

import numpy as np
import pandas as pd
import requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
YEARS = [2019, 2022, 2023, 2024]
LINES = {"45": "51", "51": "52", "60": "54", "64": "55", "2": "private"}
EXP = ["51", "52", "54", "55"]
CIN = 17140

peers = pd.read_csv(P("data", "peer_sets.csv"))
metros = [CIN] + list(peers[peers.p1].CBSA)
cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
cty = cty[cty.CBSA.isin(metros)]

z = zipfile.ZipFile(P("raw", "bea", "CAGDP9.zip"))
name = [n for n in z.namelist() if "ALL_AREAS" in n][0]
bea = pd.read_csv(io.BytesIO(z.read(name)), encoding="latin-1", dtype=str)
bea["fips"] = bea.GeoFIPS.str.replace('"', "").str.strip()
bea["LineCode"] = bea.LineCode.str.strip()
bea = bea[bea.LineCode.isin(LINES) & (bea.fips.isin(set(cty.STCOU)) | (bea.fips == "00000"))]
bea["sector"] = bea.LineCode.map(LINES)
g = bea.melt(id_vars=["fips", "sector"], value_vars=[str(y) for y in YEARS], var_name="year", value_name="gdp")
g["gdp"] = pd.to_numeric(g.gdp, errors="coerce")          # (D) suppressed and (NA) become missing
g["year"] = g.year.astype(int)


def qcew(fips, year):
    f = P("raw", "qcew_county", f"{year}_{fips}.csv")
    if not os.path.exists(f):
        r = requests.get(f"https://data.bls.gov/cew/data/api/{year}/a/area/{fips}.csv", timeout=120)
        r.raise_for_status()
        open(f, "wb").write(r.content)
    d = pd.read_csv(f, dtype={"industry_code": str, "disclosure_code": str})
    d = d[(d.own_code == 5) & (d.disclosure_code.fillna("") != "N")]
    lvl_tot, lvl_sec = (11, 14) if fips == "US000" else (71, 74)
    out = {"private": float(d.loc[d.agglvl_code == lvl_tot, "annual_avg_emplvl"].sum()) or np.nan}
    s = d[d.agglvl_code == lvl_sec].set_index("industry_code").annual_avg_emplvl
    for k in EXP:
        out[k] = float(s[k]) if k in s.index else np.nan
    return out

rows = []
for fips in sorted(set(cty.STCOU)) + ["US000"]:
    for y in YEARS:
        e = qcew(fips, y)
        for k, v in e.items():
            rows.append(dict(fips="00000" if fips == "US000" else fips, year=y, sector=k, emp=v))
e = pd.DataFrame(rows)
d = g.merge(e, on=["fips", "year", "sector"], how="outer")
ok = d.groupby("fips").apply(lambda x: x.gdp.notna().all() and x.emp.notna().all() and len(x) == len(YEARS) * 5, include_groups=False)
d = d[d.fips.isin(ok[ok].index)]
cmap = dict(zip(cty.STCOU, cty.CBSA)); cmap["00000"] = 0
d["cbsa"] = d.fips.map(cmap)
emp_all = e[(e.sector == "private") & (e.year == 2024)].assign(cbsa=lambda x: x.fips.map(cmap)).groupby("cbsa").emp.sum()

m = d.groupby(["cbsa", "year", "sector"])[["gdp", "emp"]].sum().unstack("sector")
res = []
for (cb, y), r in m.iterrows():
    ge, ee = sum(r[("gdp", k)] for k in EXP), sum(r[("emp", k)] for k in EXP)
    go, eo = r[("gdp", "private")] - ge, r[("emp", "private")] - ee
    res.append(dict(cbsa=cb, year=y, exposed_gdp_per_worker=ge * 1000 / ee, other_gdp_per_worker=go * 1000 / eo,
                    exposed_emp=ee, other_emp=eo,
                    coverage=r[("emp", "private")] / emp_all[cb] if y == 2024 else np.nan,
                    **{f"gdp_per_worker_{k}": r[("gdp", k)] * 1000 / r[("emp", k)] for k in EXP}))
R = pd.DataFrame(res)
nm = dict(zip(peers.CBSA, peers.short)); nm[0] = "United States"; nm[CIN] = "Cincinnati"
R["area"] = R.cbsa.map(nm)
R.to_csv(P("data", "h7_output_per_worker.csv"), index=False)

W = R.pivot(index="area", columns="year", values=["exposed_gdp_per_worker", "other_gdp_per_worker"])
T = pd.DataFrame({
    "exposed_2019_22": (W[("exposed_gdp_per_worker", 2022)] / W[("exposed_gdp_per_worker", 2019)] - 1) * 100,
    "exposed_2022_24": (W[("exposed_gdp_per_worker", 2024)] / W[("exposed_gdp_per_worker", 2022)] - 1) * 100,
    "other_2019_22": (W[("other_gdp_per_worker", 2022)] / W[("other_gdp_per_worker", 2019)] - 1) * 100,
    "other_2022_24": (W[("other_gdp_per_worker", 2024)] / W[("other_gdp_per_worker", 2022)] - 1) * 100})
T["gap_2022_24"] = T.exposed_2022_24 - T.other_2022_24
T["coverage_2024"] = R[R.year == 2024].set_index("area").coverage
T.to_csv(P("data", "h7_growth_table.csv"))

with open(P("output", "h7_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a)
        print(*a, file=fh)

    w("Real GDP per private-sector worker (chained 2017 dollars), Cincinnati MSA (county build):")
    w(R[R.cbsa == CIN][["year", "exposed_gdp_per_worker", "other_gdp_per_worker", "exposed_emp", "other_emp",
                        "gdp_per_worker_51", "gdp_per_worker_52", "gdp_per_worker_54", "gdp_per_worker_55"]].round(0).to_string(index=False))
    w("\nPercent change in real GDP per worker; gap = exposed minus other, 2022-24; coverage = share of 2024 private employment in counties used")
    w(T.sort_values("gap_2022_24").round(2).to_string())
    p = T.drop(index=["Cincinnati", "United States"])
    c = T.loc["Cincinnati"]
    w(f"\nCincinnati exposed-sector growth 2022-24: {c.exposed_2022_24:+.2f}% | P1 q25 {p.exposed_2022_24.quantile(.25):+.2f} "
      f"median {p.exposed_2022_24.median():+.2f} q75 {p.exposed_2022_24.quantile(.75):+.2f} | US {T.loc['United States'].exposed_2022_24:+.2f}")
    w(f"Cincinnati gap 2022-24: {c.gap_2022_24:+.2f} points | P1 q25 {p.gap_2022_24.quantile(.25):+.2f} median {p.gap_2022_24.median():+.2f} "
      f"q75 {p.gap_2022_24.quantile(.75):+.2f} | US {T.loc['United States'].gap_2022_24:+.2f}")
