"""Regression tests for every number that version 2.1 publishes.

Each test reads the data files that the 2.1 scripts write and asserts the value the report,
the deck and the site state. If a source is refreshed or a script changes and a finding moves,
the test that covers it fails and names the figure.

Two tests guard rules rather than numbers:
  test_no_metro_ai_usage_figure   no file may carry a Cincinnati-metro AI *usage* rate
                                  (the usage sources stop at state or district level)
  test_attendance_never_summed    organizer-reported attendance and membership are kept as
                                  attributed text, never as a number that could be totalled

Run:  python tests/test_study_2_1.py        (1.0's tests stay in tests/test_study.py)
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda f: os.path.join(ROOT, "data", f)
CIN = "17140"


def rows(f):
    with open(D(f), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def one(f, **where):
    r = [x for x in rows(f) if all(str(x[k]) == str(v) for k, v in where.items())]
    assert len(r) == 1, "%s: expected one row for %s, found %d" % (f, where, len(r))
    return r[0]


def close(actual, expected, tol, what):
    assert abs(float(actual) - expected) <= tol, "%s: expected %s, got %s" % (what, expected, actual)


def median(v):
    v = sorted(v); n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


# ---------------------------------------------------------------- peers
def test_peer_sets():
    p = rows("peer_sets.csv")
    assert sum(x["p1"] == "True" for x in p) == 19, "P1 must hold the Chamber's 19 peers"
    assert sum(x["p2"] == "True" for x in p) == 25, "P2 (0.6x-1.4x population) must hold 25 metros"
    p3 = sorted(x["short"] for x in p if x["p3"] == "True")
    assert p3 == ["Buffalo", "Chicago", "Cleveland", "Columbus", "Detroit", "Kansas City", "Louisville", "Minneapolis",
                  "Portland", "St. Louis"], "P3 membership changed: %s" % p3
    close(one("peer_sets.csv", CBSA=CIN)["POPESTIMATE2025"], 2312858, 0, "Cincinnati 2025 population")


# ---------------------------------------------------------------- H1-H3 hiring
HIRN = {"lm_aioe": 0.0104, "eloundou": 0.0140, "aei": 0.0291, "ms": -0.0440}


def test_h1_cincinnati_entry_door():
    for m, v in HIRN.items():
        r = one("h1_ddd.csv", cbsa=CIN, outcome="HirN", young="A03", grouping="tercile", measure=m)
        close(r["ddd"], v, 0.0006, "H1 DDD %s" % m)
        assert float(r["perm_p10"]) < float(r["ddd"]) < float(r["perm_p90"]), "H1 %s should sit inside the permutation band" % m
        assert float(r["cov_exposed"]) > 0.95 and float(r["cov_less"]) > 0.95, "H1 coverage fell below 95%% for %s" % m
    assert not any(v <= -0.05 for v in HIRN.values()), "no measure may reach the -0.05 threshold"


def test_h1_peers_show_narrowing():
    r = [x for x in rows("h1_ddd.csv") if x["outcome"] == "HirN" and x["young"] == "A03" and x["grouping"] == "tercile"]
    assert len({x["cbsa"] for x in r}) == 32, "32 metros have QWI through 2025Q4"
    assert "19820" not in {x["cbsa"] for x in r}, "Detroit must be absent (Michigan QWI ends 2021Q4)"
    for m, med, rank in (("lm_aioe", -0.0218, 14), ("eloundou", -0.0771, 18), ("aei", -0.0558, 18), ("ms", -0.1606, 19)):
        p1 = [float(x["ddd"]) for x in r if x["measure"] == m and x["p1"] == "True"]
        assert len(p1) == 18
        close(median(p1), med, 0.0006, "P1 median DDD %s" % m)
        cin = HIRN[m]
        assert sum(v < cin for v in p1) + 1 == rank, "Cincinnati's rank from the bottom of P1 on %s" % m
    neg = [float(x["ddd"]) < 0 for x in r if x["measure"] == "ms" and x["cbsa"] != CIN]
    assert all(neg), "every peer is negative on the Microsoft measure"


def test_h1_rate_checks():
    for m, ex in (("lm_aioe", 0.0237), ("eloundou", 0.0291), ("aei", 0.0489), ("ms", -0.0302)):
        r = one("h1_rate_checks.csv", cbsa=CIN, measure=m)
        close(r["ddd_excl_51_52_53"], ex, 0.0006, "DDD without information, finance, real estate (%s)" % m)
        assert float(r["placebo_vs_comp"]) > float(r["exposed_vs_comp"]), "placebo should not be more negative than exposed"


def test_h2_headcount_version():
    for m, v, pct in (("lm_aioe", -0.0134, 42.0), ("eloundou", -0.0738, 18.3), ("aei", -0.0277, 33.6), ("ms", -0.1241, 5.0)):
        r = one("h1_ddd.csv", cbsa=CIN, outcome="Emp", young="A03", grouping="tercile", measure=m)
        close(r["ddd"], v, 0.0006, "H2 employment DDD %s" % m)
        close(r["perm_pctile"], pct, 0.11, "H2 permutation percentile %s" % m)


def test_h2b_acs():
    for m, v, se in (("lm_aioe", 0.069, 0.152), ("eloundou", 0.100, 0.140), ("aei", -0.121, 0.150), ("ms", -0.017, 0.136)):
        r = one("h2b_acs.csv", cbsa=CIN, measure=m)
        close(r["ddd"], v, 0.0006, "H2b DDD %s" % m); close(r["se"], se, 0.0006, "H2b standard error %s" % m)
        assert abs(float(r["t"])) < 1.645, "Cincinnati's ACS estimate must not be reported as significant (%s)" % m


def test_h3_earnings():
    for m in HIRN:
        close(one("h3_earnings.csv", cbsa=CIN, measure=m)["ddd_earn"], 0.005, 0.006, "H3 earnings DDD %s" % m)


def test_hires_by_age_group():
    t = {(x["grp"], x["age"]): float(x["chg"]) for x in rows("h1_hires_by_age_group_cincinnati.csv")}
    for k, v in ((("Most exposed third", "22-24"), -8.9), (("Most exposed third", "35-54"), 0.5), (("Middle third", "22-24"), -16.1),
                 (("Least exposed third", "22-24"), -11.3), (("Least exposed third", "35-54"), -3.8)):
        close(t[k], v, 0.06, "change in new hires %s" % (k,))


# ---------------------------------------------------------------- H4, H10 exposure
def test_h4_exposure_average():
    c, us = one("h4_exposure_peers.csv", cbsa=CIN), one("h4_exposure_peers.csv", cbsa="0")
    for m, cv, uv in (("lm_aioe", 0.0792, 0.0948), ("eloundou", 0.3061, 0.3089), ("aei", 0.1267, 0.1305), ("ms", 0.1713, 0.1721)):
        close(c[m], cv, 0.00006, "Cincinnati %s" % m); close(us[m], uv, 0.00006, "US %s" % m)
    p1 = [x for x in rows("h4_exposure_peers.csv") if x["p1"] == "True"]
    inside = 0
    for m in ("lm_aioe", "eloundou", "aei", "ms"):
        v = sorted(float(x[m]) for x in p1)
        q1, q3 = v[4] + 0.5 * (v[5] - v[4]), v[13] + 0.5 * (v[14] - v[13])      # quartiles of 19 values
        inside += q1 <= float(c[m]) <= q3
    assert inside == 3, "Cincinnati should be inside the P1 interquartile range on 3 of 4 measures, got %d" % inside


def test_h10_gradient_is_national():
    g = rows("h10_wage_gradient.csv")
    assert all(float(x["lm_aioe_gradient"]) > 0 for x in g) and len(g) == 34, "exposure rises with pay in all 33 metros and the US"
    close(one("h10_wage_gradient.csv", cbsa=CIN)["lm_aioe_gradient"], 1.0258, 0.0002, "Cincinnati gradient")
    close(one("h10_wage_gradient.csv", cbsa="0")["lm_aioe_gradient"], 1.2001, 0.0002, "US gradient")


# ---------------------------------------------------------------- H5 adoption
def test_btos_states():
    b = [x for x in rows("btos_ai_use.csv") if x["measure"] == "current_use" and x["answer"] == "Yes"]
    per = sorted({x["period"] for x in b}); recent = set(per[-6:])
    for a, v in (("United States", 23.7), ("OH", 22.2), ("KY", 23.2), ("IN", 20.2)):
        s = [float(x["pct"]) for x in b if x["area"] == a and x["period"] in recent]
        close(sum(s) / len(s), v, 0.06, "BTOS recent AI use %s" % a)
    assert per[0] == "202524" and per[-1] == "202622", "BTOS AI series should run 202524-202622"


def test_annual_reports():
    k = {}
    for x in rows("h5_10k_ai_mentions.csv"):
        k[x["fiscal_year_end"]] = k.get(x["fiscal_year_end"], 0) + (x["mentions_artificial_intelligence"] == "True")
    assert k == {"2020": 1, "2021": 2, "2022": 1, "2023": 4, "2024": 8, "2025": 9}, "10-K AI mentions by year: %s" % k


def test_no_metro_ai_usage_figure():
    """BTOS, the Anthropic index and the Cleveland Fed survey stop at state or district level."""
    b = rows("btos_ai_use.csv")
    assert not any("Cincinnati" in x["area"] for x in b), "BTOS publishes no Cincinnati estimate; none may appear"
    a = one("awareness_like_for_like.csv", cbsa=CIN)
    assert not any("usage" in k.lower() or "adoption" in k.lower() for k in a), "the awareness file must not carry a usage or adoption rate"


# ---------------------------------------------------------------- H6 capability
def test_h6_shift_share():
    c = one("h6_shift_share.csv", cbsa=CIN)
    close(c["lq_actual"], 0.868, 0.0006, "computing LQ"); close(c["lq_expected"], 0.924, 0.0006, "expected LQ from industry mix")
    close(float(c["gap"]) * float(c["oews_total"]), -4906, 1, "gap in jobs")
    close(float(c["industry_mix"]) * float(c["oews_total"]), -2839, 1, "industry-mix jobs")
    close(float(c["within_industry"]) * float(c["oews_total"]), -2066, 1, "within-industry jobs")
    assert float(c["within_share_of_gap"]) < 0.5, "within-industry share must stay under half for the restated claim"


def _rank(f, col):
    t = rows(f); v = float(one(f, CBSA=CIN)[col])
    return v, sum(float(x[col]) > v for x in t if x["p1"] == "True") + 1


def test_h6_capability_ranks():
    for f, col, val, tol, rank in (("h6_ai_patents.csv", "ai_patents_per_100k", 44.3, 0.06, 16),
                                   ("h6_herd_computing_rd.csv", "computing_rd_per_capita", 2.80, 0.006, 14),
                                   ("h6_ipeds_completions.csv", "completions_per_100k", 130.0, 0.06, 8)):
        v, r = _rank(f, col)
        close(v, val, tol, col); assert r == rank, "%s rank: expected %d of 20, got %d" % (col, rank, r)
    close(one("h6_ai_patents.csv", CBSA=CIN)["ai_patents_2019_23"], 1025, 0, "AI patents 2019-23")
    close(one("h6_herd_computing_rd.csv", CBSA=CIN)["computing_rd_thousands"], 6469, 0, "computing R&D ($000)")


# ---------------------------------------------------------------- H7 output, H9 growth
def test_h7_output_per_worker():
    t = {x["area"]: x for x in rows("h7_growth_table.csv")}
    close(t["Cincinnati"]["exposed_2022_24"], 2.35, 0.006, "Cincinnati exposed-sector output per worker 2022-24")
    close(t["United States"]["exposed_2022_24"], 5.44, 0.006, "US exposed-sector output per worker 2022-24")


def test_h9_growth_not_slow():
    g = rows("h9_growth_peers.csv")
    cin = float(one("h9_growth_peers.csv", cbsa=CIN)["growth_pct"])
    close(cin, 0.735, 0.0006, "Cincinnati growth"); close(one("h9_growth_peers.csv", cbsa="0")["growth_pct"], 0.723, 0.0006, "US growth")
    peers = [float(x["growth_pct"]) for x in g if x["cbsa"] not in (CIN, "0")]
    assert len(peers) == 19 and sum(v > cin for v in peers) + 1 == 10, "Cincinnati should rank 10th of 20"
    close(median(peers), 0.187, 0.001, "P1 median growth")


def test_h9_replacement_share():
    s = {x["area"].split(" (")[0]: float(x["growth_share_pct"]) for x in rows("h9_projection_growth_share.csv")}
    close(s["Cincinnati"], 2.05, 0.006, "Cincinnati growth share"); close(s["United States"], 3.39, 0.006, "US growth share")
    close(s["Ohio"], 0.92, 0.006, "Ohio growth share")
    others = [s[k] for k in ("Akron", "Canton", "Cleveland", "Columbus", "Dayton", "Toledo", "Youngstown")]
    assert sum(v > s["Cincinnati"] for v in others) == 1, "only Columbus should have a higher growth share than Cincinnati"


def test_h9_labor_force():
    d = one("h9_labor_force_decomposition.csv", window="2024-2025")
    close(d["acs_lf_start"], 1215870, 0, "ACS labor force 2024"); close(d["acs_lf_end"], 1235990, 0, "ACS labor force 2025")
    close(d["age_mix"], -4254, 1, "age-mix effect"); close(d["participation"], 17319, 1, "participation effect")


# ---------------------------------------------------------------- H8 data centers
def test_h8_data_centers():
    e = {(x["item"], x["unit"]): x["value"] for x in rows("h8_data_center_evidence.csv")}
    assert e[("Duke Energy Ohio firm data-center load", "MW capacity 2028 onward")] == "250"
    assert e[("Duke Energy Ohio non-firm data-center load", "MW capacity 2032-2047")] == "1080"
    assert e[("Trenton (Prologis) permanent jobs", "full-time jobs by 31 Dec 2035")] == "120"
    assert e[("Trenton (Prologis) jobs per MW", "committed full-time jobs per MW")] == "0.48"
    q = [x for x in rows("h8_qcew_518210_counties.csv") if x["metro"] == "Cincinnati" and x["naics"] == "518210"]
    pub = lambda y: sum(float(x["emp"]) for x in q if x["year"] == y and x["suppressed"] == "False")
    assert pub("2022") == 1576 and pub("2025") == 1977, "QCEW 518210, published counties: %s -> %s" % (pub("2022"), pub("2025"))
    assert pub("2025") - pub("2022") < 1000, "DC2 threshold (+1,000) must not be met"
    assert all(x["suppressed"] == "True" for x in q if x["county"].startswith("Butler") and x["year"] >= "2022"), "Butler County is suppressed from 2022 on"


# ---------------------------------------------------------------- awareness
def test_awareness_like_for_like():
    a = rows("awareness_like_for_like.csv"); c = one("awareness_like_for_like.csv", cbsa=CIN)
    assert len(a) == 20
    for col, val, tol, rank in (("l1_per_100k", 0.363, 0.001, 15), ("l2_per_100k", 0.073, 0.001, 10), ("l3_mean", 30.67, 0.01, 17)):
        close(c[col], val, tol, col)
        assert sum(float(x[col]) > float(c[col]) for x in a if x["cbsa"] != CIN) + 1 == rank, "%s rank" % col
    assert c["l1_events"] == "5" and float(c["l2_meetings"]) == 1
    close(c["post_two_terms_per_100k"], 7.76, 0.006, "postings naming AI tools per 100k")
    assert sum(float(x["post_two_terms_per_100k"]) > float(c["post_two_terms_per_100k"]) for x in a if x["cbsa"] != CIN) + 1 == 13


def test_event_census():
    e = rows("ai_events.csv")
    assert len(e) == 56 and sum(x["status"] == "held" for x in e) == 50
    ca = [x for x in e if x["series_name"] == "CincyAI for Humans" and x["date"] <= "2026-11-14"]
    assert len(ca) == 36 and sum(x["status"] == "held" for x in ca) == 35, "CincyAI: 36 scheduled, 35 held, 1 cancelled"
    last = [x for x in e if x["status"] == "held" and "2025-11-14" < x["date"] <= "2026-11-14"]
    assert len(last) == 18 and sum(x["audience"] == "technical" for x in last) == 1
    assert all(x["source_url"] for x in e), "every census event needs a source"


def test_attendance_never_summed():
    for f, col in (("ai_event_attendance_claims.csv", "figure"), ("ai_community_groups.csv", "value")):
        for x in rows(f):
            assert not x[col].replace(",", "").replace(".", "").isdigit(), "%s: '%s' must stay attributed text, not a bare number" % (f, x[col])
    assert all(x["reported_by"] for x in rows("ai_event_attendance_claims.csv")), "every attendance claim names who reported it"


def test_agent_register_rule():
    r = rows("ai_agent_register.csv")
    ok = [x for x in r if x["read"] == "yes" and x["grade"] in ("1", "2")]
    prod = {x["employer"] for x in ok if x["kind"] == "agent" and x["stage"] == "production"}
    assert prod == {"CBTS"}, "only CBTS has read, grade 1-2 evidence of an agent in production: %s" % prod
    assert len(prod) < 3, "the sentence 'AI agents are in production at large employers' needs three; it must not be used"
    assert len(r) == 19 and len(ok) == 13 and len({x["employer"] for x in ok}) == 10
    assert not any(x["grade"] == "4" for x in r), "grade 4 sources are never recorded as evidence"


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main():
    width = max(len(t.__name__) for t in TESTS); failures = []
    print("Cincinnati AI Labor Market 2.1 - regression tests\n" + "-" * (width + 30))
    for fn in TESTS:
        try:
            fn()
        except AssertionError as exc:
            failures.append((fn.__name__, str(exc))); print("  FAIL  %-*s  %s" % (width, fn.__name__, str(exc).split("\n")[0]))
        except Exception as exc:                                  # noqa: BLE001
            failures.append((fn.__name__, "%s: %s" % (type(exc).__name__, exc))); print("  ERROR %-*s  %s: %s" % (width, fn.__name__, type(exc).__name__, exc))
        else:
            print("  pass  %s" % fn.__name__)
    print("-" * (width + 30))
    if failures:
        print("%d of %d checks failed.\n" % (len(failures), len(TESTS)))
        for name, msg in failures:
            print("%s\n    %s\n" % (name, msg))
        return 1
    print("All %d checks pass: every 2.1 figure reproduces from data/." % len(TESTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
