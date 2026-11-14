"""H16 (descriptive): what large Greater Cincinnati employers say they are doing with AI, and
with AI agents in particular. Hand-coded from sources read on 14 Nov 2026.

Coding rules (PREREGISTRATION.md 8.2)
  kind    agent      = carries out a multi-step task by itself using tools or other software,
                       with human review of the result at most (coded from what the source
                       describes, not from the label the company uses)
          assistant  = drafts, answers or suggests while a person performs each step
          other_ai   = prediction, vision, imaging or other non-generative AI
  stage   production / pilot_or_development / announced / aspirational
  grade   1 = the company's own record (filing, release, official news page)
          2 = a named executive on the record in dated reporting
          3 = vendor or partner statement about the company
          4 = third-party description of what a company could do (never used)
  read    yes = the page was opened and the wording checked in this session
          no  = seen only as a search-result summary; listed as a lead, never counted
Scope     1 = public company headquartered in CBSA 17140; 2 = on REDI Cincinnati's list of
          the region's largest employers (Business Courier Book of Lists 2024-2025, 22
          entries, three of them logo-only and not identifiable from the page text);
          3 = AI vendor or service firm based in the metro.

Output: data/ai_agent_register.csv ; output/h16_trace.txt
"""
import os
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
C = ["employer", "scope", "function", "what_the_source_describes", "kind", "label_used_by_source", "stage", "scale_stated",
     "jobs_statement", "date", "source", "grade", "read", "url"]
R = [
 ["Kroger", "1,2", "customer service / commerce", "AI Shopping Assistant; January release lists 'agentic integration, allowing the assistant to complete complex tasks from a single instruction' and says Kroger 'will roll out' the platform; September release says the assistant 'is helping customers plan meals'", "assistant", "agentic / agent", "production", "none for AI use", "", "2026-01-11; 2026-09-22", "Kroger press releases (PRNewswire, IR site)", 1, "yes", "https://ir.kroger.com/news/news-details/2026/Kroger-Details-AI-Strategy-Built-on-Decades-Retail-Expertise-at-GroceryShop-2026/default.aspx"],
 ["Kroger", "1,2", "store operations", "'The company is also working on improving agents for frontline teams'", "agent", "agents", "pilot_or_development", "none", "'the human connection to a customer or fellow associate will never be replaced by AI'", "2026-09-22", "Kroger press release", 1, "yes", "https://ir.kroger.com/news/news-details/2026/Kroger-Details-AI-Strategy-Built-on-Decades-Retail-Expertise-at-GroceryShop-2026/default.aspx"],
 ["Kroger", "1,2", "customer service", "'will also use Customer Experience Agent Studio to analyze interactions and intent on calls'", "other_ai", "Agent Studio (product name)", "announced", "none", "", "2026-01-11", "Kroger press release", 1, "yes", "https://www.thekrogerco.com/ir-feed-item/kroger-scales-generative-ai-strategy-with-google-cloud-to-drive-digital-growth-and-personalization/"],
 ["Kroger", "1,2", "store operations", "Sage associate platform: 'has over 95 use cases and is actively used by up to 150,000 associates' (attributed to a Kroger executive); a vendor partner describes it as conversational, generative and agentic", "assistant", "agentic (vendor's word)", "production", "up to 150,000 associates; 95+ use cases", "", "2026-01-14", "CIO Dive, quoting Kroger and IBM speakers at NRF 2026", 2, "yes", "https://www.ciodive.com/news/kroger-ai-google-gemini-shopping-assistant-technology-associate-platform-sage-nrf-2026/809669/"],
 ["Fifth Third Bancorp", "1,2", "software development", "AI coding tools used by all engineering teams; 'agentic workflows' and customer-facing solutions described as planned", "assistant", "agentic (planned)", "production", "~30% of new code AI-generated in Q4 2025; >80% of IT unit tests AI-executed; 56% of colleagues use AI tools daily", "No workforce reduction attributed to AI; CEO says clients indicate AI is not what is driving recent productivity gains", "FY2025 annual report (filed 2026)", "Form 10-K / annual report (verified in 1.0)", 1, "yes", "https://www.sec.gov/Archives/edgar/data/35527/000003552726000124/a2025annualreport.pdf"],
 ["Fifth Third Bancorp", "1,2", "customer service", "June 2026 release reported to describe AI search in the mobile app 'followed by future AI-powered agentic capabilities'", "agent", "agentic", "announced", "", "", "2026-06-17", "Business Wire release (page refused; search summary only)", 1, "no", "https://www.businesswire.com/news/home/20260617555789/en/"],
 ["Procter & Gamble", "1,2", "enterprise-wide knowledge work", "Internal generative tools ChatPG, ImagePG, AskPG and InsightsPG launched; a training programme 'has already educated more than 20,000 employees on how to use AI tools'; the article does not use the word agent", "assistant", "none", "production", "more than 20,000 employees trained; ~750 in a hackathon study", "", "2026-05-28", "CDO Magazine interview with a named P&G executive", 2, "yes", "https://www.cdomagazine.tech/aiml/how-pg-is-building-ai-fluency-and-measuring-enterprise-ai-impact-at-scale"],
 ["GE Aerospace", "1,2", "engineering / R&D", "Generative-AI application used in design studies of a hypersonic ramjet (release title read on the company's press-release list; body not read)", "assistant", "generative AI", "production", "", "", "2026-05-19", "GE Aerospace press release (title only)", 1, "no", "https://www.geaerospace.com/news/press-releases"],
 ["GE Aerospace", "1,2", "maintenance / operations", "March 2026 Palantir partnership reported to say 'AI agents facilitate automation of manual, repetitive tasks'", "agent", "AI agents", "announced", "", "", "2026-03-12", "Trade press copy of a release (page refused; search summary only)", 3, "no", "https://asdnews.com/news/defense/2026/03/12/ge-aerospace-palantir-expand-partnership-transform-military-aircraft-readiness-with-ai"],
 ["Cincinnati Financial", "1,2", "underwriting", "'built a proprietary generative AI chatbot for its commercial lines underwriters'; CEO: 'We are concentrating on using gen AI to gain efficiency that leads to meaningful productivity gains'", "assistant", "chatbot", "production", "none", "'the goal is to free underwriters and claims professionals to focus on the most complex decisions'", "2026 (Q4 2025 results)", "Coverager, quoting the CEO", 2, "yes", "https://coverager.com/?p=237571"],
 ["University of Cincinnati", "2", "education / administration", "BearcatGPT, a private OpenAI-based platform, live for all faculty and staff (Dec 2025) and all students (Feb 2026); Claude added July 2026; 'AI tutoring agents' in multiple courses", "assistant", "AI tutoring agents", "production", "tutoring tools 'reaching several thousand students'", "", "2025-12-09; 2026-02-17; 2026-07-27", "UC News (official)", 1, "yes", "https://www.uc.edu/news/articles/2026/02/bearcatgpt-ai-platform-now-available-to-uc-students.html"],
 ["TriHealth", "2", "nursing / imaging", "Ceiling-mounted camera and sensor devices for virtual nursing 'inside some TriHealth hospital rooms'; AI flags potentially abnormal images; CEO on agents: 'We'll be able to create agentic AI agents that help us with our workload' (about five years out)", "other_ai", "agentic (future)", "production", "some rooms; no count", "'The idea isn't to remove people from healthcare'", "2026-08-31", "WKRC Local 12, quoting the CEO and CIO", 2, "yes", "https://local12.com/health/ai-is-moving-into-trihealth-hospital-rooms-how-the-technology-is-changing-patient-care-cincinnati-fall-cancer-cameras-terri-hanlon-bremer-imaging"],
 ["The Christ Hospital Health Network", "2", "billing / clinical", "'Christ Hospital uses AI to automate insurance and claims billing'; planned pilot of AI-drafted replies to patient messages (2024)", "other_ai", "none", "production", "none", "", "2024-01-09", "Cincinnati Enquirer", 2, "yes", "https://www.yahoo.com/news/cincinnati-hospitals-artificial-intelligence-chatgpt-030509336.html"],
 ["Bon Secours Mercy Health", "2", "HR / recruiting", "'Bon Secours Mercy Health relies on AI to recruit and hire nurses'", "other_ai", "none", "production", "none", "", "2024-01-09", "Cincinnati Enquirer", 2, "yes", "https://www.yahoo.com/news/cincinnati-hospitals-artificial-intelligence-chatgpt-030509336.html"],
 ["Bon Secours Mercy Health", "2", "scheduling / governance", "Reported member of a ten-system collaborative on agentic AI; a podcast description cites agentic AI for scheduling", "agent", "agentic", "pilot_or_development", "", "", "2026", "Becker's (page refused; search summary only)", 2, "no", "https://www.beckershospitalreview.com/healthcare-information-technology/ai/10-health-systems-join-agentic-ai-collaborative"],
 ["Cincinnati Children's", "2", "nursing / patient access", "Reported launch partner for a vendor's 'Nurse Co-Pilot' and 'AI Front Door'; internal AI search over hospital protocols reported live across the workforce", "assistant", "co-pilot", "pilot_or_development", "", "", "2026-04", "Trade press on a vendor announcement (search summary only)", 3, "no", ""],
 ["Cintas", "1", "enterprise", "Management reported to describe the company as in the 'early stages' of using AI", "assistant", "none", "pilot_or_development", "", "", "2025-12-18", "Earnings call (transcript not read; search summary only)", 1, "no", ""],
 ["City of Cincinnati", "2", "permitting", "Approved FY2027 budget update funds 'Plans Examination Artificial Intelligence Enhancement', $300,000 (capital)", "other_ai", "none", "announced", "$300,000", "", "FY2027 budget update", "City budget (recorded in the 2.0 design memo)", 1, "yes", "https://www.cincinnati-oh.gov/budget/budget-documents/recommended-fy-2027-budget-update/"],
 ["CBTS", "3", "customer experience, finance, operations, workforce (own operations); sells agents to mid-market firms", "'CBTS Forge Agents are available now'; CBTS 'now runs internal agents across customer experience, finance, operations, and workforce functions'", "agent", "agents", "production", "'adoption across 2,300+ employees'; 'full ROI within 4 months' (vendor's own claims)", "'No $200K embedded engineers on a bench' (a staffing comparison in sales copy, not a statement about its own headcount)", "2026-09-01", "CBTS press release (the vendor is also the seller)", 1, "yes", "https://www.cbts.com/newsroom/cbts-launches-forge-agents-to-deliver-custom-ai-agents-in-days"],
]
NO_DISCLOSURE = ["UC Health", "St. Elizabeth Healthcare", "Hamilton County, Ohio", "Miami University", "U.S. Bank (regional operations)",
                 "DHL (CVG hub)", "American Financial Group", "CVG Airport", "Western & Southern", "E.W. Scripps"]
D = pd.DataFrame(R, columns=C)
D.to_csv(P("data", "ai_agent_register.csv"), index=False)
pd.DataFrame({"employer": NO_DISCLOSURE, "result": "no statement found in one targeted search; not evidence of no use",
              "searched": "2026-11-14"}).to_csv(P("data", "ai_agent_register_no_disclosure.csv"), index=False)

with open(P("output", "h16_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a); print(*a, file=fh)
    ok = D[(D.read == "yes") & D.grade.isin([1, 2])]
    w("Rows:", len(D), "| read and grade 1-2:", len(ok), "| employers with such a row:", ok.employer.nunique())
    w("\nRead, grade 1-2, by kind and stage (rows):")
    w(ok.groupby(["kind", "stage"]).size().to_string())
    ag = ok[(ok.kind == "agent") & (ok.stage == "production")]
    w("\nEmployers with read, grade 1-2 evidence of an AGENT in PRODUCTION:", sorted(ag.employer.unique()), "->", ag.employer.nunique())
    w("Pre-registered sentence allowed (needs 3 or more):", ag.employer.nunique() >= 3)
    w("Employers with an agent announced or in development (read, grade 1-2):",
      sorted(ok[(ok.kind == "agent") & (ok.stage != "production")].employer.unique()))
    w("Employers with an assistant or other AI in production (read, grade 1-2):",
      sorted(ok[(ok.kind != "agent") & (ok.stage == "production")].employer.unique()))
    w("Leads not read (never counted):", sorted(D[D.read == "no"].employer.unique()))
    w("No statement found:", NO_DISCLOSURE)
    w("Rows with a statement about jobs:", int((ok.jobs_statement != "").sum()), "of", len(ok))
