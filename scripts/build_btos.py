"""H5 (descriptive): Census Business Trends and Outlook Survey, AI-use question.
"In the last two weeks, did this business use Artificial Intelligence (AI) in producing goods
or services?" - share answering Yes, for Ohio, Kentucky, Indiana, the nation, and the BTOS
metros that are also P1 peers. BTOS publishes metros only for the 25 largest; Cincinnati is not
one of them, so NO Cincinnati figure exists and none is reported.
Output: data/btos_ai_use.csv ; output/btos_trace.txt
"""
import os
import openpyxl
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)


def sheet(f, name):
    ws = openpyxl.load_workbook(P("raw", "btos", f), read_only=True, data_only=True)[name]
    rows = list(ws.iter_rows(values_only=True))
    return pd.DataFrame(rows[1:], columns=[str(c) for c in rows[0]])

out = []
dates = sheet("National.xlsx", "Collection and Reference Dates")
QID = {"7": "current_use", "8": "employee_genai_use", "9": "effect_q9", "10": "effect_q10", "28": "expected_use_6m"}
qtext = {}
for f, geo in (("National.xlsx", None), ("State.xlsx", "State"), ("Top25MSA.xlsx", "MSA")):
    est, se = sheet(f, "Response Estimates"), sheet(f, "Response Standard Errors")
    est.columns = [c.strip() for c in est.columns]; se.columns = [c.strip() for c in se.columns]
    for t in (est, se):
        t["Question ID"] = t["Question ID"].astype(str).str.replace(r"\.0$", "", regex=True)
        t["Answer ID"] = t["Answer ID"].astype(str).str.replace(r"\.0$", "", regex=True)
    est = est[est["Question ID"].isin(QID)]
    se = se[se["Question ID"].isin(QID)]
    periods = [c for c in est.columns if c.isdigit()]
    for (_, r), (_, s) in zip(est.iterrows(), se.iterrows()):
        assert r["Question ID"] == s["Question ID"] and r["Answer ID"] == s["Answer ID"]
        area = "United States" if geo is None else r[geo]
        qtext[str(r["Question ID"])] = " ".join(str(r["Question"]).split())
        for p in periods:
            v = r[p]
            if v is None or not str(v).strip().rstrip("%").replace(".", "", 1).isdigit():
                continue
            sv = s[p]
            out.append(dict(area=area, geo=geo or "Nation", measure=QID[str(r["Question ID"])],
                            answer=" ".join(str(r["Answer"]).split()), period=p, pct=float(str(v).rstrip("%")),
                            se=float(str(sv).rstrip("%")) if sv is not None and str(sv).strip().rstrip("%").replace(".", "", 1).isdigit() else None))
D = pd.DataFrame(out)
D.to_csv(P("data", "btos_ai_use.csv"), index=False)
metros = sorted(D[D.geo == "MSA"].area.unique())
with open(P("output", "btos_trace.txt"), "w", encoding="utf-8") as fh:
    def w(*a):
        print(*a); print(*a, file=fh)
    w("BTOS metros published (25):", "; ".join(m.replace(" MSA", "") for m in metros))
    w("Cincinnati among them:", any("Cincinnati" in m for m in metros))
    for k, v in qtext.items():
        w(f"Q{k} ({QID[k]}): {v}")
    c = D[(D.measure == "current_use") & (D.answer == "Yes")]
    last, first = c.period.max(), c.period.min()
    w(f"\nPeriods in file: {first} to {last}")
    dd = dates.dropna(subset=["Smpdt"]).iloc[:, :9]
    dd = dd[dd.Smpdt.astype(float).astype(int).astype(str).isin([first, last])]
    w(dd.to_string(index=False))
    def avg(area, ps):   # mean of the periods listed, to damp biweekly noise
        x = c[(c.area == area) & c.period.isin(ps)]
        return x.pct.mean(), (x.se.pow(2).sum() ** 0.5) / max(len(x), 1)
    allp = sorted(c.period.unique())
    recent, early = allp[-6:], allp[:6]
    w(f"\nCurrent AI use, mean of the six most recent periods ({recent[0]}-{recent[-1]}) and the six earliest in the file ({early[0]}-{early[-1]}):")
    for a in ["United States", "OH", "KY", "IN"]:
        r, rs = avg(a, recent); e, es = avg(a, early)
        w(f"  {a:14s} recent {r:5.1f}% (se {rs:.1f})   earliest {e:5.1f}% (se {es:.1f})   latest single period {c[(c.area == a) & (c.period == last)].pct.iloc[0] if len(c[(c.area == a) & (c.period == last)]) else float('nan'):.1f}%")
    st = c[(c.geo == "State") & c.period.isin(recent)].groupby("area").pct.mean().sort_values(ascending=False)
    w(f"  State ranks (of {len(st)}), recent six periods: " + ", ".join(f"{a} {int((st > st[a]).sum()) + 1}" for a in ["OH", "KY", "IN"]) + f"; state median {st.median():.1f}%")
    ex = D[(D.measure == "expected_use_6m") & (D.answer == "Yes")]
    w("\nExpected AI use in the next six months, mean of the six most recent periods:")
    for a in ["United States", "OH", "KY", "IN"]:
        x = ex[(ex.area == a) & ex.period.isin(recent)]
        w(f"  {a:14s} {x.pct.mean():5.1f}%")
    w("\nBTOS metros that are P1 peers, current use, recent six periods:")
    ms = c[(c.geo == "MSA") & c.period.isin(recent)].groupby("area").pct.mean().sort_values(ascending=False)
    w(ms.round(1).to_string())
