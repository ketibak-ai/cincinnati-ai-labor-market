"""H6(b), measure 3: completions in computing, data science and statistics, IPEDS 2023-24.

Institutions are assigned to metros by county (IPEDS HD2024 county code -> 2023 CBSA
delineation in data/cbsa_counties.csv). Awards of every level, first majors only, CIP families:
11 (computer and information sciences), 14.09 (computer engineering), 27.05 (statistics),
30.70 (data science) and 30.71 (data analytics). Artificial intelligence (CIP 11.0102) is also
shown by itself. Online-only enrolment is not separated: awards are counted where the
institution is located, which overstates metros that host large online universities.

Output: data/h6_ipeds_completions.csv
"""
import io, os, zipfile
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda z: pd.read_csv(io.BytesIO(zipfile.ZipFile(P("raw", "ipeds", z)).read(z.replace(".zip", ".csv").lower() if False else zipfile.ZipFile(P("raw", "ipeds", z)).namelist()[0])), encoding="utf-8-sig", dtype=str, encoding_errors="replace")
hd, c = rd("HD2024.zip"), rd("C2024_A.zip")
c.columns = [x.strip() for x in c.columns]; hd.columns = [x.strip() for x in hd.columns]
cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
peers = pd.read_csv(P("data", "peer_sets.csv"))
hd["cbsa"] = hd.COUNTYCD.str.zfill(5).map(dict(zip(cty.STCOU, cty.CBSA)))
c = c[(c.MAJORNUM == "1") & (c.CIPCODE != "99")].copy()
c["n"] = pd.to_numeric(c.CTOTALT, errors="coerce").fillna(0)
cip = c.CIPCODE
c["family"] = None
c.loc[cip.str.startswith("11."), "family"] = "computing_11"
c.loc[cip.str.startswith("14.09"), "family"] = "computer_engineering_1409"
c.loc[cip.str.startswith("27.05"), "family"] = "statistics_2705"
c.loc[cip.str.startswith("30.70"), "family"] = "data_science_3070"
c.loc[cip.str.startswith("30.71"), "family"] = "data_analytics_3071"
c = c.dropna(subset=["family"]).merge(hd[["UNITID", "INSTNM", "cbsa"]], on="UNITID")
c = c[c.cbsa.isin(set(peers.CBSA))]
c["ai_110102"] = c.n.where(c.CIPCODE == "11.0102", 0)
c["bachelors_plus"] = c.n.where(c.AWLEVEL.isin(["5", "7", "17", "18", "19"]), 0)
m = c.groupby("cbsa").agg(completions=("n", "sum"), bachelors_plus=("bachelors_plus", "sum"), ai_110102=("ai_110102", "sum")).reset_index()
m = peers[["CBSA", "short", "POPESTIMATE2025", "p1", "p2", "p3"]].merge(m, left_on="CBSA", right_on="cbsa", how="left").fillna({"completions": 0, "bachelors_plus": 0, "ai_110102": 0})
m["completions_per_100k"] = m.completions / m.POPESTIMATE2025 * 1e5
m["bachelors_plus_per_100k"] = m.bachelors_plus / m.POPESTIMATE2025 * 1e5
top = c.groupby(["cbsa", "INSTNM"]).n.sum().reset_index().sort_values("n", ascending=False).groupby("cbsa").head(1)
m = m.merge(top.rename(columns={"INSTNM": "largest_institution", "n": "largest_institution_completions"}), on="cbsa", how="left")
m["largest_share"] = m.largest_institution_completions / m.completions
m.drop(columns="cbsa").to_csv(P("data", "h6_ipeds_completions.csv"), index=False)
t = m[m.p1 | (m.CBSA == 17140)].sort_values("completions_per_100k", ascending=False)
print(t[["short", "completions", "bachelors_plus", "ai_110102", "completions_per_100k", "bachelors_plus_per_100k", "largest_institution", "largest_share"]].round(2).to_string(index=False))
for col in ("completions_per_100k", "bachelors_plus_per_100k"):
    cin = float(m.loc[m.CBSA == 17140, col].iloc[0]); p1 = m[m.p1][col]
    print(col, "Cincinnati", round(cin, 1), "rank", int((p1 > cin).sum()) + 1, "of 20; P1 median", round(p1.median(), 1), "| bottom half:", cin < p1.median())
print("Cincinnati institutions:"); print(c[c.cbsa == 17140].groupby("INSTNM").n.sum().sort_values(ascending=False).head(12).to_string())
