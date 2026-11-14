"""H9 comparator: total nonfarm employment, not seasonally adjusted, for Cincinnati, each P1
peer and the US, from the BLS public API (the BLS file server refuses automated requests).
Output: raw/ces_peers/ces_total_nonfarm_api.json ; data/ces_total_nonfarm_peers.csv
"""
import json, os, datetime
import pandas as pd, requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
ST = {17140: "39", 12060: "13", 12420: "48", 12580: "24", 16740: "37", 17410: "39", 18140: "39", 19430: "39",
      19740: "08", 19820: "26", 26900: "18", 28140: "29", 31140: "21", 33340: "55", 33460: "27", 34980: "47",
      38300: "42", 39580: "37", 41180: "29", 45300: "12"}
sid = {f"SMU{s}{c}0000000001": c for c, s in ST.items()}
sid["CEU0000000001"] = 0
r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json={
    "seriesid": list(sid), "startyear": "2019", "endyear": "2026"}, timeout=120).json()
assert r["status"] == "REQUEST_SUCCEEDED", r
json.dump(r, open(P("raw", "ces_peers", "ces_total_nonfarm_api.json"), "w"))
rows = []
for s in r["Results"]["series"]:
    for o in s["data"]:
        if o["period"].startswith("M") and o["period"] != "M13":
            rows.append(dict(cbsa=sid[s["seriesID"]], series=s["seriesID"], year=int(o["year"]), month=int(o["period"][1:]),
                             value_thousands=float(o["value"]),
                             preliminary=any(f.get("code") == "P" for f in o["footnotes"]),
                             retrieved=datetime.date.today().isoformat()))
d = pd.DataFrame(rows).sort_values(["cbsa", "year", "month"])
d.to_csv(P("data", "ces_total_nonfarm_peers.csv"), index=False)
print(d.groupby("cbsa").size().to_dict()); print(d[d.cbsa == 17140].tail(3))
