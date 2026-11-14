"""Download ACS 1-year PUMS person files for the states that hold Cincinnati and its P1 peers,
keeping only employed civilians aged 22-54 and the columns the occupation-based entry-door
test (H2b) needs. The full files are never stored.

Years: 2018, 2019 (pre) and 2023, 2024 (post). The 2025 1-year PUMS was not on the Census
file server on 14 Nov 2026 (latest directory: 2024), so it is not used.

Output: raw/acs/pums_<year>_<st>.csv.gz ; raw/acs/_pums_manifest.csv
"""
import csv
import datetime
import gzip
import hashlib
import io
import os
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor

import requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "raw", "acs")
URL = "https://www2.census.gov/programs-surveys/acs/data/pums/{y}/1-Year/csv_p{st}.zip"
YEARS = [2018, 2019, 2023, 2024]
STATES = "oh ky in ga tx md nc sc co mi mo ks wi mn tn pa il fl".split()
BASE = ["PUMA", "AGEP", "ESR", "OCCP", "SOCP", "PWGTP"] + [f"PWGTP{i}" for i in range(1, 81)]


def fetch(job):
    y, st = job
    out = os.path.join(OUT, f"pums_{y}_{st}.csv.gz")
    url = URL.format(y=y, st=st)
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        return [y, st, url, "cached", "", 0, ""]
    err = ""
    for k in range(4):
        try:
            r = requests.get(url, timeout=600)
            r.raise_for_status()
            sha = hashlib.sha256(r.content).hexdigest()
            z = zipfile.ZipFile(io.BytesIO(r.content))
            name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
            n = 0
            with z.open(name) as f, gzip.open(out, "wt", newline="", encoding="utf-8") as g:
                rd = csv.reader(io.TextIOWrapper(f, encoding="utf-8"))
                head = [h.upper() for h in next(rd)]
                ix = {h: i for i, h in enumerate(head)}
                stcol = "STATE" if "STATE" in ix else "ST"
                w = csv.writer(g)
                w.writerow(["ST"] + BASE)
                for row in rd:
                    try:
                        age = int(row[ix["AGEP"]])
                    except ValueError:
                        continue
                    if 22 <= age <= 54 and row[ix["ESR"]] in ("1", "2"):   # civilian employed
                        w.writerow([row[ix[stcol]]] + [row[ix[c]] for c in BASE])
                        n += 1
            return [y, st, url, len(r.content), sha, n, datetime.date.today().isoformat()]
        except Exception as e:
            err = repr(e)
            time.sleep(10 * (k + 1))
    return [y, st, url, -1, "FAILED " + err, 0, datetime.date.today().isoformat()]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    jobs = [(y, s) for y in YEARS for s in (sys.argv[1:] or STATES)]
    man = os.path.join(OUT, "_pums_manifest.csv")
    new = not os.path.exists(man)
    with ThreadPoolExecutor(3) as ex:
        for res in ex.map(fetch, jobs):
            if res[3] == "cached":
                continue
            with open(man, "a", newline="") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(["year", "state", "url", "bytes", "sha256", "rows_kept", "downloaded"])
                    new = False
                w.writerow(res)
            print(res[:2], res[3], res[5], flush=True)
