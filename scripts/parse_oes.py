"""Parse BLS OEWS flat-file extract into a tidy occupation-level panel.

Source: https://download.bls.gov/pub/time.series/oe/oe.data.0.Current  (May 2025 reference period)
Series ID layout (oe.txt, Section 4): OE + U + areatype(1) + area(7) + industry(6) + occupation(6) + datatype(2)
"""
import csv, os, sys

SP = sys.argv[1]
OUT = sys.argv[2]

AREAS = {"0000000": "National", "3900000": "Ohio", "2100000": "Kentucky",
         "0017140": "Cincinnati MSA"}
DT = {"01": "employment", "02": "emp_rse", "03": "hourly_mean", "04": "annual_mean",
      "05": "wage_rse", "06": "hourly_p10", "07": "hourly_p25", "08": "hourly_median",
      "09": "hourly_p75", "10": "hourly_p90", "11": "annual_p10", "12": "annual_p25",
      "13": "annual_median", "14": "annual_p75", "15": "annual_p90",
      "16": "emp_per_1000", "17": "location_quotient"}

occ_names = {}
with open(os.path.join(SP, "oe.occupation"), encoding="utf-8", errors="replace") as f:
    r = csv.DictReader(f, delimiter="\t")
    for row in r:
        occ_names[row["occupation_code"].strip()] = row["occupation_name"].strip()

recs = {}
with open(os.path.join(SP, "oes_filtered.txt"), encoding="utf-8", errors="replace") as f:
    for line in f:
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        sid = parts[0].strip()
        if len(sid) != 25:
            continue
        area, industry, occ, dt = sid[4:11], sid[11:17], sid[17:23], sid[23:25]
        # Cross-industry only (000000); industry detail is not published for metros
        if industry != "000000" or area not in AREAS or dt not in DT:
            continue
        val = parts[3].strip()
        key = (AREAS[area], occ)
        recs.setdefault(key, {})[DT[dt]] = val

cols = ["area", "soc_code", "occupation", "soc_level"] + list(DT.values())
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for (area, occ), d in sorted(recs.items()):
        soc = occ[:2] + "-" + occ[2:]
        # SOC hierarchy: major XX-0000, minor XX-X000, broad XX-XXX0, detailed XX-XXXX
        if occ == "000000":
            lvl = "total"
        elif occ.endswith("0000"):
            lvl = "major"
        elif occ.endswith("000"):
            lvl = "minor"
        elif occ.endswith("0"):
            lvl = "broad"
        else:
            lvl = "detailed"
        w.writerow([area, soc, occ_names.get(occ, ""), lvl] + [d.get(c, "") for c in DT.values()])

print("rows written:", sum(1 for _ in recs))
