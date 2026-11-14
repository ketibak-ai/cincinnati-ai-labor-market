# Cincinnati AI Labor Market 2.1 — design addendum

**For:** KetiB (author) · **Date:** 14 November 2026 · **Status:** check-in draft; nothing
pushed, published or sent.

This addendum extends `RESEARCH_DESIGN_MEMO.md` (13 November). That memo still stands. Read
this one for what 2.1 adds: a sixth lens on AI awareness and participation, and a register of
AI agents in local companies' workflows.

Repository state: local branch `v2.1`, started from `v2.0`. Three commits so far: the 2.1
prompt (`PROMPT_2.1.md`, 04f4738), the pre-registration extension (`PREREGISTRATION.md`
section 8, b33e1f1), and this addendum. The pre-registration was committed before any event,
membership, search-interest or agent data was collected. The 1.0 test suite passes: 16 of 16.
`main`, the `v1.0` tag and the `v2.0` branch are untouched.

---

## 1. The short version

1. **The new lens measures convening, not use.** No survey measures how many people here use
   AI, and no one publishes audited attendance. What can be counted is events held, how
   regularly groups meet, how many people have signed up, who the events are for, and which
   employers are in the room. The study will call this *awareness and participation* and keep
   it apart from *adoption*, which means AI in use at work.
2. **"Early indicator" is a hypothesis the study will test, not a premise.** Whether community
   activity comes before firm adoption is tested two ways (H14, H15). One of them may not be
   testable, because no public monthly series of AI postings exists for the metro. If so, the
   report will say that awareness is early *in principle* and unproven here.
3. **The comparison across metros carries the finding.** AI events rose everywhere. Three
   measures that exist in the same form in every metro (platform listings, chapter meetings of
   a national organization, Google search interest) make the comparison across all 19 Chamber
   peers. A full hand-built event census is collected for Cincinnati and six nearby metros.
4. **A trend can probably be rebuilt for Cincinnati but not for most peers.** The Internet
   Archive holds snapshots of Cincinnati's main community site in 16 separate months since
   January 2024. Coverage of peer-metro pages is much thinner. Expect a three-year trend for
   Cincinnati and a latest-12-months comparison across metros, and expect the report to say so.
5. **The agent register extends a file 1.0 already has**, from eight employers to all public
   companies headquartered here, the 25 largest employers, and local AI vendors, with every
   source graded. Only a company's own record or a named executive on the record supports a
   finding.
6. **Nothing in the 2.0 design changes.** H1–H11 and the hiring test are as they were. The
   five 2.0 decisions are still open and are restated in section 6 with five new ones.

---

## 2. How the additions fit the 2.0 design

The 2.0 memo ordered the lenses as a chain: adoption → labour market and output, with
capability and infrastructure as conditions. 2.1 puts awareness and participation at the front
of that chain: **awareness → adoption → labour market and output.** The chain is a claim about
sequence, and H14 and H15 test it.

The three-way separation 1.0 introduced becomes four-way: awareness and participation,
potential exposure, observed use, attributed displacement.

What 2.1 changes in the plan:

- **The adoption lens gains firm-level evidence.** 2.0 planned a phrase count of AI terms in
  10-K filings. 2.1 adds what each company says it is doing, in which function, and whether it
  is an agent or an assistant. The phrase count stays as the consistent series; the register is
  the description.
- **A new peer-comparison workload.** The like-for-like measures need one collection day per
  measure for 20 metros. The census needs page-by-page collection and archiving for seven.
- **The outlook gains leading indicators that can be updated every six months**, which the
  official series cannot.

What it does not change: geography, the peer rule, the hiring test, the data-center section's
tests, or any decision rule in sections 1–7 of the pre-registration.

**One caution on framing.** The 2.1 prompt describes awareness as "the first indicator of AI
being embraced". That may be right. The evidence may also show an enthusiastic community that
has not reached workplaces: events with few employers in them, and no relationship across
metros between convening and AI hiring. The pre-registration fixes in advance what would
count as each.

---

## 3. Sources: what exists today

Existence was checked on 14 November 2026. No value was recorded for any measure. Source
types: G = government, I = industry or advocacy, P = private platform, O = organizer-reported,
J = journalism.

| Measure | Source | Cincinnati | Peer metros | How far back | Type |
|---|---|---|---|---|---|
| Meetings held by recurring groups (A3) | Group newsletter archives; group event pages | The main community group publishes a newsletter issue around each monthly meeting, with issues found from November 2023 | To be found group by group | Cincinnati: to late 2023. Peers: unknown | O |
| Rebuilding past years | Internet Archive snapshots | Main community site: snapshots in 16 separate months, Jan 2024–Oct 2026; its newsletter site: 14 months from Apr 2024; local chapter page of a national organization: 11 months from Sep 2024 | Columbus chapter page: 8 months from Feb 2025; Louisville: 1 month; Meetup group pages with archived copies found for Columbus and Cleveland, one for Louisville, none found for Indianapolis or Pittsburgh under the obvious names | Thin outside Cincinnati and Columbus | — |
| Chapter meetings (L2) | AI Tinkerers city chapters | Chapter page exists | Chapter pages exist for 10 of 19 peers: Atlanta, Austin, Charlotte, Columbus, Kansas City, Louisville, Nashville, Pittsburgh, Raleigh, St. Louis. For the other nine the obvious address redirected to the national home page; a chapter may exist under another name | Each chapter lists its own events; depth to check | O |
| Platform listings (L1) | Eventbrite, Luma, Meetup | Searchable by city | Searchable by city | Platform search shows upcoming events only, so this is a forward 60-day snapshot, not a history | P |
| Search interest (L3, A9) | Google Trends by media market | Cincinnati media market exists | All peers have one | Monthly, 2004 on | P |
| Community size (A4) | Groups' own statements | Stated in newsletters at several dates | Unknown until collected | As far as archived statements go | O |
| Attendance claims | Organizer recaps, news items | Several claims exist and conflict (see pre-registration 8.0) | Unknown | — | O / J |
| Public-sector presence (A7) | City council committee recordings (Clerk of Council; copies on the Internet Archive); City budget books | Recordings exist (the 2.0 memo cites one). One search did not find published agendas or minutes for the AI task force itself. That is not a finding of absence; the Clerk's records have not been searched | Not planned beyond the six-metro subset | To check | G |
| Training on offer (A8) | IPEDS completions; college catalogues; library and workforce-board calendars | The federal programme classification has a specific code for Artificial Intelligence (11.0102) and for Data Science (30.70), so completions can be counted where institutions use them | Same source, all peers | IPEDS vintage to confirm, as in the 2.0 memo | G |
| Agent register | SEC EDGAR filings; earnings-call transcripts; company newsrooms | `data/ai_adoption_employers.csv` has eight employers from 1.0 | Not collected for peers (Cincinnati description only) | 2021 on | G (filings) / I |
| Largest-employers list | REDI Cincinnati's published list; Cincinnati Business Courier Book of Lists | REDI's public page cites the Courier's 2022–2023 list. The current Courier list is behind a paywall | — | — | I / P |
| Postings naming AI tools | CareerOneStop (the source 1.0 used for phrase queries) | Works by city and radius | Same tool, any city | Current postings only; no history | G |

Three limits follow from this table, and the report will state them:

1. **No history for platform listings or postings.** Both are snapshots on the collection day.
   The monitoring sheet (deliverable 5) is what turns them into a series, from now on.
2. **Cross-metro trends are probably out of reach.** The comparison across metros will be for
   the latest 12 months. Only Cincinnati, and perhaps Columbus, gets a three-year trend.
3. **The newsletter archive's index page refused an automated request** (the individual issues
   are reachable through search). Collection will go through a browser or the Internet
   Archive's copies. This is an ordinary obstacle, not a blocker.

---

## 4. The pre-registration extension (section 8 of `PREREGISTRATION.md`)

Committed before collection. In summary:

- **What had already been seen** is listed in 8.0: Cincinnati membership statements, the 2026
  meeting schedule and conflicting attendance claims, all from search snippets. No peer value
  and no count had been seen. So statements about Cincinnati's level are descriptive, and the
  one confirmatory test is comparative.
- **H12, confirmatory:** Cincinnati is "above its peers" on AI convening only if it lies above
  the middle half of the 19 peers on at least two of the three like-for-like measures; "below"
  by the mirror rule; otherwise "within the normal range of peers".
- **H13, descriptive:** participation "reaches beyond technologists" if at least half of the
  last year's events are aimed at a non-technical audience; employers are "in the room" if at
  least 10 of the 25 largest employers appear as host, sponsor or speaker's employer in three
  years. Both thresholds are conventions and are labelled so.
- **H14, exploratory:** across 20 metros, is convening related to postings that name AI tools?
  Rank correlation, shown as scatters, called "related" only at ρ ≥ 0.4 with p < 0.10 on two of
  three measures.
- **H15, descriptive:** does convening lead postings in time? Reported as not testable if no
  monthly AI-postings series exists.
- **H16, descriptive:** the agent register, reported whatever it shows. The sentence "AI agents
  are in production at large Greater Cincinnati employers" is used only if at least three
  in-scope employers have first- or second-grade evidence of an agent, as defined, in
  production.
- **The index** is computed last and published only if Cincinnati's rank is stable when each
  component is dropped.

---

## 5. Changes to the report outline

The 2.0 outline (memo section 10) is kept, with these changes:

- **Key findings** open with one sentence naming the three kinds of evidence: infrastructure,
  employment signals, and people and firms taking AI up.
- **New section 6, "Are people showing up? AI awareness and participation"**, placed before
  adoption: the event census; meeting regularity; community size with each figure attributed;
  who events are for; employers and public bodies present; Cincinnati against peers on the
  three like-for-like measures; what this cannot show.
- **Adoption (now section 7)** gains **"Agents at work"**: the register by function and stage,
  quantified claims with sources, what companies say about jobs, how many disclose nothing,
  and postings naming AI tools against peers. The Kroger and Fifth Third case box sits here.
- **Data centers** gains one paragraph: whether operators appear in the region's AI community.
- **"What the evidence can and cannot attribute"** gains the row: event activity is never
  evidence of a change in employment.
- **Outlook:** the awareness measures join the leading indicators, each with a threshold and
  an update date.
- **Methods appendix:** the event inclusion rule, search terms, sources searched with counts
  from each, the archive rule, source grades, and deviations from the pre-registration.
- **New one-page monitoring sheet** as a separate deliverable.

Later sections renumber by one.

---

## 6. Decisions that are yours

### 6.1 Still open from the 2.0 check-in

My recommendations are unchanged; the reasoning is in the 2.0 memo, section 9.

| # | Decision | Recommendation |
|---|---|---|
| 1 | Title | **Cincinnati AI Labor Market 2.1: Early Evidence on Awareness, Adoption, Hiring and Investment in Greater Cincinnati.** Alternatives: "…2.1: Is AI Narrowing the Entry Door to Professional Work in Greater Cincinnati?"; "…2.1: Who Is Showing Up, Who Is Hiring and What Is Being Built" |
| 2 | Indeed postings | Use narrowly: labelled private, change over time only, outlook and one robustness chart |
| 3 | The Richardson line | Take the name out of the findings, cite the City's recording, offer a right of reply; someone must check the audio before the grade is quoted |
| 4 | Newer AEI or projections | No swap; nothing newer exists for the metro |
| 5 | Workbook industry sheet | Show both baselines, 2024 first |

### 6.2 New in 2.1

**6. Which metros get the full event census.** Recommendation: Cincinnati plus six, chosen by
a rule and not by hand: every Chamber peer in Ohio (Cleveland, Columbus, Dayton) and the
nearest Chamber peer in each of Indiana, Kentucky and Pennsylvania (Indianapolis, Louisville,
Pittsburgh). All 19 peers still get the three like-for-like measures. Alternative: Cincinnati
and Columbus only, which halves the work and still gives the in-state comparison.

**7. Publish an AI Participation Index, or only its components?** Recommendation: components
first, and the index only if it passes the stability rule already written. A single number
travels well with journalists and the Chamber; it is also the kind of constructed figure this
study criticizes in others, and the reviewer made that point about 1.0.

**8. Ask organizers for their figures?** Recommendation: yes, after the public record is
collected, with one identical request to every organizer in all seven metros so the answers
are comparable. It needs your approval to send. Draft:

> Subject: Request for information — independent study of AI in Greater Cincinnati
>
> Hello,
>
> I am preparing an independent research study, *Cincinnati AI Labor Market 2.1*, on how AI
> is affecting the regional economy and workforce. One part compares public AI community
> activity across seven metro areas. I am sending the same four questions to every organizer
> so the answers can be compared.
>
> 1. How many meetings or events did your group hold in each of the last three years
>    (December to November)?
> 2. How many members or subscribers do you have today, and how do you count them?
> 3. What is typical attendance at a regular meeting, and how do you record it?
> 4. Roughly what share of attendees come from employers, and what share are students or
>    job-seekers?
>
> Anything you send will be labelled as reported by your organization. The study names
> organizations, not individual attendees. If you would rather not answer, that is fine, and
> the study will say only that no figure was available. A reply by [date] would be reflected
> in the report.
>
> Thank you,
> KetiB, [AFFILIATION]

**9. Private platforms as sources.** The study has used government data wherever possible.
This lens cannot: Google Trends, Eventbrite, Luma, Meetup and organizers' own pages are all
private. Recommendation: accept them for this lens only, each labelled by type, with no
private-source figure in a headline finding unless a second, independent source agrees.
Alternative: restrict the lens to government-checkable records (council recordings, budget
lines, IPEDS), which would be rigorous and would miss most of the activity.

**10. Which list defines the 25 largest employers.** REDI Cincinnati's public list rests on
the Business Courier's 2022–2023 Book of Lists. The current Courier list is paywalled.
Recommendation: use REDI's public list, state its vintage, and add any company on the 2026
Fortune 500 headquartered here that it omits. If you have access to the current Book of
Lists, tell me and I will use that.

---

## 7. After the check-in

Order of work for the 2.1 additions, alongside the 2.0 order of work (memo section 11):

1. Amend the pre-registration with your decisions.
2. Like-for-like collection for 20 metros, one day per measure, pages archived.
3. Cincinnati event census, then the six comparison metros; rebuild back-years from archives.
4. Agent register: filings and earnings calls first, then newsrooms, then named-executive
   reporting; postings naming AI tools on one day for 20 metros.
5. Tests for every new number; `METHODS_AWARENESS.md`.
6. Run H12–H16 once, then the index rule.
7. Write the two new report sections and the monitoring sheet; carry into the deck and site.

## 8. Risks and what is not yet verified

- **Survivorship.** Deleted event pages make the past look smaller. Mitigated by rebuilding
  only from records fixed at the time, and by leaving unrecoverable metro-years out.
- **Home-metro bias.** A hand-built census will always find more in the metro the researcher
  knows. This is why the like-for-like measures, not the census, carry the comparison.
- **Chapter coverage.** Nine peers showed no chapter at the obvious address. Each must be
  searched under other names before a zero is recorded.
- **Small numbers.** Twenty metros support a rank comparison and nothing stronger.
- **Organizer incentives.** Membership and attendance figures come from the people with most
  reason to state them high. They are attributed and never summed.
- **Not verified in this design stage:** every lead listed in the prompt (membership figures,
  attendance claims, event dates, product names) comes from search-result summaries, not from
  the pages themselves. None is used as a value anywhere. The task force's meeting record has
  not been searched in the Clerk's files. Whether a monthly AI-postings series exists for the
  metro is unknown.
