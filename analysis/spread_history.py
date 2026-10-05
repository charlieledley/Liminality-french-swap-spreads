# -*- coding: utf-8 -*-
"""Spread history on both swap bases: the data behind the dislocation, roll and scenario slides.

Decision 0003 (update of 2026-10-05): until the deck's basis is chosen, every figure is built
twice, against EUR STR OIS and against the 6m Euribor swap, side by side. Charlie's IRR and
MOIC spreadsheet is on the Euribor basis.

Sign: swap minus bond (decision 0002). A cheap OAT reads negative.
Sovereign yields: Bloomberg generic benchmarks throughout (decision 0004, reversed 2026-10-05).
OIS leg: Bloomberg EESWE, which embeds the 8.5bp EONIA splice (decision 0003).

Outputs
  deck/data/spread_history_<date>.json            everything the deck builder needs
  exports/spread_history_both_bases_<date>.xlsx   the same, formatted, for Charlie to audit

Windows
  PCT_START  the percentile window: 2010-01-01, the whole euro sovereign crisis without the
             2007-09 money-market blow-out (decision 0005, Charlie 2026-10-05)
  ALT_PCT_START  2012, the draft deck's window, kept for comparison
  CHART_START  where the history charts begin; 2007 is where the OIS history begins
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "skills", "xlsx-report"))
import load_rates                                    # noqa: E402
from xlsx_report import Block, write_report          # noqa: E402

ASOF = "2026-10-05"
PCT_START = "2010-01-01"       # decision 0005: the whole euro sovereign crisis, without 2007-09
ALT_PCT_START = "2012-01-01"   # the draft deck's window, kept for comparison
CHART_START = "2007-01-02"
ITALY = ("2010-01-01", "2013-12-31")
ITALY_STRESS_BP = -350            # the scenario row Charlie added: "below -350 only ~45 days in late 2011"
PCTS = [1, 5, 10, 25, 50, 75, 90, 95, 99]
BASES = {"ois": "vs €STR OIS (EONIA less 8.5bp before Oct 2019)",
         "eur6m": "vs 6m Euribor swap"}
PRIMARY_BASIS = "eur6m"   # decision 0003, revised 2026-10-05: the scenario analysis is on 6m Euribor


def pct_rank(series, value):
    """Share of observations strictly below `value`, in percent. Low = cheap for a swap-minus-bond spread."""
    s = series.dropna()
    return float((s < value).mean() * 100)


def ladder(series, start):
    s = series[start:].dropna()
    out = {f"p{p}": float(np.percentile(s, p)) for p in PCTS}
    out.update(min=float(s.min()), min_date=str(s.idxmin().date()),
               max=float(s.max()), max_date=str(s.idxmax().date()),
               mean=float(s.mean()), n=int(len(s)),
               first=str(s.index[0].date()), last=str(s.index[-1].date()))
    return out


def build():
    w = load_rates.load()
    last_date = w["fra_ois_1y_bp"].dropna().index[-1]
    out = {"asof_data": str(last_date.date()), "received": ASOF, "sign": "swap minus bond, bp",
           "pct_start": PCT_START, "alt_pct_start": ALT_PCT_START, "bases": BASES,
           "primary_basis": PRIMARY_BASIS, "by_basis": {}}
    for b, label in BASES.items():
        d = {"label": label, "current": {}, "ladder_1y": {}, "ladder_5y": {}, "italy": {}}
        for t in ("1y", "5y"):
            s = w[f"fra_{b}_{t}_bp"]
            cur = float(s.dropna().iloc[-1])
            d["current"][f"fra_{t}"] = cur
            d["current"][f"fra_{t}_pct_since_{PCT_START[:4]}"] = pct_rank(s[PCT_START:], cur)
            d["current"][f"fra_{t}_pct_since_{ALT_PCT_START[:4]}"] = pct_rank(s[ALT_PCT_START:], cur)
            d[f"ladder_{t}"] = {PCT_START[:4]: ladder(s, PCT_START), ALT_PCT_START[:4]: ladder(s, ALT_PCT_START)}
            it = w[f"ita_{b}_{t}_bp"][ITALY[0]:ITALY[1]].dropna()
            below = it[it < ITALY_STRESS_BP]
            d["italy"][t] = {"min": float(it.min()), "min_date": str(it.idxmin().date()),
                             "p5": float(np.percentile(it, 5)), "median": float(it.median()),
                             "stress_level_bp": ITALY_STRESS_BP, "days_below_stress": int(len(below)),
                             "days_below_stress_span": ([str(below.index.min().date()), str(below.index.max().date())]
                                                        if len(below) else None)}
        # France's own 1y and 5y lows inside the euro-crisis window, for the stress-analogue page
        d["france_crisis"] = {}
        for t in ("1y", "5y"):
            fc = w[f"fra_{b}_{t}_bp"][ITALY[0]:ITALY[1]].dropna()
            d["france_crisis"][t] = {"min": float(fc.min()), "min_date": str(fc.idxmin().date())}
        # Spain 1y, whole available history (from 2011-10-06), for the executive-summary claim
        sp = w[f"esp_{b}_1y_bp"].dropna()
        spb = sp[sp < ITALY_STRESS_BP]
        d["spain"] = {"1y": {"first": str(sp.index[0].date()), "last": str(sp.index[-1].date()), "n": int(len(sp)),
                             "min": float(sp.min()), "min_date": str(sp.idxmin().date()),
                             "stress_level_bp": ITALY_STRESS_BP, "days_below_stress": int(len(spb)),
                             "days_below_stress_span": ([str(spb.index.min().date()), str(spb.index.max().date())] if len(spb) else None)}}
        bond = w[f"frtr32_{b}_bp"].dropna()
        d["current"]["frtr32"] = float(bond.iloc[-1])
        d["current"]["frtr32_date"] = str(bond.index[-1].date())
        d["current"]["frtr32_minus_fra_5y"] = float(bond.iloc[-1] - w[f"fra_{b}_5y_bp"].dropna().iloc[-1])
        # how rare today's 5y level is: days since PCT_START (before today) the 5y spread sat strictly below
        # today's 5y spread. On Bloomberg generics the 5y point is the bond itself, so this is the bond's rarity too.
        s5 = w[f"fra_{b}_5y_bp"][PCT_START:].dropna()
        below = s5.iloc[:-1][s5.iloc[:-1] < s5.iloc[-1]]
        d["current"]["days_5y_below_frtr32"] = int(len(below))
        d["current"]["days_5y_below_frtr32_span"] = ([str(below.index.min().date()), str(below.index.max().date())]
                                                     if len(below) else None)
        out["by_basis"][b] = d
    # the basis itself, bp, yearly means and current
    basis = {}
    for t in ("1y", "5y"):
        s = w[f"eur6m_ois_basis_{t}_bp"].dropna()
        basis[t] = {"current": float(s.iloc[-1]), f"mean_since_{PCT_START[:4]}": float(s[PCT_START:].mean()),
                    "mean_2008_2012": float(s["2008":"2012"].mean()),
                    "yearly_mean": {int(y): float(v) for y, v in s.groupby(s.index.year).mean().items()}}
    out["basis_eur6m_minus_ois_bp"] = basis
    # the levels on the data date, percent, for the what-is-a-swap-spread and arithmetic pages
    lv = w.loc[last_date]
    out["levels_pct"] = {k: float(lv[k]) for k in ("bbg_fra_1y", "bbg_eur6m_1y", "bbg_estr_1y",
                                                  "bbg_fra_5y", "bbg_eur6m_5y", "bbg_estr_5y", "frtr32_yield")}
    # weekly series for charts (last business day of each week), both bases, plus the basis itself
    cols = {f"fra_{b}_{t}_bp": f"fra_{t}_{b}" for b in BASES for t in ("1y", "5y")}
    cols.update({f"ita_{b}_{t}_bp": f"ita_{t}_{b}" for b in BASES for t in ("1y", "5y")})
    cols.update({f"frtr32_{b}_bp": f"frtr32_{b}" for b in BASES})
    cols.update({f"esp_{b}_1y_bp": f"esp_1y_{b}" for b in BASES})
    cols.update({f"eur6m_ois_basis_{t}_bp": f"basis_{t}" for t in ("1y", "5y")})
    wk = w[list(cols)].rename(columns=cols)[CHART_START:].resample("W-FRI").last()
    out["weekly"] = {"date": [str(x.date()) for x in wk.index],
                     **{c: [None if pd.isna(v) else round(float(v), 2) for v in wk[c]] for c in wk.columns}}
    return w, out


def workbook(w, out, path):
    B = list(BASES)
    # --- Summary: current levels and percentile ranks, both bases side by side
    rows = []
    for t in ("1y", "5y"):
        rows.append([f"France {t} spread today ({out['asof_data']})"] + [out["by_basis"][b]["current"][f"fra_{t}"] for b in B])
        rows.append([f"  percentile since {PCT_START[:4]} (low = cheap)"] + [out["by_basis"][b]["current"][f"fra_{t}_pct_since_{PCT_START[:4]}"] for b in B])
        rows.append([f"  percentile since {ALT_PCT_START[:4]}"] + [out["by_basis"][b]["current"][f"fra_{t}_pct_since_{ALT_PCT_START[:4]}"] for b in B])
        rows.append([f"  median since {PCT_START[:4]} (the draft's 50th-percentile scenario)"] + [out["by_basis"][b][f"ladder_{t}"][PCT_START[:4]]["p50"] for b in B])
    rows.append([f"FRTR 3¼ 02/25/32 spread ({out['by_basis']['ois']['current']['frtr32_date']})"] + [out["by_basis"][b]["current"]["frtr32"] for b in B])
    rows.append(["  bond minus 5y CMT point (maturity pickup)"] + [out["by_basis"][b]["current"]["frtr32_minus_fra_5y"] for b in B])
    rows.append(["6m Euribor minus €STR basis, 1y, today"] + [out["basis_eur6m_minus_ois_bp"]["1y"]["current"]] * 2)
    rows.append(["6m Euribor minus €STR basis, 5y, today"] + [out["basis_eur6m_minus_ois_bp"]["5y"]["current"]] * 2)
    summ = pd.DataFrame(rows, columns=["Measure"] + [BASES[b] for b in B])
    kinds = ["num1", "num0", "num0", "num1"] * 2 + ["num1", "num1", "num1", "num1"]
    # --- Percentile ladders
    def ladder_df(t, start):
        L = {b: out["by_basis"][b][f"ladder_{t}"][start[:4]] for b in B}
        r = [["Max (richest)"] + [L[b]["max"] for b in B]]
        suffix = {1: "st", 2: "nd", 3: "rd"}
        r += [[f"{p}{suffix.get(p % 10 if p not in (11, 12, 13) else 0, 'th')} percentile"] + [L[b][f"p{p}"] for b in B]
              for p in reversed(PCTS)]
        r += [["Min (cheapest)"] + [L[b]["min"] for b in B],
              ["Mean"] + [L[b]["mean"] for b in B],
              ["Observations"] + [L[b]["n"] for b in B]]
        df = pd.DataFrame(r, columns=["Level"] + [BASES[b] for b in B])
        note = "Daily, %s to %s. Dates of extremes: min %s / %s, max %s / %s (€STR / Euribor)." % (
            L["ois"]["first"], L["ois"]["last"], L["ois"]["min_date"], L["eur6m"]["min_date"], L["ois"]["max_date"], L["eur6m"]["max_date"])
        return df, note
    pct_blocks = []
    for t in ("1y", "5y"):
        for start in (PCT_START, ALT_PCT_START):
            df, note = ladder_df(t, start)
            pct_blocks.append(Block(f"France {t} swap spread, percentile ladder since {start[:4]} (bp, swap minus bond)",
                                    df, label_col="Level", formats={"*": "num1"}, note=note))
    # --- Basis
    by = out["basis_eur6m_minus_ois_bp"]
    years = sorted(by["1y"]["yearly_mean"])
    basis_df = pd.DataFrame({"Year": years, "1y basis (bp)": [by["1y"]["yearly_mean"][y] for y in years],
                             "5y basis (bp)": [by["5y"]["yearly_mean"][y] for y in years]})
    # --- Italy
    it_rows = []
    for t in ("1y", "5y"):
        for b in B:
            I = out["by_basis"][b]["italy"][t]
            it_rows.append([f"Italy {t}, {BASES[b]}", I["min"], I["min_date"], I["p5"], I["median"]])
    italy_df = pd.DataFrame(it_rows, columns=["Series", "Cheapest (bp)", "Date", "5th percentile", "Median"])
    # --- Weekly series with chart
    wk = pd.DataFrame(out["weekly"])
    wk_fr = wk[["date", "fra_1y_ois", "fra_5y_ois", "fra_1y_eur6m", "fra_5y_eur6m"]].rename(columns={
        "date": "Week", "fra_1y_ois": "France 1y vs €STR", "fra_5y_ois": "France 5y vs €STR",
        "fra_1y_eur6m": "France 1y vs Euribor", "fra_5y_eur6m": "France 5y vs Euribor"})
    sheets = {
        "Summary": [Block("France swap spreads, both bases (bp, swap minus bond; percentiles in %)", summ,
                          label_col="Measure", row_formats=kinds,
                          note="Yields: Citi CMT from 2011-09-22, Bloomberg generic before (decision 0004). OIS: Bloomberg EESWE. "
                               "Euribor: Bloomberg EUSA. Bond: Bloomberg mid yield. Percentile = share of daily observations below today's level.")],
        "Percentiles": pct_blocks,
        "Basis": [Block("6m Euribor swap minus €STR OIS, yearly mean (bp)", basis_df, label_col="Year",
                        formats={"*": "num1"}, chart={"kind": "line", "title": "Euribor / €STR basis, yearly mean (bp)"},
                        note="This is the amount every spread moves when the basis changes. 2021 is the low; 2008 to 2012 the high.")],
        "Italy 2010-13": [Block("Italy swap spreads in the 2010-2013 stress (bp, swap minus bond)", italy_df, label_col="Series",
                                formats={"Cheapest (bp)": "num1", "5th percentile": "num1", "Median": "num1", "Date": "text"},
                                note="Bloomberg generic yields before 2011-09-22, Citi CMT after; the join falls inside this window (decision 0004).")],
        "Weekly series": [Block("France 1y and 5y swap spreads, weekly (bp, swap minus bond)", wk_fr, label_col="Week",
                                formats={"*": "num1"}, chart={"kind": "line", "title": "France swap spreads, both bases", "width": 26, "height": 12})],
    }
    write_report(path, sheets, title="French swap spreads: history on both bases",
                 subtitle=f"Data to {out['asof_data']}, received {ASOF}. analysis/spread_history.py")


if __name__ == "__main__":
    w, out = build()
    os.makedirs(os.path.join(HERE, "..", "deck", "data"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "..", "exports"), exist_ok=True)
    jp = os.path.join(HERE, "..", "deck", "data", f"spread_history_{ASOF}.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    xp = os.path.join(HERE, "..", "exports", f"spread_history_both_bases_{ASOF}.xlsx")
    workbook(w, out, xp)
    print("wrote", os.path.relpath(jp, os.path.join(HERE, "..")), "and", os.path.relpath(xp, os.path.join(HERE, "..")))
    for b in BASES:
        c = out["by_basis"][b]["current"]
        L1 = out["by_basis"][b]["ladder_1y"][PCT_START[:4]]
        print(f"\n{BASES[b]}  (data to {out['asof_data']})")
        print(f"  France 1y {c['fra_1y']:7.1f} bp  pct since {PCT_START[:4]} {c[f'fra_1y_pct_since_{PCT_START[:4]}']:5.1f}%   median {L1['p50']:6.1f}  p10 {L1['p10']:6.1f}  min {L1['min']:6.1f} ({L1['min_date']})")
        L5 = out["by_basis"][b]["ladder_5y"][PCT_START[:4]]
        print(f"  France 5y {c['fra_5y']:7.1f} bp  pct since {PCT_START[:4]} {c[f'fra_5y_pct_since_{PCT_START[:4]}']:5.1f}%   median {L5['p50']:6.1f}  p10 {L5['p10']:6.1f}  min {L5['min']:6.1f} ({L5['min_date']})")
        print(f"  FRTR 32   {c['frtr32']:7.1f} bp ({c['frtr32_date']}), {c['frtr32_minus_fra_5y']:+.1f} vs the 5y point")
        I = out["by_basis"][b]["italy"]
        print(f"  Italy 2010-13 cheapest: 1y {I['1y']['min']:.0f} ({I['1y']['min_date']}), 5y {I['5y']['min']:.0f} ({I['5y']['min_date']})")
    by = out["basis_eur6m_minus_ois_bp"]
    print(f"\nbasis today 1y {by['1y']['current']:.1f}, 5y {by['5y']['current']:.1f}; 2008-12 mean 1y {by['1y']['mean_2008_2012']:.1f}, 5y {by['5y']['mean_2008_2012']:.1f}")
