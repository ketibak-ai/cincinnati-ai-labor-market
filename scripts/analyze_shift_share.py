"""H6, part (a): is the region's low share of computing jobs explained by its industry mix?

Expected computer-and-mathematical (SOC 15-0000) employment in a metro
    = SUM over industries of (metro QCEW 2025 employment in the industry
                              x national OEWS May 2025 share of SOC 15-0000 in that industry)

OEWS publishes no occupation-by-industry data for metros, so the national staffing pattern is
applied to the local industry mix. The gap between the metro's actual share of computing jobs
and the national share is split in two:

    industry mix     = expected share - national share
    within industry  = actual share   - expected share

Metro industry employment is the sum of QCEW county cells (the MSA-level QCEW files suppress
most industry detail). Where a county's 4-digit cell is suppressed, its employment is not
guessed: the remainder of the published 3-digit total gets the 3-digit staffing rate, the
remainder of the sector total gets the sector rate, and the remainder of the county's private
total gets the all-industry rate. The script reports how much employment each level carried.

Outputs: data/h6_shift_share.csv, output/h6_shift_share_trace.txt
"""
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
CIN = 17140
num = lambda s: pd.to_numeric(s.astype(str).str.replace(",", ""), errors="coerce")


def rates(fname):
    d = pd.read_csv(P("raw", "oes", fname), dtype=str)
    d["emp"] = num(d.TOT_EMP)
    tot = d[d.OCC_CODE == "00-0000"].set_index("NAICS").emp
    c15 = d[d.OCC_CODE == "15-0000"].set_index("NAICS").emp
    return (c15.reindex(tot.index).fillna(0) / tot), d[d.OCC_CODE == "00-0000"].set_index("NAICS").NAICS_TITLE

r4, t4 = rates("nat4d_M2025.csv")
r3, _ = rates("nat3d_M2025.csv")
r2, _ = rates("natsector_M2025.csv")
nat = pd.read_csv(P("raw", "oes", "national_M2025.csv"), dtype=str)
NAT_RATE = float(num(nat[nat.OCC_CODE == "15-0000"].TOT_EMP).iloc[0] / num(nat[nat.OCC_CODE == "00-0000"].TOT_EMP).iloc[0])

# OEWS combines some 4-digit industries ("3250A1 ... (3251, 3252, 3253, and 3259 only)")
rate4 = {k[:4]: v for k, v in r4.items() if re.match(r"^\d{4}00$", k)}
for code, title in t4.items():
    if not re.match(r"^\d{4}00$", code) and "only)" in str(title):
        for n in re.findall(r"\b(\d{4})\b", title.split("(")[-1]):
            rate4[n] = r4[code]
rate3 = {k[:3]: v for k, v in r3.items()}
rate2 = dict(r2.items())
GOV = {1: "999100", 2: "999200", 3: "999300"}

cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
peers = pd.read_csv(P("data", "peer_sets.csv"))
msa = pd.read_csv(P("raw", "oes", "MSA_M2025.csv"), dtype=str)
msa = msa[msa.OCC_CODE.isin(["00-0000", "15-0000"])].assign(emp=lambda x: num(x.TOT_EMP), cbsa=lambda x: x.AREA.astype(int))
actual = msa.pivot_table(index="cbsa", columns="OCC_CODE", values="emp")


def county_expected(fips):
    d = pd.read_csv(P("raw", "qcew_county", f"2025_{fips}.csv"), dtype={"industry_code": str, "disclosure_code": str})
    d = d[d.disclosure_code.fillna("") != "N"]
    lv = {"n4": 0.0, "n3": 0.0, "n2": 0.0, "all": 0.0, "gov": 0.0}
    exp = 0.0
    p = d[d.own_code == 5]
    tot_priv = float(p.loc[p.agglvl_code == 71, "annual_avg_emplvl"].sum())
    e2 = p[p.agglvl_code == 74].set_index("industry_code").annual_avg_emplvl
    e3 = p[p.agglvl_code == 75].set_index("industry_code").annual_avg_emplvl
    e4 = p[p.agglvl_code == 76].set_index("industry_code").annual_avg_emplvl
    used2 = 0.0
    for s, es in e2.items():
        used2 += es
        lo, hi = (int(x) for x in s.split("-")) if "-" in s else (int(s), int(s))
        kids3 = e3[[lo <= int(k[:2]) <= hi for k in e3.index]] if s != "99" else e3.iloc[0:0]
        used3 = 0.0
        for t, et in kids3.items():
            kids4 = e4[e4.index.str[:3] == t]
            kids4 = kids4[[k in rate4 for k in kids4.index]]
            got = float(kids4.sum())
            if got > et:                      # rounding of annual averages
                kids4, got = kids4 * et / got, float(et)
            exp += sum(v * rate4[k] for k, v in kids4.items()); lv["n4"] += got
            rest = et - got
            if t in rate3:
                exp += rest * rate3[t]; lv["n3"] += rest; used3 += et
            else:
                used3 += got
        rest = max(es - used3, 0.0)
        exp += rest * rate2.get(s, NAT_RATE); lv["n2"] += rest
    rest = max(tot_priv - used2, 0.0)
    exp += rest * NAT_RATE; lv["all"] += rest
    # Government: schools (611), hospitals (622) and the postal service (491) use those
    # industries' rates, as OEWS classifies them there; the rest uses the OEWS government rates.
    for own, code in GOV.items():
        g = d[d.own_code == own]
        tg = float(g.loc[g.agglvl_code == 71, "annual_avg_emplvl"].sum())
        g3 = g[g.agglvl_code == 75].set_index("industry_code").annual_avg_emplvl
        special = 0.0
        for t in ("611", "622", "491"):
            if t in g3.index:
                exp += g3[t] * rate3[t]; special += g3[t]
        exp += max(tg - special, 0.0) * r4.get(code, NAT_RATE)
        lv["gov"] += tg
    total = tot_priv + lv["gov"]
    return exp, total, lv

rows = []
for cbsa in sorted(set(peers.CBSA)):
    E = T = 0.0
    lv = {"n4": 0.0, "n3": 0.0, "n2": 0.0, "all": 0.0, "gov": 0.0}
    for fips in cty.loc[cty.CBSA == cbsa, "STCOU"]:
        e, t, l = county_expected(fips)
        E += e; T += t
        for k in lv: lv[k] += l[k]
    a = actual.loc[cbsa]
    act_share, exp_share = a["15-0000"] / a["00-0000"], E / T
    rows.append(dict(cbsa=cbsa, actual_15=a["15-0000"], oews_total=a["00-0000"], qcew_total=T, expected_15_at_qcew=E,
                     actual_share=act_share, expected_share=exp_share, national_share=NAT_RATE,
                     gap=act_share - NAT_RATE, industry_mix=exp_share - NAT_RATE, within_industry=act_share - exp_share,
                     lq_actual=act_share / NAT_RATE, lq_expected=exp_share / NAT_RATE,
                     **{"emp_share_" + k: v / T for k, v in lv.items()}))
R = pd.DataFrame(rows).merge(peers[["CBSA", "short", "p1", "p2", "p3"]], left_on="cbsa", right_on="CBSA").drop(columns="CBSA")
R["within_share_of_gap"] = R.within_industry / R.gap
R.to_csv(P("data", "h6_shift_share.csv"), index=False)

with open(P("output", "h6_shift_share_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a)
        print(*a, file=fh)

    c = R[R.cbsa == CIN].iloc[0]
    w(f"National share of employment in computer and mathematical occupations (OEWS May 2025): {NAT_RATE:.4%}")
    w(f"Cincinnati actual share: {c.actual_share:.4%}  ({c.actual_15:,.0f} of {c.oews_total:,.0f}); LQ {c.lq_actual:.3f}")
    w(f"Cincinnati expected share from its industry mix: {c.expected_share:.4%}; LQ expected {c.lq_expected:.3f}")
    w(f"Gap vs nation: {c.gap * 100:+.3f} points = industry mix {c.industry_mix * 100:+.3f} + within-industry {c.within_industry * 100:+.3f}")
    w(f"Within-industry share of the gap: {c.within_share_of_gap:.1%}")
    w(f"In jobs (at the OEWS total): gap {c.gap * c.oews_total:+,.0f} = mix {c.industry_mix * c.oews_total:+,.0f} + within {c.within_industry * c.oews_total:+,.0f}")
    w("Employment carried at each level of industry detail (Cincinnati):",
      {k: round(float(c['emp_share_' + k]), 4) for k in ("n4", "n3", "n2", "all", "gov")})
    w("\nAll metros, sorted by within-industry component (points):")
    t = R.sort_values("within_industry")[["short", "p1", "lq_actual", "lq_expected", "gap", "industry_mix", "within_industry"]].copy()
    for k in ("gap", "industry_mix", "within_industry"):
        t[k] = t[k] * 100
    w(t.round(3).to_string(index=False))
    p1 = R[R.p1]
    w(f"\nP1: Cincinnati within-industry rank {int((p1.within_industry < c.within_industry).sum()) + 1} of {len(p1) + 1} from the bottom; "
      f"P1 q25 {p1.within_industry.quantile(.25) * 100:+.3f}, median {p1.within_industry.median() * 100:+.3f}, q75 {p1.within_industry.quantile(.75) * 100:+.3f}")
