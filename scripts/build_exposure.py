"""Merge May 2025 OEWS employment with published AI-exposure measures.

Inputs
  data/oes_may2025_cincinnati_panel.csv          built by parse_oes.py from BLS oe.data.0.Current
  raw/aioe/AIOE_DataAppendix.xlsx                Felten, Raj & Seamans (2021), Appendix A: AIOE by 6-digit SOC
  raw/aioe/Language Modeling AIOE and AIIE.xlsx  Felten, Raj & Seamans (2023): language-model AIOE
  raw/aioe/Image Generation AIOE and AIIE.xlsx   Felten, Raj & Seamans (2023): image-generation AIOE
  raw/aei/job_exposure.csv                       Anthropic Economic Index: observed task exposure by SOC

Output
  data/cincinnati_occupation_exposure.csv

All SOC aggregation levels are retained so that totals and major groups remain available, but
exposure measures are joined ONLY to detailed occupations. Aggregates would otherwise be
double-counted in any employment-weighted statistic.
"""
import csv
import os
import sys

import openpyxl

BASE = sys.argv[1]
D = lambda *p: os.path.join(BASE, *p)


def xlsx_col(path, sheet, keycol=0, valcol=2):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    out = {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        k, v = row[keycol], row[valcol]
        if k is None or v is None:
            continue
        try:
            out[str(k).strip()] = float(v)
        except ValueError:
            continue
    wb.close()
    return out


aioe = xlsx_col(D("raw", "aioe", "AIOE_DataAppendix.xlsx"), "Appendix A")
lm = xlsx_col(D("raw", "aioe", "Language Modeling AIOE and AIIE.xlsx"), "LM AIOE")
ig = xlsx_col(D("raw", "aioe", "Image Generation AIOE and AIIE.xlsx"), "IG AIOE")

obs = {}
with open(D("raw", "aei", "job_exposure.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(f):
        try:
            obs[row["occ_code"].strip()] = float(row["observed_exposure"])
        except ValueError:
            pass


def num(s):
    s = (s or "").strip().replace(",", "")
    if s in ("", "-", "*", "**", "#"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


rows = list(csv.DictReader(open(D("data", "oes_may2025_cincinnati_panel.csv"), encoding="utf-8")))

out = []
for r in rows:
    emp = num(r["employment"])
    if emp is None:
        continue
    soc = r["soc_code"]
    detailed = r["soc_level"] == "detailed"
    out.append({
        "area": r["area"], "soc_code": soc, "occupation": r["occupation"],
        "soc_level": r["soc_level"],
        "employment": emp,
        "annual_median": num(r["annual_median"]),
        "annual_mean": num(r["annual_mean"]),
        "location_quotient": num(r["location_quotient"]),
        "emp_per_1000": num(r["emp_per_1000"]),
        "aioe": aioe.get(soc) if detailed else None,
        "aioe_language_modeling": lm.get(soc) if detailed else None,
        "aioe_image_generation": ig.get(soc) if detailed else None,
        "observed_exposure": obs.get(soc) if detailed else None,
    })

with open(D("data", "cincinnati_occupation_exposure.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

AREAS = ["Cincinnati MSA", "Ohio", "Kentucky", "National"]

print("Match rates on DETAILED occupations "
      "(share of detailed-occupation employment with a non-missing measure)\n")
hdr = f"{'area':16s} {'detail occ':>10s} {'emp covered':>12s} {'AIOE':>7s} {'LM-AIOE':>8s} {'Observed':>9s}"
print(hdr)
print("-" * len(hdr))
for area in AREAS:
    sub = [r for r in out if r["area"] == area and r["soc_level"] == "detailed"]
    tot = sum(r["employment"] for r in sub)
    cov = lambda k: 100 * sum(r["employment"] for r in sub if r[k] is not None) / tot
    print(f"{area:16s} {len(sub):10d} {tot:12,.0f} {cov('aioe'):6.1f}% "
          f"{cov('aioe_language_modeling'):7.1f}% {cov('observed_exposure'):8.1f}%")

print("\nEmployment-weighted mean exposure over detailed occupations "
      "(AIOE standardised across occupations: mean 0, sd 1)\n")
hdr2 = f"{'area':16s} {'AIOE':>8s} {'LM-AIOE':>9s} {'IG-AIOE':>9s} {'Observed':>9s}"
print(hdr2)
print("-" * len(hdr2))
res = {}
for area in AREAS:
    sub = [r for r in out if r["area"] == area and r["soc_level"] == "detailed"]
    vals = []
    for k in ("aioe", "aioe_language_modeling", "aioe_image_generation", "observed_exposure"):
        s = [(r["employment"], r[k]) for r in sub if r[k] is not None]
        w_ = sum(e for e, _ in s)
        vals.append(sum(e * v for e, v in s) / w_ if w_ else float("nan"))
    res[area] = vals
    print(f"{area:16s} {vals[0]:8.4f} {vals[1]:9.4f} {vals[2]:9.4f} {vals[3]:9.4f}")

g = [res["Cincinnati MSA"][i] - res["National"][i] for i in range(4)]
print("\nCincinnati minus National:")
print(f"  AIOE {g[0]:+.4f}   LM-AIOE {g[1]:+.4f}   IG-AIOE {g[2]:+.4f}   Observed {g[3]:+.4f}")

print("\nSanity check - published totals vs sum of detailed occupations:")
for area in AREAS:
    t = next((r["employment"] for r in out if r["area"] == area and r["soc_level"] == "total"), None)
    d = sum(r["employment"] for r in out if r["area"] == area and r["soc_level"] == "detailed")
    print(f"  {area:16s} published total {t:12,.0f}   detailed sum {d:12,.0f}   "
          f"detailed covers {100*d/t:5.1f}%")
