"""H1-H3: the entry-door test, as PREREGISTRATION.md section 5 specifies.

For each metro (state parts of the CBSA summed) and each exposure measure:

  DDD = { [ln H(young,exposed) - ln H(old,exposed)] - [ln H(young,less) - ln H(old,less)] } post
      - { same } pre

  young = QWI age group A03 (22-24); old = A05 + A06 (35-54); secondary young = A04 (25-34)
  pre   = 2018Q1-2019Q4
  post  = 2023Q1-2025Q4 (the last quarter of the combined Cincinnati MSA; the same window is
          used for every metro so the comparison is like for like and each period holds whole
          years, which removes seasonality)
  exposed / less exposed = top / bottom tercile of NAICS 3-digit industries
          (data/industry_exposure_naics3.csv)
  H = mean quarterly value over the period of the sum across industries and state parts.

Suppressed cells (status flag 5) are never imputed. To keep the two periods comparable, a
state-part x industry series is used only if every cell needed (young, A05, A06) is published
in every quarter of both periods. Otherwise the whole series is dropped, and the share of
employment that survives is reported as coverage.

Outputs: data/h1_ddd.csv, data/h1_event_time.csv, data/h1_rate_checks.csv, data/h3_earnings.csv,
         output/h1_trace.txt
"""
import glob
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
MEASURES = ["lm_aioe", "eloundou", "aei", "ms"]
PRE = [(y, q) for y in (2018, 2019) for q in (1, 2, 3, 4)]
POST = [(y, q) for y in (2023, 2024, 2025) for q in (1, 2, 3, 4)]
MID = [(y, q) for y in (2020, 2021, 2022) for q in (1, 2, 3, 4)]
OUTCOMES = {"HirN": "sHirN", "HirAS": "sHirAS", "Emp": "sEmp"}
SEED, NPERM = 20261114, 1000
CIN = 17140

peers = pd.read_csv(P("data", "peer_sets.csv"))
ind = pd.read_csv(P("data", "industry_exposure_naics3.csv"), dtype={"naics3": str}).set_index("naics3")
metros = set(peers.CBSA)

frames = []
for f in sorted(glob.glob(P("raw", "qwi", "qwi_*_filtered.csv.gz"))):
    d = pd.read_csv(f, dtype={"geography": str, "industry": str})
    d["cbsa"] = d.geography.str[2:].astype(int)
    d["part"] = d.geography.str[:2]
    frames.append(d[d.cbsa.isin(metros)])
q = pd.concat(frames, ignore_index=True)
q["yq"] = list(zip(q.year, q.quarter))
last = q.groupby(["cbsa", "part"]).yq.max()
usable = {c for c in metros if c in last.index.get_level_values(0) and (last[c] >= (2025, 4)).all()}
dropped_metros = sorted(metros - usable)
q = q[q.cbsa.isin(usable) & q.yq.isin(PRE + MID + POST)].copy()
q["key"] = q.part + "_" + q.industry


def balanced(sub, outcome, young):
    """Period sums by industry x period x age, for series published in every pre and post
    quarter for the young group and both old groups. Returns (table, set of part_industry)."""
    flag = OUTCOMES[outcome]
    need = [young, "A05", "A06"]
    s = sub[sub.agegrp.isin(need) & sub.yq.isin(PRE + POST)]
    ok = s[s[flag].isin([1, 9]) & s[outcome].notna()]
    n = ok.groupby("key").size()
    keep = set(n[n == len(need) * (len(PRE) + len(POST))].index)
    ok = ok[ok.key.isin(keep)].copy()
    ok["period"] = np.where(ok.yq.isin(PRE), "pre", "post")
    ok["age"] = np.where(ok.agegrp == young, "young", "old")
    return ok.groupby(["industry", "period", "age"])[outcome].sum().unstack(["period", "age"]), keep


NQ = {"pre": len(PRE), "post": len(POST)}


def gap(v, p):
    return np.log(v[(p, "young")] / NQ[p]) - np.log(v[(p, "old")] / NQ[p])


def dd_single(tab, ix):
    """Change from pre to post in ln(young/old) for one group of industries."""
    v = tab.reindex(ix).sum()
    return gap(v, "post") - gap(v, "pre")


def ddd_from(tab, exp_ix, less_ix):
    return dd_single(tab, exp_ix) - dd_single(tab, less_ix)


rng = np.random.default_rng(SEED)
res, checks, events = [], [], []
for cbsa in sorted(usable):
    sub = q[q.cbsa == cbsa]
    a00 = sub[(sub.agegrp == "A00") & sub.yq.isin(PRE)].groupby(["key", "industry"]).Emp.sum().reset_index()
    for outcome in OUTCOMES:
        for young in ("A03", "A04"):
            if outcome != "HirN" and young == "A04":
                continue
            tab, keep = balanced(sub, outcome, young)
            if tab.empty:
                continue
            have = set(tab.index)
            for m in MEASURES:
                for k, col in (("tercile", m + "_tercile"), ("quartile", m + "_quartile")):
                    primary = outcome == "HirN" and young == "A03"
                    if k == "quartile" and not primary:
                        continue
                    top = 3 if k == "tercile" else 4
                    exp_all, less_all = ind.index[ind[col] == top], ind.index[ind[col] == 1]
                    exp_ix = [i for i in exp_all if i in have]
                    less_ix = [i for i in less_all if i in have]
                    if len(exp_ix) < 3 or len(less_ix) < 3:
                        continue
                    d = ddd_from(tab, exp_ix, less_ix)
                    row = dict(cbsa=cbsa, outcome=outcome, young=young, measure=m, grouping=k, ddd=d,
                               n_exposed=len(exp_ix), n_less=len(less_ix))
                    if k == "tercile" and young == "A03":
                        pool = np.array(sorted(have))
                        perm = np.empty(NPERM)
                        for b in range(NPERM):
                            pick = rng.permutation(pool)
                            perm[b] = ddd_from(tab, pick[:len(exp_ix)], pick[len(exp_ix):len(exp_ix) + len(less_ix)])
                        row.update(perm_p10=np.nanpercentile(perm, 10), perm_p90=np.nanpercentile(perm, 90),
                                   perm_pctile=float(np.nanmean(perm < d) * 100))
                        for g, ix in (("exposed", exp_all), ("less", less_all)):
                            allg = a00[a00.industry.isin(ix)].Emp.sum()
                            kept = a00[a00.industry.isin(ix) & a00.key.isin(keep)].Emp.sum()
                            row["cov_" + g] = kept / allg if allg else np.nan
                    res.append(row)
                    if primary and k == "tercile":
                        # Rate-shock check 1: drop information, finance, real estate
                        fin = lambda i: i[:2] in ("51", "52", "53")
                        e2 = [i for i in exp_ix if not fin(i)]
                        l2 = [i for i in less_ix if not fin(i)]
                        d_ex = ddd_from(tab, e2, l2) if len(e2) >= 3 and len(l2) >= 3 else np.nan
                        # Rate-shock check 2: placebo (construction 23, durable manufacturing 33)
                        # against the less-exposed group with those industries taken out
                        plac = [i for i in have if i[:2] in ("23", "33")]
                        comp = [i for i in less_ix if i[:2] not in ("23", "33")]
                        okc = len(comp) >= 3
                        checks.append(dict(
                            cbsa=cbsa, measure=m, ddd=d, ddd_excl_51_52_53=d_ex, n_exposed_excl=len(e2),
                            exposed_vs_comp=dd_single(tab, exp_ix) - dd_single(tab, comp) if okc else np.nan,
                            placebo_vs_comp=dd_single(tab, plac) - dd_single(tab, comp) if okc and len(plac) >= 3 else np.nan,
                            n_placebo=len(plac), n_comp=len(comp)))
                        # Rate-shock check 3: timing. Yearly gap relative to the 2018-19 mean.
                        s = sub[sub.agegrp.isin(["A03", "A05", "A06"]) & sub.key.isin(keep)]
                        s = s.assign(age=np.where(s.agegrp == "A03", "young", "old"),
                                     grp=np.where(s.industry.isin(exp_ix), "exp",
                                                  np.where(s.industry.isin(less_ix), "less", "")))
                        s = s[(s.grp != "") & s.sHirN.isin([1, 9])]
                        cnt = s.groupby(["year", "grp", "age"]).HirN.count().unstack(["grp", "age"])
                        y = s.groupby(["year", "grp", "age"]).HirN.sum(min_count=1).unstack(["grp", "age"])
                        full = cnt.eq(cnt.loc[2018]).all(axis=1)
                        g_ = (np.log(y[("exp", "young")] / y[("exp", "old")])
                              - np.log(y[("less", "young")] / y[("less", "old")]))
                        base = g_.loc[[2018, 2019]].mean()
                        for yr in g_.index:
                            events.append(dict(cbsa=cbsa, measure=m, year=int(yr), gap_vs_pre=g_[yr] - base,
                                               complete=bool(full[yr])))

names = peers[["CBSA", "short", "p1", "p2", "p3"]]
R = pd.DataFrame(res).merge(names, left_on="cbsa", right_on="CBSA").drop(columns="CBSA")
R.to_csv(P("data", "h1_ddd.csv"), index=False)
C = pd.DataFrame(checks).merge(names[["CBSA", "short"]], left_on="cbsa", right_on="CBSA").drop(columns="CBSA")
C.to_csv(P("data", "h1_rate_checks.csv"), index=False)
E = pd.DataFrame(events).merge(names[["CBSA", "short"]], left_on="cbsa", right_on="CBSA").drop(columns="CBSA")
E.to_csv(P("data", "h1_event_time.csv"), index=False)

# H3: monthly earnings of new stable hires, young relative to old, exposed vs less exposed.
# EarnHirNS needs the following quarter, so the post window ends 2025Q3 for every metro.
earn = []
EPOST = [t for t in POST if t <= (2025, 3)]
for cbsa in sorted(usable):
    sub = q[(q.cbsa == cbsa) & q.agegrp.isin(["A03", "A05", "A06"]) & q.sEarnHirNS.isin([1, 9])
            & q.HirNS.notna() & q.EarnHirNS.notna() & q.yq.isin(PRE + EPOST)]
    sub = sub.assign(period=np.where(sub.year <= 2019, "pre", "post"),
                     age=np.where(sub.agegrp == "A03", "young", "old"))
    for m in MEASURES:
        g = sub.assign(grp=sub.industry.map(ind[m + "_tercile"]).map({3: "exp", 1: "less"})).dropna(subset=["grp"])
        w = g.assign(pay=g.EarnHirNS * g.HirNS).groupby(["grp", "period", "age"])[["pay", "HirNS"]].sum()
        e = w.pay / w.HirNS
        try:
            f = lambda grp, per: np.log(e[(grp, per, "young")] / e[(grp, per, "old")])
            earn.append(dict(cbsa=cbsa, measure=m,
                             ddd_earn=(f("exp", "post") - f("less", "post")) - (f("exp", "pre") - f("less", "pre")),
                             young_exp_pre=e[("exp", "pre", "young")], young_exp_post=e[("exp", "post", "young")],
                             old_exp_pre=e[("exp", "pre", "old")], old_exp_post=e[("exp", "post", "old")]))
        except KeyError:
            pass
H3 = pd.DataFrame(earn).merge(names[["CBSA", "short"]], left_on="cbsa", right_on="CBSA").drop(columns="CBSA")
H3.to_csv(P("data", "h3_earnings.csv"), index=False)

with open(P("output", "h1_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a)
        print(*a, file=fh)

    sh = peers.set_index("CBSA").short
    w("Metros in the peer sets without QWI through 2025Q4 (excluded):", [(c, sh[c]) for c in dropped_metros])
    w("Usable metros:", len(usable))
    main = R[(R.outcome == "HirN") & (R.young == "A03") & (R.grouping == "tercile")]
    w("\nCincinnati, new hires (HirN), ages 22-24 vs 35-54, terciles:")
    w(main[main.cbsa == CIN][["measure", "ddd", "perm_p10", "perm_p90", "perm_pctile", "n_exposed", "n_less",
                              "cov_exposed", "cov_less"]].round(4).to_string(index=False))
    for pset in ("p1", "p2", "p3"):
        w(f"\nPeer distribution ({pset.upper()}), HirN DDD:")
        for m in MEASURES:
            pp = main[(main.measure == m) & main[pset]]
            cin = main[(main.measure == m) & (main.cbsa == CIN)].ddd.iloc[0]
            w(f"  {m:9s} n={len(pp):2d} q25={pp.ddd.quantile(.25):+.4f} median={pp.ddd.median():+.4f} "
              f"q75={pp.ddd.quantile(.75):+.4f} | Cincinnati {cin:+.4f} rank {int((pp.ddd < cin).sum()) + 1} "
              f"of {len(pp) + 1} | in bottom quartile: {bool(cin < pp.ddd.quantile(.25))}")
    w("\nOther outcomes and groupings, Cincinnati:")
    other = R[(R.cbsa == CIN) & ~((R.outcome == "HirN") & (R.young == "A03") & (R.grouping == "tercile"))]
    w(other[["outcome", "young", "grouping", "measure", "ddd", "perm_pctile"]].round(4).to_string(index=False))
    w("\nRate-shock checks 1 and 2, Cincinnati:")
    w(C[C.cbsa == CIN].drop(columns=["cbsa", "short"]).round(4).to_string(index=False))
    w("\nRate-shock check 3 (timing), Cincinnati: yearly gap relative to the 2018-19 mean")
    w(E[E.cbsa == CIN].pivot(index="year", columns="measure", values="gap_vs_pre").round(4).to_string())
    w("\nAll usable metros, HirN DDD by measure:")
    w(main.groupby("measure").ddd.describe()[["count", "25%", "50%", "75%"]].round(4).to_string())
    w("\nShare of metros with DDD < 0 and with DDD <= -0.05:")
    w(main.groupby("measure").ddd.agg(neg=lambda s: (s < 0).mean(), le05=lambda s: (s <= -0.05).mean()).round(3).to_string())
    w("\nShare of metros whose DDD is below their own permutation 10th percentile:")
    w(main.assign(sig=main.ddd < main.perm_p10).groupby("measure").sig.mean().round(3).to_string())
    w("\nH3 earnings of new stable hires, Cincinnati (ddd_earn; young and old monthly earnings in exposed industries):")
    w(H3[H3.cbsa == CIN].drop(columns=["cbsa", "short"]).round(3).to_string(index=False))
