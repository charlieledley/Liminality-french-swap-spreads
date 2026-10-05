# Scenario points for the IRR / MOIC slide (opened 2026-10-05, window revised the same day)

Status: points set by Claude from the Euribor-basis history on the 2010 window (decision 0005);
Charlie to read IRR and MOIC from the spreadsheet at each point, or share the model so the grid
is run from the repo.

All levels are the **at-expiry 1-year France swap spread, versus the 6m Euribor swap, swap
minus bond, bp** (decisions 0002 and 0003), from `analysis/spread_history.py` on data to
2026-10-02, Citi CMT yields from 2011-09-22 and Bloomberg generics before (decision 0004),
percentiles since 2010-01-01 (decision 0005). Negative = OAT cheap to swaps.

## Named scenarios (the slide's labelled rows)

| # | Scenario | At-expiry 1y spread | Where it comes from |
|---|---|---|---|
| S1 | Richer than history: 90th percentile since 2010 | +64 | 1y ladder, p90 |
| S2 | Median since 2010 (the draft's "50th percentile") | +30 | 1y ladder, p50 |
| S3 | 10th percentile since 2010 | +12 | 1y ladder, p10 |
| S4 | Roll to spot, nothing changes: the bond rolls to a 1y spread of -1.3bp | -1.3 | Charlie's model: interpolated to the bond's maturity at expiry, not the +6bp 1y CMT point (2026-10-05) |
| S5 | Cheapest 1y since 2010 | -2 | 1y ladder, min (2025-01-03) |
| S6 | No roll: the bond's spread stays where it is today | -83 | FRTR 3¼ 02/25/32 today |
| S7 | 5y point at its euro-crisis low | -91 | 5y ladder since 2010, min (2011-11-16) |
| S8 | Italy, November 2011, 1y point | -556 | Italy 1y, 2010-13 min (2011-11-09) |
| B/E | Investment break-even | **-445** | solved in Charlie's model, 2026-10-05 |
| 100% | Full impairment at expiry | **-572** | solved in Charlie's model, 2026-10-05 |

**Returns received 2026-10-05** in `analysis/model/french_ss_details_and_returns_2026-10-05.xlsx`,
ingested by `analysis/scenario_returns.py` into `deck/data/scenario_irr_moic_2026-10-05.json`.

S2, S4 and S6 are the three rows the draft already carries (43%, 42%, 36% in the draft, on an
unknown construction). S8 is the stress analogue the draft's slide 8 placeholder asked for.
The 2012 window would have given S1 +60, S2 +28, S3 +11, S7 -76; the change from 2010 is small
at the 1y point and large at the 5y low.

## Grid for the IRR and MOIC curve (the chart behind the rows)

Read IRR and MOIC at each of these, so the slide can show a line rather than a few dots:

```
+64  +40  +30  +20  +12  +6  0  -25  -50  -75  -91  -100  -150  -200  -300  -400  -500  -556  -600
```

plus the two solved levels (break-even, full impairment). Nineteen reads and two solves.

## What the spreadsheet should return for each point

IRR (annualised, 4 years), MOIC (multiple of invested capital), and once, the model's inputs
as used: entry spread and date, financing spread over €STR, floor strike, leverage or capital
per unit of notional, the rate level assumed, fee basis (gross or net), and the day-count or
compounding convention for the IRR. These go on the slide next to the table (decision 0002).

## Alternative: run the grid from the repo

If the workbook is shared (copied into `analysis/model/` or left in the OneDrive folder with
its path given), the grid can be run here against the live model, either by replicating the
calculation in `analysis/scenario_irr.py` and tying it to the spreadsheet's own numbers, or by
driving Excel on this PC through COM automation so the workbook itself does the arithmetic.
Which of the two depends on the size of the model and is decided after reading it.
