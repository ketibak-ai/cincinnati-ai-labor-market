"""H6(b), measure 2: university R&D in computer and information sciences, NSF HERD FY2024.
Institutions are assigned to metros through their IPEDS unit ID and county (HD2024), using
the 2023 CBSA delineation. Dollars are thousands, as reported.
Output: data/h6_herd_computing_rd.csv
"""
import io, os, zipfile
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
z = zipfile.ZipFile(P("raw", "herd", "higher_education_r_and_d_2024.zip"))
d = pd.read_csv(io.BytesIO(z.read("herd2024.csv")), encoding="latin-1", dtype=str)
# Computer and information sciences R&D = federal (question 09A) + nonfederal (question 11A), column "Total"
f = d[d.questionnaire_no.isin(["09A", "11A"]) & (d.column == "Total") & d.row.str.startswith("Computer and information sciences", na=False)].copy()
f["v"] = pd.to_numeric(f.data, errors="coerce").fillna(0)
tot = f.groupby(["inst_id", "ipeds_unitid", "inst_name_long", "inst_city", "inst_state_code", "inst_zip"], dropna=False).v.sum().reset_index()
qn = "09A + 11A"
allrd = d[(d.question == "Source") & (d.row == "Total")].assign(total_rd=lambda x: pd.to_numeric(x.data, errors="coerce"))[["inst_id", "total_rd"]]
hd = pd.read_csv(io.BytesIO(zipfile.ZipFile(P("raw", "ipeds", "HD2024.zip")).read("HD2024.csv")), encoding="utf-8-sig", dtype=str, encoding_errors="replace")
cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
hd["fips"] = hd.COUNTYCD.str.zfill(5)
cmap = dict(zip(cty.STCOU, cty.CBSA))
# County of each HERD institution: IPEDS unit ID first; if HERD's ID is not an IPEDS campus
# record, the institution's ZIP code; then its city and state. ZIP and city are resolved to a
# county through the IPEDS directory (the county of institutions at that ZIP or in that city).
by_id = dict(zip(hd.UNITID, hd.fips))
by_zip = hd.assign(z=hd.ZIP.str[:5]).groupby("z").fips.agg(lambda x: x.mode().iloc[0]).to_dict()
by_city = hd.assign(k=hd.CITY.str.upper().str.strip() + "|" + hd.STABBR).groupby("k").fips.agg(lambda x: x.mode().iloc[0]).to_dict()
t = tot.merge(allrd, on="inst_id", how="left")
t["fips"] = t.ipeds_unitid.map(by_id)
t["how"] = t.fips.notna().map({True: "unitid", False: None})
z5 = t.inst_zip.astype(str).str[:5]
m_ = t.fips.isna() & z5.isin(by_zip); t.loc[m_, "fips"] = z5[m_].map(by_zip); t.loc[m_, "how"] = "zip"
k = t.inst_city.str.upper().str.strip() + "|" + t.inst_state_code
m_ = t.fips.isna() & k.isin(by_city); t.loc[m_, "fips"] = k[m_].map(by_city); t.loc[m_, "how"] = "city"
t["cbsa"] = t.fips.map(cmap)
t["UNITID"] = t.fips
print("county assigned by:", t.how.value_counts(dropna=False).to_dict())
print("institutions with computing R&D:", len(t), "| no county found:", int(t.fips.isna().sum()), "| their R&D ($000):", int(t[t.fips.isna()].v.sum()), "| national total ($000):", int(t.v.sum()))
peers = pd.read_csv(P("data", "peer_sets.csv"))
m = t.dropna(subset=["cbsa"]).groupby("cbsa").agg(computing_rd_thousands=("v", "sum"), total_rd_thousands=("total_rd", "sum"), institutions=("inst_id", "nunique")).reset_index()
top = t.dropna(subset=["cbsa"]).sort_values("v", ascending=False).groupby("cbsa").head(1)[["cbsa", "inst_name_long", "v"]].rename(columns={"inst_name_long": "largest_institution", "v": "largest_thousands"})
m = peers[["CBSA", "short", "POPESTIMATE2025", "p1", "p2", "p3"]].merge(m, left_on="CBSA", right_on="cbsa", how="left").merge(top, on="cbsa", how="left")
m[["computing_rd_thousands", "total_rd_thousands", "institutions"]] = m[["computing_rd_thousands", "total_rd_thousands", "institutions"]].fillna(0)
m["computing_rd_per_capita"] = m.computing_rd_thousands * 1000 / m.POPESTIMATE2025
m["question_used"] = qn
m.drop(columns="cbsa").to_csv(P("data", "h6_herd_computing_rd.csv"), index=False)
s = m[m.p1 | (m.CBSA == 17140)].sort_values("computing_rd_per_capita", ascending=False)
print(s[["short", "computing_rd_thousands", "total_rd_thousands", "institutions", "computing_rd_per_capita", "largest_institution"]].round(2).to_string(index=False))
cin = float(m.loc[m.CBSA == 17140, "computing_rd_per_capita"].iloc[0]); p1 = m[m.p1].computing_rd_per_capita
print("Cincinnati", round(cin, 2), "rank", int((p1 > cin).sum()) + 1, "of 20; P1 median", round(p1.median(), 2), "| bottom half:", cin < p1.median())
print(t[t.cbsa == 17140][["inst_name_long", "v", "total_rd"]].to_string(index=False))
