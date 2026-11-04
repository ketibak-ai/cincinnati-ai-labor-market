"""Parse Cincinnati MSA CES (industry employment) and LAUS (unemployment) history.

Sources: https://download.bls.gov/pub/time.series/sm/sm.data.36.Ohio   (filtered to area 17140)
         https://download.bls.gov/pub/time.series/la/la.data.42.Ohio   (filtered to MT3917140)
CES series: SM + seasonal + state(2) + area(5) + industry(8) + datatype(2)
LAUS measure codes: 03 unemployment rate, 04 unemployment, 05 employment, 06 labor force
"""
import csv, os, sys
B = sys.argv[1]

lab = {}
for r in csv.DictReader(open(os.path.join(B, "raw", "ces", "sm.industry"), encoding="utf-8", errors="replace"), delimiter="\t"):
    lab[r["industry_code"].strip()] = r["industry_name"].strip()

ces = {}
for line in open(os.path.join(B, "raw", "ces", "cincinnati_ces.txt"), encoding="utf-8", errors="replace"):
    p = line.split("\t")
    if len(p) < 4:
        continue
    sid = p[0].strip()
    if len(sid) != 20 or sid[18:20] != "01":
        continue
    seas, ind = sid[2], sid[10:18]
    per = p[2].strip()
    if not per.startswith("M") or per == "M13":
        continue
    try:
        v = float(p[3].strip())
    except ValueError:
        continue
    ces.setdefault((seas, ind), {})[(int(p[1]), int(per[1:]))] = v

rows = []
for (seas, ind), d in ces.items():
    for (y, m), v in d.items():
        rows.append({"seasonal": seas, "industry_code": ind,
                     "industry_name": lab.get(ind, ""), "year": y, "month": m,
                     "employment_thousands": v})
rows.sort(key=lambda r: (r["seasonal"], r["industry_code"], r["year"], r["month"]))
with open(os.path.join(B, "data", "cincinnati_ces_history.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"CES rows written: {len(rows):,}")

laus = {}
MEAS = {"03": "unemployment_rate", "04": "unemployment", "05": "employment", "06": "labor_force"}
for line in open(os.path.join(B, "raw", "laus", "cincinnati_laus.txt"), encoding="utf-8", errors="replace"):
    p = line.split("\t")
    if len(p) < 4:
        continue
    sid = p[0].strip()
    meas = sid[-2:]
    if meas not in MEAS:
        continue
    per = p[2].strip()
    if not per.startswith("M") or per == "M13":
        continue
    try:
        v = float(p[3].strip())
    except ValueError:
        continue
    laus.setdefault((int(p[1]), int(per[1:])), {})[MEAS[meas]] = v
lr = [{"year": y, "month": m, **d} for (y, m), d in sorted(laus.items())]
with open(os.path.join(B, "data", "cincinnati_laus_history.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["year", "month", "labor_force", "employment", "unemployment", "unemployment_rate"])
    w.writeheader()
    for r in lr:
        w.writerow({k: r.get(k, "") for k in w.fieldnames})
print(f"LAUS rows written: {len(lr):,}  latest: {lr[-1]}")

# ---------- trend table: NSA industry employment, same month each year ----------
KEY = ["00000000","15000000","30000000","40000000","43400089","43481000","50000000",
       "55000000","55522000","55524000","60000000","60540000","60550000","60560000",
       "60561300","65000000","65620000","70000000","80000000","90000000","42000000","41000000"]
def pick(ind, y, m):
    return ces.get(("U", ind), {}).get((y, m))

latest = max(k for k in ces[("U", "00000000")])
ly, lm = latest
print(f"\nLatest CES month: {ly}-{lm:02d}\n")
print("TABLE. Cincinnati MSA industry employment (thousands, not seasonally adjusted), month of "
      f"{lm:02d}\n")
print(f"{'Industry':54s} {'2019':>8s} {'2022':>8s} {str(ly-1):>8s} {str(ly):>8s} {'1yr%':>7s} {'vs2019%':>8s}")
print("-" * 104)
for ind in KEY:
    a, b, c, d = pick(ind, 2019, lm), pick(ind, 2022, lm), pick(ind, ly-1, lm), pick(ind, ly, lm)
    if d is None:
        continue
    y1 = 100*(d-c)/c if c else float('nan')
    y5 = 100*(d-a)/a if a else float('nan')
    nm = lab.get(ind, ind)[:54]
    print(f"{nm:54s} {(a if a else 0):8.1f} {(b if b else 0):8.1f} {c:8.1f} {d:8.1f} {y1:+6.1f}% {y5:+7.1f}%")
