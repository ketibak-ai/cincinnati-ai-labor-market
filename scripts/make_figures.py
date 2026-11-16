"""Draw the 2.1 report's charts from the data files. Output: docs/figures/*.png

Style: one highlight colour for Cincinnati, neutral grey for peers, a second colour only where
a second series needs it; thin marks, light grid, direct labels, a source line on every chart.
"""
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("docs", "figures")
os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, GREY, INK, INK2, SURF, GRID = "#2a78d6", "#eb6834", "#b9b8b1", "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.facecolor": SURF, "figure.facecolor": SURF, "savefig.facecolor": SURF, "axes.titlesize": 11.5,
                     "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlecolor": INK})
CIN = 17140
MEAS = {"lm_aioe": "Language-model exposure\n(Felten et al.)", "eloundou": "GPT exposure\n(Eloundou et al.)",
        "aei": "Observed use\n(Anthropic index)", "ms": "AI applicability\n(Microsoft)"}


def finish(fig, name, source, sub=None, title=None, extra_top=0.0):
    """Title and subtitle are placed in figure space and wrapped to the figure width, so a long
    title can never run off the edge or collide with the subtitle."""
    import textwrap
    w, h = fig.get_size_inches()
    tl = textwrap.wrap(title, int(w * 10.2)) if title else []
    sl = textwrap.wrap(sub, int(w * 13.5)) if sub else []
    y = h - 0.12
    if tl:
        fig.text(0.012, y / h, "\n".join(tl), color=INK, fontsize=11.5, fontweight="bold", va="top", linespacing=1.25)
        y -= 0.215 * len(tl) + 0.06
    if sl:
        fig.text(0.012, y / h, "\n".join(sl), color=INK2, fontsize=9, va="top", linespacing=1.3)
        y -= 0.17 * len(sl) + 0.04
    y -= 0.16 + extra_top
    srcl = textwrap.wrap("Source: " + source, int(w * 16.5))
    fig.text(0.012, 0.012, "\n".join(srcl), color=INK2, fontsize=7.5, va="bottom", linespacing=1.3)
    pos = fig.subplotpars
    fig.subplots_adjust(top=y / h, bottom=max(pos.bottom, (0.13 * len(srcl) + 0.5) / h))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=200)
    plt.close(fig)


def hbar(ax, labels, vals, hi, fmt="{:.1f}", other=None):
    cols = [BLUE if l == hi else (INK2 if other and l == other else GREY) for l in labels]
    y = np.arange(len(labels))
    ax.barh(y, vals, color=cols, height=0.62)
    ax.set_yticks(y, labels)
    for t, l in zip(ax.get_yticklabels(), labels):
        if l == hi:
            t.set_fontweight("bold"); t.set_color(INK)
    span = (max(vals) - min(min(vals), 0)) or 1
    for yi, v in zip(y, vals):
        ax.text(v + (span * 0.012 if v >= 0 else -span * 0.012), yi, fmt.format(v), va="center", ha="left" if v >= 0 else "right", fontsize=8, color=INK2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.grid(axis="x", color=GRID, lw=0.7); ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.invert_yaxis()

# 1. Job growth against peers
g = pd.read_csv(P("data", "h9_growth_peers.csv")).sort_values("growth_pct", ascending=False)
fig, ax = plt.subplots(figsize=(7.2, 6.2)); fig.subplots_adjust(left=0.2, right=0.95, top=0.88, bottom=0.1)
hbar(ax, list(g.area), list(g.growth_pct), "Cincinnati", "{:+.1f}%", other="United States")
ax.margins(x=0.12)
finish(fig, "fig01_job_growth_peers", "BLS Current Employment Statistics, total nonfarm, not seasonally adjusted; September 2026 is preliminary.",
       "Change in total nonfarm employment, September 2024 to September 2026", title="Cincinnati's job growth sits in the middle of its peers")

# 2. Hiring test: Cincinnati against peers
h = pd.read_csv(P("data", "h1_ddd.csv"))
m = h[(h.outcome == "HirN") & (h.young == "A03") & (h.grouping == "tercile")]
fig, ax = plt.subplots(figsize=(7.4, 4.6)); fig.subplots_adjust(left=0.25, right=0.96, top=0.8, bottom=0.27)
rng = np.random.default_rng(1)
for i, k in enumerate(MEAS):
    s = m[m.measure == k]
    pe = s[s.cbsa != CIN].ddd.values
    ax.scatter(pe, i + rng.uniform(-0.13, 0.13, len(pe)), s=22, color=GREY, edgecolor=SURF, lw=0.6, zorder=2)
    c = float(s[s.cbsa == CIN].ddd.iloc[0])
    ax.scatter([c], [i], s=85, color=BLUE, edgecolor=SURF, lw=1.2, zorder=3)
    ax.text(c, i - 0.3, f"Cincinnati {c:+.2f}", color=INK, fontsize=8, ha="center", fontweight="bold")
ax.axvline(0, color=INK2, lw=0.9); ax.axvline(-0.05, color=INK2, lw=0.8, ls=(0, (3, 3)))
ax.text(-0.056, -0.55, "pre-registered threshold (-0.05)", fontsize=7.5, color=INK2, ha="right", va="center")
ax.set_yticks(range(4), list(MEAS.values())); ax.set_ylim(3.6, -0.75)
ax.grid(axis="x", color=GRID, lw=0.7); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.set_xlabel("Change in the young-to-experienced hiring ratio, exposed minus\nless-exposed industries (log points)")
finish(fig, "fig02_hiring_test", "Census LEHD Quarterly Workforce Indicators; 2018-19 against 2023-25; 32 metros in the three peer sets (grey), four exposure measures.",
       "Each grey dot is a peer metro. Negative = 22-24-year-olds lost ground in exposed industries after 2022.", title="Most peer metros show a narrowing entry door. Cincinnati does not.")

# 3. Hires by age and industry group, Cincinnati
ind = pd.read_csv(P("data", "industry_exposure_naics3.csv"), dtype={"naics3": str}).set_index("naics3")
fr = []
for st in ("oh", "ky", "in"):
    d = pd.read_csv(P("raw", "qwi", f"qwi_{st}_sa_gm_n3_op_filtered.csv.gz"), dtype={"geography": str, "industry": str})
    fr.append(d[d.geography.str[2:] == str(CIN)])
q = pd.concat(fr)
q["per"] = np.where(q.year.isin([2018, 2019]), "pre", np.where(q.year.isin([2023, 2024, 2025]), "post", ""))
q = q[q.per != ""]
q["grp"] = q.industry.map(ind.lm_aioe_tercile).map({3: "Most exposed third", 2: "Middle third", 1: "Least exposed third"})
q["age"] = q.agegrp.map({"A03": "22-24", "A04": "25-34", "A05": "35-54", "A06": "35-54"})
t = q.dropna(subset=["age", "grp"]).groupby(["grp", "age", "per"]).HirN.sum().unstack("per")
t["chg"] = ((t.post / 12) / (t.pre / 8) - 1) * 100
t.reset_index().to_csv(P("data", "h1_hires_by_age_group_cincinnati.csv"), index=False)
fig, ax = plt.subplots(figsize=(7.2, 3.9)); fig.subplots_adjust(left=0.1, right=0.97, top=0.78, bottom=0.2)
groups = ["Most exposed third", "Middle third", "Least exposed third"]; ages = ["22-24", "25-34", "35-54"]
shade = {"22-24": BLUE, "25-34": "#86b6ef", "35-54": GREY}
for j, a in enumerate(ages):
    v = [t.loc[(gp, a), "chg"] for gp in groups]
    x = np.arange(3) + (j - 1) * 0.26
    ax.bar(x, v, width=0.24, color=shade[a], label="Ages " + a)
    for xi, vi in zip(x, v):
        ax.text(xi, vi - 0.5 if vi < 0 else vi + 0.3, f"{vi:+.0f}%", ha="center", va="top" if vi < 0 else "bottom", fontsize=8, color=INK2)
ax.axhline(0, color=INK2, lw=0.8); ax.set_xticks(range(3), [g_ + "\nof industries" for g_ in groups]); ax.tick_params(length=0)
ax.grid(axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True); ax.set_ylabel("Change in average quarterly new hires (%)"); ax.set_ylim(-19, 3.5)
ax.legend(frameon=False, ncol=3, loc="lower right", fontsize=8.5)
finish(fig, "fig03_hires_by_age", "Census LEHD Quarterly Workforce Indicators, Cincinnati MSA (Ohio, Kentucky and Indiana parts), private sector; all published cells.",
       "Greater Cincinnati, new hires, 2023-25 against 2018-19; industries grouped by language-model exposure", title="Young workers' hiring fell in every kind of industry, not only the AI-exposed ones")

# 4. Shift-share
s = pd.read_csv(P("data", "h6_shift_share.csv")); c = s[s.cbsa == CIN].iloc[0]
mix, within = c.industry_mix * c.oews_total, c.within_industry * c.oews_total
fig, ax = plt.subplots(figsize=(7.2, 2.5)); fig.subplots_adjust(left=0.04, right=0.96, top=0.62, bottom=0.2)
ax.barh([0], [mix], color=GREY, height=0.5); ax.barh([0], [within], left=[mix], color=BLUE, height=0.5, edgecolor=SURF, lw=2)
ax.text(mix / 2, 0, f"Industry mix\n{mix:,.0f} jobs ({mix / (mix + within):.0%})", ha="center", va="center", fontsize=9, color=INK)
ax.text(mix + within / 2, 0, f"Within industries\n{within:,.0f} jobs ({within / (mix + within):.0%})", ha="center", va="center", fontsize=9, color="white")
ax.set_yticks([]); ax.set_xlim(mix + within - 200, 200); ax.spines["left"].set_visible(False); ax.tick_params(length=0)
ax.set_xlabel("Computer and mathematical jobs, Greater Cincinnati, relative to the national rate")
finish(fig, "fig04_shift_share", "BLS OEWS May 2025 (metro and national staffing patterns) and QCEW 2025 county files; author's shift-share.",
       f"The region has {abs(mix + within):,.0f} fewer computing jobs than the national rate would give it", title="Most of the region's shortfall in computing jobs comes from its industry mix")

# 5. Capability measures
pat = pd.read_csv(P("data", "h6_ai_patents.csv")); herd = pd.read_csv(P("data", "h6_herd_computing_rd.csv")); ip = pd.read_csv(P("data", "h6_ipeds_completions.csv"))
fig, axes = plt.subplots(1, 3, figsize=(10.5, 6.0)); fig.subplots_adjust(left=0.09, right=0.98, top=0.83, bottom=0.09, wspace=0.62)
for ax, (d, col, ttl, fmt) in zip(axes, ((pat, "ai_patents_per_100k", "AI patents, 2019-23,\nper 100,000 residents", "{:.0f}"),
                                         (herd, "computing_rd_per_capita", "University computing R&D,\nFY2024, dollars per resident", "{:.1f}"),
                                         (ip, "completions_per_100k", "Computing and data awards,\n2023-24, per 100,000 residents", "{:.0f}"))):
    x = d[d.p1 | (d.CBSA == CIN)].sort_values(col, ascending=False)
    hbar(ax, list(x.short), list(x[col]), "Cincinnati", fmt); ax.set_title(ttl, fontsize=9.5, fontweight="normal", color=INK2); ax.margins(x=0.16)
    ax.tick_params(labelsize=8)
finish(fig, "fig05_capability", "USPTO AI Patent Dataset (2023) with PatentsView inventor locations; NSF HERD FY2024; NCES IPEDS completions 2023-24. Cincinnati and its 19 Chamber peers.", title="Building capability: low on patents and research, above the middle on graduates", extra_top=0.55)

# 6. Awareness, like-for-like
a = pd.read_csv(P("data", "awareness_like_for_like.csv"))
fig, axes = plt.subplots(1, 3, figsize=(10.5, 6.0)); fig.subplots_adjust(left=0.09, right=0.98, top=0.83, bottom=0.09, wspace=0.62)
for ax, (col, ttl, fmt) in zip(axes, (("l1_per_100k", "AI events listed for the next 60 days,\nper 100,000 adults aged 18-64", "{:.2f}"),
                                      ("l2_per_100k", "Meetings of a national AI builder\nnetwork's chapter, last 12 months,\nper 100,000 adults", "{:.2f}"),
                                      ("l3_mean", "Google search interest in three AI\ntools, last 12 months (index)", "{:.0f}"))):
    x = a.sort_values(col, ascending=False)
    hbar(ax, list(x.area), list(x[col]), "Cincinnati", fmt); ax.set_title(ttl, fontsize=9.5, fontweight="normal", color=INK2); ax.margins(x=0.16)
    ax.tick_params(labelsize=8)
finish(fig, "fig06_awareness", "Eventbrite and Meetup public listings (14 Nov 2026); AI Tinkerers chapter pages; Google Trends by media market. Private platforms and organizer-reported.", title="Public AI activity: Cincinnati is in the lower half of its peers on all three comparable measures", extra_top=0.55)

# 7. Data-centre load, Duke Energy Ohio
yrs = ["2027", "2028", "2029", "2030", "2031", "2032-47"]; firm = [231, 250, 250, 250, 250, 250]; nonfirm = [0, 123, 302, 520, 755, 1080]
fig, ax = plt.subplots(figsize=(7.2, 3.9)); fig.subplots_adjust(left=0.1, right=0.97, top=0.76, bottom=0.2)
x = np.arange(6)
ax.bar(x, firm, width=0.6, color=BLUE, label="Signed service obligation"); ax.bar(x, nonfirm, width=0.6, bottom=firm, color=GREY, edgecolor=SURF, lw=2, label="Not signed (utility's own probability discount applied)")
for xi, f, n in zip(x, firm, nonfirm):
    ax.text(xi, f / 2, str(f), ha="center", va="center", color="white", fontsize=8.5)
    if n:
        ax.text(xi, f + n + 20, f"{f + n:,}", ha="center", va="bottom", color=INK2, fontsize=8.5)
ax.set_xticks(x, yrs); ax.tick_params(length=0); ax.grid(axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True); ax.set_ylabel("Megawatts of capacity")
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
finish(fig, "fig07_datacenter_load", "Duke Energy, Large Load Submittal for Duke Energy Ohio and Kentucky, PJM Load Analysis Subcommittee, 29 September 2026.",
       "Data-center load Duke Energy Ohio submitted to the grid operator for the 2027 forecast", title="Only 250 MW of data-center load is under contract in Duke Energy Ohio's territory")

# 8. BTOS AI use
b = pd.read_csv(P("data", "btos_ai_use.csv"), dtype={"period": str})
b = b[(b.measure == "current_use") & (b.answer == "Yes") & b.area.isin(["United States", "OH", "KY", "IN"])]
per = sorted(b.period.unique()); pos = {p: i for i, p in enumerate(per)}
fig, ax = plt.subplots(figsize=(7.2, 3.9)); fig.subplots_adjust(left=0.09, right=0.86, top=0.78, bottom=0.2)
for area, col, lw, lab in (("United States", INK2, 2.2, "United States"), ("OH", BLUE, 2.2, "Ohio"), ("KY", ORANGE, 1.6, "Kentucky"), ("IN", "#1baf7a", 1.6, "Indiana")):
    s_ = b[b.area == area].sort_values("period"); y = s_.pct.rolling(3, min_periods=1).mean()
    ax.plot([pos[p] for p in s_.period], y, color=col, lw=lw)
    ax.text(len(per) - 0.6, y.iloc[-1], f"{lab} {y.iloc[-1]:.0f}%", color=INK, fontsize=8.5, va="center")
ax.set_xticks([0, len(per) // 2, len(per) - 1], ["Nov 2025", "May 2026", "Oct 2026"]); ax.tick_params(length=0)
ax.grid(axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True); ax.set_ylabel("Share of businesses using AI"); ax.set_ylim(12, 28)
finish(fig, "fig08_btos", "Census Bureau Business Trends and Outlook Survey, biweekly, three-period moving average. No Cincinnati metro estimate is published.",
       "Businesses answering yes to using AI in any business function in the last two weeks", title="About one business in four now reports using AI; the three states track the nation")

# 9. Annual reports mentioning AI
k = pd.read_csv(P("data", "h5_10k_ai_mentions.csv")).groupby("fiscal_year_end").mentions_artificial_intelligence.sum()
fig, ax = plt.subplots(figsize=(7.2, 3.4)); fig.subplots_adjust(left=0.09, right=0.97, top=0.74, bottom=0.22)
ax.bar(k.index.astype(str), k.values, width=0.55, color=BLUE)
for xi, v in enumerate(k.values):
    ax.text(xi, v + 0.15, str(int(v)), ha="center", fontsize=9, color=INK2)
ax.set_ylim(0, 10); ax.tick_params(length=0); ax.grid(axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
ax.set_ylabel("Companies (of nine)"); ax.set_xlabel("Fiscal year of the annual report")
finish(fig, "fig09_annual_reports", "SEC EDGAR full-text search, phrase \"artificial intelligence\", Form 10-K, nine companies headquartered in the metro.",
       "Annual reports (Form 10-K) that mention \"artificial intelligence\"", title="By 2025 every large Cincinnati-based public company named AI in its annual report")

# 10. Output per worker
o = pd.read_csv(P("data", "h7_growth_table.csv")).sort_values("exposed_2022_24", ascending=False)
o = o[o.coverage_2024 >= 0.8]
fig, ax = plt.subplots(figsize=(7.2, 6.0)); fig.subplots_adjust(left=0.2, right=0.95, top=0.86, bottom=0.11)
hbar(ax, list(o.area), list(o.exposed_2022_24), "Cincinnati", "{:+.1f}%", other="United States"); ax.margins(x=0.12)
finish(fig, "fig10_output_per_worker", "BEA real GDP by county and industry (chained 2017 dollars) and BLS QCEW, summed over each metro's counties; Indianapolis omitted (24% coverage). Descriptive only.",
       "Change in real GDP per worker, 2022 to 2024: information, finance, professional services and management of companies", title="Output per worker in AI-exposed sectors grew more slowly here than in most peers")
print(sorted(os.path.basename(f) for f in glob.glob(os.path.join(OUT, "*.png"))))
