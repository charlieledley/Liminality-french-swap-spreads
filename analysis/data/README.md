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

## Expected files for the swap-spread history (decision 0003)

| File | Content | Status |
|---|---|---|
| `oat_yields_*.csv` | OAT yields at the 1y and ~5y points, or FRTR 3¼ 02/25/32 yield and z-spread | awaited from Charlie |
| `estr_ois_*.csv` | €STR OIS swap rates, 1y and 5y, from 2019-10-02 | awaited |
| `eonia_ois_*.csv` | EONIA OIS swap rates, 1y and 5y, before 2019-10-02 | awaited |
| `euribor6m_swap_*.csv` | 6m Euribor swap rates, 1y and 5y (the trade's actual curve, layered in later) | awaited |
| `btp_*.csv` | Italian BTP yields and matching OIS, 2010-2013, for the stress analogue | awaited |

The scenario IRRs and MOICs come from Charlie's spreadsheet, not from this folder. Its output
lands in `deck/data/scenario_irr_moic_<date>.json` (or the workbook itself under `analysis/`
if the model is shared), with the model's inputs recorded beside the numbers.
