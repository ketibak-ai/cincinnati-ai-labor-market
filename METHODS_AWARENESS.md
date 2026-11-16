# How AI awareness and participation were measured (version 2.1)

This note gives the search terms, sources and rules behind section 5 of the report, so the
collection can be repeated. Collection day: **14 November 2026**. All of these sources are
private platforms or organizer-reported. None is audited.

## What is measured, and what is not

The measures count **public convening around AI**: events held, how regularly groups meet, how
many people have signed up, and who events are for. They do not measure AI use. People who
attend are self-selected, private training is invisible, and organizers have a reason to state
high numbers. Membership and attendance figures are recorded as attributed quotations and are
never added together (a test enforces this).

## Like-for-like measures (20 metros)

Run identically for Greater Cincinnati and the 19 metros in the Chamber's peer set. Each is
divided by residents aged 18 to 64 (Census Vintage 2025 county estimates).

### L1. Events listed on public platforms

- **Script:** `scripts/collect_l1_platform_listings.py`. Output: `data/l1_platform_events.csv`,
  `data/l1_platform_counts.csv`.
- **Sources:** Eventbrite's public search page for each principal city (every results page, up
  to five); Meetup's public "find events" page for the city (first results page).
- **Search terms (seven):** AI; artificial intelligence; generative AI; machine learning; LLM;
  ChatGPT; agents.
- **Kept if:** in person; dated within 60 days after the collection day; the title passes a
  fixed test for AI terms (the pattern is in the script); for Eventbrite, the venue is within
  25 miles of the principal city's centre. De-duplicated by title and date.
- **Requests:** 575 pages; all succeeded after one retry of 24 that were rate-limited.
- **Known weaknesses:** Luma is not covered (no search by city and keyword). The title test
  misses AI events that do not say so in the title. Each platform's ranking and search area are
  its own. Two rules were added after the first count (the 25-mile limit, and titles ending in
  "AI" such as "CincyAI"); both apply to every metro and are logged as deviation D13.

### L2. Chapter meetings of a national organization

- **Script:** `scripts/build_l2_chapter_meetings.py`. Output: `data/l2_chapter_events.csv`,
  `data/l2_chapter_meetings.csv`.
- **Source:** AI Tinkerers chapter pages (`<city>.aitinkerers.org`), each of which lists every
  chapter event with its date. Dates were transcribed from the pages.
- **Counted:** events held from 15 November 2025 to 14 November 2026.
- **Coverage:** 10 metros have a chapter with events; 3 have a chapter page with no events; for
  7 no chapter was found at the obvious address or by a site search. The network's chapter
  directory sat behind a bot check and was not read, so those seven are "not found", not
  verified zeros.
- **Known weakness:** one organization. A metro whose main community is home-grown, as
  Cincinnati's is, is understated.

### L3. Search interest

- **Source:** Google Trends, "Interest by subregion" at metro (media market) resolution, United
  States, past 12 months, exported from the page as CSV. Files: `raw/awareness/trends/`.
- **Terms collected (three of seven planned):** ChatGPT; Claude AI; Microsoft Copilot. The
  service stopped supplying the export after three terms. The metro's score is the mean of its
  three values.
- **Known weaknesses:** a sampled index, relative within each term; media markets are larger
  than metros.

### Postings naming AI tools (the adoption-side comparison)

- **Source:** CareerOneStop Job Finder (US Department of Labor, National Labor Exchange),
  phrase search, 25-mile radius of each principal city. The count is the site's own results
  line. Output: `data/postings_ai_tools_20_metros.csv`.
- **Phrases collected (three of fourteen planned):** "AI agent"; "ChatGPT"; "large language
  model". "agentic" was dropped because the tool stems it to "agent". One search failed twice
  (Raleigh, "ChatGPT").

## The Cincinnati event census

- **Script:** `scripts/build_event_census.py`. Output: `data/ai_events.csv` (56 rows),
  `data/ai_community_groups.csv`, `data/ai_event_attendance_claims.csv`.
- **Window:** 1 December 2023 to 30 November 2026, in three years ending 30 November.
- **Inclusion rule:** AI is the stated main subject; open to people outside the host; held in
  person in the metro, or virtual and run by an organizer based in it. A multi-day conference
  is one event. An event is listed only if a dated public record of it was read.
- **Sources read:** the CincyAI for Humans newsletter archive (83 issues, October 2023 to
  November 2026); the AI Tinkerers Cincinnati chapter page; University of Cincinnati news
  pages; the L1 platform search.
- **How past years were rebuilt:** from records fixed at the time (one newsletter issue around
  each meeting), not from today's event pages, which lose old events.
- **Not done:** hosts and sponsors were not recorded for each event, so employer presence could
  not be measured. Training on offer was not measured. The City AI task force's meeting record
  was not searched in the Clerk's files. Sources listed in the plan but not searched: LinkedIn
  Events, the public library and workforce-board calendars, Chamber and CAIC event pages.
  Pages were not saved to the Internet Archive in this round.

## Repeating the collection

Run on one day, in this order:

```
python scripts/collect_l1_platform_listings.py    # set TODAY in the script to the new day
python scripts/build_l2_chapter_meetings.py       # after updating the transcribed dates
python scripts/analyze_awareness.py               # after exporting new Trends files and re-running the postings searches
python scripts/build_event_census.py              # after adding new events to the lists in the script
python tests/test_study_2_1.py                    # the tests will fail on changed values: update them deliberately
```
