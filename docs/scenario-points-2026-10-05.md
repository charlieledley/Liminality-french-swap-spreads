# Scenario points for the IRR / MOIC slide (opened 2026-10-05, revised the same evening)

Status: rows set with Charlie on 2026-10-05. Returns are from Charlie's spreadsheet
(`analysis/model/french_ss_details_and_returns_2026-10-05.xlsx`), ingested by
`analysis/scenario_returns.py` into `deck/data/scenario_irr_moic_2026-10-05.json`.

All levels are the **at-expiry 1-year France swap spread, versus the 6m Euribor swap, swap
minus bond, bp** (decisions 0002 and 0003), from `analysis/spread_history.py` on data to
2026-10-02, Citi CMT yields from 2011-09-22 and Bloomberg generics before (decision 0004),
percentiles since 2010-01-01 (decision 0005). Negative = OAT cheap to swaps. IRR and MOIC are
gross of fees; where a level is off the spreadsheet's grid the return is linearly interpolated
between the two nearest grid points.

## The slide's rows

| # | Scenario | Spread | What it rests on |
|---|---|---|---|
| S1 | Median since 2010 | +30 | 1y ladder, p50 |
| S2 | 10th percentile since 2010 | +12 | 1y ladder, p10 |
| S3 | Roll to spot: the bond rolls to a 1y spread of -1.3bp, within 1bp of the 1y point's cheapest since 2010 | -1.3 | Charlie's model (interpolated to the bond's maturity at expiry); 1y low -2.0 on 2025-01-03 |
| S4 | No roll: the bond's spread stays at -83bp, within 8bp of the 5y point's euro-crisis low | -83 | FRTR 3¼ 02/25/32 on 2026-10-02; 5y low -91 on 2011-11-16 |
| S5 | Italy's 2011 crisis level: the 1y point was below -350bp on only 29 trading days, 4 Nov to 14 Dec 2011 | -350 | Italy 1y vs Euribor, 2010-13 |
| B/E | Investment break-even | -445 | solved in Charlie's model |
| S6 | Italy's 1y point at its euro-crisis low, 9 November 2011 | -556 | Italy 1y min 2010-13 |
| 100% | Full impairment at expiry | -572 | solved in Charlie's model |

## Rows removed or merged on 2026-10-05 (Charlie)

- 90th percentile since 2010 (+64bp): dropped.
- Cheapest 1y since 2010 (-2bp): merged into roll-to-spot; the two are 0.7bp apart.
- 5y point at its euro-crisis low (-91bp): merged into no-roll; 8bp and 0.5pp of IRR apart.

## The Italy -350bp row, checked against the data

Charlie recalled that Italy's 1y spread was below -350bp for only about 45 days in late 2011.
On the deck's basis (vs 6m Euribor) it was below -350bp on **29 trading days, 2011-11-04 to
2011-12-14**, about six calendar weeks, and never outside that window in the whole 2006-2026
history. Below -300bp: 38 days, the last on 2012-07-25. Below -400bp: 23 days. On the €STR
basis the count is 59 trading days, stretching to 2012-07-25, because the Euribor / OIS basis
was near 100bp at the time. Italy's 5y point spent far longer below -350bp (134 trading days
on the Euribor basis, October 2011 to September 2012), which is why the 1y point is the
relevant one for a bond that has rolled to one year.

## Grid for the IRR and MOIC curve

The spreadsheet carries IRR and MOIC at:

```
+64 +40 +30 +20 +12 +6 0 -25 -50 -75 -91 -100 -150 -200 -300 -400 -445 -500 -556 -572
```

-350 (S5) and -1.3 (S3) are interpolated. If Charlie reads the model at -350 and -1.3 directly,
`scenario_returns.py` will pick up the exact values from the grid instead.

## What the slide states beside the table (model inputs, decision 0002)

Trade date 2026-10-02, option expiry 2031-02-25 (4.4 years), financing €STR + 17bp, floor 30bp
below the at-the-money forward spread, 1.1m of capital including the option premium per 100m of
bond notional, gross of fees. IRR and MOIC are one horizon apart (IRR = MOIC^(1/4.42) - 1).
