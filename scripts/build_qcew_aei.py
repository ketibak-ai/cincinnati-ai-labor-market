"""Build two datasets:

1. QCEW county-level covered employment and wages for the seven core Greater Cincinnati
   counties, separating the Ohio and Kentucky portions.
   Source: https://data.bls.gov/cew/data/api/{year}/a/area/{fips}.csv  (annual averages)
   Aggregation levels used: 70 = county total, all ownerships; 71 = county by ownership;
   74 = county by ownership and NAICS sector.
   QCEW covers jobs covered by unemployment insurance; it excludes most self-employment.

2. Anthropic Economic Index state-level AI usage metrics for Ohio, Kentucky and the US.
   Source: https://huggingface.co/datasets/Anthropic/EconomicIndex (release 2026-06-26)
"""
import csv
import os
import sys

COUNTIES = {
    "39061": ("Hamilton", "OH"),
    "39017": ("Butler", "OH"),
    "39025": ("Clermont", "OH"),
    "39165": ("Warren", "OH"),
    "21015": ("Boone", "KY"),
    "21117": ("Kenton", "KY"),
    "21037": ("Campbell", "KY"),
}
OWN = {"0": "Total, all ownerships", "1": "Federal government",
       "2": "State government", "3": "Local government", "5": "Private"}


def build_qcew(base: str) -> None:
    titles = {}
    tp = os.path.join(base, "raw", "qcew", "industry_titles.csv")
    if os.path.exists(tp):
        for r in csv.DictReader(open(tp, encoding="utf-8", errors="replace")):
            titles[r["industry_code"].strip()] = r["industry_title"].strip()

    out = []
    for year in ("2024", "2025"):
        for fips, (county, state) in COUNTIES.items():
            p = os.path.join(base, "raw", "qcew", f"{year}_{fips}.csv")
            if not os.path.exists(p):
                print(f"  MISSING {p}")
                continue
            for r in csv.DictReader(open(p, encoding="utf-8", errors="replace")):
                agg, own, ind = r["agglvl_code"], r["own_code"], r["industry_code"]
                keep = (
                    (agg == "70" and own == "0" and ind == "10")
                    or (agg == "71" and own in ("1", "2", "3", "5") and ind == "10")
                    or (agg == "74" and own == "5")
                )
                if not keep:
                    continue
                def i(k):
                    try:
                        return int(r[k])
                    except (ValueError, KeyError):
                        return None
                def f(k):
                    try:
                        return float(r[k])
                    except (ValueError, KeyError):
                        return None
                out.append({
                    "year": year, "area_fips": fips, "county": county, "state": state,
                    "portion": "Ohio (4-county)" if state == "OH" else "Northern Kentucky (3-county)",
                    "agglvl_code": agg, "ownership": OWN.get(own, own),
                    "industry_code": ind,
                    "industry_title": titles.get(ind, "Total, all industries" if ind == "10" else ""),
                    "establishments": i("annual_avg_estabs"),
                    "employment": i("annual_avg_emplvl"),
                    "total_annual_wages": i("total_annual_wages"),
                    "avg_weekly_wage": i("annual_avg_wkly_wage"),
                    "avg_annual_pay": i("avg_annual_pay"),
                    "location_quotient_employment": f("lq_annual_avg_emplvl"),
                    "emp_chg_yoy": i("oty_annual_avg_emplvl_chg"),
                    "emp_pct_chg_yoy": f("oty_annual_avg_emplvl_pct_chg"),
                    "disclosure_suppressed": "Y" if r.get("disclosure_code", "").strip() else "",
                })
    dest = os.path.join(base, "data", "qcew_cincinnati_counties.csv")
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    print(f"QCEW rows written: {len(out):,}")

    for year in ("2024", "2025"):
        oh = sum(r["employment"] for r in out
                 if r["year"] == year and r["agglvl_code"] == "70" and r["state"] == "OH")
        ky = sum(r["employment"] for r in out
                 if r["year"] == year and r["agglvl_code"] == "70" and r["state"] == "KY")
        ohw = sum(r["total_annual_wages"] for r in out
                  if r["year"] == year and r["agglvl_code"] == "70" and r["state"] == "OH")
        kyw = sum(r["total_annual_wages"] for r in out
                  if r["year"] == year and r["agglvl_code"] == "70" and r["state"] == "KY")
        print(f"  {year}: Ohio 4-county {oh:,} jobs (avg pay ${ohw/oh:,.0f}) | "
              f"NKY 3-county {ky:,} jobs (avg pay ${kyw/ky:,.0f}) | total {oh+ky:,}")


METRICS = {
    "usage_pct", "usage_per_capita_index", "use_case_work_pct",
    "collaboration_bucket_automation_pct", "collaboration_bucket_augmentation_pct",
    "collaboration_directive_pct", "collaboration_feedback_loop_pct",
    "collaboration_task_iteration_pct", "collaboration_learning_pct",
    "collaboration_validation_pct", "ai_autonomy_mean", "human_only_ability_pct",
    "multitasking_pct", "human_education_years_mean", "ai_education_years_mean",
}
GEO = {"US-OH": "Ohio", "US-KY": "Kentucky", "USA": "United States", "US-IN": "Indiana"}


def build_aei(base: str) -> None:
    src = os.path.join(base, "raw", "aei", "aei_states_filtered.csv")
    overall, soc = [], []
    for r in csv.DictReader(open(src, encoding="utf-8")):
        if r["geo_id"] not in GEO:
            continue
        row = {"geography": GEO[r["geo_id"]], "geo_id": r["geo_id"],
               "geo_level": r["geo_level"], "month": r["date_start"],
               "metric_id": r["metric_id"], "value": r["value"],
               "node_name": r["node_name"], "node_external_id": r["node_external_id"]}
        if r["category_name"] == "overall" and r["metric_id"] in METRICS:
            overall.append(row)
        elif (r["category_name"] == "soc_occupation" and r["hierarchy_level"] == "1"
              and r["metric_id"] == "pct"):
            soc.append(row)

    d1 = os.path.join(base, "data", "aei_state_overall.csv")
    with open(d1, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(overall[0].keys()))
        w.writeheader(); w.writerows(sorted(overall, key=lambda r: (r["geography"], r["month"], r["metric_id"])))
    d2 = os.path.join(base, "data", "aei_state_soc_major_groups.csv")
    with open(d2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(soc[0].keys()))
        w.writeheader(); w.writerows(sorted(soc, key=lambda r: (r["geography"], r["month"], r["node_name"])))
    print(f"AEI overall rows: {len(overall):,}; SOC major-group rows: {len(soc):,}")


if __name__ == "__main__":
    b = sys.argv[1]
    build_qcew(b)
    build_aei(b)
