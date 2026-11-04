"""Distributional analysis of AI exposure across Cincinnati MSA employment."""
import csv, os, sys, statistics as st

BASE = sys.argv[1]
rows = [r for r in csv.DictReader(open(os.path.join(BASE, "data", "cincinnati_occupation_exposure.csv"), encoding="utf-8"))]
def f(v):
    return float(v) if v not in ("", None) else None
for r in rows:
    for k in ("employment", "annual_median", "annual_mean", "location_quotient",
              "aioe", "aioe_language_modeling", "aioe_image_generation", "observed_exposure"):
        r[k] = f(r[k])

cin = [r for r in rows if r["area"] == "Cincinnati MSA"]
nat = [r for r in rows if r["area"] == "National"]

# National UNWEIGHTED occupation distribution sets the thresholds, so "high exposure"
# means the same thing in every geography.
def quartile_cuts(key):
    vals = sorted(r[key] for r in nat if r[key] is not None)
    n = len(vals)
    return [vals[int(n * q)] for q in (0.25, 0.50, 0.75)]

print("=" * 78)
print("TABLE 1. Cincinnati MSA employment by national AI-exposure quartile (May 2025)")
print("=" * 78)
for key, label in [("aioe", "AIOE (all AI)"), ("aioe_language_modeling", "AIOE (language modeling)"),
                   ("observed_exposure", "Observed exposure (Claude usage)")]:
    c = quartile_cuts(key)
    buckets = {1: [], 2: [], 3: [], 4: []}
    for r in cin:
        v = r[key]
        if v is None:
            continue
        q = 1 if v <= c[0] else 2 if v <= c[1] else 3 if v <= c[2] else 4
        buckets[q].append(r)
    tot = sum(r["employment"] for b in buckets.values() for r in b)
    print(f"\n  {label}   (occupations covering {tot:,.0f} Cincinnati jobs)")
    print(f"  {'Quartile':24s} {'Employment':>11s} {'% of cov.':>9s} {'Median wage':>12s}")
    for q in (4, 3, 2, 1):
        b = buckets[q]
        e = sum(r["employment"] for r in b)
        wv = [(r["employment"], r["annual_median"]) for r in b if r["annual_median"]]
        mw = sum(x * y for x, y in wv) / sum(x for x, _ in wv) if wv else float("nan")
        nm = {4: "Q4 highest exposure", 3: "Q3", 2: "Q2", 1: "Q1 lowest exposure"}[q]
        print(f"  {nm:24s} {e:11,.0f} {100*e/tot:8.1f}% {mw:12,.0f}")

print("\n" + "=" * 78)
print("TABLE 2. Largest Cincinnati occupations in the top national exposure quartile")
print("         (LM-AIOE, i.e. generative-AI/language-model exposure)")
print("=" * 78)
c = quartile_cuts("aioe_language_modeling")[2]
top = sorted([r for r in cin if r["aioe_language_modeling"] is not None and r["aioe_language_modeling"] > c],
             key=lambda r: -r["employment"])[:25]
print(f"{'SOC':9s} {'Occupation':44s} {'Emp':>8s} {'LQ':>5s} {'MedWage':>8s} {'LM':>6s} {'Obs':>6s}")
for r in top:
    print(f"{r['soc_code']:9s} {r['occupation'][:44]:44s} {r['employment']:8,.0f} "
          f"{(r['location_quotient'] or 0):5.2f} {(r['annual_median'] or 0):8,.0f} "
          f"{r['aioe_language_modeling']:6.2f} {(r['observed_exposure'] or float('nan')):6.3f}")

print("\n" + "=" * 78)
print("TABLE 3. Exposure gradient across the Cincinnati wage distribution")
print("=" * 78)
wr = [r for r in cin if r["annual_median"] and r["aioe_language_modeling"] is not None]
wr.sort(key=lambda r: r["annual_median"])
tot = sum(r["employment"] for r in wr)
cum, edges, cuts = 0.0, [], [0.2, 0.4, 0.6, 0.8]
bucket, bi = [], 0
groups = [[] for _ in range(5)]
for r in wr:
    cum += r["employment"]
    idx = min(4, int(5 * (cum - r["employment"] / 2) / tot))
    groups[idx].append(r)
print(f"{'Wage quintile':16s} {'Emp':>10s} {'Wage range':>22s} {'LM-AIOE':>8s} {'Observed':>9s}")
for i, g in enumerate(groups):
    if not g:
        continue
    e = sum(r["employment"] for r in g)
    lm = sum(r["employment"] * r["aioe_language_modeling"] for r in g) / e
    ob = [(r["employment"], r["observed_exposure"]) for r in g if r["observed_exposure"] is not None]
    obm = sum(x * y for x, y in ob) / sum(x for x, _ in ob) if ob else float("nan")
    print(f"Q{i+1} {'(lowest)' if i==0 else '(highest)' if i==4 else '':11s} {e:10,.0f} "
          f"{min(r['annual_median'] for r in g):>10,.0f}-{max(r['annual_median'] for r in g):<10,.0f} "
          f"{lm:8.3f} {obm:9.3f}")

print("\n" + "=" * 78)
print("TABLE 4. Exposure vs. observed use: the four quadrants")
print("         (national medians split each axis; Cincinnati employment shown)")
print("=" * 78)
lm_med = st.median([r["aioe_language_modeling"] for r in nat if r["aioe_language_modeling"] is not None])
ob_med = st.median([r["observed_exposure"] for r in nat if r["observed_exposure"] is not None])
quad = {"High exp / High use": [], "High exp / Low use": [],
        "Low exp / High use": [], "Low exp / Low use": []}
for r in cin:
    if r["aioe_language_modeling"] is None or r["observed_exposure"] is None:
        continue
    hi_e = r["aioe_language_modeling"] > lm_med
    hi_u = r["observed_exposure"] > ob_med
    k = ("High exp / " if hi_e else "Low exp / ") + ("High use" if hi_u else "Low use")
    quad[k].append(r)
tot = sum(len(v) and sum(x["employment"] for x in v) or 0 for v in quad.values())
print(f"  national medians: LM-AIOE={lm_med:.4f}  observed={ob_med:.4f}\n")
print(f"  {'Quadrant':22s} {'Occs':>5s} {'Employment':>11s} {'% cov':>7s} {'MedWage':>9s}")
for k in ["High exp / High use", "High exp / Low use", "Low exp / High use", "Low exp / Low use"]:
    v = quad[k]
    e = sum(r["employment"] for r in v)
    wv = [(r["employment"], r["annual_median"]) for r in v if r["annual_median"]]
    mw = sum(a * b for a, b in wv) / sum(a for a, _ in wv) if wv else float("nan")
    print(f"  {k:22s} {len(v):5d} {e:11,.0f} {100*e/tot:6.1f}% {mw:9,.0f}")
for k in ["High exp / High use", "High exp / Low use"]:
    print(f"\n  Largest Cincinnati occupations — {k}:")
    for r in sorted(quad[k], key=lambda r: -r["employment"])[:10]:
        print(f"    {r['employment']:8,.0f}  {r['occupation'][:50]:50s} ${(r['annual_median'] or 0):,.0f}")
