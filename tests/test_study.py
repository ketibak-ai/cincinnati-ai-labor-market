"""Regression tests for every figure the study publishes.

Each test recomputes a published number from the files in data/ and asserts that it
still matches what the paper, the deck and the site say. If a source file is
refreshed and a finding moves, the test that covers it fails and names the figure.

Two tests exist because the work got those things wrong once. test_soc_levels_partition
guards the occupational misclassification that double-counted national employment by
about 58%; test_exposure_band_table guards four wrong values in the exposure-band table.
Both bugs reached a published draft. Neither can return silently.

Run it:

    python tests/test_study.py            # plain, no dependencies
    python -m pytest tests/ -v            # same tests, if pytest is installed

Exit code 0 means every published figure reproduces. Exit code 1 lists what moved.
"""

import csv
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

BANK = ("Credit Intermediation and Related Activities "
        "including Monetary Authorities - Central Bank")

# The seventeen sectors plotted in the paper's sector chart.
PANEL = [
    "Mining, Logging and Construction", "Private Education and Health Services",
    "Leisure and Hospitality", "Manufacturing",
    "Professional, Scientific, and Technical Services",
    "Professional and Business Services", "Employment Services", "Other Services",
    "Retail Trade", "Financial Activities", "Government",
    "Insurance Carriers and Related Activities",
    "Trade, Transportation, and Utilities", BANK, "Information",
    "Transportation and Warehousing", "Federal Government",
]


# ---------------------------------------------------------------- helpers ----

def load(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def close(got, want, tol, label):
    assert got is not None, "%s: computed nothing" % label
    assert abs(got - want) <= tol, (
        "%s: published %s, recomputed %.6f (tolerance %s)" % (label, want, got, tol))


def wmean(rows, key):
    """Employment-weighted mean, excluding missing scores from BOTH sides.

    Treating a missing score as zero would drag every regional average toward the
    middle; the study excludes instead, and so does this check.
    """
    pairs = [(num(r["employment"]), num(r[key])) for r in rows]
    pairs = [(e, s) for e, s in pairs if e and s is not None]
    if not pairs:
        return None
    return sum(e * s for e, s in pairs) / sum(e for e, _ in pairs)


def detailed(rows, area):
    return [r for r in rows
            if r["area"] == area and r["soc_level"] == "detailed"]


# ------------------------------------------------------------ definitions ----

def test_soc_levels_partition():
    """Detailed occupations must not double-count their own aggregates.

    The original bug classified broad codes (XX-XXX0) as detailed, so national
    detailed employment summed to 234,970,310 against a published 155,495,730 --
    about 58% too high. Detailed employment must stay below the published total.
    """
    rows = load("cincinnati_occupation_exposure.csv")
    for area in ("National", "Cincinnati MSA", "Ohio", "Kentucky"):
        tot = [r for r in rows if r["area"] == area and r["soc_level"] == "total"]
        assert tot, "%s: no total row" % area
        published = num(tot[0]["employment"])
        summed = sum(num(r["employment"]) or 0 for r in detailed(rows, area))
        assert summed <= published, (
            "%s: detailed occupations sum to %.0f but the published total is %.0f "
            "-- aggregates are being counted twice" % (area, summed, published))
        coverage = summed / published * 100
        assert 90.0 <= coverage <= 100.0, (
            "%s: detailed coverage %.1f%% is outside the expected 90-100%% band"
            % (area, coverage))


def test_headline_exposure_gap():
    """Cincinnati 0.088 against a national 0.093 -- a gap of 0.005 SD.

    "Generative-AI exposure" is the AIOE language-modeling variant, not observed
    exposure: a different column with a different scale, and mixing them up moves
    the headline from 0.088 to 0.127.
    """
    rows = load("cincinnati_occupation_exposure.csv")
    cin = wmean(detailed(rows, "Cincinnati MSA"), "aioe_language_modeling")
    nat = wmean(detailed(rows, "National"), "aioe_language_modeling")
    close(cin, 0.088, 0.0005, "Cincinnati observed exposure")
    close(nat, 0.093, 0.0005, "National observed exposure")
    close(abs(cin - nat), 0.005, 0.0005, "exposure gap")


def test_exposure_band_table():
    """The five observed-exposure bands, as published.

    An earlier draft published 57 and 20 occupations in the top two bands at
    $66,159 and $62,210. The correct figures are 47 and 30 at $69,113 and $59,383.

    Two definitions matter here. "None measured" is a measured zero, not a missing
    value: 46 occupations carry no observed score at all and are excluded from the
    table entirely, so the denominator is matched employment (1,008,490), not all
    detailed employment. And the band wage is the employment-weighted MEAN of
    occupational medians -- not a median of medians, which would give $40,350 for
    the first band instead of $50,964.
    """
    rows = [r for r in detailed(load("cincinnati_occupation_exposure.csv"),
                                "Cincinnati MSA")
            if num(r["employment"]) and r["observed_exposure"] != ""]
    total_emp = sum(num(r["employment"]) for r in rows)
    assert abs(total_emp - 1008490) < 1, (
        "matched employment should be 1,008,490, got %.0f" % total_emp)

    bands = [
        ("None measured", lambda v: v == 0, 297, 417870, 41.4, 50964),
        ("Low, up to 0.10", lambda v: 0 < v <= 0.10, 131, 230970, 22.9, 73333),
        ("Moderate, 0.10-0.25", lambda v: 0.10 < v <= 0.25, 87, 127660, 12.7, 83964),
        ("High, 0.25-0.40", lambda v: 0.25 < v <= 0.40, 47, 131160, 13.0, 69113),
        ("Very high, above 0.40", lambda v: v > 0.40, 30, 100830, 10.0, 59383),
    ]
    seen = 0
    for label, test, n_occ, emp, share, wage in bands:
        got = [r for r in rows if test(num(r["observed_exposure"]))]
        assert len(got) == n_occ, (
            "%s: published %d occupations, recomputed %d" % (label, n_occ, len(got)))
        got_emp = sum(num(r["employment"]) for r in got)
        assert abs(got_emp - emp) < 1, (
            "%s: published %d jobs, recomputed %.0f" % (label, emp, got_emp))
        close(got_emp / total_emp * 100, share, 0.05, "%s share" % label)
        close(wmean(got, "annual_median"), wage, 1.0, "%s median wage" % label)
        seen += len(got)
    assert seen == len(rows), (
        "the five bands do not partition the matched occupations: %d of %d"
        % (seen, len(rows)))


def test_wage_gradient_top_quintile():
    """Language-model exposure reaches +0.703 SD in the top wage quintile.

    Quintiles are cut at equal CUMULATIVE EMPLOYMENT, not equal numbers of
    occupations, so each holds about a fifth of workers rather than of job titles.
    """
    rows = [r for r in detailed(load("cincinnati_occupation_exposure.csv"),
                                "Cincinnati MSA")
            if num(r["annual_median"]) and num(r["employment"])]
    rows.sort(key=lambda r: num(r["annual_median"]))
    total = sum(num(r["employment"]) for r in rows)
    cum = 0.0
    for r in rows:
        e = num(r["employment"])
        cum += e
        r["_q"] = min(4, int(5 * (cum - e / 2) / total))
    top = [r for r in rows if r["_q"] == 4]
    close(wmean(top, "aioe_language_modeling"), 0.703, 0.002,
          "top wage quintile LM exposure")
    bottom = [r for r in rows if r["_q"] == 0]
    got = wmean(bottom, "aioe_language_modeling")
    assert got < 0, (
        "the published finding is that exposure rises with pay: the bottom "
        "quintile should be negative, recomputed %.3f" % got)


def test_projection_churn():
    """98.0% of projected annual openings come from churn, not growth.

    101,316 is the published TOTAL row (SOC 00-0000), not a sum over occupations:
    adding every row together counts the aggregates as well and reaches 301,270.
    Detailed occupations alone come to 94,871, which is the coverage check below.
    """
    rows = load("cincinnati_oh_projections_2022_2032.csv")
    tot = [r for r in rows if r["soc_code"].replace("-", "") == "000000"]
    assert len(tot) == 1, "expected exactly one total row, found %d" % len(tot)
    t = tot[0]
    growth = num(t["open_growth"])
    total = num(t["open_total"])
    assert abs(total - 101316) < 1, "published 101,316 openings, got %.0f" % total
    assert abs(growth - 2074) < 1, "published 2,074 from growth, got %.0f" % growth
    close(growth / total * 100, 2.0, 0.05, "growth share of openings")
    close(100 - growth / total * 100, 98.0, 0.05, "churn share of openings")
    assert abs((growth + num(t["open_exits"]) + num(t["open_transfers"])) - total) < 1, (
        "growth + exits + transfers does not reconcile to the published total")

    det = [r for r in rows
           if r["soc_code"].replace("-", "")[-1] != "0"]
    det_total = sum(num(r["open_total"]) or 0 for r in det)
    assert det_total < total, (
        "detailed occupations (%.0f) must not exceed the published total (%.0f)"
        % (det_total, total))
    assert det_total / total > 0.90, (
        "detailed coverage of projected openings fell to %.1f%%"
        % (det_total / total * 100))


def test_computing_location_quotient():
    """Computer and mathematical occupations carry an LQ of 0.87."""
    rows = load("cincinnati_occupation_exposure.csv")
    got = [r for r in rows
           if r["area"] == "Cincinnati MSA" and r["soc_code"] == "15-0000"]
    assert got, "SOC 15-0000 not found for the Cincinnati MSA"
    close(num(got[0]["location_quotient"]), 0.87, 0.005,
          "computing location quotient")


def test_four_geographies_differ():
    """The four things called 'Cincinnati' differ by about 194,000 jobs."""
    published = {
        "Cincinnati OH-KY-IN MSA": 1101030,
        "ODJFS Cincinnati MSA (Ohio only)": 907032,
    }
    rows = load("cincinnati_occupation_exposure.csv")
    tot = [r for r in rows
           if r["area"] == "Cincinnati MSA" and r["soc_level"] == "total"]
    assert abs(num(tot[0]["employment"]) - published["Cincinnati OH-KY-IN MSA"]) < 1
    spread = (published["Cincinnati OH-KY-IN MSA"]
              - published["ODJFS Cincinnati MSA (Ohio only)"])
    assert abs(spread - 193998) < 100, (
        "the published spread is about 194,000 jobs, got %d" % spread)


def test_rebased_to_2024():
    """Total nonfarm +0.7% and 8,600 jobs; banking -4.1% against -13.9%."""
    rows = {r["industry"]: r for r in load("cincinnati_rebased_2024.csv")}
    tn = rows["Total Nonfarm"]
    base, end = num(tn["sep_2024"]), num(tn["sep_2026"])
    close((end / base - 1) * 100, 0.7, 0.05, "total nonfarm since 2024")
    assert abs((end - base) * 1000 - 8600) < 50, (
        "published 8,600 jobs added, recomputed %.0f" % ((end - base) * 1000))
    bank = rows[BANK]
    close(num(bank["pct_change_from_2024"]), -4.1, 0.05, "banking since 2024")
    close(num(bank["pct_change_from_2019"]), -13.9, 0.05, "banking since 2019")
    pre = ((num(bank["sep_2019"]) - num(bank["sep_2024"]))
           / (num(bank["sep_2019"]) - num(bank["sep_2026"])) * 100)
    close(pre, 73.7, 0.1, "share of banking fall predating 2024")


def test_seven_sectors_reverse():
    """Seven of the seventeen plotted sectors change sign between baselines.

    An earlier draft said two, and named banking as one of them. Banking falls on
    both baselines and does not reverse.
    """
    rows = {r["industry"]: r for r in load("cincinnati_rebased_2024.csv")}
    missing = [n for n in PANEL if n not in rows]
    assert not missing, "sectors missing from the panel: %s" % missing
    reversers = [n for n in PANEL
                 if num(rows[n]["pct_change_from_2024"])
                 * num(rows[n]["pct_change_from_2019"]) < 0]
    assert len(reversers) == 7, (
        "published 7 of 17 reversing, recomputed %d: %s"
        % (len(reversers), reversers))
    assert BANK not in reversers, (
        "banking must NOT be counted as a reverser -- it falls on both baselines")
    assert "Transportation and Warehousing" in reversers


def test_labour_force_fell_faster_than_employment():
    """The unemployment rate improved for the wrong reason."""
    rows = {(r["year"], r["month"]): r for r in load("cincinnati_laus_history.csv")}
    a, z = rows[("2024", "9")], rows[("2026", "9")]
    lf = num(z["labor_force"]) - num(a["labor_force"])
    emp = num(z["employment"]) - num(a["employment"])
    assert abs(lf - (-9374)) < 1, "published -9,374 labour force, got %.0f" % lf
    assert abs(emp - (-2161)) < 1, "published -2,161 employment, got %.0f" % emp
    assert lf < emp < 0, (
        "the published claim is that BOTH fell and the labour force fell faster")
    close(num(z["unemployment_rate"]), 3.6, 0.001, "Sept 2026 unemployment rate")
    close(num(a["unemployment_rate"]), 4.1, 0.001, "Sept 2024 unemployment rate")


def test_state_ai_usage_below_parity():
    """Ohio 0.59 and Kentucky 0.39 against population parity, May 2026."""
    rows = load("aei_state_overall.csv")
    want = {"Ohio": 0.59, "Kentucky": 0.39, "Indiana": 0.61}
    for geo, published in want.items():
        hit = [r for r in rows
               if r["geography"] == geo and r["month"] == "2026-05-01"
               and r["metric_id"] == "usage_per_capita_index"]
        assert hit, "%s: no May 2026 usage index" % geo
        close(num(hit[0]["value"]), published, 0.005, "%s usage index" % geo)
        assert num(hit[0]["value"]) < 1.0, (
            "%s is published as below parity (1.00)" % geo)


def test_no_metro_level_ai_usage_is_claimed():
    """The index publishes states, never metros. Guards against a false claim."""
    rows = load("aei_state_overall.csv")
    levels = {r["geo_level"] for r in rows}
    assert levels <= {"subregion", "country", "region"}, (
        "unexpected geography level in the AI usage data: %s" % levels)
    assert not any("Cincinnati" in r["geography"] for r in rows), (
        "there is no metro-level AI usage estimate -- none may be published")


def test_national_benchmark_cross_check():
    """Cincinnati should track the New York Fed's national benchmarks.

    The Fed finds roughly 40% of US workers in zero-exposure occupations and under
    10% above 0.40. Cincinnati at 41.4% and 10.0% is the study's sanity check that
    the method is not producing an artefact.
    """
    rows = [r for r in detailed(load("cincinnati_occupation_exposure.csv"),
                                "Cincinnati MSA")
            if num(r["employment"]) and r["observed_exposure"] != ""]
    total = sum(num(r["employment"]) for r in rows)
    zero = sum(num(r["employment"]) for r in rows
               if num(r["observed_exposure"]) == 0)
    high = sum(num(r["employment"]) for r in rows
               if num(r["observed_exposure"]) > 0.40)
    close(zero / total * 100, 41.4, 0.1, "zero-exposure share")
    close(high / total * 100, 10.0, 0.1, "above-0.40 share")
    assert 35 <= zero / total * 100 <= 45, (
        "zero-exposure share has drifted far from the national ~40% benchmark")
    assert high / total * 100 < 15, (
        "the share above 0.40 should stay near the national benchmark of under 10%")


# ----------------------------------------------------------------- runner ----

def main():
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    width = max(len(n) for n, _ in tests)
    failures = []
    print("=" * (width + 30))
    print("Cincinnati AI labor market study -- %d checks" % len(tests))
    print("=" * (width + 30))
    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failures.append((name, str(exc)))
            print("  FAIL  %-*s  %s" % (width, name, str(exc).split("\n")[0]))
        except Exception as exc:                      # noqa: BLE001
            failures.append((name, "%s: %s" % (type(exc).__name__, exc)))
            print("  ERROR %-*s  %s: %s" % (width, name, type(exc).__name__, exc))
        else:
            print("  pass  %s" % name)
    print("-" * (width + 30))
    if failures:
        print("%d of %d checks failed.\n" % (len(failures), len(tests)))
        for name, msg in failures:
            print("%s\n    %s\n" % (name, msg))
        return 1
    print("All %d published figures reproduce from data/." % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
