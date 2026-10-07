# analysis/data

Hand-supplied market data. Tracked in git because it is metered or came from sources that
cannot be re-pulled by script. Nothing in here is edited by hand after it lands; a correction is
a new file with a new date.

## Rules

- One series family per file, named `<what>_<source>_<YYYY-MM-DD>.csv` (the date is the date the
  data was received, not the last observation).
- Columns: `date` (ISO), one column per series, plus `source` (the provider and the ticker or
  screen it came from) and `note` where a value is a splice, a proxy or an adjustment.
- Dates are observation dates as the provider stamps them. Monthly joins use PeriodIndex.
- The raw file as received (xlsx, csv, clipboard paste) is kept beside the tidy CSV under
  `raw/`, unchanged, so the tidy file can be audited.

## Files for the swap-spread history (decision 0003), received 2026-10-05

Written by `analysis/load_rates.py` from the four workbooks in `raw/`. Findings on coverage
and source agreement are in `docs/data-inventory-2026-10-05.md`.

| File | Content | Source |
|---|---|---|
| `eur_swaps_1y5y_bbg_2026-10-05.csv` | 1y/5y swap vs 6m Euribor, EONIA OIS, €STR OIS (€STR back-filled as EONIA less 8.5bp before 2019-10-02) | Bloomberg |
| `france_italy_yields_1y5y_bbg_2026-10-05.csv` | France and Italy generic 1y/5y benchmark yields from 2006 | Bloomberg |
| `eur_ois_1y5y_citi_2026-10-05.csv` | 1y/5y €STR and EONIA par OIS (5y €STR unreliable before 2013) | Citi |
| `france_italy_cmt_eur_swaps_1y5y_citi_2026-10-05.csv` | France and Italy 1y/5y CMT yields from 2011-09; EUR par swaps (1y is 3m basis, 5y is 6m basis) | Citi |
| `oat_curve_vs_euribor6m_swaps_2026-10-02_bbg.csv` | One-day snapshot, 2026-10-02: France sovereign curve (I14) and EUR vs 6m Euribor swap curve (S45), 1y to 30y, with the spread; written by `analysis/curve_snapshot.py` | Bloomberg |
| `frtr_3.25_feb2032_yield_zspread_bbg_2026-10-05.csv` | FRTR 3¼ 02/25/2032 mid yield (daily from 2026-05-15) and mid z-spread (from 2026-07-14), z-spread vs the 6m Euribor swap curve, bond minus swap sign | Bloomberg |

| `spain_1y_bbg_2026-10-05.csv` | Spain generic 1y benchmark yield (Bloomberg id YI278613), daily from 2011-10-06; the EUSA1 and spread columns in the export are dropped after a 0.01bp check against the repo's own | Bloomberg |

| `fiscal_eurostat_oecd_bbg_2026-10-05.csv` | Eurostat gross debt and balance (% GDP) for FR, IT, ES, DE, GR (debt only) and OECD net interest (% GDP) for FR, IT, ES, DE, annual 2005-2025, pulled through the Desktop API by `analysis/fiscal.py`; France's ratings in the JSON | Bloomberg (Eurostat, OECD) |
| `hedge_pair_history_bbg_2026-10-05.csv` | Daily yields and prices of FRTR 0½ 2040 and FRTR 4½ 2041 from 2020-10-01, Desktop API pull | Bloomberg |
| `frtr32_price_yield_bbg_2026-10-07.csv` | FRTR 3¼ 02/25/2032 (DK7998596 Govt, ISIN FR0014018OI0): PX_LAST, PX_MID and YLD_YTM_MID, daily 2026-09-25 to 2026-10-07, Desktop API pull for the trade box on slide 4 (price 94.908 and yield 4.326% on the trade date, 2026-10-02) | Bloomberg |
| `hedge_pair_2026-10-02.csv` | FRTR 0½ 05/25/2040 and FRTR 4½ 04/25/2041: price and mid yield on 2026-10-02, transcribed from Charlie's Bloomberg screenshot (`raw/hedge_pair_..._screen_2026-10-02.png`); durations computed in `analysis/hedge_pair.py` | Bloomberg screen, transcribed |

The bond's z-spread is on the opposite sign and the Euribor curve. To put it on the deck's
basis (swap minus bond, €STR OIS) negate it and subtract the 6m Euribor / €STR basis at 5y,
or use bond yield minus `ois_5y` directly; `load_rates.load()` does the latter as
`frtr32_ois_bp` and keeps `frtr32_eur6m_bp` beside it.

The scenario IRRs and MOICs come from Charlie's spreadsheet, not from this folder. Its output
workbook is kept unchanged in `analysis/model/` and ingested by `analysis/scenario_returns.py`
into `deck/data/scenario_irr_moic_<date>.json`, with the model's inputs recorded beside the
numbers.
