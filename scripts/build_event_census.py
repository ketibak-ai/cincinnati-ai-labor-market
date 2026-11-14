"""Cincinnati AI event census, 1 Dec 2023 - 30 Nov 2026 (PREREGISTRATION.md 8.2, measures A1-A5, A7).

Built from records fixed at the time, read on 14 Nov 2026:
  - the CincyAI for Humans newsletter archive (83 issues, Oct 2023 - Nov 2026): each monthly
    meeting has a dated reminder or recap issue;
  - the AI Tinkerers Cincinnati chapter page (dated list of every chapter event);
  - event pages and news items found through the fixed platform search (L1) and web searches.
An event is listed only if a dated public record of it was read. Events dated after the
collection day are marked upcoming and not counted as held.

Limits, stated in the report: this census is certainly incomplete for one-off events (university
talks, chamber breakfasts, vendor workshops), most complete for recurring series, and has no
employer-sponsor coding (A6 was not measured: it needs every event page read for host and
sponsor names). No full census was built for the six comparison metros; their comparison rests
on the like-for-like measures.

Output: data/ai_events.csv, data/ai_community_groups.csv, data/ai_event_attendance_claims.csv,
        output/event_census_trace.txt
"""
import datetime
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
COLLECTED = datetime.date(2026, 11, 14)
NL = "https://cincyai.beehiiv.com/archive"
TK = "https://cincinnati.aitinkerers.org/"
rows = []


def add(date, name, series, organizer, otype, audience, fmt, source, note="", status=None, precision="day"):
    d = datetime.date.fromisoformat(date)
    rows.append(dict(metro="Cincinnati", date=date, date_precision=precision, event_name=name, series_name=series, organizer=organizer,
                     organizer_type=otype, audience=audience, format=fmt, source_url=source, note=note,
                     status=status or ("held" if d <= COLLECTED else "upcoming"), date_collected=COLLECTED.isoformat()))

# CincyAI for Humans monthly meetups (dates from newsletter subject lines)
cincyai = ["2023-12-05", "2024-01-09", "2024-02-06", "2024-03-05", "2024-04-16", "2024-05-07", "2024-06-04", "2024-07-09",
           "2024-08-06", "2024-09-17", "2024-10-08", "2024-11-05", "2024-12-03", "2025-01-14", "2025-02-04", "2025-03-04",
           "2025-04-01", "2025-05-06", "2025-06-17", "2025-07-01", "2025-08-05", "2025-09-02", "2025-10-07", "2025-11-04",
           "2025-12-02", "2026-01-06", "2026-02-10", "2026-03-03", "2026-04-07", "2026-05-05", "2026-06-02", "2026-07-21",
           "2026-08-04", "2026-09-01", "2026-10-20", "2026-11-03", "2026-12-01"]
for d in cincyai:
    approx = d in ("2023-12-05", "2024-01-09")
    add(d, "CincyAI for Humans monthly meetup", "CincyAI for Humans", "CincyAI for Humans", "community", "general public", "in person", NL,
        note="day inferred from the recap issue's date; the month is certain" if approx else "",
        status="cancelled (snow)" if d == "2025-12-02" else None, precision="month" if approx else "day")
add("2024-08-28", "CincyAI happy hour", "", "CincyAI for Humans", "community", "general public", "in person", NL, "announced in the 26 Aug 2024 issue; day approximate", precision="month")
add("2026-07-23", "CincyAI summer mixer", "", "CincyAI for Humans", "community", "general public", "in person", NL)
add("2026-09-08", "MidwestCon x CincyAI", "MidwestCon", "Disruption Now / CincyAI for Humans", "community", "general public", "in person", NL)
# AI Tinkerers Cincinnati
for d, n in (("2024-10-30", "Inaugural meetup"), ("2024-12-06", "Innovation & Collaboration Lab"), ("2025-03-27", "Midwest Innovation Hub (Xavier University)"),
             ("2025-06-12", "Meetup at Northern Kentucky University"), ("2026-02-28", "OpenClaw Global Unhackathon")):
    add(d, "AI Tinkerers Cincinnati: " + n, "AI Tinkerers Cincinnati", "AI Tinkerers Cincinnati", "community", "technical", "in person", TK)
# Annual and one-off events with a dated record read in this session
add("2024-06-11", "Cincy AI Week 2024", "Cincy AI Week", "Cincy AI Week organizers", "community", "general public", "in person",
    "https://www.uc.edu/news/articles/2024/06/community-of-ai-enthusiasts-expands-in-cincinnati.html", "three-day event; start day approximate", precision="month")
add("2025-06-10", "Cincy AI Week 2025 (10-12 June)", "Cincy AI Week", "Cincy AI Week organizers", "community", "general public", "in person", NL)
add("2026-06-09", "Cincy AI Week 2026 (9-11 June)", "Cincy AI Week", "Cincy AI Week organizers", "community", "general public", "in person", NL)
add("2024-07-15", "Mayor's AI symposium", "", "City of Cincinnati / Mayor's office", "government", "public sector", "in person",
    "https://www.uc.edu/news/articles/2024/07/mayor-pureval-rob-richardson-lead-ethical-ai-symposium.html", "day approximate", precision="month")
add("2026-05-15", "UC 1819 Innovation Hub AI + Robotics Summit", "", "University of Cincinnati 1819 Innovation Hub", "university", "business or executive", "in person",
    "https://www.uc.edu/news/articles/2026/05/from-humanoids-to-drones-1819-innovation-hub-debuts-ai--robotics-summit.html", "day approximate", precision="month")
add("2026-01-29", "2025 Year in Review (CincyAI with Cincinnati AI Catalyst)", "", "CincyAI for Humans / Cincinnati AI Catalyst", "community", "general public", "virtual", NL)
add("2026-11-04", "OhioX State of AI: Cincinnati", "OhioX State of AI", "OhioX", "chamber or advocacy", "business or executive", "in person", NL)
add("2026-11-17", "Cincy AI Defenders (CAID) quarterly meetup", "Cincy AI Defenders", "Cincy AI Defenders", "community", "technical", "in person", "https://www.eventbrite.com/d/oh--cincinnati/ai/")
E = pd.DataFrame(rows)
# upcoming listings from the L1 platform search that are not already in the census
l1 = pd.read_csv(P("data", "l1_platform_events.csv"))
l1 = l1[l1.cbsa == 17140]
have = set(E.date)
for _, r in l1.iterrows():
    if r.date in have and ("CincyAI" in r.title or "CAID" in r.title):
        continue
    E.loc[len(E)] = dict(metro="Cincinnati", date=r.date, date_precision="day", event_name=r.title, series_name="", organizer="(platform listing)",
                         organizer_type="not coded", audience="not coded", format="in person", source_url=r.url, note="found by the fixed platform search (" + r.platform + ")",
                         status="upcoming", date_collected=COLLECTED.isoformat())
E = E.sort_values("date").reset_index(drop=True)
E.insert(0, "event_id", ["CIN-%03d" % (i + 1) for i in range(len(E))])
E.to_csv(P("data", "ai_events.csv"), index=False)

G = pd.DataFrame([
    ["CincyAI for Humans", "membership", "over 1,700", "2025-10-13", "'With over 1,700 members strong'", "organizer-reported (newsletter)", "https://cincyai.beehiiv.com/p/rsvp-to-nov-4-next-cincyai-for-humans-oct-2-year-anniversary-recap", "yes"],
    ["CincyAI for Humans", "membership", "over 2,000", "2026-03-09", "'we've officially surpassed 2k members'", "organizer-reported (newsletter)", "https://cincyai.beehiiv.com/p/rsvp-to-april-7-next-cincyai-for-humans-claude-code-1-year-anniversary-celebration-march-recap", "yes"],
    ["CincyAI for Humans", "membership", "over 1,400", "2025 (issue not located)", "search-result summary only", "organizer-reported (not read)", "", "no"],
    ["CincyAI for Humans", "membership basis", "newsletter sign-up", "2026", "free membership is a newsletter sign-up; a paid tier ($25 a month) exists", "organizer-reported (newsletter)", NL, "yes"],
    ["AI Tinkerers (global network)", "membership", "144,000+ in 277 cities", "2026-11-14", "network-wide figure on the chapter page; no Cincinnati chapter count is published", "organizer-reported (chapter page)", TK, "yes"],
], columns=["group", "measure", "value", "as_of", "wording", "source_type", "url", "read"])
G.to_csv(P("data", "ai_community_groups.csv"), index=False)
A = pd.DataFrame([
    ["CincyAI for Humans meetup, 2 June 2026", "over 200", "organizer", "'our largest CincyAI for Humans to date, with over 200 attendees'", "2026-06-07", "https://cincyai.beehiiv.com/p/rsvp-to-july-21-next-cincyai-for-humans-june-recap-cincy-ai-week-updates", "yes"],
    ["Cincy AI Week 2024", "nearly 1,500", "news item (Knoxville business news)", "search-result summary only", "2024", "", "no"],
    ["Cincy AI Week 2025", "1,100 over 3 days", "recap newsletter (third party)", "search-result summary only", "2025", "https://kendratech.substack.com/p/cincy-ai-week-recap", "no"],
    ["Cincy AI Week (year unclear)", "over 1,000 attendees, 175 speakers, 150 volunteers", "recap newsletter (third party)", "search-result summary only", "unclear", "", "no"],
    ["OhioX Ohio AI Summit 2024 (statewide)", "375+", "local guide", "search-result summary only", "2024", "", "no"],
], columns=["event", "figure", "reported_by", "wording_or_status", "date", "url", "read"])
A.to_csv(P("data", "ai_event_attendance_claims.csv"), index=False)

with open(P("output", "event_census_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a); print(*a, file=fh)
    E["d"] = pd.to_datetime(E.date)
    E["yr"] = pd.cut(E.d, [pd.Timestamp("2023-11-30"), pd.Timestamp("2024-11-30"), pd.Timestamp("2025-11-30"), pd.Timestamp("2026-11-30")],
                     labels=["Dec 2023-Nov 2024", "Dec 2024-Nov 2025", "Dec 2025-Nov 2026"])
    held = E[E.status == "held"]
    w("Census rows:", len(E), "| held:", len(held), "| upcoming:", int((E.status == "upcoming").sum()), "| cancelled:", int(E.status.str.startswith("cancel").sum()))
    w("\nA1 events held per year (the last year runs to the collection day, 14 Nov 2026):")
    w(held.groupby("yr", observed=False).size().to_string())
    w("\nA2 organizers with at least one held event, by year:")
    w(held.groupby("yr", observed=False).organizer.nunique().to_string())
    w("\nA3 meeting regularity, recurring series (held meetings by year):")
    w(held[held.series_name != ""].groupby(["series_name", "yr"], observed=False).size().unstack().to_string())
    c = E[E.series_name == "CincyAI for Humans"]
    w("CincyAI for Humans: scheduled in the three-year window (to 14 Nov 2026):", int((c.d <= pd.Timestamp(COLLECTED)).sum()), "| held:", int((c.status == "held").sum()),
      "| cancelled:", int(c.status.str.startswith("cancel").sum()))
    last = held[held.d > pd.Timestamp("2025-11-14")]
    w("\nA5 audience of events held in the last 12 months (15 Nov 2025 - 14 Nov 2026):")
    w(last.audience.value_counts().to_string())
    nt = (last.audience != "technical").mean()
    w(f"Share aimed at an audience other than 'technical': {nt:.1%} of {len(last)} -> reaches beyond technologists: {nt >= 0.5}")
    w("\nA7 public-sector presence: events organised by a public body in the census:", int((E.organizer_type == "government").sum()))
    w("\nUpcoming in-person AI events found by the platform search (next 60 days):", int((E.status == "upcoming").sum()))
