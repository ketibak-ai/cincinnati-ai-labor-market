"""H6(b), measure 1: AI patents by inventor location.

USPTO Artificial Intelligence Patent Dataset (AIPD, 2023 update) flags each granted patent
that falls in any of eight AI component technologies. PatentsView gives each inventor's
disambiguated location with a county code. A patent counts for a metro if at least one of
its inventors is located in one of the metro's counties (2023 CBSA delineation).

Primary: granted patents published 2019-2023 with predict86_any_ai = 1 (the USPTO's
86%-threshold flag). Sensitivity: predict93_any_ai.

Both files were taken from the Internet Archive's copies of the USPTO and PatentsView bulk
files (the live portals now require an account); checksums are in raw/patents/_fetch.log.
PatentsView vintage: March 2025 snapshot. AIPD: 2023 update, snapshot of February 2025.

Output: data/h6_ai_patents.csv
"""
import csv
import io
import os
import zipfile

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
csv.field_size_limit(10 ** 9)

ai86, ai93, n_pat = set(), set(), 0
with zipfile.ZipFile(P("raw", "patents", "ai_model_predictions.csv.zip")) as z, z.open("ai_model_predictions.csv") as f:
    rd = csv.reader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
    h = next(rd); ix = {c: i for i, c in enumerate(h)}
    a, b, c, d, e = ix["doc_id"], ix["flag_patent"], ix["pub_dt"], ix["predict86_any_ai"], ix["predict93_any_ai"]
    for r in rd:
        if r[b] == "1" and "2019" <= r[c][:4] <= "2023":
            n_pat += 1
            if r[d] == "1":
                ai86.add(r[a])
                if r[e] == "1":
                    ai93.add(r[a])
print("granted patents 2019-2023:", n_pat, "| AI (86):", len(ai86), "| AI (93):", len(ai93), flush=True)

loc = pd.read_csv(zipfile.ZipFile(P("raw", "patents", "g_location_disambiguated.tsv.zip")).open("g_location_disambiguated.tsv"),
                  sep="\t", dtype=str)
loc = loc[loc.disambig_country == "US"].dropna(subset=["state_fips", "county_fips"])
loc["fips"] = loc.state_fips.str.zfill(2) + loc.county_fips.str.zfill(3)
cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
loc["cbsa"] = loc.fips.map(dict(zip(cty.STCOU, cty.CBSA)))
l2c = loc.dropna(subset=["cbsa"]).set_index("location_id").cbsa.astype(int).to_dict()
us_loc = set(loc.location_id)

pairs86, pairs93, us86 = set(), set(), set()
with zipfile.ZipFile(P("raw", "patents", "g_inventor_disambiguated.tsv.zip")) as z, z.open("g_inventor_disambiguated.tsv") as f:
    rd = csv.reader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"), delimiter="\t")
    h = next(rd); pi, li = h.index("patent_id"), h.index("location_id")
    for r in rd:
        p = r[pi]
        if p in ai86:
            if r[li] in us_loc:
                us86.add(p)
            cb = l2c.get(r[li])
            if cb:
                pairs86.add((p, cb))
                if p in ai93:
                    pairs93.add((p, cb))
print("AI patents (86) with a US inventor:", len(us86), flush=True)
peers = pd.read_csv(P("data", "peer_sets.csv"))
c86 = pd.Series([c for _, c in pairs86]).value_counts()
c93 = pd.Series([c for _, c in pairs93]).value_counts()
R = peers[["CBSA", "short", "POPESTIMATE2025", "p1", "p2", "p3"]].copy()
R["ai_patents_2019_23"] = R.CBSA.map(c86).fillna(0).astype(int)
R["ai_patents_2019_23_p93"] = R.CBSA.map(c93).fillna(0).astype(int)
R["ai_patents_per_100k"] = R.ai_patents_2019_23 / R.POPESTIMATE2025 * 1e5
R["ai_patents_per_100k_p93"] = R.ai_patents_2019_23_p93 / R.POPESTIMATE2025 * 1e5
R["us_ai_patents_2019_23"] = len(us86)
R.to_csv(P("data", "h6_ai_patents.csv"), index=False)
t = R[R.p1 | (R.CBSA == 17140)].sort_values("ai_patents_per_100k", ascending=False)
print(t[["short", "ai_patents_2019_23", "ai_patents_2019_23_p93", "ai_patents_per_100k", "ai_patents_per_100k_p93"]].round(1).to_string(index=False))
for col in ("ai_patents_per_100k", "ai_patents_per_100k_p93"):
    cin = float(R.loc[R.CBSA == 17140, col].iloc[0]); p1 = R[R.p1][col]
    print(col, "Cincinnati", round(cin, 1), "rank", int((p1 > cin).sum()) + 1, "of 20; P1 median", round(p1.median(), 1), "| bottom half:", cin < p1.median())
