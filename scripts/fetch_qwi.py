"""Stream Census LEHD QWI metro files (sex-by-age, NAICS 3-digit, private ownership) and keep
only the rows the 2.1 hiring test needs. The full state files are 0.1-0.8 GB each, so they are
filtered while downloading and never stored whole.

Usage: python scripts/fetch_qwi.py oh ky in ...
Output: raw/qwi/qwi_<st>_sa_gm_n3_op_filtered.csv.gz and raw/qwi/_manifest.csv
"""
import csv, gzip, io, sys, zlib, os, time, datetime
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = "https://lehd.ces.census.gov/data/qwi/latest_release/{st}/qwi_{st}_sa_f_gm_n3_op_u.csv.gz"
OUT = os.path.join(os.path.dirname(__file__), "..", "raw", "qwi")
KEEP = ["geography", "industry", "agegrp", "year", "quarter", "Emp", "EmpS", "HirA", "HirN",
        "HirAS", "HirNS", "EarnS", "EarnHirAS", "EarnHirNS",
        "sEmp", "sEmpS", "sHirA", "sHirN", "sHirAS", "sHirNS", "sEarnS", "sEarnHirAS", "sEarnHirNS"]
AGES = {"A00", "A03", "A04", "A05", "A06"}


def lines_from_gzip_stream(resp):
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    buf = b""
    for chunk in resp.iter_content(chunk_size=1 << 20):
        buf += d.decompress(chunk)
        while d.unused_data:  # concatenated gzip members
            rest = d.unused_data
            d = zlib.decompressobj(16 + zlib.MAX_WBITS)
            buf += d.decompress(rest)
        *full, buf = buf.split(b"\n")
        for ln in full:
            yield ln.decode("utf-8")
    if buf:
        yield buf.decode("utf-8")


def fetch(st):
    url = BASE.format(st=st)
    out = os.path.join(OUT, f"qwi_{st}_sa_gm_n3_op_filtered.csv.gz")
    for attempt in range(4):
        try:
            t0 = time.time()
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                lastmod = r.headers.get("Last-Modified", "")
                size = r.headers.get("Content-Length", "")
                it = lines_from_gzip_stream(r)
                header = next(csv.reader([next(it)]))
                ix = {c: i for i, c in enumerate(header)}
                kept = 0
                maxyq = (0, 0)
                with gzip.open(out, "wt", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(KEEP)
                    for row in csv.reader(it):
                        if len(row) < len(header):
                            continue
                        if row[ix["geo_level"]] != "M" or row[ix["sex"]] != "0":
                            continue
                        if row[ix["agegrp"]] not in AGES or row[ix["ind_level"]] != "3":
                            continue
                        y = int(row[ix["year"]])
                        if y < 2017:
                            continue
                        q = int(row[ix["quarter"]])
                        if (y, q) > maxyq:
                            maxyq = (y, q)
                        w.writerow([row[ix[c]] for c in KEEP])
                        kept += 1
            return [st, url, size, lastmod, kept, f"{maxyq[0]}Q{maxyq[1]}",
                    datetime.date.today().isoformat(), round(time.time() - t0)]
        except Exception as e:  # retry on network errors
            err = repr(e)
            time.sleep(10 * (attempt + 1))
    return [st, url, "", "", -1, "FAILED " + err, datetime.date.today().isoformat(), 0]


if __name__ == "__main__":
    states = [s.lower() for s in sys.argv[1:]]
    os.makedirs(OUT, exist_ok=True)
    man = os.path.join(OUT, "_manifest.csv")
    new = not os.path.exists(man)
    with ThreadPoolExecutor(4) as ex:
        for res in ex.map(fetch, states):
            with open(man, "a", newline="") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(["state", "url", "bytes", "last_modified", "rows_kept",
                                "last_quarter", "downloaded", "seconds"])
                    new = False
                w.writerow(res)
            print(res, flush=True)
