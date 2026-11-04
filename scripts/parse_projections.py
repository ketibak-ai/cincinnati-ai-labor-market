"""Parse ODJFS long-term occupational projections (Ohio portion of the Cincinnati MSA)
and join them to the AI-exposure measures.

Source: https://ohiolmi.com/_docs/PROJ/MSA/LTOP_Cincinnati2032.xlsx
        ODJFS Bureau of Labor Market Information, June 2025. Projection period 2022-2032.
Geography caveat: ODJFS equates its "Cincinnati MSA" projections with the Southwest Ohio
JobsOhio region, i.e. OHIO COUNTIES ONLY. Northern Kentucky and Indiana are excluded.
"Annual openings" are projected average annual openings (growth + exits + transfers),
NOT current job vacancies.
"""
import csv, os, sys, openpyxl

B = sys.argv[1]
wb = openpyxl.load_workbook(os.path.join(B, "raw", "proj", "LTOP_Cincinnati2032.xlsx"),
                            read_only=True, data_only=True)
ws = wb["Occupational Detail"]
out = []
for row in ws.iter_rows(min_row=7, values_only=True):
    soc = row[0]
    if not soc or not isinstance(soc, str) or len(soc) != 7 or soc[2] != "-":
        continue
    def n(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    out.append({
        "soc_code": soc, "occupation": row[1],
        "emp_2022": n(row[2]), "emp_2032": n(row[3]),
        "chg": n(row[4]), "pct_chg": n(row[5]),
        "open_growth": n(row[6]), "open_exits": n(row[7]),
        "open_transfers": n(row[8]), "open_total": n(row[9]),
        "median_wage_may2023_raw": row[10],
    })
wb.close()

with open(os.path.join(B, "data", "cincinnati_oh_projections_2022_2032.csv"), "w",
          newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader(); w.writerows(out)
print(f"parsed {len(out)} projection rows")

# ---- join to exposure ----
exp = {}
for r in csv.DictReader(open(os.path.join(B, "data", "cincinnati_occupation_exposure.csv"), encoding="utf-8")):
    if r["area"] == "Cincinnati MSA":
        exp[r["soc_code"]] = r

def f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

det = [r for r in out if not r["soc_code"].endswith("0") and r["open_total"] is not None]
tot = [r for r in out if r["soc_code"] == "00-0000"]
print(f"\nODJFS Cincinnati (Ohio portion) totals: 2022={tot[0]['emp_2022']:,.0f}  "
      f"2032={tot[0]['emp_2032']:,.0f}  change={tot[0]['chg']:+,.0f} ({100*tot[0]['pct_chg']:+.2f}%)")
print(f"  projected average annual openings, all occupations: {tot[0]['open_total']:,.0f}")
print(f"    of which growth {tot[0]['open_growth']:,.0f} | exits {tot[0]['open_exits']:,.0f} | transfers {tot[0]['open_transfers']:,.0f}")

matched = [(r, exp[r["soc_code"]]) for r in det if r["soc_code"] in exp]
print(f"\ndetailed occupations in projections: {len(det)}; matched to OEWS exposure: {len(matched)}")

lm = [(p, e) for p, e in matched if f(e["aioe_language_modeling"]) is not None]
lm.sort(key=lambda t: -f(t[1]["aioe_language_modeling"]))
tot_open = sum(p["open_total"] for p, _ in lm)
n = len(lm)
print(f"\nProjected annual openings by LM-AIOE exposure tercile (matched set, {tot_open:,.0f} openings/yr)")
for lbl, sl in [("Top third (most exposed)", lm[:n//3]),
                ("Middle third", lm[n//3:2*n//3]),
                ("Bottom third (least exposed)", lm[2*n//3:])]:
    o = sum(p["open_total"] for p, _ in sl)
    g = sum(p["open_growth"] for p, _ in sl)
    e22 = sum(p["emp_2022"] for p, _ in sl)
    e32 = sum(p["emp_2032"] for p, _ in sl)
    print(f"  {lbl:30s} openings/yr {o:8,.0f} ({100*o/tot_open:4.1f}%)  "
          f"net growth 2022-32 {100*(e32-e22)/e22:+5.2f}%  growth-driven openings {100*g/o:4.1f}%")

print("\nLargest projected DECLINES, Cincinnati (Ohio portion), 2022-2032, with exposure")
dec = sorted([(p, e) for p, e in matched if p["chg"] is not None], key=lambda t: t[0]["chg"])[:18]
print(f"  {'Chg':>7s} {'%':>7s} {'LM':>6s} {'Obs':>6s}  Occupation")
for p, e in dec:
    lmv = f(e["aioe_language_modeling"]); ob = f(e["observed_exposure"])
    print(f"  {p['chg']:7,.0f} {100*p['pct_chg']:6.1f}% "
          f"{(lmv if lmv is not None else float('nan')):6.2f} {(ob if ob is not None else float('nan')):6.2f}  {p['occupation'][:46]}")
