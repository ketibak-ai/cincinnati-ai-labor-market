"""Download QCEW 2025 annual county files for every county in the 60 most populous MSAs and
in the P1 peers. BLS suppresses most private-sector cells in the MSA-level files for many
multi-county metros (19 of 20 sectors for Cincinnati in 2024 and 2025 H1), so metro industry
detail is built by summing published county cells instead.

Usage: python scripts/fetch_qcew_counties.py [year] [p1]
Output: raw/qcew_county/<year>_<fips>.csv ; data/cbsa_counties.csv
"""
import os, sys, time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd, requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2025     # optional: year; then "p1" to limit to P1 + Cincinnati
pop = pd.read_csv(P("raw", "census", "cbsa-est2025-alldata.csv"), encoding="latin-1", dtype={"STCOU": str})
msa = pop[pop.LSAD == "Metropolitan Statistical Area"]
top60 = set(msa.sort_values("POPESTIMATE2025", ascending=False).head(60).CBSA) | {19430, 17140}
cty = pop[pop.LSAD.str.contains("County|Parish|Planning Region|city|Borough|Municipio", na=False) & pop.STCOU.notna() & pop.CBSA.isin(top60)]
cty = cty[["CBSA", "STCOU", "NAME", "POPESTIMATE2025"]].copy()
cty["STCOU"] = cty.STCOU.str.zfill(5)
cty.to_csv(P("data", "cbsa_counties.csv"), index=False)
if len(sys.argv) > 2 and sys.argv[2] == "p1":
    pe = pd.read_csv(P("data", "peer_sets.csv"))
    cty = cty[cty.CBSA.isin(set(pe[pe.p1].CBSA) | {17140})]
os.makedirs(P("raw", "qcew_county"), exist_ok=True)


def get(fips):
    f = P("raw", "qcew_county", f"{YEAR}_{fips}.csv")
    if os.path.exists(f) and os.path.getsize(f) > 1000:
        return fips, "cached"
    for k in range(5):
        try:
            r = requests.get(f"https://data.bls.gov/cew/data/api/{YEAR}/a/area/{fips}.csv", timeout=120)
            if r.status_code == 200:
                open(f, "wb").write(r.content); return fips, len(r.content)
            if r.status_code == 404:
                return fips, "404"
        except Exception as e:
            pass
        time.sleep(4 * (k + 1))
    return fips, "FAILED"

with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(get, cty.STCOU))
bad = [r for r in res if r[1] in ("404", "FAILED")]
print(len(res), "counties;", len(bad), "not retrieved:", bad[:40])
