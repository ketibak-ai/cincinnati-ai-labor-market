# Monitoring sheet: Cincinnati AI Labor Market 2.1

One page. These are the indicators that will show whether the bull case or the bear case in
the report's outlook is happening. Values are as of mid-November 2026.

| # | Indicator | Value now | Bear signal | Bull signal | Source | How to update | How often |
|---|---|---|---|---|---|---|---|
| 1 | Hiring test: young workers' share of new hires in AI-exposed industries (four measures) | +0.01, +0.01, +0.03, −0.04 | −0.05 or lower on two measures | Stays inside the chance range | Census QWI | `fetch_qwi.py oh ky in`, then `analyze_hiring.py` (extend the post-period) | Quarterly |
| 2 | New hires of ages 22–24, all industries, against 2018–19 | −9% to −16% by industry group | Keeps falling | Recovers | Census QWI | Same run; `make_figures.py` writes `h1_hires_by_age_group_cincinnati.csv` | Quarterly |
| 3 | Share of Ohio businesses using AI | 22.2% (US 23.7%) | Gap with the US widens | Gap closes | Census BTOS | `fetch_public.py btos_state btos_national`, then `build_btos.py` | Monthly |
| 4 | Postings naming "AI agent" or "large language model", per 100,000 adults | 7.8; rank 13 of 20 | Rank falls | Above the peer median (8.3) | CareerOneStop | Repeat the searches in `METHODS_AWARENESS.md`; edit `analyze_awareness.py` | Every six months |
| 5 | AI events listed for the next 60 days, per 100,000 adults | 0.36; rank 15 of 20 | Rank stays 15th or lower | Above the peer median (0.50) | Eventbrite, Meetup | `collect_l1_platform_listings.py` | Every six months |
| 6 | CincyAI for Humans: meetings held in the last 12 months | 11 of 12 | Fewer than 9 | 11 or 12 | Newsletter archive | Add dates in `build_event_census.py` | Every six months |
| 7 | CincyAI for Humans: stated membership | "over 2,000" (March 2026) | No new figure, or lower | A higher stated figure | Newsletter | Add a row to `ai_community_groups.csv` via the script | Every six months |
| 8 | Large employers with a verified AI agent in production | 1 (a vendor) | Still 1 in a year | 3 or more | Company filings and releases | Add rows in `build_agent_register.py` | Yearly, after annual reports (March) |
| 9 | Annual reports naming AI (nine companies) | 9 of 9 for fiscal 2025 | — | Reports state scale or job effects | SEC EDGAR | Repeat the search in the report's methods | Yearly |
| 10 | Output per worker, exposed sectors, two-year change | +2.4% (peer median +7.5%) | Gap widens | Reaches the peer median | BEA county GDP; QCEW | `fetch_public.py bea_cagdp9`, `fetch_qcew_counties.py <year> p1`, `analyze_output.py` | Yearly (December) |
| 11 | Data-center load under contract, Duke Energy Ohio | 250 MW | — | More than 250 MW, with jobs above 0.5 per MW | PJM Load Analysis Subcommittee | Read the next Duke submittal; add rows to `h8_data_center_evidence.csv` | Yearly (autumn) |
| 12 | Data-center industry jobs, published metro counties | 1,977 (2025) | — | Up by 1,000 on 2022 (1,576) | BLS QCEW | `fetch_qcew_counties.py <year> p1` and the block in the report's methods | Yearly |
| 13 | Total jobs, two-year change, rank among 20 | +0.7%; 10th | Bottom quarter | Top half | BLS CES | `fetch_ces_peers.py`, `analyze_h9.py` | Yearly |
| 14 | Labor force | Up in ACS to 2025; down in monthly series since Sept 2025 | 2026 ACS confirms a fall | 2026 ACS shows no fall | ACS; LAUS benchmark | `analyze_h9.py` with the 2026 file | March and September 2027 |

After any update, run `python tests/test_study_2_1.py`. A failing test means a published number
has moved: change the report first, then the test.

**Four pieces to add when time allows:** state layoff notices coded by stated reason; hosts and
sponsors of each event; the same event census for Columbus; the four remaining search terms.
