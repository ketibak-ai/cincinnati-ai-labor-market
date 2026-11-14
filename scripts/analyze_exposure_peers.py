"""H4 and H10: is Cincinnati's AI exposure, and its rise with pay, different from its peers'?

H4  Employment-weighted mean exposure on four measures (OEWS May 2025, detailed occupations),
    for Cincinnati, the nation and every metro in P1, P2 and P3. "Average" if Cincinnati lies
    inside the P1 interquartile range on at least three of the four measures.
    Band robustness: share of covered employment above 0.30, 0.40 and 0.50 observed exposure
    (AEI) and in the top national decile of occupations.
H10 Wage-quintile gradient (top quintile minus bottom quintile of mean exposure, quintiles cut
    at equal cumulative employment by occupational median wage, as in 1.0) for the nation and
    each peer. "A national pattern" if Cincinnati lies inside the P1 interquartile range.

Outputs: data/h4_exposure_peers.csv, data/h4_bands.csv, data/h10_wage_gradient.csv,
         output/h4_h10_trace.txt
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
MEASURES = ["lm_aioe", "eloundou", "aei", "ms"]
CIN = 17140

peers = pd.read_csv(P("data", "peer_sets.csv"))
occ = pd.read_csv(P("data", "occupation_exposure_4measures.csv")).set_index("soc")
num = lambda s: pd.to_numeric(s.astype(str).str.replace(",", ""), errors="coerce")

msa = pd.read_csv(P("raw", "oes", "MSA_M2025.csv"), dtype=str)
msa = msa[(msa.O_GROUP == "detailed") & msa.AREA.astype(int).isin(set(peers.CBSA))].copy()
msa["cbsa"] = msa.AREA.astype(int)
nat = pd.read_csv(P("raw", "oes", "national_M2025.csv"), dtype=str)
nat = nat[nat.O_GROUP == "detailed"].copy()
nat["cbsa"] = 0
d = pd.concat([msa, nat], ignore_index=True)
d["emp"], d["wage"] = num(d.TOT_EMP), num(d.A_MEDIAN)
d = d.dropna(subset=["emp"]).merge(occ, left_on="OCC_CODE", right_index=True, how="left")
name = dict(zip(peers.CBSA, peers.short)); name[0] = "United States"

# --- H4 means
rows = []
for c, g in d.groupby("cbsa"):
    r = {"cbsa": c, "area": name[c], "detailed_emp": g.emp.sum()}
    for m in MEASURES:
        ok = g[m].notna()
        r[m] = np.average(g.loc[ok, m], weights=g.loc[ok, "emp"])
        r[m + "_cov"] = g.loc[ok, "emp"].sum() / g.emp.sum()
    rows.append(r)
H4 = pd.DataFrame(rows).merge(peers[["CBSA", "p1", "p2", "p3"]], left_on="cbsa", right_on="CBSA", how="left").drop(columns="CBSA")
H4[["p1", "p2", "p3"]] = H4[["p1", "p2", "p3"]].fillna(False)
H4.to_csv(P("data", "h4_exposure_peers.csv"), index=False)

# --- H4 bands (observed exposure; national unweighted top decile of scored occupations)
dec = {m: occ[m].dropna().quantile(0.9) for m in MEASURES}
brow = []
for c, g in d.groupby("cbsa"):
    a = g[g.aei.notna()]
    r = {"cbsa": c, "area": name[c]}
    for cut in (0.30, 0.40, 0.50):
        r[f"aei_share_above_{cut:.2f}"] = a.loc[a.aei >= cut, "emp"].sum() / a.emp.sum()
    for m in MEASURES:
        s = g[g[m].notna()]
        r[f"{m}_share_top_decile"] = s.loc[s[m] >= dec[m], "emp"].sum() / s.emp.sum()
    brow.append(r)
B = pd.DataFrame(brow).merge(peers[["CBSA", "p1"]], left_on="cbsa", right_on="CBSA", how="left").drop(columns="CBSA")
B["p1"] = B.p1.fillna(False)
B.to_csv(P("data", "h4_bands.csv"), index=False)


# --- H10 wage gradient
def gradient(g, m):
    s = g.dropna(subset=["wage", m]).sort_values("wage")
    mid = (s.emp.cumsum() - s.emp / 2) / s.emp.sum()
    qn = np.floor(5 * mid).clip(0, 4).astype(int)
    means = s.groupby(qn).apply(lambda x: np.average(x[m], weights=x.emp), include_groups=False)
    return means

grow = []
for c, g in d.groupby("cbsa"):
    r = {"cbsa": c, "area": name[c]}
    for m in MEASURES:
        q = gradient(g, m)
        r[m + "_q1"], r[m + "_q5"], r[m + "_gradient"] = q[0], q[4], q[4] - q[0]
    grow.append(r)
G = pd.DataFrame(grow).merge(peers[["CBSA", "p1", "p2", "p3"]], left_on="cbsa", right_on="CBSA", how="left").drop(columns="CBSA")
G[["p1", "p2", "p3"]] = G[["p1", "p2", "p3"]].fillna(False)
G.to_csv(P("data", "h10_wage_gradient.csv"), index=False)

with open(P("output", "h4_h10_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a)
        print(*a, file=fh)

    def position(T, col, pset):
        pp = T[T[pset]][col]
        cin = T.loc[T.cbsa == CIN, col].iloc[0]
        q1, med, q3 = pp.quantile([.25, .5, .75])
        where = "inside IQR" if q1 <= cin <= q3 else ("above IQR" if cin > q3 else "below IQR")
        return cin, q1, med, q3, int((pp > cin).sum()) + 1, len(pp) + 1, where

    us = H4[H4.cbsa == 0].iloc[0]
    w("H4. Employment-weighted mean exposure, OEWS May 2025")
    for pset in ("p1", "p2", "p3"):
        w(f"\n  Against {pset.upper()}:")
        for m in MEASURES:
            cin, q1, med, q3, rk, n, where = position(H4, m, pset)
            w(f"  {m:9s} Cincinnati {cin:+.4f} | US {us[m]:+.4f} | peers q25 {q1:+.4f} median {med:+.4f} q75 {q3:+.4f} | "
              f"rank {rk} of {n} (1 = most exposed) | {where}")
    inside = sum(position(H4, m, "p1")[6] == "inside IQR" for m in MEASURES)
    w(f"\n  Inside the P1 interquartile range on {inside} of 4 measures -> "
      f"{'AVERAGE' if inside >= 3 else 'NOT average by the pre-registered rule'}")
    w("\n  Coverage of detailed employment by measure, Cincinnati:",
      {m: round(float(H4.loc[H4.cbsa == CIN, m + '_cov'].iloc[0]), 3) for m in MEASURES})
    w("\nH4 bands (share of AEI-covered employment at or above each observed-exposure cut; top national decile by measure)")
    for col in [c for c in B.columns if c.startswith("aei_share") or c.endswith("top_decile")]:
        cin, q1, med, q3, rk, n, where = position(B, col, "p1")
        w(f"  {col:28s} Cincinnati {cin:.4f} | US {B.loc[B.cbsa == 0, col].iloc[0]:.4f} | P1 q25 {q1:.4f} median {med:.4f} q75 {q3:.4f} | {where}")
    w("\nH10. Wage gradient (top quintile minus bottom quintile of mean exposure)")
    usg = G[G.cbsa == 0].iloc[0]
    for m in MEASURES:
        cin, q1, med, q3, rk, n, where = position(G, m + "_gradient", "p1")
        w(f"  {m:9s} Cincinnati {cin:+.4f} | US {usg[m + '_gradient']:+.4f} | P1 q25 {q1:+.4f} median {med:+.4f} q75 {q3:+.4f} | "
          f"rank {rk} of {n} | {where}")
    w("  Metros (of all in the peer sets, plus the US) with a positive LM-AIOE gradient:",
      int((G.lm_aioe_gradient > 0).sum()), "of", len(G))
