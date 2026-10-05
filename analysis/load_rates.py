# -*- coding: utf-8 -*-
"""Load the euro rates and sovereign yield history behind every spread figure.

Raw workbooks (as received from Charlie, 2026-10-05, unchanged) sit in analysis/data/raw/.
This module turns each into a tidy CSV in analysis/data/ with a `source` column, and
exposes `load()` which returns one wide daily DataFrame plus the derived spreads.

Series and tickers
------------------
Bloomberg (BGN):
  EUSA1 / EUSA5         1y / 5y EUR swap vs 6m Euribor, annual fixed
  EUSWE1 / EUSWE5       1y / 5y EONIA OIS            (ends 2021-12-31)
  EESWE1 / EESWE5       1y / 5y EUR STR OIS          (from 2007-01-02: Bloomberg back-fills
                        the pre-October-2019 history as EONIA OIS less 8.5bp; verified to
                        0.1bp against EUSWE in data_inventory_2026-10-05.md)
  GTFRF1YR / GTFRF5YR   France generic 1y / 5y benchmark bond yield
  GTITL1YR / GTITL5YR   Italy generic 1y / 5y benchmark bond yield
Citi (Velocity export):
  EUR EUROSTR 1Y/5Y Par OIS Rate; EUR 1Y/5Y Par OIS Rate (EONIA)
  1Y/5Y FRA and ITA Sovereign CMT Yield; EUR 1Y/5Y Par Swap Rate
  (the Citi 1y par swap is on a 3m Euribor basis, the 5y on 6m: see the inventory note)

Spread sign convention (decision 0002, decided 2026-10-05): swap minus bond, so a cheap OAT
reads negative.

Sovereign yields (decision 0004, decided 2026-10-05): Citi CMT from 2011-09-22, Bloomberg
generic benchmark before that. `load()` builds `fra_1y`, `fra_5y`, `ita_1y`, `ita_5y` that
way and keeps both raw series alongside for the appendix cross-check.

The 8.5bp EONIA splice of decision 0003 is applied in `estr_spliced()` and only used where a
series does not already embed it. Bloomberg EESWE does; Citi's series do not.
"""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
DATA = os.path.join(HERE, "data")
RECEIVED = "2026-10-05"
EONIA_ESTR_BP = 8.5                     # ECB recalibration, EONIA = EUR STR + 8.5bp, from 2019-10-02
ESTR_START = pd.Timestamp("2019-10-02")  # first EUR STR publication

BBG_SWAPS = {"EUSA1 BGN Curncy": "bbg_eur6m_1y", "EUSA5 BGN Curncy": "bbg_eur6m_5y",
             "EUSWE1 Curncy": "bbg_eonia_1y", "EUSWE5 Curncy": "bbg_eonia_5y",
             "EESWE1 BGN Curncy": "bbg_estr_1y", "EESWE5 BGN Curncy": "bbg_estr_5y"}
BBG_GOV = {"GTITL1YR @BGN Corp": "bbg_ita_1y", "GTITL5YR @BGN Corp": "bbg_ita_5y",
           "GTFRF1YR @BGN Corp": "bbg_fra_1y", "GTFRF5YR @BGN Corp": "bbg_fra_5y"}
CITI_OIS = {"EUR EUROSTR 1Y Par OIS Rate": "citi_estr_1y", "EUR EUROSTR 5Y Par OIS Rate": "citi_estr_5y",
            "EUR 1Y Par OIS Rate (EONIA)": "citi_eonia_1y", "EUR 5Y Par OIS Rate (EONIA)": "citi_eonia_5y"}
CITI_GOV = {"1Y FRA Sovereign CMT Yield": "citi_fra_1y", "5Y FRA Sovereign CMT Yield": "citi_fra_5y",
            "1Y ITA Sovereign CMT Yield": "citi_ita_1y", "5Y ITA Sovereign CMT Yield": "citi_ita_5y",
            "EUR 1Y Par Swap Rate": "citi_eur3m_1y", "EUR 5Y Par Swap Rate": "citi_eur6m_5y"}

BBG_BOND = {"FRTR 3 ¼ 02/25/2032 Corp - Mid Yield To Maturity": "frtr32_yield",
            "FRTR 3 ¼ 02/25/2032 Corp - Mid Z-Spread (bp)": "frtr32_zspread_bp"}

FILES = [  # raw file, reader, column map, tidy file stem
    ("frtr_3.25_feb2032_yield_zspread_2026-10-05.xlsx", "bbg", BBG_BOND, "frtr_3.25_feb2032_yield_zspread_bbg"),
    ("estr_eonia_euribor6m_1y5y_bbg_2026-10-05.xlsx", "bbg", BBG_SWAPS, "eur_swaps_1y5y_bbg"),
    ("france_italy_1y5y_bbg_2026-10-05.xlsx", "bbg", BBG_GOV, "france_italy_yields_1y5y_bbg"),
    ("estr_eonia_1y5y_citi_2026-10-05.xlsx", "citi", CITI_OIS, "eur_ois_1y5y_citi"),
    ("france_italy_cmt_euribor_1y5y_citi_2026-10-05.xlsx", "citi", CITI_GOV, "france_italy_cmt_eur_swaps_1y5y_citi"),
]


def _read_bbg(path, colmap):
    d = pd.read_excel(path, header=1).iloc[:, 1:]
    d = d.rename(columns=colmap)
    d["Date"] = pd.to_datetime(d["Date"])
    return d.set_index("Date").sort_index().astype(float)


def _read_citi(path, colmap):
    d = pd.read_excel(path, sheet_name="Data Table")
    d = d[pd.to_datetime(d["Date"], errors="coerce").notna()].copy()   # drops the footer rows
    d["Date"] = pd.to_datetime(d["Date"])
    d = d.rename(columns=colmap)
    return d.set_index("Date").sort_index().astype(float)


def build_tidy(write=True):
    """Read every raw workbook, write one tidy CSV per workbook, return the merged wide frame."""
    frames = []
    for raw, kind, colmap, stem in FILES:
        path = os.path.join(RAW, raw)
        d = (_read_bbg if kind == "bbg" else _read_citi)(path, colmap)
        d = d.dropna(how="all")
        d.index.name = "date"
        if write:
            out = d.copy()
            out["source"] = ("Bloomberg BGN, exported by Charlie" if kind == "bbg"
                             else "Citi Velocity, exported by Charlie")
            out["raw_file"] = raw
            out.to_csv(os.path.join(DATA, f"{stem}_{RECEIVED}.csv"), float_format="%.6f")
        frames.append(d)
    wide = pd.concat(frames, axis=1, sort=True)
    return wide


def estr_spliced(estr, eonia):
    """EUR STR OIS series with EONIA OIS less 8.5bp before EUR STR exists (decision 0003)."""
    pre = eonia[eonia.index < ESTR_START] - EONIA_ESTR_BP / 100.0
    post = estr[estr.index >= ESTR_START]
    return pd.concat([pre, post]).sort_index()


CMT_START = pd.Timestamp("2011-09-22")   # first Citi CMT observation


def sovereign(w, country, tenor):
    """Decision 0004: Citi CMT from 2011-09-22, Bloomberg generic benchmark before. Percent."""
    citi = w[f"citi_{country}_{tenor}"]
    bbg = w[f"bbg_{country}_{tenor}"]
    out = citi.where(w.index >= CMT_START)
    out = out.where(out.notna(), bbg.where(w.index < CMT_START))
    return out


def load(write=False):
    """Wide daily frame of all series plus derived spreads, in percent (yields) and bp (spreads).

    Weekend rows (Citi stamps some) are dropped so the frame is business days only.
    """
    w = build_tidy(write=write)
    w = w[w.index.dayofweek < 5]
    # Bloomberg's EESWE already embeds the 8.5bp splice back to 2007; keep it as the primary OIS.
    for t in ("1y", "5y"):
        w[f"ois_{t}"] = w[f"bbg_estr_{t}"]
        for c in ("fra", "ita"):
            w[f"{c}_{t}"] = sovereign(w, c, t)
            # Swap minus bond, bp. Negative = sovereign cheap to swaps.
            w[f"{c}_ois_{t}_bp"] = (w[f"ois_{t}"] - w[f"{c}_{t}"]) * 100
            w[f"{c}_eur6m_{t}_bp"] = (w[f"bbg_eur6m_{t}"] - w[f"{c}_{t}"]) * 100
            # Bloomberg-generic construction kept for the appendix cross-check
            w[f"{c}_ois_{t}_bbggeneric_bp"] = (w[f"ois_{t}"] - w[f"bbg_{c}_{t}"]) * 100
        w[f"eur6m_ois_basis_{t}_bp"] = (w[f"bbg_eur6m_{t}"] - w[f"ois_{t}"]) * 100
    # The actual bond, on the deck's basis (swap minus bond). Its Bloomberg z-spread is bond
    # minus the 6m Euribor curve, so the sign flips and the basis moves it (inventory finding 7).
    w["frtr32_ois_bp"] = (w["ois_5y"] - w["frtr32_yield"]) * 100
    w["frtr32_eur6m_bp"] = (w["bbg_eur6m_5y"] - w["frtr32_yield"]) * 100
    return w


if __name__ == "__main__":
    w = load(write=True)
    cov = pd.DataFrame({"first": w.apply(lambda s: s.first_valid_index()),
                        "last": w.apply(lambda s: s.last_valid_index()),
                        "n": w.notna().sum()})
    print(cov.to_string())
    cols = ["fra_ois_1y_bp", "fra_ois_5y_bp", "ita_ois_1y_bp", "ita_ois_5y_bp",
            "fra_eur6m_1y_bp", "fra_eur6m_5y_bp", "eur6m_ois_basis_1y_bp", "eur6m_ois_basis_5y_bp"]
    print("\nlast observations (bp, swap minus bond):")
    print(w[cols].dropna(how="all").iloc[-5:].round(1).to_string())
    print("\naround the CMT join (2011-09-22), France 1y spread, decided vs Bloomberg-generic construction:")
    j = w.loc["2011-09-15":"2011-09-29", ["fra_ois_1y_bp", "fra_ois_1y_bbggeneric_bp"]]
    print(j.round(1).to_string())
