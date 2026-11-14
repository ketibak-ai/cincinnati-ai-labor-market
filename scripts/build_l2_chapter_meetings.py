"""L2 (PREREGISTRATION.md 8.2): meetings held in the last 12 months by local chapters of a
national AI community organization that runs a standard format and publishes a dated event
list per chapter. Source: AI Tinkerers chapter pages (<city>.aitinkerers.org), read in a
browser on 14 Nov 2026. Organizer-reported, private platform.

The event dates below were transcribed from each chapter's public page. Window: events held
from 15 Nov 2025 to 14 Nov 2026 (events listed as upcoming are excluded).
"no_chapter_found" = the obvious address redirected to the national home page and a site
search for the city found no chapter; the chapter directory itself sat behind a bot check and
was not read, so a chapter under an unexpected name cannot be ruled out.
Output: data/l2_chapter_events.csv, data/l2_chapter_meetings.csv
"""
import datetime, os
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
COLLECTED = datetime.date(2026, 11, 14)
START = datetime.date(2025, 11, 15)
E = {  # cbsa: (slug, status, [dates of every event on the page])
    17140: ("cincinnati", "chapter", "2024-10-30 2024-12-06 2025-03-27 2025-06-12 2026-02-28"),
    18140: ("columbus", "chapter", "2024-11-06 2024-12-05 2026-03-02 2026-04-06 2026-05-04 2026-06-01 2026-07-06 2026-08-03 2026-09-07 2026-09-12 2026-10-05 2026-11-02 2026-12-14"),
    31140: ("louisville", "chapter", "2026-06-11 2026-07-30 2026-08-27 2026-09-12 2026-11-19"),
    12060: ("atlanta", "chapter", "2024-07-25 2024-08-22 2024-09-18 2024-10-21 2024-11-19 2025-01-23 2025-02-27 2025-04-04 2025-04-30 2025-05-22 2025-06-11 2025-07-31 2025-08-28 2025-09-11 2025-10-14 2025-11-18 2025-12-16 2026-01-27 2026-02-28 2026-03-30 2026-04-21 2026-05-09 2026-06-23 2026-07-30 2026-08-13 2026-09-12 2026-10-29 2026-11-24"),
    12420: ("austin", "chapter", "2024-02-15 2024-03-21 2024-04-11 2024-06-13 2024-07-11 2024-07-20 2024-08-08 2024-09-12 2024-10-10 2025-01-16 2025-02-13 2025-04-14 2025-06-05 2025-07-10 2025-09-11 2025-10-09 2025-11-10 2025-12-11 2026-01-22 2026-03-16 2026-04-16 2026-05-09 2026-06-18 2026-06-26 2026-10-15 2026-11-10"),
    34980: ("nashville", "chapter", "2025-04-09 2025-06-23 2025-09-05 2025-10-28 2026-01-29 2026-03-25 2026-05-21 2026-07-21 2026-09-29 2026-11-17"),
    39580: ("raleigh", "chapter", "2025-09-30 2025-12-10 2026-02-11 2026-05-06 2026-06-08 2026-08-12"),
    41180: ("st-louis", "chapter", "2025-06-05 2025-10-22 2026-02-04 2026-04-14 2026-06-03 2026-08-19 2026-10-14"),
    19740: ("denver-boulder", "chapter", "2023-06-06 2023-07-18 2023-08-08 2023-09-12 2023-11-22 2023-12-20 2024-01-17 2024-03-18 2024-04-15 2024-05-13 2024-06-10 2024-07-08 2024-08-02 2024-09-19 2024-10-16 2025-01-30 2025-02-24 2025-05-14 2025-06-11 2025-07-09 2025-10-24 2025-11-24 2026-02-28 2026-03-25 2026-04-27 2026-06-30"),
    33460: ("minneapolis-saint-paul", "chapter", "2025-07-16 2025-09-10 2025-11-05 2026-02-28 2026-05-06 2026-07-29 2026-09-24"),
    38300: ("pittsburgh", "chapter_page_no_events", ""),
    16740: ("charlotte", "chapter_page_no_events", ""),
    28140: ("kansas-city", "chapter_page_no_events", ""),
    12580: ("baltimore", "no_chapter_found", ""), 17410: ("cleveland", "no_chapter_found", ""),
    19430: ("dayton", "no_chapter_found", ""), 19820: ("detroit", "no_chapter_found", ""),
    26900: ("indianapolis", "no_chapter_found", ""), 33340: ("milwaukee", "no_chapter_found", ""),
    45300: ("tampa", "no_chapter_found", "")}
peers = pd.read_csv(P("data", "peer_sets.csv")); nm = dict(zip(peers.CBSA, peers.short))
ev, rows = [], []
pop = pd.read_csv(P("data", "l1_platform_counts.csv")).set_index("cbsa").pop_18_64 if os.path.exists(P("data", "l1_platform_counts.csv")) else None
for cbsa, (slug, status, dates) in E.items():
    ds = [datetime.date.fromisoformat(x) for x in dates.split()]
    for d in ds:
        ev.append(dict(cbsa=cbsa, area=nm[cbsa], chapter=slug, date=d.isoformat(), held=d <= COLLECTED,
                       in_window=START <= d <= COLLECTED, source_url=f"https://{slug}.aitinkerers.org/", collected=COLLECTED.isoformat()))
    held = [d for d in ds if START <= d <= COLLECTED]
    rows.append(dict(cbsa=cbsa, area=nm[cbsa], chapter=slug, status=status, meetings_last_12m=len(held),
                     months_with_meeting=len({(d.year, d.month) for d in held}),
                     first_event=min(ds).isoformat() if ds else "", events_all_time_listed=len([d for d in ds if d <= COLLECTED])))
pd.DataFrame(ev).to_csv(P("data", "l2_chapter_events.csv"), index=False)
R = pd.DataFrame(rows)
if pop is not None:
    R["pop_18_64"] = R.cbsa.map(pop); R["meetings_per_100k_18_64"] = R.meetings_last_12m / R.pop_18_64 * 1e5
R.to_csv(P("data", "l2_chapter_meetings.csv"), index=False)
print(R.sort_values("meetings_last_12m", ascending=False).to_string(index=False))
