"""Re-base the study's historical comparisons to 2024.

The study's analytical window begins in 2024 rather than 2019. This matters for an
AI study: a 2019 baseline runs through the pandemic collapse and recovery, so every
"change since 2019" conflates a once-in-a-century labour shock with whatever
generative AI has done since. A 2024 baseline brackets the generative-AI period
roughly -- broad enterprise deployment begins in 2023-24 -- and removes the pandemic
round trip from the comparison.

Three of the study's inputs have no 2024 edition and are NOT re-based:
  * OEWS occupational employment and wages  -- single vintage, May 2025
  * ODJFS long-term projections            -- fixed base year 2022, horizon 2032
  * Anthropic Economic Index               -- released for April and May 2026 only
Those stay as they are and are labelled single-vintage wherever they appear.

Method notes
------------
Industry comparisons use NOT SEASONALLY ADJUSTED series compared same-month
(September to September). BLS publishes a seasonally adjusted metro series only for
Total Nonfarm, so an adjusted industry panel does not exist; comparing like months
cancels seasonality without needing adjustment. Total Nonfarm is additionally
reported on the adjusted series where that is available.

Usage:  python -I scripts/rebase_2024.py .
"""

import csv
import io
import os
import sys
import collections

BASE_YEAR = 2024
PRIOR_BASE = 2019          # the baseline being replaced, kept for the contrast column
COMPARE_MONTH = 9          # September: latest month with data in every year used


def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def pct(new, old):
    """Percent change, old -> new. Returns None when the base is missing or zero."""
    if old in (None, 0) or new is None:
        return None
    return (new / old - 1.0) * 100.0


def load_ces(root):
    """industry -> {(year, month): employment_in_thousands} for unadjusted series."""
    rows = read(os.path.join(root, "data", "cincinnati_ces_history.csv"))
    panel = collections.defaultdict(dict)
    adjusted = collections.defaultdict(dict)
    for r in rows:
        try:
            value = float(r["employment_thousands"])
        except (TypeError, ValueError):
            continue
        key = (int(r["year"]), int(r["month"]))
        if r["seasonal"] == "U":
            panel[r["industry_name"]][key] = value
        else:
            adjusted[r["industry_name"]][key] = value
    return panel, adjusted


def latest_september(panel):
    years = {y for series in panel.values() for (y, m) in series if m == COMPARE_MONTH}
    return max(years)


def industry_table(panel, end_year):
    out = []
    for name, series in panel.items():
        base = series.get((BASE_YEAR, COMPARE_MONTH))
        prior = series.get((PRIOR_BASE, COMPARE_MONTH))
        end = series.get((end_year, COMPARE_MONTH))
        if base is None or end is None:
            continue
        out.append({
            "industry": name,
            "sep_%d" % PRIOR_BASE: prior,
            "sep_%d" % BASE_YEAR: base,
            "sep_%d" % end_year: end,
            "pct_change_from_%d" % BASE_YEAR: pct(end, base),
            "pct_change_from_%d" % PRIOR_BASE: pct(end, prior),
            "jobs_change_from_%d_thousands" % BASE_YEAR: round(end - base, 1),
        })
    out.sort(key=lambda r: r["pct_change_from_%d" % BASE_YEAR])
    return out


def unemployment(root, end_year):
    rows = read(os.path.join(root, "data", "cincinnati_laus_history.csv"))
    by_year = collections.defaultdict(list)
    monthly = {}
    for r in rows:
        try:
            rate = float(r["unemployment_rate"])
            lf = float(r["labor_force"])
        except (TypeError, ValueError):
            continue
        y, m = int(r["year"]), int(r["month"])
        by_year[y].append(rate)
        monthly[(y, m)] = {"rate": rate, "labor_force": lf}
    annual = {y: sum(v) / len(v) for y, v in by_year.items() if len(v) == 12}
    return {
        "annual_average": annual,
        "sep_base": monthly.get((BASE_YEAR, COMPARE_MONTH)),
        "sep_end": monthly.get((end_year, COMPARE_MONTH)),
        "sep_prior": monthly.get((PRIOR_BASE, COMPARE_MONTH)),
    }


def counties(root):
    rows = read(os.path.join(root, "data", "qcew_cincinnati_counties.csv"))
    keep = [r for r in rows
            if r["agglvl_code"] == "70" and r["industry_code"] == "10"]
    by_county = collections.defaultdict(dict)
    for r in keep:
        try:
            by_county[(r["county"], r["state"], r["portion"])][int(r["year"])] = {
                "employment": int(r["employment"]),
                "avg_annual_pay": int(r["avg_annual_pay"]),
                "establishments": int(r["establishments"]),
            }
        except (TypeError, ValueError):
            continue
    out = []
    for (county, state, portion), years in sorted(by_county.items()):
        a, b = years.get(BASE_YEAR), years.get(BASE_YEAR + 1)
        if not a or not b:
            continue
        out.append({
            "county": county, "state": state, "portion": portion,
            "employment_%d" % BASE_YEAR: a["employment"],
            "employment_%d" % (BASE_YEAR + 1): b["employment"],
            "employment_pct_change": pct(b["employment"], a["employment"]),
            "avg_annual_pay_%d" % BASE_YEAR: a["avg_annual_pay"],
            "avg_annual_pay_%d" % (BASE_YEAR + 1): b["avg_annual_pay"],
            "pay_pct_change": pct(b["avg_annual_pay"], a["avg_annual_pay"]),
        })
    return out


def fmt(v, width=9, places=1, suffix="%"):
    return "n/a".rjust(width) if v is None else ("%+*.*f%s" % (width - 1, places, v, suffix))


def main(root):
    panel, adjusted = load_ces(root)
    end_year = latest_september(panel)
    table = industry_table(panel, end_year)
    laus = unemployment(root, end_year)
    county_rows = counties(root)

    line = "=" * 92
    print(line)
    print("RE-BASED TO %d  |  Cincinnati OH-KY-IN MSA  |  September %d -> September %d"
          % (BASE_YEAR, BASE_YEAR, end_year))
    print(line)
    print("Industry series are not seasonally adjusted and are compared same-month,")
    print("so seasonality cancels without adjustment. Employment in thousands.")
    print()
    print("%-44s %9s %9s %10s %10s" % ("INDUSTRY", "Sep-%d" % BASE_YEAR,
                                       "Sep-%d" % end_year, "vs %d" % BASE_YEAR,
                                       "vs %d" % PRIOR_BASE))
    print("-" * 92)
    for r in table:
        print("%-44s %9.1f %9.1f %s %s" % (
            r["industry"][:44],
            r["sep_%d" % BASE_YEAR], r["sep_%d" % end_year],
            fmt(r["pct_change_from_%d" % BASE_YEAR], 10),
            fmt(r["pct_change_from_%d" % PRIOR_BASE], 10)))

    print()
    print(line)
    print("TOTAL NONFARM")
    print(line)
    tn = panel.get("Total Nonfarm", {})
    base, end = tn.get((BASE_YEAR, COMPARE_MONTH)), tn.get((end_year, COMPARE_MONTH))
    prior = tn.get((PRIOR_BASE, COMPARE_MONTH))
    print("  unadjusted  Sep-%d %.1fk -> Sep-%d %.1fk  = %s   (from %d: %s)"
          % (BASE_YEAR, base, end_year, end, fmt(pct(end, base), 8),
             PRIOR_BASE, fmt(pct(end, prior), 8)))
    tna = adjusted.get("Total Nonfarm", {})
    if tna:
        ab = tna.get((BASE_YEAR, 1))
        ae = max((k for k in tna if k[0] == end_year), default=None)
        if ab and ae:
            print("  adjusted    Jan-%d %.1fk -> %04d-%02d %.1fk  = %s"
                  % (BASE_YEAR, ab, ae[0], ae[1], tna[ae], fmt(pct(tna[ae], ab), 8)))
    print("  formula     pct = (end / base - 1) * 100")

    print()
    print(line)
    print("UNEMPLOYMENT RATE")
    print(line)
    for y in sorted(laus["annual_average"]):
        if y >= BASE_YEAR - 1:
            print("  %d annual average   %.2f%%" % (y, laus["annual_average"][y]))
    if laus["sep_base"] and laus["sep_end"]:
        print("  Sep-%d %.1f%%  ->  Sep-%d %.1f%%   (%+.1f pp)"
              % (BASE_YEAR, laus["sep_base"]["rate"], end_year,
                 laus["sep_end"]["rate"],
                 laus["sep_end"]["rate"] - laus["sep_base"]["rate"]))
        print("  labour force {:,.0f} -> {:,.0f}".format(
            laus["sep_base"]["labor_force"], laus["sep_end"]["labor_force"]))

    print()
    print(line)
    print("COUNTY EMPLOYMENT AND PAY, %d -> %d  (QCEW annual averages)" % (BASE_YEAR, BASE_YEAR + 1))
    print(line)
    print("%-14s %-3s %11s %11s %9s %10s %10s %8s"
          % ("COUNTY", "ST", "emp %d" % BASE_YEAR, "emp %d" % (BASE_YEAR + 1), "emp chg",
             "pay %d" % BASE_YEAR, "pay %d" % (BASE_YEAR + 1), "pay chg"))
    print("-" * 92)
    for r in county_rows:
        print("%-14s %-3s %11d %11d %s %10d %10d %s"
              % (r["county"][:14], r["state"],
                 r["employment_%d" % BASE_YEAR], r["employment_%d" % (BASE_YEAR + 1)],
                 fmt(r["employment_pct_change"], 9),
                 r["avg_annual_pay_%d" % BASE_YEAR], r["avg_annual_pay_%d" % (BASE_YEAR + 1)],
                 fmt(r["pay_pct_change"], 8)))

    out_path = os.path.join(root, "data", "cincinnati_rebased_2024.csv")
    fields = ["industry", "sep_%d" % PRIOR_BASE, "sep_%d" % BASE_YEAR,
              "sep_%d" % end_year, "pct_change_from_%d" % BASE_YEAR,
              "pct_change_from_%d" % PRIOR_BASE,
              "jobs_change_from_%d_thousands" % BASE_YEAR]
    with io.open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in table:
            w.writerow({k: ("" if r.get(k) is None else
                            (round(r[k], 2) if isinstance(r.get(k), float) else r.get(k)))
                        for k in fields})
    print()
    print("wrote %s  (%d industries)" % (out_path, len(table)))
    print("NOT re-based: OEWS May 2025, ODJFS projections 2022-2032, AEI April-May 2026.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
