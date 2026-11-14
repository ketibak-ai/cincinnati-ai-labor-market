"""H2b: the occupation-based entry-door test (pre-registration amendment of 13 Nov 2026).

ACS 1-year PUMS, employed civilians. Outcome: employment of ages 22-25 relative to ages 35-54
in occupations in the top tercile of AI exposure against the bottom tercile.

    DDD = { [ln E(22-25, top) - ln E(35-54, top)] - [ln E(22-25, bottom) - ln E(35-54, bottom)] } post
        - { same } pre

Pre = 2018 and 2019 pooled. Post = 2023 and 2024 pooled. The amendment named 2023-2025, but
the 2025 1-year PUMS was not on the Census file server on 14 Nov 2026, so 2025 is not used
(logged as a deviation). Terciles are cut on detailed occupations weighted by national OEWS
May 2022 employment. Standard errors use the 80 ACS replicate weights.

Metros are built from PUMAs: a PUMA belongs to a metro if at least half of its census tracts
lie in the metro's counties (2010 PUMAs for 2018-19, 2020 PUMAs for 2023-24). This is an
approximation of the CBSA, and the PUMA count is reported.

Run for Cincinnati and the P1 peers only (the secondary test; P2 and P3 are not run).
Outputs: data/h2b_acs.csv, output/h2b_trace.txt
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
MEASURES = ["lm_aioe", "eloundou", "aei", "ms"]
CIN = 17140
ST = {"oh": "39", "ky": "21", "in": "18", "ga": "13", "tx": "48", "md": "24", "nc": "37", "sc": "45", "co": "08",
      "mi": "26", "mo": "29", "ks": "20", "wi": "55", "mn": "27", "tn": "47", "pa": "42", "il": "17", "fl": "12"}
REPS = [f"PWGTP{i}" for i in range(1, 81)]

peers = pd.read_csv(P("data", "peer_sets.csv"))
metros = [CIN] + list(peers[peers.p1].CBSA)
cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
c2m = dict(zip(cty.STCOU, cty.CBSA))


def puma_map(fname):
    t = pd.read_csv(P("raw", "acs", fname), dtype=str, encoding="utf-8-sig")
    t["cbsa"] = (t.STATEFP + t.COUNTYFP).map(c2m)
    t["key"] = t.STATEFP + t.PUMA5CE
    share = t.groupby("key").cbsa.agg(lambda x: x.value_counts(dropna=False, normalize=True).iloc[0])
    top = t.groupby("key").cbsa.agg(lambda x: x.value_counts(dropna=False).index[0])
    m = top[(share >= 0.5) & top.notna()]
    return m[m.isin(metros)].astype(int).to_dict()

PM = {2018: puma_map("2010_Census_Tract_to_2010_PUMA.txt"), 2019: None, 2023: puma_map("2020_Census_Tract_to_2020_PUMA.txt"), 2024: None}
PM[2019], PM[2024] = PM[2018], PM[2023]

# occupational exposure terciles, weighted by national OEWS May 2022 employment
occ = pd.read_csv(P("data", "occupation_exposure_4measures.csv")).set_index("soc")
nat = pd.read_csv(P("raw", "oes", "national_M2022.csv"), dtype=str)
nat = nat[nat.O_GROUP == "detailed"].assign(emp=lambda x: pd.to_numeric(x.TOT_EMP.str.replace(",", ""), errors="coerce")).dropna(subset=["emp"])
w22 = nat.set_index("OCC_CODE").emp
occ = occ.join(w22.rename("emp"), how="inner")
cuts = {}
for m in MEASURES:
    s = occ.dropna(subset=[m]).sort_values(m)
    cum = (s.emp.cumsum() - s.emp / 2) / s.emp.sum()
    cuts[m] = (s.loc[cum <= 1 / 3, m].max(), s.loc[cum <= 2 / 3, m].max())
occ["soc6"] = occ.index.str.replace("-", "")


def socp_exposure(codes):
    """Mean exposure for each ACS SOCP code. Codes ending in X/Y cover several SOC codes:
    use the OEWS-employment-weighted mean of the detailed codes they span."""
    out = {}
    for c in codes:
        stem = c.rstrip("XY")
        fam = occ[occ.soc6.str.startswith(stem)] if len(stem) < 6 else occ[occ.soc6 == stem]
        if len(fam):
            out[c] = {m: (np.average(fam[m].dropna(), weights=fam.loc[fam[m].notna(), "emp"]) if fam[m].notna().any() else np.nan)
                      for m in MEASURES}
    return pd.DataFrame(out).T

frames = []
for y in (2018, 2019, 2023, 2024):
    for st, fp in ST.items():
        d = pd.read_csv(P("raw", "acs", f"pums_{y}_{st}.csv.gz"), dtype={"PUMA": str, "SOCP": str, "ST": str})
        d["cbsa"] = (fp + d.PUMA.str.zfill(5)).map(PM[y])
        d = d.dropna(subset=["cbsa"])
        d = d[d.AGEP.between(22, 25) | d.AGEP.between(35, 54)]
        d["year"] = y
        frames.append(d)
D = pd.concat(frames, ignore_index=True)
D["cbsa"] = D.cbsa.astype(int)
D["age"] = np.where(D.AGEP <= 25, "young", "old")
D["period"] = np.where(D.year <= 2019, "pre", "post")
ex = socp_exposure(D.SOCP.dropna().unique())
D = D.merge(ex, left_on="SOCP", right_index=True, how="left")
W = ["PWGTP"] + REPS
coverage = D.groupby("cbsa").apply(lambda g: g.loc[g.lm_aioe.notna(), "PWGTP"].sum() / g.PWGTP.sum(), include_groups=False)

rows = []
for m in MEASURES:
    lo, hi = cuts[m]
    D["grp"] = np.where(D[m] > hi, "top", np.where(D[m] <= lo, "bottom", None))
    g = D.dropna(subset=["grp"]).groupby(["cbsa", "period", "age", "grp"])[W].sum()
    n = D.dropna(subset=["grp"]).groupby(["cbsa", "period", "age", "grp"]).size()
    for cb in metros:
        try:
            x = g.loc[cb]
            f = lambda per: (np.log(x.loc[(per, "young", "top")] / x.loc[(per, "old", "top")])
                             - np.log(x.loc[(per, "young", "bottom")] / x.loc[(per, "old", "bottom")]))
            v = f("post") - f("pre")
        except KeyError:
            continue
        est = v["PWGTP"]
        se = np.sqrt(4 / 80 * ((v[REPS] - est) ** 2).sum())
        rows.append(dict(cbsa=cb, measure=m, ddd=est, se=se, t=est / se if se else np.nan,
                         n_young_top_pre=int(n.loc[(cb, "pre", "young", "top")]), n_young_top_post=int(n.loc[(cb, "post", "young", "top")]),
                         young_top_pre=x.loc[("pre", "young", "top"), "PWGTP"] / 2, young_top_post=x.loc[("post", "young", "top"), "PWGTP"] / 2,
                         old_top_pre=x.loc[("pre", "old", "top"), "PWGTP"] / 2, old_top_post=x.loc[("post", "old", "top"), "PWGTP"] / 2,
                         young_bottom_pre=x.loc[("pre", "young", "bottom"), "PWGTP"] / 2, young_bottom_post=x.loc[("post", "young", "bottom"), "PWGTP"] / 2,
                         old_bottom_pre=x.loc[("pre", "old", "bottom"), "PWGTP"] / 2, old_bottom_post=x.loc[("post", "old", "bottom"), "PWGTP"] / 2,
                         occupation_coverage=coverage[cb]))
R = pd.DataFrame(rows).merge(peers[["CBSA", "short"]], left_on="cbsa", right_on="CBSA", how="left").drop(columns="CBSA")
R["short"] = R.short.fillna("Cincinnati")
npuma = {y: pd.Series(PM[y]).value_counts() for y in (2018, 2023)}
R["pumas_2010"] = R.cbsa.map(npuma[2018]); R["pumas_2020"] = R.cbsa.map(npuma[2023])
R.to_csv(P("data", "h2b_acs.csv"), index=False)

with open(P("output", "h2b_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a)
        print(*a, file=fh)

    w("Tercile cut points by measure (bottom <=, top >):", {m: tuple(round(float(v), 4) for v in cuts[m]) for m in MEASURES})
    c = R[R.cbsa == CIN]
    w("\nCincinnati (PUMAs: %s in 2010 geography, %s in 2020 geography):" % (int(c.pumas_2010.iloc[0]), int(c.pumas_2020.iloc[0])))
    w(c[["measure", "ddd", "se", "t", "n_young_top_pre", "n_young_top_post", "young_top_pre", "young_top_post", "old_top_pre",
         "old_top_post", "young_bottom_pre", "young_bottom_post", "old_bottom_pre", "old_bottom_post", "occupation_coverage"]].round(3).to_string(index=False))
    w("\nAgainst P1 peers:")
    for m in MEASURES:
        pp = R[(R.measure == m) & (R.cbsa != CIN)]
        cv = float(c[c.measure == m].ddd.iloc[0])
        w(f"  {m:9s} Cincinnati {cv:+.4f} | P1 n={len(pp)} q25 {pp.ddd.quantile(.25):+.4f} median {pp.ddd.median():+.4f} q75 {pp.ddd.quantile(.75):+.4f} "
          f"| rank {int((pp.ddd < cv).sum()) + 1} of {len(pp) + 1} from the bottom | peers with |t| > 1.645: {int((pp.t.abs() > 1.645).sum())} "
          f"(negative: {int(((pp.t < -1.645)).sum())})")
    w("\nPooled across all 20 metros (sum of weighted employment):")
    for m in MEASURES:
        lo, hi = cuts[m]
        D["grp"] = np.where(D[m] > hi, "top", np.where(D[m] <= lo, "bottom", None))
        x = D.dropna(subset=["grp"]).groupby(["period", "age", "grp"])[W].sum()
        f = lambda per: (np.log(x.loc[(per, "young", "top")] / x.loc[(per, "old", "top")]) - np.log(x.loc[(per, "young", "bottom")] / x.loc[(per, "old", "bottom")]))
        v = f("post") - f("pre"); est = v["PWGTP"]; se = np.sqrt(4 / 80 * ((v[REPS] - est) ** 2).sum())
        w(f"  {m:9s} DDD {est:+.4f} (se {se:.4f}, t {est / se:+.2f})")
