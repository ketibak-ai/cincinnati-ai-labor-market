"""L1 (PREREGISTRATION.md 8.2): AI events listed on public event platforms, one collection day,
identical searches for Cincinnati and each of the 19 P1 peers.

For each metro's principal city and each of seven fixed search terms, this reads
  - Eventbrite's public search page for the city (every results page the site returns, up to 5)
  - Meetup's public "find events" page for the city (first page of results only: further pages
    need the site's private API)
and keeps events that are (a) in person, (b) dated within 60 days after the collection day,
and (c) about AI by a fixed test on the event title. De-duplicated by title and date.

Deviations from the pre-registration, both logged there:
  - Luma is not included. It has no public search by city and keyword.
  - "AI is the stated main subject" is applied as a title test (TITLE_RE below), because the
    screen has to be identical across 20 metros. Events that are about AI but do not say so
    in the title are missed everywhere alike.

Private-platform source: counts depend on each platform's own search radius and ranking.
Raw responses are kept in raw/awareness/l1/ (not redistributed).

Usage: python scripts/collect_l1_platform_listings.py            (collect)
Output: data/l1_platform_events.csv, data/l1_platform_counts.csv
"""
import datetime
import hashlib
import json
import os
import re
import time

import pandas as pd
import requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
TERMS = ["AI", "artificial intelligence", "generative AI", "machine learning", "LLM", "ChatGPT", "agents"]
TITLE_RE = re.compile(r"(?<![A-Za-z])A\.?I\.?(?![A-Za-z])|(?-i:[a-z]AI\b)|artificial intelligence|generative|machine learning|"
                      r"\bLLMs?\b|chatgpt|\bGPTs?\b|copilot|\bclaude\b|\bgemini\b|agentic|\bAI agents?\b|"
                      r"prompt engineering|deep learning|\bMLOps\b|data science", re.I)
CITIES = {  # cbsa: (eventbrite slug, meetup location)
    17140: ("oh--cincinnati", "us--oh--Cincinnati"), 12060: ("ga--atlanta", "us--ga--Atlanta"),
    12420: ("tx--austin", "us--tx--Austin"), 12580: ("md--baltimore", "us--md--Baltimore"),
    16740: ("nc--charlotte", "us--nc--Charlotte"), 17410: ("oh--cleveland", "us--oh--Cleveland"),
    18140: ("oh--columbus", "us--oh--Columbus"), 19430: ("oh--dayton", "us--oh--Dayton"),
    19740: ("co--denver", "us--co--Denver"), 19820: ("mi--detroit", "us--mi--Detroit"),
    26900: ("in--indianapolis", "us--in--Indianapolis"), 28140: ("mo--kansas-city", "us--mo--Kansas City"),
    31140: ("ky--louisville", "us--ky--Louisville"), 33340: ("wi--milwaukee", "us--wi--Milwaukee"),
    33460: ("mn--minneapolis", "us--mn--Minneapolis"), 34980: ("tn--nashville", "us--tn--Nashville"),
    38300: ("pa--pittsburgh", "us--pa--Pittsburgh"), 39580: ("nc--raleigh", "us--nc--Raleigh"),
    41180: ("mo--st-louis", "us--mo--St. Louis"), 45300: ("fl--tampa", "us--fl--Tampa")}
# City-hall coordinates of each principal city. Eventbrite's own search area spills into
# neighbouring metros (Cincinnati's results included Louisville and Dayton-area events), so an
# Eventbrite event is kept only if its venue lies within 25 miles of the principal city.
CENTER = {17140: (39.1031, -84.5120), 12060: (33.7490, -84.3880), 12420: (30.2672, -97.7431), 12580: (39.2904, -76.6122),
          16740: (35.2271, -80.8431), 17410: (41.4993, -81.6944), 18140: (39.9612, -82.9988), 19430: (39.7589, -84.1916),
          19740: (39.7392, -104.9903), 19820: (42.3314, -83.0458), 26900: (39.7684, -86.1581), 28140: (39.0997, -94.5786),
          31140: (38.2527, -85.7585), 33340: (43.0389, -87.9065), 33460: (44.9778, -93.2650), 34980: (36.1627, -86.7816),
          38300: (40.4406, -79.9959), 39580: (35.7796, -78.6382), 41180: (38.6270, -90.1994), 45300: (27.9506, -82.4572)}
RADIUS_MILES = 25


def miles(a, b):
    import math
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))

TODAY = datetime.date(2026, 11, 14)          # the collection day (fixed so cached responses are reused)
END = TODAY + datetime.timedelta(days=60)
RAW = P("raw", "awareness", "l1")
os.makedirs(RAW, exist_ok=True)
S = requests.Session()
log = []


def get(url, tag):
    f = os.path.join(RAW, f"{TODAY}_{tag}.html")
    if os.path.exists(f):
        return open(f, encoding="utf-8", errors="replace").read()
    for k in range(3):
        try:
            r = S.get(url, timeout=60)
            if r.status_code == 200:
                open(f, "w", encoding="utf-8").write(r.text)
                log.append((tag, url, 200, hashlib.sha256(r.content).hexdigest()[:16]))
                time.sleep(1.5)
                return r.text
            log.append((tag, url, r.status_code, ""))
            if r.status_code in (403, 404):
                return None
        except Exception as e:
            log.append((tag, url, repr(e)[:60], ""))
        time.sleep(8 * (k + 1))
    return None


def eventbrite(cbsa, slug, term):
    out, pages = [], 1
    p = 1
    while p <= min(pages, 5):
        url = f"https://www.eventbrite.com/d/{slug}/{requests.utils.quote(term)}/?page={p}"
        h = get(url, f"eb_{cbsa}_{term.replace(' ', '-')}_{p}")
        if not h:
            break
        m = re.search(r"window\.__SERVER_DATA__\s*=\s*(\{.*?\});\s*\n", h, re.S)
        if not m:
            break
        ev = json.loads(m.group(1)).get("search_data", {}).get("events", {})
        pages = (ev.get("pagination") or {}).get("page_count", 1) or 1
        for e in ev.get("results", []):
            v = e.get("primary_venue") or {}
            ad = v.get("address") or {}
            try:
                dist = miles(CENTER[cbsa], (float(ad.get("latitude")), float(ad.get("longitude"))))
            except (TypeError, ValueError):
                dist = None
            out.append(dict(platform="eventbrite", cbsa=cbsa, term=term, title=e.get("name", ""), date=e.get("start_date"),
                            in_person=not e.get("is_online_event", False), city=ad.get("city"), miles_from_center=dist,
                            url=e.get("url"), cancelled=bool(e.get("is_cancelled"))))
        p += 1
    return out


def meetup(cbsa, loc, term):
    url = f"https://www.meetup.com/find/?keywords={requests.utils.quote(term)}&location={requests.utils.quote(loc)}&source=EVENTS"
    h = get(url, f"mu_{cbsa}_{term.replace(' ', '-')}")
    out = []
    if not h:
        return out
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', h, re.S)
    if not m:
        return out
    st = json.loads(m.group(1))["props"]["pageProps"].get("__APOLLO_STATE__", {})
    for k, e in st.items():
        if k.startswith("Event:") and e.get("title"):
            out.append(dict(platform="meetup", cbsa=cbsa, term=term, title=e.get("title", ""), date=(e.get("dateTime") or "")[:10],
                            in_person=e.get("eventType") == "PHYSICAL", city=None, miles_from_center=None, url=e.get("eventUrl"), cancelled=False))
    return out


rows = []
for cbsa, (slug, loc) in CITIES.items():
    for t in TERMS:
        rows += eventbrite(cbsa, slug, t)
        rows += meetup(cbsa, loc, t)
    print(cbsa, len(rows), flush=True)
A = pd.DataFrame(rows)
A["collected"] = TODAY.isoformat()
A["date"] = pd.to_datetime(A.date, errors="coerce").dt.date
A["title_is_ai"] = A.title.fillna("").map(lambda s: bool(TITLE_RE.search(s)))
A["in_window"] = A.date.map(lambda d: pd.notna(d) and TODAY <= d <= END)
A["in_radius"] = (A.platform == "meetup") | (A.miles_from_center <= RADIUS_MILES)     # Meetup searches are already centred on the city
K = A[A.in_person & A.title_is_ai & A.in_window & ~A.cancelled & A.in_radius].copy()
K["key"] = K.title.str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip() + "|" + K.date.astype(str)
K = K.sort_values(["cbsa", "platform"]).drop_duplicates(["cbsa", "key"])
K.drop(columns="key").to_csv(P("data", "l1_platform_events.csv"), index=False)

cc = pd.read_csv(P("raw", "census", "cc-est2025-agesex-all.csv"), encoding="latin-1", dtype={"STATE": str, "COUNTY": str})
cc = cc[cc.YEAR == cc.YEAR.max()]
cc["fips"] = cc.STATE.str.zfill(2) + cc.COUNTY.str.zfill(3)
cty = pd.read_csv(P("data", "cbsa_counties.csv"), dtype={"STCOU": str})
cc["cbsa"] = cc.fips.map(dict(zip(cty.STCOU, cty.CBSA)))
pop = cc.dropna(subset=["cbsa"]).assign(p1864=lambda x: x.AGE18PLUS_TOT - x.AGE65PLUS_TOT).groupby("cbsa").p1864.sum()
peers = pd.read_csv(P("data", "peer_sets.csv"))
nm = dict(zip(peers.CBSA, peers.short))
C = pd.DataFrame({"cbsa": list(CITIES)})
C["area"] = C.cbsa.map(nm)
C["raw_results"] = C.cbsa.map(A.groupby("cbsa").size()).fillna(0).astype(int)
C["dropped_outside_radius"] = C.cbsa.map(A[A.in_person & A.title_is_ai & A.in_window & ~A.cancelled & ~A.in_radius].drop_duplicates(["cbsa", "title", "date"]).groupby("cbsa").size()).fillna(0).astype(int)
C["events"] = C.cbsa.map(K.groupby("cbsa").size()).fillna(0).astype(int)
C["events_eventbrite"] = C.cbsa.map(K[K.platform == "eventbrite"].groupby("cbsa").size()).fillna(0).astype(int)
C["events_meetup"] = C.cbsa.map(K[K.platform == "meetup"].groupby("cbsa").size()).fillna(0).astype(int)
C["pop_18_64"] = C.cbsa.map(pop)
C["events_per_100k_18_64"] = C.events / C.pop_18_64 * 1e5
C["collected"] = TODAY.isoformat()
C["window_end"] = END.isoformat()
C.to_csv(P("data", "l1_platform_counts.csv"), index=False)
pd.DataFrame(log, columns=["tag", "url", "status", "sha256_16"]).to_csv(os.path.join(RAW, f"_log_{TODAY}_run{len(os.listdir(RAW))}.csv"), index=False)
print(C.sort_values("events_per_100k_18_64", ascending=False).to_string(index=False))
print("failed requests:", sum(1 for l in log if l[2] != 200))
