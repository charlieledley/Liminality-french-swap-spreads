# 0004 · Which sovereign yield series the spreads are built on

**Status:** decided 2026-10-05 (Charlie, in chat): Citi CMT yields from 2012, Bloomberg generics
before 2011-09-22, as proposed below.

## The choice

Two series are on hand for the 1y and 5y France and Italy points
(`docs/data-inventory-2026-10-05.md`, finding 5):

| | Bloomberg generic benchmark (GTFRF1YR etc.) | Citi constant-maturity (CMT) |
|---|---|---|
| What it is | the yield of one actual bond, the current benchmark nearest the tenor; its maturity drifts between rolls | a yield fitted to exactly 1y or 5y from the sovereign curve |
| History | from 2006-10-05 | from 2011-09-22 |
| Matches the swap leg | the swap is a par rate at an exact tenor, so a CMT yield is the like-for-like | |
| Differences | mean 1 to 4bp, standard deviation 6 to 8bp, yearly means up to 17bp apart at the 1y point | |
| Covers the Italy 2011 stress | yes, all of it | starts 2011-09-22, after the summer but before the November peak |
| Same provider as the swap legs | yes (Bloomberg) | no |

## Decision (as proposed)

Use the **Citi CMT yields** as the primary series for the spread history from 2012, which is the
window the deck quotes percentiles on, because a constant-maturity yield against a par swap
rate is the spread the trade actually has, and because the 1y point, where generic drift is
worst, is the axis of the scenario slide. Use the **Bloomberg generics** for anything before
2011-09-22 (the Italy stress analogue slide, and any chart that starts in 2007), and say so
on that slide. Show the Bloomberg-generic spread as a second line on the percentile chart in
the appendix so an investor can see the construction does not drive the conclusion.

## The alternative

Bloomberg generics throughout: one provider, one construction, the full window from 2007,
and the series a Bloomberg user would pull to check us. The cost is a few bp of maturity-drift
noise at the 1y point, which widens the percentile bands rather than moving their centre.

## Known step at the join

On 2011-09-22 the France 1y spread vs €STR OIS reads -17.2bp on the Citi CMT yield and -5.6bp
on the Bloomberg generic, so the series steps by about 11bp where the construction changes,
in the middle of the 2011 stress. Any chart that crosses 2011-09-22 states this in its
footnote, and the Bloomberg-generic construction is kept in `load_rates.load()` as
`*_bbggeneric_bp` for the appendix comparison. On 2026-10-02 the France 5y spread is -103bp
on CMT and -115bp on the generic, so the difference is live today too.

## What it changes

Which column `analysis/load_rates.py` maps to `fra_1y` and `fra_5y`, and the footnote on every
spread chart.
