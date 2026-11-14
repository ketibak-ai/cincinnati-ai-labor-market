"""H12-H14: AI awareness and participation, Cincinnati against the 19 Chamber peers (P1).

Like-for-like measures (PREREGISTRATION.md 8.2), each per 100,000 residents aged 18-64:
  L1  AI events listed on Eventbrite and Meetup for the next 60 days (data/l1_platform_counts.csv)
  L2  meetings held in the last 12 months by chapters of a national AI builder community
      (data/l2_chapter_meetings.csv)
  L3  Google Trends interest by media market, last 12 months, mean across search terms
      (raw/awareness/trends/geoMap_*.csv, exported from the Trends page on 14 Nov 2026)
Adoption-side comparison for H14: job postings naming AI tools, CareerOneStop / National Labor
Exchange, 25-mile radius of each principal city, 14 Nov 2026 (entered below as read from the
site's results line, e.g. "94 jobs found").

Deviations logged in the pre-registration: L1 omits Luma and uses a title test; L3 uses three
search terms (ChatGPT, Claude AI, Microsoft Copilot) because Google Trends stopped serving the
export after three terms; the postings measure uses three phrases, not fourteen ("agentic" was
dropped because the search tool stems it to "agent").

Outputs: data/awareness_like_for_like.csv, data/postings_ai_tools_20_metros.csv,
         output/awareness_trace.txt
"""
import glob
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
CIN = 17140
DMA = {17140: "Cincinnati OH", 12060: "Atlanta GA", 12420: "Austin TX", 12580: "Baltimore MD", 16740: "Charlotte NC",
       17410: "Cleveland-Akron (Canton) OH", 18140: "Columbus OH", 19430: "Dayton OH", 19740: "Denver CO", 19820: "Detroit MI",
       26900: "Indianapolis IN", 28140: "Kansas City MO", 31140: "Louisville KY", 33340: "Milwaukee WI",
       33460: "Minneapolis-St. Paul MN", 34980: "Nashville TN", 38300: "Pittsburgh PA", 39580: "Raleigh-Durham (Fayetteville) NC",
       41180: "St. Louis MO", 45300: "Tampa-St. Petersburg (Sarasota) FL"}
# postings: (AI agent, ChatGPT, large language model); None = the site returned an error twice
POST = {17140: (94, 129, 13), 12060: (239, 212, 37), 12420: (229, 129, 38), 12580: (140, 208, 25), 16740: (127, 119, 24),
        17410: (92, 163, 8), 18140: (157, 150, 29), 19430: (3, 58, 4), 19740: (155, 234, 31), 19820: (121, 228, 12),
        26900: (132, 139, 19), 28140: (82, 135, 7), 31140: (40, 94, 3), 33340: (86, 114, 10), 33460: (195, 203, 33),
        34980: (174, 130, 20), 38300: (105, 142, 12), 39580: (146, None, 14), 41180: (75, 182, 7), 45300: (90, 159, 11)}
CIN_EXTRA = {"generative AI": 64, "OpenAI": 63, "prompt engineering": 3, "agentic (stemmed by the tool; not used)": 862}

l1 = pd.read_csv(P("data", "l1_platform_counts.csv")).set_index("cbsa")
l2 = pd.read_csv(P("data", "l2_chapter_meetings.csv")).set_index("cbsa")
T = l1[["area", "pop_18_64", "events", "events_eventbrite", "events_meetup", "events_per_100k_18_64"]].rename(
    columns={"events": "l1_events", "events_per_100k_18_64": "l1_per_100k"})
T["l2_meetings"] = l2.meetings_last_12m
T["l2_per_100k"] = T.l2_meetings / T.pop_18_64 * 1e5
T["l2_status"] = l2.status
tr = {}
for f in sorted(glob.glob(P("raw", "awareness", "trends", "geoMap_*.csv"))):
    term = os.path.basename(f)[7:-4].replace("_", " ")
    d = pd.read_csv(f, skiprows=2, names=["dma", "v"])
    tr[term] = pd.to_numeric(d.set_index("dma").v, errors="coerce")
TR = pd.DataFrame(tr)
for term in TR.columns:
    T["l3_" + term.replace(" ", "_")] = T.index.map(lambda c: TR[term].get(DMA[c], np.nan))
l3cols = [c for c in T.columns if c.startswith("l3_")]
T["l3_mean"] = T[l3cols].mean(axis=1)
T["us_markets_ranked"] = len(TR)
T["l3_rank_among_us_markets_chatgpt"] = T.index.map(lambda c: int((TR["ChatGPT"] > TR["ChatGPT"].get(DMA[c], np.nan)).sum()) + 1)
PT = pd.DataFrame(POST, index=["post_ai_agent", "post_chatgpt", "post_llm"]).T
T = T.join(PT)
T["post_two_terms"] = T.post_ai_agent + T.post_llm                 # available for all 20 metros
T["post_two_terms_per_100k"] = T.post_two_terms / T.pop_18_64 * 1e5
T["post_chatgpt_per_100k"] = T.post_chatgpt / T.pop_18_64 * 1e5
T.to_csv(P("data", "awareness_like_for_like.csv"))
PT.assign(area=T.area, collected="2026-11-14", source="CareerOneStop Job Finder (NLx), 25-mile radius").to_csv(P("data", "postings_ai_tools_20_metros.csv"))


def spearman_perm(x, y, n=20000, seed=20261114):
    ok = x.notna() & y.notna()
    rx, ry = x[ok].rank(), y[ok].rank()
    rho = np.corrcoef(rx, ry)[0, 1]
    rng = np.random.default_rng(seed)
    hits = sum(abs(np.corrcoef(rx, rng.permutation(ry.values))[0, 1]) >= abs(rho) for _ in range(n))
    return rho, (hits + 1) / (n + 1), int(ok.sum())

with open(P("output", "awareness_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a)
        print(*a, file=fh)

    peers = T.drop(index=CIN)
    w("H12. Convening relative to P1 (19 peers)")
    verdicts = []
    for col, label in (("l1_per_100k", "L1 platform listings per 100k"), ("l2_per_100k", "L2 chapter meetings per 100k"), ("l3_mean", "L3 search interest (index)")):
        c = T.loc[CIN, col]; q1, med, q3 = peers[col].quantile([.25, .5, .75])
        where = "above IQR" if c > q3 else ("below IQR" if c < q1 else "inside IQR")
        verdicts.append(where)
        w(f"  {label:34s} Cincinnati {c:7.3f} | P1 q25 {q1:7.3f} median {med:7.3f} q75 {q3:7.3f} | rank {int((peers[col] > c).sum()) + 1} of 20 | {where}")
    ab, be = verdicts.count("above IQR"), verdicts.count("below IQR")
    w("  Verdict:", "ABOVE its peers" if ab >= 2 else ("BELOW its peers" if be >= 2 else "WITHIN the normal range of peers"), f"(above on {ab}, below on {be} of 3)")
    w("\n  Raw counts:")
    w(T.sort_values("l1_per_100k", ascending=False)[["area", "l1_events", "events_eventbrite", "events_meetup", "l1_per_100k", "l2_meetings", "l2_status",
                                                      "l2_per_100k"] + l3cols + ["l3_mean"]].round(2).to_string())
    w(f"\n  Cincinnati's media market ranks {T.loc[CIN, 'l3_rank_among_us_markets_chatgpt']} of {len(TR)} US markets for 'ChatGPT'.")
    w("\nH14. Is convening related to postings that name AI tools? (Spearman, exact-style permutation p, 20 metros)")
    rel = 0
    for col in ("l1_per_100k", "l2_per_100k", "l3_mean"):
        rho, p, n = spearman_perm(T[col], T.post_two_terms_per_100k)
        rel += (rho >= 0.4 and p < 0.10)
        rho2, p2, n2 = spearman_perm(T[col], T.post_chatgpt_per_100k)
        w(f"  {col:12s} vs postings ('AI agent' + 'large language model') per 100k: rho {rho:+.2f}, p {p:.3f}, n {n}"
          f" | vs 'ChatGPT' postings: rho {rho2:+.2f}, p {p2:.3f}, n {n2}")
    w("  Verdict:", "RELATED (rho >= 0.4 and p < 0.10 on at least two of three)" if rel >= 2 else f"no relationship established by the rule (met on {rel} of 3)")
    w("\n  Postings naming AI tools, per 100k aged 18-64:")
    w(T.sort_values("post_two_terms_per_100k", ascending=False)[["area", "post_ai_agent", "post_llm", "post_chatgpt", "post_two_terms_per_100k", "post_chatgpt_per_100k"]].round(2).to_string())
    c = T.loc[CIN, "post_two_terms_per_100k"]
    w(f"  Cincinnati {c:.2f} | P1 median {peers.post_two_terms_per_100k.median():.2f} | rank {int((peers.post_two_terms_per_100k > c).sum()) + 1} of 20")
    w("  Other Cincinnati phrase counts (same day):", CIN_EXTRA)
