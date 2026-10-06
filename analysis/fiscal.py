# -*- coding: utf-8 -*-
"""Fiscal background for the French credit-risk section (slides 12 to 15), pulled from the terminal.

Bloomberg Desktop API, pulled 2026-10-05. Annual series, calendar years, latest full year 2025:
  EUDB60xx Index   Eurostat general government gross debt, % of GDP      (FR, IT, ES, DE, GR)
  EUBDxxxx Index   Eurostat general government balance, % of GDP         (FR: EUBDFRAN, IT: EUBDITAL, ES: EUBDSPAI, DE: EUBDGERM, GR: EUBDGREE)
  OEEOxxPV Index   OECD Economic Outlook net government interest payments, % of GDP (FR, IT, ES, DE)
Ratings: reference fields on FRTR 3.25 02/25/32 Govt (S&P local-currency issuer, Moody's long-term,
Fitch long-term where the field answers).

Writes analysis/data/fiscal_eurostat_oecd_bbg_2026-10-05.csv (tidy, with source) and
deck/data/fiscal_2026-10-05.json. Re-run to refresh after a Eurostat release (April and October).
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "skills", "bbg-pull"))
import bbg  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ASOF = "2026-10-05"
CSV = os.path.join(HERE, "data", f"fiscal_eurostat_oecd_bbg_{ASOF}.csv")
JSON = os.path.join(HERE, "..", "deck", "data", f"fiscal_{ASOF}.json")
DEBT = {"FR": "EUDB60FR Index", "IT": "EUDB60IT Index", "ES": "EUDB60ES Index", "DE": "EUDB60DE Index", "GR": "EUDB60GR Index"}
BAL = {"FR": "EUBDFRAN Index", "IT": "EUBDITAL Index", "ES": "EUBDSPAI Index", "DE": "EUBDGERM Index", "GR": "EUBDGREE Index"}
INT = {"FR": "OEEOFRPV Index", "IT": "OEEOITPV Index", "ES": "OEEOESPV Index", "DE": "OEEODEPV Index"}
RATING_FIELDS = ["RTG_SP_LT_LC_ISSUER_CREDIT", "RTG_SP_OUTLOOK", "RTG_MOODY_LONG_TERM", "RTG_FITCH_LONG_TERM",
                 "RTG_FITCH_LT_ISSUER_DEFAULT", "RTG_FITCH_OUTLOOK"]


def pull():
    s = bbg.session()
    cols, src = {}, {}
    for fam, tick, label in ((DEBT, "debt_pct_gdp", "Eurostat gross debt % GDP"), (BAL, "balance_pct_gdp", "Eurostat balance % GDP"),
                             (INT, "net_interest_pct_gdp", "OECD net interest % GDP")):
        for cc, t in fam.items():
            ser, errs = bbg.history(s, t, "PX_LAST", "20050101", "20261005", period="YEARLY")
            if errs or not len(ser):
                print("  no data:", t, errs)
                continue
            ser.index = ser.index.year
            cols[f"{cc}_{tick}"] = ser
            src[f"{cc}_{tick}"] = f"{t} ({label})"
    df = pd.DataFrame(cols)
    df.index.name = "year"
    ref, errs = bbg.reference(s, ["FRTR 3.25 02/25/32 Govt"], RATING_FIELDS)
    ratings = {k: v for k, v in ref.get("FRTR 3.25 02/25/32 Govt", {}).items() if v}
    return df, src, ratings


def build():
    df, src, ratings = pull()
    out = df.copy()
    out["source"] = "Bloomberg Desktop API pulled %s by Claude; tickers: %s" % (ASOF, "; ".join(f"{k}={v}" for k, v in src.items()))
    out.to_csv(CSV, float_format="%.2f")
    last = int(df.index.max())
    j = {"asof": ASOF, "latest_year": last, "sources": src, "ratings_frtr": ratings,
         "years": [int(y) for y in df.index],
         "series": {c: [None if pd.isna(v) else round(float(v), 2) for v in df[c]] for c in df.columns},
         "latest": {c: (None if pd.isna(df[c].iloc[-1]) else round(float(df[c].iloc[-1]), 1)) for c in df.columns},
         "greece_peak": {"debt_pct_gdp": round(float(df["GR_debt_pct_gdp"].max()), 1), "year": int(df["GR_debt_pct_gdp"].idxmax())}
         if "GR_debt_pct_gdp" in df else None}
    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(j, f, indent=1)
    return df, j


if __name__ == "__main__":
    df, j = build()
    print(df.loc[2010:].round(1).to_string())
    print("ratings:", j["ratings_frtr"])
    print("Greece peak:", j["greece_peak"])
    print("wrote", os.path.relpath(CSV, os.path.join(HERE, "..")), "and", os.path.relpath(JSON, os.path.join(HERE, "..")))
