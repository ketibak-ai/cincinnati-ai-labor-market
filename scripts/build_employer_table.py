"""Build the structured employer AI-adoption evidence table.

Each row records what a Cincinnati-region employer has actually deployed, what it has
quantified, what workforce action it has taken, and - critically - whether the employer
itself attributed that workforce action to AI. This separates documented AI deployment
from AI-attributed job displacement.
"""
import csv
import sys

COLS = [
    "employer", "sector", "cincinnati_role", "evidence_date", "evidence_type",
    "source_tier", "ai_deployment_evidence", "quantified_metrics", "workforce_action",
    "ai_attributed_by_company", "analyst_caveat", "source",
]

ROWS = [
    dict(
        employer="Kroger",
        sector="Retail / grocery",
        cincinnati_role="Headquarters (Cincinnati); ~8,200 corporate employees company-wide",
        evidence_date="2026-10-12",
        evidence_type="CEO memo reported by Reuters; company AI strategy release",
        source_tier="Secondary reporting of a primary internal memo",
        ai_deployment_evidence=(
            "Proprietary models for demand forecasting, operational optimisation, "
            "personalisation and generative AI; AI Shopping Assistant launched July 2026; "
            "conversational search; RFID plus computer vision and robotics for inventory; "
            "frontline associate agents in development"
        ),
        quantified_metrics=(
            "RFID bakery pilot in ~1,500 stores: 98% read rate, ~70% faster inventory counts, "
            "50% drop in waste; rollout to 2,300+ stores by 2029; AI literacy training to "
            "400,000+ associates"
        ),
        workforce_action=(
            "~3,000 corporate roles to be eliminated over three years (~37% of 8,200 corporate "
            "staff), not backfilled. Follows ~1,000 corporate cuts in June 2025."
        ),
        ai_attributed_by_company=(
            "PARTIAL. The memo cites 'more layers, more handoffs and more overhead than we "
            "need' and does not state how many roles AI replaces. The September 2026 AI "
            "strategy release said the aim is not to automate everything and that human "
            "connection 'will never be replaced by AI'."
        ),
        analyst_caveat=(
            "Media framing is 'AI job cuts'; the primary memo frames it as delayering. "
            "Analysts noted some cuts would have occurred regardless of AI. The share of the "
            "3,000 located in Cincinnati is not disclosed."
        ),
        source=(
            "https://ir.kroger.com/news/news-details/2026/Kroger-Details-AI-Strategy-Built-on-"
            "Decades-Retail-Expertise-at-GroceryShop-2026/default.aspx | "
            "https://www.foxbusiness.com/retail/kroger-cut-3000-corporate-jobs-ai-expansion"
        ),
    ),
    dict(
        employer="Fifth Third Bancorp",
        sector="Banking / financial services",
        cincinnati_role="Headquarters (Cincinnati)",
        evidence_date="2026 (FY2025 annual report)",
        evidence_type="Shareholder letter and Form 10-K",
        source_tier="PRIMARY - SEC filing",
        ai_deployment_evidence=(
            "All engineering teams use AI tools and have applied them to decode nearly all "
            "legacy applications; all colleagues have access to AI tools; generative AI "
            "training launched 2025; agentic workflows and customer-facing solutions planned"
        ),
        quantified_metrics=(
            "Q4 2025: ~30% of new code AI-generated; >80% of IT unit tests AI-executed; "
            "change-failure rate down >20% year over year; 56% of colleagues using AI tools daily"
        ),
        workforce_action="None announced in connection with AI",
        ai_attributed_by_company=(
            "NO workforce reduction attributed to AI. CEO Tim Spence states that his "
            "commercial clients indicate AI is NOT what is driving recent productivity gains, "
            "attributing those instead to post-COVID investment in legacy automation technologies."
        ),
        analyst_caveat=(
            "Secondary sources reported '60%' daily usage; the primary filing says 56%. Use 56%."
        ),
        source=(
            "https://www.sec.gov/Archives/edgar/data/35527/000003552726000124/"
            "a2025annualreport.pdf"
        ),
    ),
    dict(
        employer="Procter & Gamble",
        sector="Consumer goods",
        cincinnati_role="Headquarters (Cincinnati)",
        evidence_date="2025-06-05 announced; programme ongoing through 2026",
        evidence_type="Company restructuring announcement; press coverage",
        source_tier="Secondary reporting of a company announcement",
        ai_deployment_evidence=(
            "Company language centres on 'digitization and automation'; reporting notes freed "
            "resources may fund AI-powered tools in demand forecasting and supply chain; "
            "recruiting PhD interns in data science and generative AI in Cincinnati"
        ),
        quantified_metrics="Restructuring cost $1.0-1.6bn",
        workforce_action=(
            "Up to 7,000 non-manufacturing roles over two years (~15% of non-manufacturing "
            "roles; ~6% of total workforce). Office and support roles, not plants."
        ),
        ai_attributed_by_company=(
            "NO. The company cited costs, tariffs and consumer uncertainty. Layoff trackers "
            "record that none of these cuts were publicly blamed on AI."
        ),
        analyst_caveat=(
            "Frequently cited in AI-displacement commentary despite no company AI attribution. "
            "Cincinnati-specific share not disclosed."
        ),
        source=(
            "https://www.nbcnews.com/business/business-news/procter-gamble-cut-7000-jobs-part-"
            "broader-restructuring-rcna211263"
        ),
    ),
    dict(
        employer="GE Aerospace",
        sector="Aerospace manufacturing",
        cincinnati_role=(
            "Headquarters (Evendale); major Cincinnati-region manufacturing and engineering base"
        ),
        evidence_date="2026",
        evidence_type="Company investment announcement; Bipartisan Policy Center case study",
        source_tier="Mixed - company announcement plus think-tank case study",
        ai_deployment_evidence=(
            "The Services Technology Acceleration Center (STAC) in Evendale refines every new "
            "process, including new AI processes, before company-wide deployment; co-op "
            "pipeline with Cincinnati State"
        ),
        quantified_metrics=(
            ">$115 million directed to the Cincinnati region in 2026 within a $1 billion US "
            "manufacturing investment; 8 Cincinnati-area postings matching 'data analytics' "
            "(October 2026)"
        ),
        workforce_action="Net hiring and expansion in manufacturing and engineering",
        ai_attributed_by_company=(
            "AI positioned as process improvement within manufacturing operations, not as a "
            "workforce reduction lever"
        ),
        analyst_caveat=(
            "No published AI-specific headcount or AI hiring target for Evendale. The AI "
            "evidence rests largely on a single case study."
        ),
        source="https://bipartisanpolicy.org/issue-brief/aerospace-manufacturing-workforce/",
    ),
    dict(
        employer="Cincinnati Children's Hospital Medical Center",
        sector="Healthcare / pediatrics",
        cincinnati_role="Major regional employer and academic medical centre",
        evidence_date="2026",
        evidence_type="Institutional research communications; clinical trial registration",
        source_tier="Mixed - institutional blog plus trial registration",
        ai_deployment_evidence=(
            "AI-enabled virtual health platforms; imaging tools assisting radiologists; AI "
            "alerts for epilepsy surgery referral eligibility; ambient documentation studied "
            "in pediatric subspecialty practice (trial NCT06812234); partner in a new Imaging "
            "R&D Center with UC, UC Health, GE HealthCare and JobsOhio"
        ),
        quantified_metrics="None published for system-wide deployment",
        workforce_action="None announced",
        ai_attributed_by_company=(
            "Framed as clinical augmentation and documentation-burden reduction"
        ),
        analyst_caveat=(
            "No source confirms system-wide ambient documentation deployment. Clinical AI here "
            "is augmentation, not displacement."
        ),
        source=(
            "https://scienceblog.cincinnatichildrens.org/translating-ai-digital-health-into-"
            "impact/ | https://clinicaltrials.gov/study/NCT06812234"
        ),
    ),
    dict(
        employer="University of Cincinnati / UC Health",
        sector="Higher education / academic health",
        cincinnati_role="Major regional employer; regional talent pipeline",
        evidence_date="2026-01",
        evidence_type="University announcements",
        source_tier="PRIMARY - institutional press releases",
        ai_deployment_evidence=(
            "$1.1m AMA grant for 'Ambient AI for precision feedback' in physician training; "
            "$1m grant for precision medical education; Lindner College of Business delivering "
            "private generative AI workshops to employers including Fifth Third"
        ),
        quantified_metrics="$1.1m and $1.0m grants",
        workforce_action="None announced",
        ai_attributed_by_company="Framed as training, education and workforce development",
        analyst_caveat="Education and training capacity, not evidence of labour displacement.",
        source=(
            "https://www.uc.edu/news/articles/2026/01/university-of-cincinnati-gets-11m-for-ai-"
            "physician-training.html | https://www.business.uc.edu/about/ai.html"
        ),
    ),
    dict(
        employer="Professional-services firms (Deloitte, Accenture, EY, PwC, KPMG)",
        sector="Professional services / consulting",
        cincinnati_role="Large Cincinnati-area offices; dominant AI-role advertisers in the metro",
        evidence_date="2026-10-30",
        evidence_type="Job postings census (CareerOneStop / National Labor Exchange)",
        source_tier="PRIMARY - observed postings",
        ai_deployment_evidence=(
            "Named AI and generative AI delivery roles advertised into the Cincinnati market, "
            "e.g. Oracle Generative AI Senior Consultant and Google Gemini Enterprise for CX "
            "Technical Leader"
        ),
        quantified_metrics=(
            "Deloitte 57 and Accenture 11 postings matching 'artificial intelligence'; "
            "Accenture 35, EY 30, Deloitte 25 and PwC 10 matching 'data analytics'"
        ),
        workforce_action="Net hiring",
        ai_attributed_by_company="AI positioned as a service line",
        analyst_caveat=(
            "These are intermediaries. Their postings indicate demand for AI implementation "
            "capacity routed through national firms rather than indigenous AI job creation by "
            "Cincinnati employers."
        ),
        source=(
            "CareerOneStop Job Finder (National Labor Exchange), retrieved 2026-10-30"
        ),
    ),
    dict(
        employer="Staffing firms (Kelly Services, Eliassen Group, Aerotek, Actalent)",
        sector="Employment services",
        cincinnati_role="Intermediaries placing workers with Cincinnati-area employers",
        evidence_date="2026-10-30",
        evidence_type="Job postings census (CareerOneStop / National Labor Exchange)",
        source_tier="PRIMARY - observed postings",
        ai_deployment_evidence="Advertising AI and machine-learning contract roles into the metro",
        quantified_metrics=(
            "Kelly Services 40 and Eliassen Group 13 postings matching 'artificial intelligence'"
        ),
        workforce_action="Contingent placement",
        ai_attributed_by_company="n/a",
        analyst_caveat=(
            "Staffing postings can double-count a single end-client vacancy and may be "
            "re-posted, so treat counts as upper bounds. Cincinnati MSA employment services "
            "payrolls fell from 39,700 (September 2022) to 29,800 (September 2026)."
        ),
        source=(
            "CareerOneStop Job Finder (National Labor Exchange), retrieved 2026-10-30 | "
            "BLS CES series SMU39171400605613001"
        ),
    ),
]


def main(base: str) -> None:
    out = f"{base}/data/ai_adoption_employers.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(ROWS)
    print(f"employer rows written: {len(ROWS)} -> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
