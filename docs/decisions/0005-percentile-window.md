# 0005 · Start date for the percentile ladder on the scenario slide

**Status:** decided 2026-10-05 (Charlie, in chat): the percentile window starts **2010-01-01**,
so it holds the whole euro sovereign crisis (Greece late 2009 to the Draghi speech, July 2012)
and leaves out the 2007-09 money-market blow-out, which Charlie judged unnecessary and
possibly confusing. The draft's 2012 window is kept in the workbook and deck data for comparison
(`ALT_PCT_START`). Claude's proposal below (2012 headline) was superseded by this.

## What the 2010 window gives (Euribor basis, swap minus bond, data to 2026-10-02)

| | 1y | 5y |
|---|---|---|
| Median | +30bp | +17bp |
| 10th percentile | +12bp | -27bp |
| 90th percentile | +64bp | +37bp |
| Cheapest | -2bp (2025-01-03) | -91bp (2011-11-16) |
| Richest | +118bp (2022-09-06) | +79bp (2022-10-10) |
| Today | +6bp, 3.0th percentile | -71bp, 0.2nd percentile |

Two things the 2010 window shows that 2012 hid: the 5y point's cheapest level was November
2011 at -91bp, not January 2012 at -76bp, and today's -71bp is within 20bp of it. And on the
Euribor basis the 1y point never went negative during the sovereign crisis (its low since 2010
is January 2025), whereas on the €STR basis it reached -88bp on 2011-11-24. The gap is the
1y Euribor / €STR basis, near 100bp in late 2011. The slide footnote for the 1y history says
so, because the roll-to-1y argument leans on the 1y point staying anchored.

The yield construction join (2011-09-22, decision 0004) falls inside this window and is
footnoted on the chart.

---

*The proposal as originally written, for the record:*

## What the extra years contain

France 1y spread vs 6m Euribor, swap minus bond, yearly mean (bp), and the 1y Euribor / €STR
basis the same year (`analysis/load_rates.py`, data to 2026-10-02):

| Year | 1y spread, Euribor basis | 1y spread, €STR basis | Euribor / €STR basis |
|---|---|---|---|
| 2007 | +36 | 0 | 36 |
| 2008 | +87 | -8 | 96 |
| 2009 | +61 | -14 | 75 |
| 2010 | +56 | -4 | 60 |
| 2011 | +66 | -8 | 74 |
| 2012 | +61 | -6 | 67 |
| 2013 to 2021 | +17 to +38 | -9 to +19 | 6 to 35 |
| 2022 to 2023 | +56 to +58 | +35 to +39 | 17 to 23 |
| 2024 to 2026 | +7 to +19 | -17 to -2 | 21 to 28 |

On the Euribor basis, 2007 to 2012 shows OATs 60 to 90bp rich to swaps. On the €STR basis the
same years are flat to slightly cheap. The difference is the basis column: in the crisis years
the 6m Euribor swap sat 60 to 96bp above OIS, so a bond measured against it looks rich for a
reason that has nothing to do with France. On the Euribor basis, 42% of 2007-2011 days sit
above the since-2012 90th percentile.

## What the start date does to the ladder (Euribor basis)

| Start | Obs | Median | 10th pct | 90th pct | Max | Today's percentile |
|---|---|---|---|---|---|---|
| 2007 | 4999 | +32 | +13 | +73 | +185 | 2.5% |
| 2010 | 4233 | +30 | +12 | +64 | +118 | 3.0% |
| 2012 | 3721 | +28 | +11 | +60 | +118 | 3.4% |
| 2014 | 3220 | +26 | +9 | +56 | +118 | 3.9% |

Going back further raises the median by 4bp and makes today rarer, not more common. The
conclusion does not change; the median scenario's IRR would move a little.

## Proposal: keep 2012 as the headline window, show 2007 in the appendix

Two reasons that are about the data rather than the chart:

1. **One yield construction.** The sovereign yields switch from Bloomberg generics to Citi CMT
   on 2011-09-22 (decision 0004), with an 11bp step at the join. A ladder from 2012 sits
   entirely on the CMT series; a ladder from 2007 straddles the join.
2. **The Euribor basis blow-out.** Since the scenario analysis is on the Euribor basis (decision
   0003), a 2007 start folds the 2008-2012 Libor/OIS dislocation into the France percentiles.
   That is a euro money-market event, not a French credit event, and it would make the
   "median" scenario a little richer than France's own history supports.

The body of the slide says: "Percentiles since 2012. From 2007 the median is +32bp rather than
+28bp and today's level is rarer." The since-2007 ladder is already in the workbook and the
deck data (`alt_pct_start`), so the appendix costs nothing.

## The alternative

Start in 2007 and take the longer record, on the argument that 2008 and 2011 are exactly the
stress regimes an investor asks about. If so, the chart should show the €STR line too, so the
reader can see how much of the pre-2012 richness is basis. The Italy 2011 stress analogue uses
the full history either way, because that is where the stress is.
