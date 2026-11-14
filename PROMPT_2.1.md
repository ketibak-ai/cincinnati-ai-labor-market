# Independent research assignment: Cincinnati AI Labor Market 2.1

Author: [KetiB, AFFILIATION]

This prompt replaces the 2.0 prompt. Everything 2.0 asked for still stands. 2.1 adds two things:
a sixth lens, **awareness and participation** (the region's AI events, communities and
training), and a **register of how local companies are putting AI agents into their workflows**.
Sections marked **NEW IN 2.1** are the additions; the rest is carried over from 2.0.

---

## Your role

You are the lead economic researcher on this study, and the study is yours. The research
questions, methods and conclusions are your call. You will defend them to expert reviewers, and
you will keep building on this work. Do not simply polish the existing report. Treat it as a
preliminary draft: verify it independently, research further, and correct it, substantially
where the evidence requires.

I'm personally bullish on what AI can do for this region. Don't let that steer the findings.
The findings follow the evidence: where it supports optimism, say so plainly, and where it
doesn't, say that too. A study that reads as advocacy would lose the readers below, and the
strongest bull case is one that has survived the evidence.

## Objective

Produce a rigorous economic research study of how AI is affecting Greater Cincinnati: its
economy, employment, occupational demand and workforce requirements, and how far its people and
firms have begun to take AI up.

The study rests on three kinds of evidence, and the report should say so early:

1. **Infrastructure**: data centers and the power, money and policy around them.
2. **Employment signals**: hiring, occupations, wages, layoffs and what employers say.
3. **People and firms taking it up** (NEW IN 2.1): AI events, communities, training, and
   companies putting AI agents into real work.

Write it in the style of a Brookings Metro report:

- key findings up front;
- evidence before interpretation;
- comparisons with peer metros;
- findings kept separate from policy implications;
- a nonpartisan tone;
- charts with source lines;
- plain language a policy reader can follow;
- a methods appendix with endnotes.

Follow the style only. Don't use Brookings branding or imply any affiliation.

Readers: economists who may referee it, journalists, and regional decision-makers (the Chamber,
CAIC, JobsOhio, city and county officials, and Ohio legislators working on data center bills).
It has to hold up against a hostile expert reader.

## What exists

**Version 1.0 (published):**

- Report (with methodology appendix): claude.ai/artifact/RszZtyNchr44mfR2PeNqvZ
- Presentation (22 slides): claude.ai/artifact/K8Q7ijPQZQkuGuwqFpyqMV
- Website: ketibak-ai.github.io/cincinnati-ai-labor-market
- Repo (data, code, Excel workbook, tests):
  `C:\Users\Twink\OneDrive\Documents\PiNK Analytica\cincinnati-ai-labor-market`, synced with
  github.com/ketibak-ai/cincinnati-ai-labor-market. Tag `v1.0` marks it.

**Version 2.0 (design stage only, never published):** on the local branch `v2.0` there is a
research design memo (`RESEARCH_DESIGN_MEMO.md`), a draft pre-registration
(`PREREGISTRATION.md`, hypotheses H1–H11), a new Part I in `AUDIT.md`, and a plain-text copy of
the 1.0 report in `archive/v1.0/`. No 2.0 analysis has been run. Five decisions from the 2.0
check-in are still open (title, Indeed postings, the Richardson line, AEI and projections
vintages, the workbook's industry sheet).

Start by reading `README.md`, `CALCULATIONS.md`, `VERIFICATION.md`, `AUDIT.md`,
`RESEARCH_DESIGN_MEMO.md` and `PREREGISTRATION.md`, and run `python tests/test_study.py`. The
repo tells you what 1.0's numbers are, not whether they are right. Keep the 2.0 design: 2.1
extends it, and does not restart it.

1.0's main claims. Treat each as a hypothesis to re-test:

1. AI exposure in the region is average (0.088 vs 0.093 nationally).
2. The real fragility is slow growth: jobs grew only 0.7% in two years while the labor force
   shrank, and 98% of projected openings come from replacing workers who leave, not from growth.
3. Exposure rises with pay. The most exposed jobs are professional: accountants, HR
   specialists, analysts, financial managers.
4. The region buys AI capability rather than building it.
5. Data centers are not a jobs story. The Chamber's own table gives 0.15 FTE per MW, while the
   figure that circulates is 3,203 jobs.
6. There are no measurable AI-caused job losses so far. The main risk is fewer entry-level
   hires in exposed professional jobs, which is hard to see in job counts.

Your knowledge ends around June 2026. Look up anything after that.

## Measure AI's impact beyond job counts

1.0 measured AI's impact almost entirely through employment levels. The labor market stays at
the center, but employment levels alone can't separate AI from everything else moving the
economy. Build the study on these six lenses. If you find a better framework, use it and say
why.

1. **Awareness and participation (NEW IN 2.1): are people here showing up for AI?** Events,
   meetups, community membership, training. This is the earliest signal available: people
   attend a meetup or take a class before their employer changes a workflow, and long before
   anything reaches the employment data. Full method in the next section.
2. **Adoption: are local firms using AI?** Sources: Census Business Trends and Outlook Survey
   (state level; no Cincinnati metro estimate exists), AI job postings, the Cleveland Fed's
   Beige Book and SORCE survey, AI disclosures in SEC filings of companies headquartered here,
   Anthropic Economic Index (state level), and the agent register below (NEW IN 2.1).
3. **Capability: is the region building AI or buying it?** Sources: AI patents by inventor
   location (USPTO AI Patent Dataset with PatentsView), university R&D (NSF HERD), graduates in
   AI, data science and computing (IPEDS), venture funding (private sources, labeled as such).
4. **Labor market: who is hired, into what, with which skills?** Sources: Census Quarterly
   Workforce Indicators (hires and new-hire earnings by worker age and industry, by county),
   OEWS occupations and wages, CES and LAUS, WARN layoff notices and their stated reasons,
   skill requirements in job postings.
5. **Output: are exposed industries producing more per worker?** Source: BEA GDP by county and
   industry, compared with employment in the same industries.
6. **Infrastructure: what physical investment is AI bringing?** See the data center section.

Read the lenses as a sequence: awareness → adoption → changes in hiring and output, with
capability and infrastructure as the conditions around it. The sequence is a hypothesis to
test, not an assumption. People attending events may never change how firms work.

Attributing anything to AI needs comparisons, not levels:

- exposed vs less-exposed industries and occupations;
- early-career vs experienced workers;
- before vs after late 2022;
- Cincinnati vs peer metros.

QWI hires by age and industry are the direct test of 1.0's central risk: a narrowing entry door
to professional work. Brynjolfsson, Chandar and Chen (2025) used this kind of design nationally
with payroll data. The main threat to this design: the 2022–23 interest-rate rises hit finance
and tech, the most AI-exposed industries, just as generative AI arrived. Address it explicitly.
Even with these designs, say plainly what the evidence can and can't attribute to AI.

---

## NEW IN 2.1: Measuring AI awareness and early adoption

### Why this lens, and what it is called

No survey measures how many people in Greater Cincinnati use or understand AI. What can be
observed is whether people organize around it and turn up: how many AI events are held, by
whom, for whom, how regularly, and how large the communities behind them are. Call the thing
being measured **AI awareness and participation**. Do not call it adoption. Adoption means AI
in use at work, and that is lens 2.

Keep four rungs apart everywhere in the report, because each is evidence of a different thing:

| Rung | What it shows | Example evidence |
|---|---|---|
| 1. Awareness | People are curious enough to convene | Events held, organizers active, search interest |
| 2. Participation | People keep turning up | Meeting regularity, membership, sold-out events |
| 3. Skill-building | People are learning to do it | Courses, certificates, hackathons, completions |
| 4. Use at work | Firms have put it into workflows | The agent register, postings naming AI tools, filings |

### The honest constraint: there is no attendance data

No one publishes audited attendance for these events. Do not estimate it and do not add up
organizer claims into a regional total. Measure what is countable and checkable instead:

- **Events held** can be counted from dated public pages.
- **Meeting regularity** can be counted: how many meetings a group held in a year, and whether
  it missed any.
- **Membership and subscriber counts** are published by some groups. They are self-reported.
- **Attendance figures** exist only as organizer statements or press reports. Record each with
  its source and label it organizer-reported. Report them as individual, attributed figures.

### Step 1: build an event census

Create `data/ai_events.csv`, one row per event, for **Greater Cincinnati and each comparison
metro**, covering **1 December 2023 to 30 November 2026** (three years, so there are two
year-over-year changes, and the start falls just after the region's main AI community group
was founded).

Columns: `event_id`, `metro`, `event_name`, `series_name` (blank if one-off), `organizer`,
`organizer_type` (community, university, employer, vendor, chamber or advocacy, government,
library or nonprofit), `date`, `format` (in person, virtual, hybrid), `venue`, `county`,
`audience` (general public, technical, business or executive, student, sector-specific,
public sector), `price` (free, paid, amount), `attendance_reported`, `attendance_source`,
`attendance_source_type`, `capacity_or_rsvp_shown`, `sold_out_flag`, `employers_named`
(hosts, sponsors, speakers' employers), `source_url`, `archive_url`, `date_collected`.

**Inclusion rule, fixed before collecting:** an event counts if (a) AI is its stated main
subject, not one talk in a general programme; (b) it was open to people outside the hosting
organization; and (c) it was held in person in the metro, or was virtual or hybrid and run by
an organizer based in the metro. Company-internal training does not count here (it belongs in
the agent register if the company discloses it). A multi-day conference is one event, with its
number of days and sessions recorded.

**Where to look.** Search every one of these and record how many events each produced, so a
reader can see how hard you looked:

- event platforms: Eventbrite, Luma, Meetup, LinkedIn Events, searched by metro and a fixed
  list of terms written down in advance;
- community groups' own sites and newsletter archives;
- universities and colleges: UC (including the 1819 Innovation Hub), Xavier, NKU, Miami,
  Cincinnati State, Gateway;
- institutions: the Cincinnati Regional Chamber, Cincinnati AI Catalyst (CAIC), OhioX,
  Cintrifuse, Main Street Ventures, REDI Cincinnati, the Northern Kentucky Chamber;
- public bodies: the City's AI task force and council committees (agendas and recordings are
  public records, which makes them the most checkable series of all), Hamilton County, the
  public library's programme calendar, workforce boards, SCORE and the SBDC;
- local news event listings.

**Archive every page.** Event pages are deleted after the event. Save each source page to the
Internet Archive when you collect it and store the archive link in the row. An event with no
archived or live page behind it does not go in the census.

### Step 2: rebuild the past from archived snapshots, not from today's pages

This is the main threat to any trend in this lens. Groups delete old event pages, so a count
made today undercounts earlier years and manufactures growth. For each recurring group, rebuild
its history from dated records that were fixed at the time: newsletter archives with one issue
per meeting, Internet Archive snapshots of the group's page, and dated news coverage. Report,
for each group and year, how many meetings you could confirm and from what. If a year can't be
rebuilt for a metro, say so and leave that year out of the comparison. Never fill it in.

### Step 3: the measures

Define each of these in `PREREGISTRATION.md` before collecting. Report them separately first.

| # | Measure | Definition | What it answers |
|---|---|---|---|
| A1 | Events per year | Census events in each 12 months, per 100,000 residents aged 18–64 | How much AI convening is there, and is it growing? |
| A2 | Active organizers | Distinct organizers with at least one event in the year; and how many are new | Is this one group or a broad scene? |
| A3 | Meeting regularity | For each recurring series: meetings held in the last 12 months, and months with no meeting | "How many meetings were held in the past year?" |
| A4 | Community size | Membership or subscriber count each group publishes, with the date; earlier values from archived pages | How many people have opted in? |
| A5 | Reach beyond technologists | Share of events aimed at general public, business, students, public sector or a non-tech industry | Is awareness spreading past engineers? |
| A6 | Employer presence | Distinct local employers named as host, sponsor or speaker's employer | Are firms in the room, or only individuals? |
| A7 | Public-sector presence | Meetings of public AI bodies held; public bodies hosting events | Is government engaged? |
| A8 | Training on offer | AI courses, certificates and non-credit classes offered locally; completions where IPEDS reports them | Can people here learn it? |
| A9 | Search interest | Google Trends, Cincinnati media market vs peers and the US, fixed list of terms, monthly | An independent check that needs no organizer |

A6 is the bridge to lens 2. An event scene with no employers in it is a hobbyist scene. One
where the region's large employers host, sponsor and speak suggests awareness is reaching
workplaces.

Report attendance figures in their own table: event, figure, who reported it, date, source.
Where two sources disagree about the same event, show both.

### Step 4: compare with other metros using like-for-like sources

A count for Cincinnati alone means nothing. Use the peer rule already fixed in
`PREREGISTRATION.md` section 2. The event census is labor-intensive, so collect it in full for
a **named subset** chosen before collecting: Columbus, Louisville, Indianapolis, Cleveland and
Pittsburgh, plus Dayton as an adjacent labor market whose events draw on the same people.
State that this is a subset and why.

Prefer sources that exist in the same form in every metro, because they are comparable by
construction: national organizations with city chapters that run a standard format (count each
chapter's meetings the same way), Google Trends media markets, IPEDS, and one fixed search on
each event platform run identically for every metro on the same day. A hand-built census will
always be more complete for the home metro than for peers. Say so, and treat the like-for-like
sources as the primary comparison and the full census as description of Cincinnati.

### Step 5: test whether awareness means anything

Awareness is only worth reporting as an "early indicator" if it relates to something later.
Test it; don't assert it.

- **Across metros:** do the metros with more AI convening per person (A1, A3, A9) also show
  more AI job postings per posting, and higher state BTOS AI-use rates? With six or seven
  metros this is a rank comparison shown as a scatter, not a regression. Say so.
- **Inside Cincinnati:** do the employers that appear in the event census (A6) also appear in
  the agent register and in AI-related postings? Report the overlap as counts.
- **Over time:** did growth in convening come before, with, or after growth in AI postings?

If awareness is unrelated to every adoption measure, say that plainly: the region has an
enthusiastic community that has not yet shown up in how firms work. That is a finding.

### Step 6: an index, only if it earns its place

After the separate measures, you may combine A1, A3, A4, A5, A6 and A9 into one **AI
Participation Index** for the comparison metros. Rules: components standardized across metros,
equal weights fixed before any value is computed, one sensitivity check dropping each component
in turn, and the index labeled as a constructed summary, the same label the study applies to
other people's model output. If the ranking changes when one component is dropped, report the
components and leave the index out.

### What this lens cannot show

Write these into the report:

- It measures convening, not use. A person can attend ten events and never use AI at work.
- People who attend are self-selected. Nothing here describes the average resident or worker.
- It misses everything private: internal company training, vendor workshops, online courses
  taken alone. Those may be most of the real learning.
- Membership counts are self-reported, never audited, and include people who signed up once.
- Organizers and sponsors have a reason to report high numbers.
- Platform coverage changes: a group moving from one platform to another looks like a group
  dying and another being born.
- Virtual events have no geography.

### Asking organizers directly

Published records may not include membership or attendance. A short, identical request to each
organizer in every comparison metro would fill gaps: meetings held in each of the last three
years, current membership and how it is counted, typical attendance, and share of attendees
from employers versus students or job-seekers. Draft the request. **Sending it needs my
approval**, like any message. Anything received is labeled organizer-reported, and
non-responses are reported too.

### Leads from earlier sessions. All unverified

- CincyAI for Humans: a community group founded October 2023, monthly meetups, registration
  through Eventbrite and its own site (not Meetup), a newsletter archive with roughly one issue
  per meeting. Its own newsletters have stated membership of over 1,400, then over 1,700, then
  over 2,000 by spring 2026. It calls itself the largest AI meetup in Ohio.
- Cincy AI Week: an annual multi-day event each June since 2024. Attendance figures in
  circulation conflict: "nearly 1,500" for 2024 in one report; "1,100 over three days" in a
  2025 recap; "over 1,000 attendees, 175 speakers, 150 volunteers" in another. Don't use any of
  them until each is traced to who said it and about which year.
- AI Tinkerers has a Cincinnati chapter and chapters in other cities, which makes it a possible
  like-for-like comparison. Check which peer metros have one.
- CincyDATA (Cincinnati Data and AI Users Group) is reported to meet monthly.
- OhioX runs an Ohio AI Summit (a 2024 figure of 375+ attendees is in circulation; one is
  listed for 18 November 2026). A separate "Ohio AI & Innovation Summit" on 30 July 2026 was
  run by a different organization. Don't merge them.
- UC's 1819 Innovation Hub held an AI + Robotics Summit in May 2026 and has hosted sessions on
  agentic AI.
- Technology First (Dayton) runs AI events that Cincinnati-area people may attend.
- Louisville held an AI Week in February 2026.
- The Internet Archive holds snapshots of cincyai.org in 16 separate months from January 2024
  and of the group's newsletter site in 14 months from April 2024; coverage of peer-metro
  chapter pages is thinner (Columbus 8 months, Louisville 1, Indianapolis none found).

---

## NEW IN 2.1: How local companies are putting AI agents into their work

The repo already has `data/ai_adoption_employers.csv` (eight employers). Extend it into a
register of **what local companies say they are doing with AI, and with AI agents in
particular, and how**.

**Who is in scope.** (1) Public companies headquartered in the metro; (2) the 25 largest
employers in the metro whoever owns them, including hospitals, universities and governments;
(3) AI vendors and service firms based here that sell agents to others. Group 3 is the supply
side and feeds the "buying or building" test (H6).

**Define the terms before coding anything.** An **AI agent** is a system that carries out a
task of several steps by itself, using tools or other software, with a person reviewing the
result at most. An **AI assistant** drafts or suggests and a person carries out each step. A
company calling something an "agent" does not make it one: code what the source describes.

**For each company record:** the business function (software development, customer service,
marketing, supply chain, finance and accounting, HR and recruiting, claims or underwriting,
clinical documentation, legal and compliance, other); whether it is an agent or an assistant;
its stage (announced, pilot, in production); the scale the company states (users, share of
work, volume handled); what the company says it does to jobs, in its own words; the date; the
source; and the source grade below.

**Grade every source. Only grades 1 and 2 support a finding.**

| Grade | Source | Use |
|---|---|---|
| 1 | The company's own record: SEC filing, earnings call transcript, investor presentation, official press release | Findings |
| 2 | A named executive on the record in dated reporting or a recorded talk | Findings, attributed |
| 3 | A vendor's case study naming the company | Context only; the vendor is selling |
| 4 | A consultant's or marketer's description of what the company could do | Not used as evidence about the company |

**Add a measure with a real sample behind it.** In the job-postings data, count postings in the
metro that name specific AI tools or agent skills (a fixed term list written in advance), by
occupation group and employer, and compare with peers. Postings show what firms will pay for.

**What to report.** A table by function showing where agents are in production against where
they are only announced; the quantified claims, each with its source; what each company says
about jobs (keeping the three-way separation: capability, use, and the company's own
attribution of job changes); and how many in-scope companies disclose nothing at all. Silence
is common and is not evidence of no use. Give the Kroger and Fifth Third comparison the space
the reviewer asked for.

**Leads, unverified:** Fifth Third's filings mention planned "agentic workflows"; Kroger has
described "frontline associate agents in development"; CBTS (Cincinnati) announced a product
called Forge Agents in September 2026; small local firms selling agents include 513 AI and DH
Studios; a May 2026 CDO Magazine roundtable in Cincinnati discussed infrastructure for agentic
AI. A consultancy's page on what agents "could" do at The Cincinnati Insurance Company is a
grade 4 source.

---

## Lenses for interpretation

Bring three analysts' published thinking to the interpretation of your findings, and test it
against the strongest skeptics.

- **Noah Smith** (Noahpinion): comparative advantage. Even where AI can do a task, people keep
  the work where their relative advantage lies, and the binding limits are compute and energy
  (for example, "Plentiful, high-paying jobs in the age of AI", 2024). Ask: what is Greater
  Cincinnati's comparative advantage when routine cognitive work gets cheap, and which local
  jobs does AI complement rather than replace?
- **Ezra Klein** (with Derek Thompson, *Abundance*, 2025): growth is limited by the ability to
  build housing, energy and transmission, and by the capacity of public institutions. Ask: can
  the region build fast enough (power, housing for young workers, permitting, city and state
  capacity) to capture AI-driven growth? Klein has also discussed AI's risks to workers and to
  institutions. Represent that side of his thinking too.
- **Azeem Azhar** (Exponential View; *The Exponential Age*, 2021): technologies improve and get
  cheaper exponentially, while institutions adapt slowly. He calls this the "exponential gap".
  Ask: how fast is adoption moving here, and where is the gap between what firms adopt and what
  workers, schools and governments are ready for? The awareness lens bears directly on this
  question: compare how fast community participation is growing with how fast institutions
  (schools, workforce boards, city government) are responding.
- **The skeptics:** Daron Acemoglu ("The Simple Macroeconomics of AI", 2024) expects modest
  productivity gains. David Autor argues that AI can rebuild middle-skill work only if it is
  used to extend workers' expertise rather than replace it. Use them to test the bull case, not
  as decoration. For the awareness lens, add the diffusion literature: awareness of a
  technology has historically run far ahead of productive use. Cite specific work you have
  confirmed exists.

Use each person's published arguments, cite the specific piece, and check that you describe
their position accurately. Don't attribute views they haven't stated, and don't imitate their
voices. The report's voice stays that of a Brookings-style study.

Put this interpretation in an outlook section that is clearly separate from the findings. It
gives a bull case, a bear case, and the leading indicators that will show which one is
happening in Greater Cincinnati. The awareness measures belong among the leading indicators,
each with the level or change that would count as a signal.

## Sources to include

Alongside the government data, use these sources wherever they bear on the study:

- **OhioX**, the statewide tech and innovation industry association: its reports, data and
  policy positions on Ohio's tech workforce, AI and data centers, and its events. It is an
  industry advocacy group, so treat its figures as you treat the Chamber's: trace each one to
  its method and primary source before using it, and label it.
- **Marketplace**, from American Public Media: its reporting on AI and work, data centers, and
  Ohio and Cincinnati. Use it for on-the-ground reporting, employer and worker voices, and
  national context. Trace any number it reports to the primary source. Cite each story or
  episode with its date. Quote briefly with attribution; don't reproduce articles or
  transcripts.
- **Community organizers' own records** (NEW IN 2.1): newsletters, event pages, recaps. They
  are the only record of most events. Label them organizer-reported and archive each page.

## Scope

**Geography:** define "Greater Cincinnati" once and use that definition everywhere. The default
is the Cincinnati, OH-KY-IN MSA (CBSA 17140). Watch for sources that use the name for a
different area: Ohio's "Cincinnati MSA" projections leave out the Kentucky and Indiana
counties. For events, the venue's county decides. Dayton-area events are recorded and reported
separately, not counted as Cincinnati's.

**Data window:** use the latest data available up to 30 November 2026, and nothing dated later.

- Official series lag and will end earlier. Never extrapolate to fill the gap; state the last
  real data point.
- Postings, legislation, regulatory filings, company announcements, events and news can run to
  November.
- Keep a vintage table (series, last data point, release date, source) in the report and in
  `CALCULATIONS.md`. The event census and the agent register each get a row giving their
  collection date.
- Check whether newer releases exist of the Anthropic Economic Index and of the state
  projections. Don't swap either until I decide.

**Versioning:**

- `v1.0` stays tagged and untouched. The `v2.0` branch stays as the record of the design stage.
  Work on the branch `v2.1`, which starts from `v2.0`.
- Name the project "Cincinnati AI Labor Market 2.1" everywhere. 2.0 was never published, so the
  public sequence is 1.0 then 2.1; say once, in the report's front matter, that 2.0 was an
  unpublished design stage.
- On `v2.1`, update the tests to the new values and give every new number a test, including
  the event census counts and the agent register. The `v1.0` tag keeps 1.0's tests.
- When 2.1 is published, with my approval, 1.0 stays reachable: add an archive page on the
  site, and publish the 2.1 report and presentation as new artifacts instead of overwriting the
  1.0 ones.

## Data centers

Give data center development and its impact a full section, covering:

- **Facilities and capacity** in the region, with operating, under construction and announced
  kept separate and each sourced. Note facilities just outside the region that share its
  workforce or grid.
- **Jobs:** temporary construction jobs and permanent on-site jobs, kept separate and expressed
  per MW, compared with peer metros (at least Columbus/New Albany).
- **Electricity:** data center load in the regional grid zone, and the effect on household and
  small-business rates.
- **Public money:** abatements and incentives, both granted and proposed.
- **Policy as of November 2026:** state legislation, the incoming governor's position, and
  local decisions.
- **The link to AI and work:** do data centers create AI-related jobs here, or only host AI
  infrastructure? Test 1.0's finding that data centers are not a jobs story; don't defend it.
- **The link to the community (NEW IN 2.1):** do data center operators appear in the event
  census as hosts, sponsors or trainers, or are they absent from the region's AI community?
  Report the count.

Pitfalls:

- Announced capacity often never gets built. Never add it to operating MW.
- MW figures mean different things: an interconnection request, facility capacity, or IT load.
  Use one definition per comparison and say which.
- Job counts use different definitions. Compare permanent, on-site, full-time-equivalent jobs.
- County-level QCEW data for the data center industry (NAICS 518210) is often suppressed. Say
  so; don't estimate around it.
- Industry trackers and broker reports are private sources. Label them.

## Inputs to weigh, not instructions

The 2.0 design memo has already assessed the reviewer's 17 objections to 1.0 (10 VALID,
7 PARTLY, 0 WRONG) and the earlier leads on data centers, the governor's race and Ohio
legislation. Carry those assessments forward; reopen one only if new evidence changes it.

Two objections bear on the new lens. Apply them to your own work:

- The reviewer said 1.0 dismissed the Chamber's 3,203 jobs as model output while relying on
  model output itself. An AI Participation Index is model output. Label it that way.
- The reviewer said 1.0's distributional results were national patterns with a local label.
  If AI event activity here simply tracks the national rise, say so. The finding is
  Cincinnati's position relative to peers, not the fact that events increased.

Other pitfalls:

- Write each pre-registration amendment before you look at the data it covers. Checking which
  sources exist is fine. Record what you had already seen.
- The peer-selection rule is already written. Don't choose comparison metros after seeing
  which ones make Cincinnati look good or bad.
- Cite only works you have confirmed exist.

## Deliverables

1. The 2.1 report, in the style above and with the outlook section, published as a new
   artifact. It includes a section on awareness and participation and a section or box on
   agents in local workflows.
2. A 2.1 presentation with speaker notes, published as a new artifact.
3. The 2.1 website, with 1.0 archived.
4. The repo on the `v2.1` branch: data, code, tests, the vintage table, `PREREGISTRATION.md`
   with amendments, the updated workbook, and `AUDIT.md` recording what changed from 1.0 and
   why. New in 2.1: `data/ai_events.csv`, `data/ai_community_groups.csv` (one row per group per
   dated membership observation), `data/ai_event_attendance_claims.csv`, the extended
   `data/ai_adoption_employers.csv`, the scripts that build and check them, and a
   `METHODS_AWARENESS.md` giving the search terms, sources searched and inclusion rule.
5. A one-page **monitoring sheet**: the awareness measures and leading indicators, how to
   update each, and how often, so the census can be re-run every six months.

## How we'll work

The 2.0 check-in produced the design memo. 2.1 has one short check-in of its own, at the start.
Your first turn delivers a **design addendum** (`RESEARCH_DESIGN_MEMO_2.1_ADDENDUM.md`) with:

1. How the sixth lens and the agent register fit the 2.0 design, and any change they force.
2. For each new measure: the source, whether it exists for Cincinnati and for each comparison
   metro, and how far back it can be rebuilt. Check existence only. Record no values.
3. The pre-registration amendment: new research questions and hypotheses, definitions,
   decision rules, and what you had already seen.
4. The changes to the report outline.
5. Your recommendations on the decisions that are mine:
   - the five still open from 2.0 (restated in one line each, titles now including "2.1");
   - which metros get the full event census;
   - whether to publish an AI Participation Index or only its components;
   - whether to send organizers a request for their figures (draft it);
   - whether Google Trends and event platforms, both private sources, are acceptable in a study
     that has used government data wherever possible.

Then stop for my answers. After that, carry 2.1 through to the end, stopping only for the
actions under Approvals.

## Approvals

Ask me first before you:

- push anything to GitHub, including tags and branches;
- change the live website or publish any artifact;
- send any message to anyone, including event organizers and companies.

These need no approval:

- creating branches and tags locally;
- reading, editing and restructuring files in the repo;
- writing scripts, data files and tests;
- updating or correcting findings;
- downloading public data, reading public web pages, and retrying failed downloads;
- saving public pages to the Internet Archive;
- running scripts and tests;
- making local commits.

Record every correction to a 1.0 number in `AUDIT.md` and at the top of your final report.

## Research standards

These standards are why the study is credible. Each has a reason.

- Keep four things separate: **awareness and participation** (people convening), **potential
  exposure** (task overlap), **observed use** (actual AI usage), and **attributed displacement**
  (an employer's own words about its own cuts). Most writing on AI and jobs blurs them.
- Never present an organizer's attendance or membership figure without naming who reported it.
  Never sum such figures into a regional total.
- Make no causal claim the evidence can't support, and mark inference as inference. Event
  activity is never evidence that AI changed employment.
- Label every data vintage. Never present two different time windows as a trend.
- The Anthropic Economic Index stops at state level, so never state a metro-level AI usage
  figure. A test enforces this.
- Label each source by type: government, academic, industry or advocacy, journalism,
  commentary, private platform, or organizer-reported.
- Claims that something doesn't exist are where this project has been wrong before. An earlier
  draft said the City of Cincinnati had no AI activity, and it has a task force. Before writing
  that a metro has no AI community, a company has no AI programme, or a group held no meetings,
  search several ways and say how hard you looked.
- People who organize or attend community events are private individuals. Name organizations,
  not attendees. Name an organizer only in their public role and only where the finding needs
  it.

## Finishing work

After the check-in, keep going until 2.1 is done. Brief status notes are welcome. If you notice
yourself offering to wait or inviting me to redirect you, carry on with the next part instead.

You will meet ordinary obstacles, such as a download that times out, a file that moved, an
event page that has been deleted, a series ID that doesn't resolve, or a failing test. Diagnose
them and work through them: retry, fix the request, use the archived copy, or use another
official source. Deliberate limits are different: the actions under Approvals, and the
decisions I make at the check-in. Leave those alone, say what you found, and finish everything
else. If one part is truly blocked, complete every other part and say exactly what you left out
and why. None of this overrides the Approvals section.

## Communicating clearly

Before reporting progress, check each claim against a tool result from this session. Report
only work you can point to evidence for, and say plainly what is not yet verified. If tests
fail, say so and show the output.

I know the study, but I won't have seen your tool calls, your reasoning or the files you
opened. Write so I can follow without digging for context. Put the key points first. Use plain
words and full sentences, and don't use terms you made up during the work.

Your final report covers:

- what 2.1 found, by lens, with the awareness findings and what they can and can't show;
- how it differs from 1.0, and why;
- corrections to 1.0;
- the reviewer's objections and what you did about each;
- what you verified and what you couldn't;
- what you left out, and why.
