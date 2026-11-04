"""Re-derive every published figure from the built datasets, printing the formula for each.

This is the audit trail behind CALCULATIONS.md. Every number quoted in the research paper,
the executive briefing or the workbook should appear here with the arithmetic that produced it.

Run:  python -I scripts/trace_numbers.py <base_dir>
"""
import csv
import os
import statistics as st
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "."


def load(name):
    with open(os.path.join(BASE, "data", name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    if s in ("", "-", "*", "**", "#", "nan", "None"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def head(n, title):
    print()
    print("=" * 96)
    print(f"{n}. {title}")
    print("=" * 96)


def line(label, value, formula):
    print(f"  {label:<52} {value:>18}   {formula}")


# ----------------------------------------------------------------------------------
occ = load("cincinnati_occupation_exposure.csv")
det = [r for r in occ if r["soc_level"] == "detailed"]
cin = [r for r in det if r["area"] == "Cincinnati MSA"]
nat = [r for r in det if r["area"] == "National"]

head(1, "OEWS May 2025 published totals (read directly, no arithmetic)")
for area in ("Cincinnati MSA", "Ohio", "Kentucky", "National"):
    tot = next(r for r in occ if r["area"] == area and r["soc_code"] == "00-0000")
    line(f"{area} total employment", f"{num(tot['employment']):,.0f}", "series datatype 01, occupation 000000")
    if area == "Cincinnati MSA":
        line("  median annual wage", f"${num(tot['annual_median']):,.0f}", "datatype 13")
        line("  mean annual wage", f"${num(tot['annual_mean']):,.0f}", "datatype 04")

head(2, "Detailed-occupation coverage  =  sum(detailed employment) / published total")
for area in ("Cincinnati MSA", "Ohio", "Kentucky", "National"):
    sub = [r for r in det if r["area"] == area]
    d = sum(num(r["employment"]) for r in sub)
    t = num(next(r for r in occ if r["area"] == area and r["soc_code"] == "00-0000")["employment"])
    line(f"{area}", f"{100*d/t:.1f}%", f"{d:,.0f} / {t:,.0f}  over {len(sub)} occupations")

head(3, "Exposure match rate  =  sum(employment where measure present) / sum(detailed employment)")
for area in ("Cincinnati MSA", "Ohio", "Kentucky", "National"):
    sub = [r for r in det if r["area"] == area]
    tot = sum(num(r["employment"]) for r in sub)
    for key, lbl in (("aioe", "AIOE"), ("observed_exposure", "observed exposure")):
        cov = sum(num(r["employment"]) for r in sub if num(r[key]) is not None)
        line(f"{area} — {lbl}", f"{100*cov/tot:.1f}%", f"{cov:,.0f} / {tot:,.0f}")

head(4, "Employment-weighted exposure  =  SUM(emp_i * score_i) / SUM(emp_i), over occupations where score exists")
def wmean(rows, key):
    pairs = [(num(r["employment"]), num(r[key])) for r in rows if num(r[key]) is not None]
    w = sum(e for e, _ in pairs)
    return sum(e * v for e, v in pairs) / w if w else float("nan")

res = {}
for area in ("Cincinnati MSA", "Ohio", "Kentucky", "National"):
    sub = [r for r in det if r["area"] == area]
    res[area] = {k: wmean(sub, k) for k in
                 ("aioe", "aioe_language_modeling", "aioe_image_generation", "observed_exposure")}
    r_ = res[area]
    line(area, f"{r_['aioe_language_modeling']:.4f}",
         f"AIOE {r_['aioe']:.4f} | IG {r_['aioe_image_generation']:.4f} | observed {r_['observed_exposure']:.4f}")
gap = res["Cincinnati MSA"]["aioe_language_modeling"] - res["National"]["aioe_language_modeling"]
line("Cincinnati minus National (LM-AIOE)", f"{gap:+.4f}",
     f"{res['Cincinnati MSA']['aioe_language_modeling']:.4f} - {res['National']['aioe_language_modeling']:.4f}")

head(5, "National thresholds — UNWEIGHTED across occupations, so a band means the same everywhere")
def cuts(key):
    v = sorted(num(r[key]) for r in nat if num(r[key]) is not None)
    return [v[int(len(v) * p)] for p in (0.25, 0.50, 0.75)], len(v)

lm_cuts, n_lm = cuts("aioe_language_modeling")
line("LM-AIOE quartile cut points", f"{lm_cuts[0]:.4f}", f"median {lm_cuts[1]:.4f}, Q3 {lm_cuts[2]:.4f}, n={n_lm}")
obs_vals = [num(r["observed_exposure"]) for r in nat if num(r["observed_exposure"]) is not None]
zeros = sum(1 for v in obs_vals if v == 0)
line("observed exposure national median", f"{st.median(obs_vals):.4f}", f"{zeros}/{len(obs_vals)} = {100*zeros/len(obs_vals):.1f}% are exactly 0")
lm_med, ob_med = lm_cuts[1], st.median(obs_vals)

head(6, "Cincinnati employment by observed-exposure band  =  SUM(emp) where band matches")
bands = [("0.00 none measured", lambda v: v == 0), ("0.00-0.10", lambda v: 0 < v <= .10),
         ("0.10-0.25", lambda v: .10 < v <= .25), ("0.25-0.40", lambda v: .25 < v <= .40),
         ("above 0.40", lambda v: v > .40)]
cov_rows = [r for r in cin if num(r["observed_exposure"]) is not None]
cov_tot = sum(num(r["employment"]) for r in cov_rows)
for nm, fn in bands:
    g = [r for r in cov_rows if fn(num(r["observed_exposure"]))]
    e = sum(num(r["employment"]) for r in g)
    wv = [(num(r["employment"]), num(r["annual_median"])) for r in g if num(r["annual_median"])]
    mw = sum(a * b for a, b in wv) / sum(a for a, _ in wv)
    line(nm, f"{e:,.0f}", f"{100*e/cov_tot:.1f}% of {cov_tot:,.0f} | emp-wtd median wage ${mw:,.0f} | {len(g)} occs")

head(7, "Cincinnati employment by LM-AIOE national quartile")
lmc = [r for r in cin if num(r["aioe_language_modeling"]) is not None]
lm_tot = sum(num(r["employment"]) for r in lmc)
def qband(v):
    return "Q1" if v <= lm_cuts[0] else "Q2" if v <= lm_cuts[1] else "Q3" if v <= lm_cuts[2] else "Q4"
for q in ("Q4", "Q3", "Q2", "Q1"):
    g = [r for r in lmc if qband(num(r["aioe_language_modeling"])) == q]
    e = sum(num(r["employment"]) for r in g)
    line(f"{q}{' (most exposed)' if q=='Q4' else ''}", f"{e:,.0f}", f"{100*e/lm_tot:.1f}% of {lm_tot:,.0f}")

head(8, "Four quadrants  =  split at national LM-AIOE median and national observed median")
both = [r for r in cin if num(r["aioe_language_modeling"]) is not None and num(r["observed_exposure"]) is not None]
q_tot = sum(num(r["employment"]) for r in both)
for hi_e in (True, False):
    for hi_u in (True, False):
        g = [r for r in both if (num(r["aioe_language_modeling"]) > lm_med) == hi_e
             and (num(r["observed_exposure"]) > ob_med) == hi_u]
        e = sum(num(r["employment"]) for r in g)
        wv = [(num(r["employment"]), num(r["annual_median"])) for r in g if num(r["annual_median"])]
        mw = sum(a * b for a, b in wv) / sum(a for a, _ in wv)
        nm = ("High" if hi_e else "Low") + " exposure / " + ("some" if hi_u else "no") + " use"
        line(nm, f"{e:,.0f}", f"{100*e/q_tot:.1f}% of {q_tot:,.0f} | median wage ${mw:,.0f} | {len(g)} occs")

head(9, "Wage quintiles  =  sort by median wage, cut at equal CUMULATIVE EMPLOYMENT (not equal occupations)")
cw = sorted([r for r in cin if num(r["annual_median"]) and num(r["employment"])],
            key=lambda r: num(r["annual_median"]))
tote = sum(num(r["employment"]) for r in cw)
cum = 0.0
for r in cw:
    e = num(r["employment"])
    cum += e
    r["_q"] = min(4, int(5 * (cum - e / 2) / tote))
for i in range(5):
    g = [r for r in cw if r["_q"] == i]
    e = sum(num(r["employment"]) for r in g)
    lo = min(num(r["annual_median"]) for r in g)
    hi = max(num(r["annual_median"]) for r in g)
    line(f"Q{i+1}  ${lo:,.0f}-${hi:,.0f}", f"{e:,.0f}",
         f"LM-AIOE {wmean(g,'aioe_language_modeling'):+.3f} | observed {wmean(g,'observed_exposure'):.3f}")

head(10, "ODJFS projections, Ohio portion (read directly from the workbook, then two ratios)")
proj = load("cincinnati_oh_projections_2022_2032.csv")
tot = next(r for r in proj if r["soc_code"] == "00-0000")
e22, e32 = num(tot["emp_2022"]), num(tot["emp_2032"])
g, x, t_, all_ = (num(tot["open_growth"]), num(tot["open_exits"]),
                  num(tot["open_transfers"]), num(tot["open_total"]))
line("2022 base", f"{e22:,.0f}", "published")
line("2032 projected", f"{e32:,.0f}", "published")
line("change", f"{e32-e22:+,.0f}", f"{e32:,.0f} - {e22:,.0f}  =  {100*(e32-e22)/e22:+.2f}%")
line("total annual openings", f"{all_:,.0f}", f"growth {g:,.0f} + exits {x:,.0f} + transfers {t_:,.0f}")
line("growth share of openings", f"{100*g/all_:.1f}%", f"{g:,.0f} / {all_:,.0f}")
line("replacement share", f"{100*(all_-g)/all_:.1f}%", f"({all_:,.0f} - {g:,.0f}) / {all_:,.0f}")

head(11, "Projected openings by exposure tercile (matched detailed occupations only)")
expmap = {r["soc_code"]: r for r in cin}
m = [(p, expmap[p["soc_code"]]) for p in proj
     if not p["soc_code"].endswith("0") and num(p["open_total"]) is not None
     and p["soc_code"] in expmap and num(expmap[p["soc_code"]]["aioe_language_modeling"]) is not None]
m.sort(key=lambda t: -num(t[1]["aioe_language_modeling"]))
n3 = len(m) // 3
tot_open = sum(num(p["open_total"]) for p, _ in m)
for lbl, sl in (("top third (most exposed)", m[:n3]), ("middle third", m[n3:2*n3]),
                ("bottom third", m[2*n3:])):
    o = sum(num(p["open_total"]) for p, _ in sl)
    gr = sum(num(p["open_growth"]) for p, _ in sl)
    a, b = sum(num(p["emp_2022"]) for p, _ in sl), sum(num(p["emp_2032"]) for p, _ in sl)
    line(lbl, f"{o:,.0f}", f"{100*o/tot_open:.1f}% of {tot_open:,.0f} | net {100*(b-a)/a:+.2f}% | growth-driven {100*gr/o:.1f}%")

head(12, "QCEW county employment and pay  (avg annual pay = total wages / employment)")
q = load("qcew_cincinnati_counties.csv")
tots = [r for r in q if r["agglvl_code"] == "70"]
for year in ("2024", "2025"):
    for state, lbl in (("OH", "Ohio 4-county"), ("KY", "Northern Kentucky 3-county")):
        g = [r for r in tots if r["year"] == year and r["state"] == state]
        e = sum(num(r["employment"]) for r in g)
        w = sum(num(r["total_annual_wages"]) for r in g)
        line(f"{year} {lbl}", f"{e:,.0f}", f"avg pay ${w/e:,.0f}  =  ${w:,.0f} / {e:,.0f}")
    g = [r for r in tots if r["year"] == year]
    e = sum(num(r["employment"]) for r in g)
    w = sum(num(r["total_annual_wages"]) for r in g)
    line(f"{year} seven-county total", f"{e:,.0f}", f"avg pay ${w/e:,.0f}")
for state, lbl in (("OH", "Ohio 4-county"), ("KY", "NKY 3-county")):
    a = sum(num(r["employment"]) for r in tots if r["year"] == "2024" and r["state"] == state)
    b = sum(num(r["employment"]) for r in tots if r["year"] == "2025" and r["state"] == state)
    line(f"{lbl} employment change", f"{100*(b-a)/a:+.2f}%", f"({b:,.0f} - {a:,.0f}) / {a:,.0f}")

head(13, "CES industry employment, September of each year (levels published in thousands)")
ces = load("cincinnati_ces_history.csv")
idx = {}
for r in ces:
    if r["seasonal"] == "U" and int(r["month"]) == 9:
        idx[(r["industry_code"], int(r["year"]))] = num(r["employment_thousands"])
names = {"00000000": "Total nonfarm", "55522000": "Credit intermediation",
         "60561300": "Employment services", "65620000": "Health care and social assistance",
         "50000000": "Information", "43400089": "Transportation and warehousing",
         "42000000": "Retail trade", "43481000": "Air transportation"}
for code, nm in names.items():
    a, b, c = idx.get((code, 2019)), idx.get((code, 2025)), idx.get((code, 2026))
    if None in (a, b, c):
        continue
    line(nm, f"{c*1000:,.0f}", f"vs 2019 {100*(c-a)/a:+.1f}%  |  vs 2025 {100*(c-b)/b:+.1f}%")
p22 = idx.get(("60561300", 2022))
p26 = idx.get(("60561300", 2026))
line("Employment services vs 2022 peak", f"{100*(p26-p22)/p22:+.1f}%", f"({p26*1000:,.0f} - {p22*1000:,.0f}) / {p22*1000:,.0f}")

head(14, "LAUS, September (published levels; rate = unemployment / labour force)")
laus = load("cincinnati_laus_history.csv")
for y in (2019, 2025, 2026):
    r = next((x for x in laus if int(x["year"]) == y and int(x["month"]) == 9), None)
    if r:
        lf, em, un = num(r["labor_force"]), num(r["employment"]), num(r["unemployment"])
        line(f"September {y}", f"{num(r['unemployment_rate']):.1f}%",
             f"LF {lf:,.0f} | employed {em:,.0f} | unemployed {un:,.0f} | check {100*un/lf:.2f}%")
a = next(x for x in laus if int(x["year"]) == 2025 and int(x["month"]) == 9)
b = next(x for x in laus if int(x["year"]) == 2026 and int(x["month"]) == 9)
line("employment change 2025-2026", f"{num(b['employment'])-num(a['employment']):+,.0f}", "September to September")
line("labour force change 2025-2026", f"{num(b['labor_force'])-num(a['labor_force']):+,.0f}", "September to September")

head(15, "Job postings — the ONE derived figure, stated as a calculation in the paper")
bpc = load("bpc_metro_ai_postings.csv")
c = next(r for r in bpc if r["metro"].startswith("Cincinnati"))
added, growth = num(c["ai_postings_added"]), num(c["ai_posting_growth_1yr_pct"])
base = added / (growth / 100)
line("Cincinnati AI postings added", f"{added:,.0f}", "published by BPC/Lightcast")
line("growth rate", f"{growth:.0f}%", "published by BPC/Lightcast")
line("implied prior-year base", f"{base:,.0f}", f"{added:,.0f} / ({growth:.0f}/100)   [DERIVED, not published]")
line("implied current total", f"{base+added:,.0f}", f"{base:,.0f} + {added:,.0f}   [DERIVED, not published]")

head(16, "Anthropic Economic Index — state level, read directly (no arithmetic)")
aei = load("aei_state_overall.csv")
for geo in ("Ohio", "Kentucky", "United States"):
    vals = {r["metric_id"]: r["value"] for r in aei if r["geography"] == geo and r["month"] == "2026-05-01"}
    line(geo, vals.get("usage_per_capita_index", "n/a"),
         f"automation {vals.get('collaboration_bucket_automation_pct','?')}% | "
         f"augmentation {vals.get('collaboration_bucket_augmentation_pct','?')}% | "
         f"work use {vals.get('use_case_work_pct','?')}%")

head(17, "Re-based to 2024 — industry and labour force (September to September, not seasonally adjusted)")
reb = load("cincinnati_rebased_2024.csv")
rb = {r["industry"]: r for r in reb}
BANK = "Credit Intermediation and Related Activities including Monetary Authorities - Central Bank"
for name, label in (("Total Nonfarm", "Total nonfarm"),
                    ("Federal Government", "Federal government"),
                    ("Transportation and Warehousing", "Transportation and warehousing"),
                    ("Information", "Information"),
                    (BANK, "Credit intermediation (banking)"),
                    ("Finance and Insurance", "Finance and insurance"),
                    ("Professional, Scientific, and Technical Services", "Professional/scientific/technical"),
                    ("Manufacturing", "Manufacturing"),
                    ("Health Care and Social Assistance", "Health care and social assistance"),
                    ("Specialty Trade Contractors", "Specialty trade contractors")):
    r = rb.get(name)
    if not r:
        continue
    b, e = num(r["sep_2024"]), num(r["sep_2026"])
    line(label, f"{(e/b-1)*100:+.1f}%",
         f"({e:,.1f} / {b:,.1f} - 1) x 100    vs-2019 {num(r['pct_change_from_2019']):+.1f}%"
         if r["pct_change_from_2019"] else f"({e:,.1f} / {b:,.1f} - 1) x 100")

tn = rb["Total Nonfarm"]
b, e = num(tn["sep_2024"]), num(tn["sep_2026"])
line("total nonfarm jobs added", f"{(e-b)*1000:,.0f}", f"({e:,.1f} - {b:,.1f}) x 1,000")
bk = rb[BANK]
pre = (num(bk["sep_2019"]) - num(bk["sep_2024"])) / (num(bk["sep_2019"]) - num(bk["sep_2026"])) * 100
line("share of banking fall predating 2024", f"{pre:.1f}%",
     f"({num(bk['sep_2019']):.1f} - {num(bk['sep_2024']):.1f}) / ({num(bk['sep_2019']):.1f} - {num(bk['sep_2026']):.1f})")

laus = load("cincinnati_laus_history.csv")
pick = {(r["year"], r["month"]): r for r in laus}
a, z = pick.get(("2024", "9")), pick.get(("2026", "9"))
if a and z:
    line("labour force change", f"{num(z['labor_force'])-num(a['labor_force']):,.0f}",
         f"{num(z['labor_force']):,.0f} - {num(a['labor_force']):,.0f}   Sept 2024 to Sept 2026")
    line("employment change", f"{num(z['employment'])-num(a['employment']):,.0f}",
         f"{num(z['employment']):,.0f} - {num(a['employment']):,.0f}")
    line("unemployment rate", f"{num(z['unemployment_rate']):.1f}%",
         f"from {num(a['unemployment_rate']):.1f}% — fell while BOTH employment and labour force fell")

print()
print("=" * 96)
print("End of trace. Every figure above is recomputed from data/ at run time.")
print("=" * 96)
