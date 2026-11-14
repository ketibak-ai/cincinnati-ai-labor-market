"""Download the public source files 2.1 uses and record each in raw/_manifest_2_1.csv
(url, local path, bytes, sha256, date). BLS's own file server refuses automated requests, so
BLS zip files are taken from the Internet Archive's dated copies of the same URLs.

Usage: python scripts/fetch_public.py [name ...]   (no names = everything not yet present)
"""
import csv, hashlib, os, sys, datetime, time
import requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WB = "http://web.archive.org/web/{ts}id_/{url}"
BLS = "https://www.bls.gov/oes/special-requests/"
FILES = {
    # name: (url, local path)
    "pop_cbsa": ("https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/metro/totals/cbsa-est2025-alldata.csv", "raw/census/cbsa-est2025-alldata.csv"),
    "pop_county_age": ("https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/asrh/cc-est2025-agesex-all.csv", "raw/census/cc-est2025-agesex-all.csv"),
    "oes22_in4": (WB.format(ts="20261006080407", url=BLS + "oesm22in4.zip"), "raw/oes/oesm22in4.zip"),
    "oes25_ma": (WB.format(ts="20260926212022", url=BLS + "oesm25ma.zip"), "raw/oes/oesm25ma.zip"),
    "oes25_in4": (WB.format(ts="20260927013753", url=BLS + "oesm25in4.zip"), "raw/oes/oesm25in4.zip"),
    "oes25_nat": (WB.format(ts="20261107120602", url=BLS + "oesm25nat.zip"), "raw/oes/oesm25nat.zip"),
    "oes22_nat": (WB.format(ts="20261006075701", url=BLS + "oesm22nat.zip"), "raw/oes/oesm22nat.zip"),
    "soc_xwalk": (WB.format(ts="20260819173804", url="https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx"), "raw/exposure/soc_2010_to_2018_crosswalk.xlsx"),
    "eloundou": ("https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occ_level.csv", "raw/exposure/eloundou_occ_level.csv"),
    "ms_applicability": ("https://raw.githubusercontent.com/microsoft/working-with-ai/main/ai_applicability_scores.csv", "raw/exposure/ms_ai_applicability_scores.csv"),
    "ms_readme": ("https://raw.githubusercontent.com/microsoft/working-with-ai/main/README.md", "raw/exposure/ms_working_with_ai_README.md"),
    "bea_cagdp9": ("https://apps.bea.gov/regional/zip/CAGDP9.zip", "raw/bea/CAGDP9.zip"),
    "bea_cagdp2": ("https://apps.bea.gov/regional/zip/CAGDP2.zip", "raw/bea/CAGDP2.zip"),
    "ipeds_c2024": ("https://nces.ed.gov/ipeds/datacenter/data/C2024_A.zip", "raw/ipeds/C2024_A.zip"),
    "ipeds_hd2024": ("https://nces.ed.gov/ipeds/datacenter/data/HD2024.zip", "raw/ipeds/HD2024.zip"),
    "btos_state": ("https://www.census.gov/hfp/btos/downloads/State.xlsx", "raw/btos/State.xlsx"),
    "btos_national": ("https://www.census.gov/hfp/btos/downloads/National.xlsx", "raw/btos/National.xlsx"),
    "btos_msa": ("https://www.census.gov/hfp/btos/downloads/Top%2025%20MSA.xlsx", "raw/btos/Top25MSA.xlsx"),
}


def get(name):
    url, rel = FILES[name]
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    err = ""
    for attempt in range(4):
        try:
            h = hashlib.sha256(); n = 0
            with requests.get(url, stream=True, timeout=180) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for ch in r.iter_content(1 << 20):
                        f.write(ch); h.update(ch); n += len(ch)
            return [name, url, rel, n, h.hexdigest(), datetime.date.today().isoformat()]
        except Exception as e:
            err = repr(e); time.sleep(8 * (attempt + 1))
    return [name, url, rel, -1, "FAILED " + err, datetime.date.today().isoformat()]


if __name__ == "__main__":
    names = sys.argv[1:] or [n for n, (u, p) in FILES.items() if not os.path.exists(os.path.join(ROOT, p))]
    man = os.path.join(ROOT, "raw", "_manifest_2_1.csv")
    new = not os.path.exists(man)
    for n in names:
        res = get(n)
        with open(man, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["name", "url", "path", "bytes", "sha256", "downloaded"]); new = False
            w.writerow(res)
        print(res[0], res[3], res[4][:60], flush=True)
