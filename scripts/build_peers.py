"""Fix the three peer sets exactly as PREREGISTRATION.md section 2 defines them.

P1: the Chamber's 19 peers (State of the Region 2026, p. 6) - listed by hand.
P2: all MSAs with July 2025 population between 0.6x and 1.4x Cincinnati's (Census Vintage 2025).
P3: the 10 MSAs among the 60 most populous with the lowest Duncan dissimilarity index to
    Cincinnati's 2025 QCEW private employment shares across 2-digit NAICS sectors.

Run scripts/fetch_qcew_counties.py first.
Output: data/peer_sets.csv
"""
import os
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
CIN = 17140
P1 = {12060: "Atlanta", 12420: "Austin", 12580: "Baltimore", 16740: "Charlotte", 17410: "Cleveland",
      18140: "Columbus", 19430: "Dayton", 19740: "Denver", 19820: "Detroit", 26900: "Indianapolis",
      28140: "Kansas City", 31140: "Louisville", 33340: "Milwaukee", 33460: "Minneapolis",
      34980: "Nashville", 38300: "Pittsburgh", 39580: "Raleigh", 41180: "St. Louis", 45300: "Tampa"}

pop = pd.read_csv(P("raw", "census", "cbsa-est2025-alldata.csv"), encoding="latin-1")
msa = pop[pop.LSAD == "Metropolitan Statistical Area"][["CBSA", "NAME", "POPESTIMATE2025"]].copy()
cin_pop = int(msa.loc[msa.CBSA == CIN, "POPESTIMATE2025"].iloc[0])
msa["p2"] = msa.POPESTIMATE2025.between(0.6 * cin_pop, 1.4 * cin_pop) & (msa.CBSA != CIN)
top60 = msa.sort_values("POPESTIMATE2025", ascending=False).head(60)



CTY = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})


def sector_shares(cbsa):
    """Private employment by NAICS sector, 2025 annual averages, summed over the metro's
    counties (QCEW county files, own_code 5, agglvl 74). The MSA-level QCEW files could not be
    used: on 14 Nov 2026 the 2025 annual MSA file held only the all-industry total, 2025 Q3-Q4
    detail was not yet published, and 2025 Q1-Q2 sector cells were suppressed for 45-48 of the
    60 largest MSAs (19-20 of 20 sectors for Cincinnati). Suppressed county cells are missing,
    not zero; the second value returned is the share of private employment the published
    sector cells cover. Logged as a deviation in PREREGISTRATION.md."""
    tot, parts = 0.0, []
    for fips in CTY.loc[CTY.CBSA == cbsa, "STCOU"]:
        d = pd.read_csv(P("raw", "qcew_county", f"2025_{fips}.csv"), dtype={"industry_code": str, "disclosure_code": str})
        d = d[d.own_code == 5]
        tot += float(d.loc[d.agglvl_code == 71, "annual_avg_emplvl"].sum())
        s = d[(d.agglvl_code == 74) & (d.disclosure_code.fillna("") != "N")]
        parts.append(s[["industry_code", "annual_avg_emplvl"]])
    emp = pd.concat(parts).groupby("industry_code").annual_avg_emplvl.sum().astype(float)
    return emp, emp.sum() / tot

base, _ = sector_shares(CIN)
rows = []
for c in top60.CBSA:
    if c == CIN:
        continue
    e, cov = sector_shares(c)
    idx = base.index.union(e.index)
    a, b = base.reindex(idx).fillna(0) / base.sum(), e.reindex(idx).fillna(0) / e.sum()
    rows.append((c, 0.5 * (a - b).abs().sum(), len(idx), round(cov, 4)))
dis = pd.DataFrame(rows, columns=["CBSA", "duncan", "sectors_compared", "private_emp_covered"]).sort_values("duncan")
p3 = set(dis.head(10).CBSA)

out = msa.merge(dis, on="CBSA", how="left")
out["p1"] = out.CBSA.isin(P1); out["p3"] = out.CBSA.isin(p3)
out["short"] = out.CBSA.map(P1).fillna(out.NAME.str.split("[-,/]").str[0])
out = out[(out.p1 | out.p2 | out.p3) | (out.CBSA == CIN)].sort_values("POPESTIMATE2025", ascending=False)
out.loc[out.CBSA == CIN, "short"] = "Cincinnati"
out.to_csv(P("data", "peer_sets.csv"), index=False)
print("Cincinnati coverage of private employment by published sector cells:", round(_, 4))
print("Cincinnati pop 2025:", cin_pop, "| P1", out.p1.sum(), "| P2", out.p2.sum(), "| P3", out.p3.sum())
print(dis.head(12).merge(msa[["CBSA", "NAME"]]).to_string(index=False))
print("P1 metros missing from the population file:", sorted(set(P1) - set(msa.CBSA)))
