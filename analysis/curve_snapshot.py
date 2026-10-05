# -*- coding: utf-8 -*-
"""One-day snapshot of the French sovereign curve against the 6m Euribor swap curve.

Source: analysis/data/raw/oat_curve_vs_euribor6m_swaps_2026-10-02_bbg.xlsx, Charlie's Bloomberg
export received 2026-10-05, as of Friday 2026-10-02: the I14 EUR France sovereign curve and the
S45 EUR (vs 6m Euribor) swap curve, 1y to 30y, plus Bloomberg's own spread column (S45 less I14,
bp, the deck's swap-minus-bond sign). The 1y row is two rows in the export (12M swap, 1Y bond);
they are merged here and the spread computed, which Bloomberg left blank for that tenor.

The 5y point of the sovereign curve (4.326%) is the FRTR 3.25 02/25/2032 yield, so the curve's
5y spread (-82.5bp) is the bond's. Writes the tidy CSV and deck/data/curve_<date>.json for the
what-is-a-swap-spread page.
"""
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ASOF = "2026-10-02"
RAW = os.path.join(HERE, "data", "raw", f"oat_curve_vs_euribor6m_swaps_{ASOF}_bbg.xlsx")
CSV = os.path.join(HERE, "data", f"oat_curve_vs_euribor6m_swaps_{ASOF}_bbg.csv")
JSON = os.path.join(HERE, "..", "deck", "data", f"curve_{ASOF}.json")
YEARS = {"12M": 1, "1Y": 1, "2Y": 2, "3Y": 3, "4Y": 4, "5Y": 5, "6Y": 6, "7Y": 7, "8Y": 8, "9Y": 9, "10Y": 10,
         "15Y": 15, "20Y": 20, "25Y": 25, "30Y": 30}


def build():
    d = pd.read_excel(RAW, header=0).iloc[:, 1:]
    d.columns = ["tenor", "oat_yield", "swap_rate", "bbg_spread_bp"]
    d["years"] = d["tenor"].map(YEARS)
    g = d.groupby("years").agg(oat_yield=("oat_yield", "max"), swap_rate=("swap_rate", "max"),
                               bbg_spread_bp=("bbg_spread_bp", "max")).reset_index()
    g["spread_bp"] = (g["swap_rate"] - g["oat_yield"]) * 100
    chk = (g["spread_bp"] - g["bbg_spread_bp"]).abs().max()
    assert chk < 0.05, f"recomputed spread differs from Bloomberg's by {chk:.3f}bp"
    g["source"] = "Bloomberg I14 (France sovereign) and S45 (EUR vs 6m Euribor) curves, exported by Charlie, as of %s" % ASOF
    g.to_csv(CSV, index=False, float_format="%.4f")
    out = {"asof": ASOF, "sign": "swap minus bond, bp", "swap_curve": "EUR vs 6m Euribor (Bloomberg S45)",
           "sovereign_curve": "France (Bloomberg I14)", "years": g["years"].tolist(),
           "oat_yield_pct": g["oat_yield"].round(4).tolist(), "swap_rate_pct": g["swap_rate"].round(4).tolist(),
           "spread_bp": g["spread_bp"].round(2).tolist(),
           "note": "1y spread computed (Bloomberg's export left it blank); the 5y sovereign point is the FRTR 3.25 02/25/2032 yield."}
    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    return g


if __name__ == "__main__":
    g = build()
    print(g[["years", "oat_yield", "swap_rate", "spread_bp"]].to_string(index=False))
    print("wrote", os.path.relpath(CSV, os.path.join(HERE, "..")), "and", os.path.relpath(JSON, os.path.join(HERE, "..")))
