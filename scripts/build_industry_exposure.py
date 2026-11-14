"""Industry AI exposure for the hiring test (PREREGISTRATION.md section 4).

Industry exposure = employment-weighted mean occupational exposure within each NAICS 3-digit
industry, using NATIONAL OEWS May 2022 industry staffing patterns (the last reference period
before ChatGPT). Four occupational measures, each run separately:
  lm_aioe   Felten, Raj & Seamans (2023) language-modelling AIOE          (potential)
  eloundou  Eloundou et al. (2024), human-rated beta                       (potential)
  aei       Anthropic Economic Index observed exposure                     (revealed use)
  ms        Microsoft Research AI applicability score (Tomlinson et al.)   (revealed use)
Exposed = top tercile of industries, weighted by national 2022 industry employment;
less exposed = bottom tercile. Quartiles are kept for the sensitivity check.

Outputs: data/occupation_exposure_4measures.csv ; data/industry_exposure_naics3.csv
"""
import os
import numpy as np, pandas as pd, openpyxl

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
MEASURES = ["lm_aioe", "eloundou", "aei", "ms"]


def xlsx_col(path, sheet, keycol=0, valcol=2):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for i, row in enumerate(wb[sheet].iter_rows(values_only=True)):
        if i and row[keycol] is not None and row[valcol] is not None:
            try: out[str(row[keycol]).strip()] = float(row[valcol])
            except ValueError: pass
    return out

lm = pd.Series(xlsx_col(P("raw", "aioe", "Language Modeling AIOE and AIIE.xlsx"), "LM AIOE"), name="lm_aioe")
el = pd.read_csv(P("raw", "exposure", "eloundou_occ_level.csv"))
el["soc"] = el["O*NET-SOC Code"].str[:7]
el_h = el.groupby("soc").human_rating_beta.mean().rename("eloundou")          # primary: human-rated beta
el_g = el.groupby("soc").dv_rating_beta.mean().rename("eloundou_gpt")         # sensitivity: GPT-4-rated beta
aei = pd.read_csv(P("raw", "aei", "job_exposure.csv")).set_index("occ_code").observed_exposure.rename("aei")
ms = pd.read_csv(P("raw", "exposure", "ms_ai_applicability_scores.csv")).set_index("SOC Code").ai_applicability_score.rename("ms")
# Felten et al. publish on 2010 SOC codes; OEWS 2022 uses 2018 SOC. Where a 2018 code has no
# direct score, take the mean score of the 2010 codes the official BLS crosswalk maps to it.
xw = pd.DataFrame([r for i, r in enumerate(openpyxl.load_workbook(
    P("raw", "exposure", "soc_2010_to_2018_crosswalk.xlsx"), read_only=True)["Sorted by 2010"].iter_rows(values_only=True))
    if i > 8 and r[0]], columns=["soc10", "t10", "soc18", "t18"])
xw["v"] = xw.soc10.map(lm)
lm18 = xw.dropna(subset=["v"]).groupby("soc18").v.mean()
lm = lm.combine_first(lm18).rename("lm_aioe")

occ = pd.concat([lm, el_h, el_g, aei, ms], axis=1)
occ.index.name = "soc"
# OEWS reports some occupations only as a combined code ending in 0 (e.g. 31-1120 = 31-1121 +
# 31-1122). Where a measure has no score for such a code, use the mean of the detailed codes
# that share its first six characters.
oews_codes = set(pd.read_csv(P("raw", "oes", "nat3d_M2022.csv"), dtype=str, usecols=["OCC_CODE", "O_GROUP"])
                 .query("O_GROUP == 'detailed'").OCC_CODE)
add = {}
for c in sorted(oews_codes):
    if c.endswith("0"):
        fam = occ[occ.index.str.startswith(c[:6]) & (occ.index != c)]
        if len(fam):
            add[c] = fam.mean()
fb = pd.DataFrame(add).T
occ = occ.combine_first(fb) if len(fb) else occ
occ.index.name = "soc"
occ.to_csv(P("data", "occupation_exposure_4measures.csv"))

st = pd.read_csv(P("raw", "oes", "nat3d_M2022.csv"), dtype=str)
st = st[(st.O_GROUP == "detailed") | (st.O_GROUP == "total")].copy()
st["emp"] = pd.to_numeric(st.TOT_EMP.str.replace(",", ""), errors="coerce")
st["naics3"] = st.NAICS.str[:3]
tot = st[st.O_GROUP == "total"].groupby("naics3").emp.sum().rename("oews2022_emp")
det = st[st.O_GROUP == "detailed"].dropna(subset=["emp"]).merge(occ, left_on="OCC_CODE", right_index=True, how="left")
title = st.drop_duplicates("naics3").set_index("naics3").NAICS_TITLE

rows = {}
for n3, g in det.groupby("naics3"):
    r = {"detailed_emp": g.emp.sum()}
    for m in MEASURES + ["eloundou_gpt"]:
        ok = g[m].notna()
        r[m] = np.average(g.loc[ok, m], weights=g.loc[ok, "emp"]) if ok.any() else np.nan
        r[m + "_cov"] = g.loc[ok, "emp"].sum() / g.emp.sum()
    rows[n3] = r
ind = pd.DataFrame(rows).T.join(tot).join(title.rename("title"))
ind = ind[ind.index.str.match(r"^\d{3}$") & ~ind.index.isin(["999"])]          # drop government (999)


def wq(v, w, k):
    """Group 1..k by exposure, cut where cumulative national employment reaches 1/k, 2/k, ..."""
    o = v.dropna().sort_values().index
    cum = (w[o].cumsum() - w[o] / 2) / w[o].sum()
    return np.ceil(cum * k).clip(1, k).astype(int).reindex(v.index)

for m in MEASURES + ["eloundou_gpt"]:
    ind[m + "_tercile"] = wq(ind[m], ind.oews2022_emp, 3)
    ind[m + "_quartile"] = wq(ind[m], ind.oews2022_emp, 4)
ind.index.name = "naics3"
ind.to_csv(P("data", "industry_exposure_naics3.csv"))
print(len(ind), "NAICS 3-digit private industries")
print("min employment coverage by measure:", {m: round(ind[m + "_cov"].min(), 3) for m in MEASURES})
print("rank correlation of industry exposure across measures:\n", ind[MEASURES].corr(method="spearman").round(2))
for m in MEASURES:
    top = ind[ind[m + "_tercile"] == 3].sort_values("oews2022_emp", ascending=False)
    print(m, "exposed tercile, largest:", "; ".join(f"{i} {t[:28]}" for i, t in top.title.head(6).items()))
print("exposed on all four:", sorted(ind[(ind[[m + '_tercile' for m in MEASURES]] == 3).all(axis=1)].index))
print("less exposed on all four:", sorted(ind[(ind[[m + '_tercile' for m in MEASURES]] == 1).all(axis=1)].index))
