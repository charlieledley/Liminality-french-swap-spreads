# Data inventory and source comparison, 2026-10-05

Four workbooks received from Charlie on 2026-10-05, copied unchanged to `analysis/data/raw/`.
Tidy CSVs are written by `analysis/load_rates.py`. All figures below are from that script's
first run on the raw files, daily data, no adjustments.

## Coverage

| Series | Source | First | Last | Obs |
|---|---|---|---|---|
| 1y / 5y EUR swap vs 6m Euribor (EUSA1, EUSA5) | Bloomberg | 2006-10-05 | 2026-10-02 | 5166 |
| 1y / 5y EONIA OIS (EUSWE1, EUSWE5) | Bloomberg | 2007-01-02 | 2021-12-31 | 3864 |
| 1y / 5y €STR OIS (EESWE1, EESWE5) | Bloomberg | 2007-01-02 | 2026-10-02 | 5064 |
| France generic 1y / 5y (GTFRF1YR, GTFRF5YR) | Bloomberg | 2006-10-05 | 2026-10-02 | 5104 |
| Italy generic 1y / 5y (GTITL1YR, GTITL5YR) | Bloomberg | 2006-10-05 | 2026-10-02 | 5112 |
| 1y €STR par OIS | Citi | 2019-10-01 | 2026-10-04 | 1829 |
| 5y €STR par OIS | Citi | 2007-10-04 | 2026-10-04 | 4909 |
| 1y / 5y EONIA par OIS | Citi | 2010-11-26 / 2007-10-04 | 2025-09-08 / 2025-08-15 | 3832 / 4611 |
| France / Italy 1y and 5y CMT yield | Citi | 2011-09-22 | 2026-10-03 | 3792 / 3804 |
| EUR 1y / 5y par swap | Citi | 2011-07-06 | 2026-10-02 | 3960 |

Citi stamps some observations on Saturdays and Sundays (2026-10-03, 2026-10-04); Bloomberg
leaves weekend rows blank. Joins are on date after dropping blank rows.

## Findings

**1. Bloomberg's €STR OIS series already contains the 8.5bp splice.** EESWE1 and EESWE5 run
from 2007-01-02, two and a half years before €STR existed. Over 2007 to 2021, EONIA OIS minus
€STR OIS on Bloomberg is 8.50bp with a standard deviation of 0.12bp, every year. Bloomberg has
back-filled €STR as EONIA less 8.5bp, which is exactly option A of decision 0003. The script
therefore uses EESWE directly and does not shift it again. The Citi series do not embed it.

**2. Citi's 1y EUR par swap is on a 3-month Euribor basis, as Charlie suspected.** Citi 1y
minus Bloomberg EUSA1 (6m basis) averages -9.8bp, never positive in a sustained way, and tracks
the 3m/6m basis (-27bp in 2011-12, -3bp in 2021, -11bp in 2026). Citi's 5y par swap matches
EUSA5 to 0.1bp, so the 5y is on the 6m basis. Bloomberg is used for both Euribor swap tenors.

**3. Citi's 5y €STR history before 2013 is not €STR.** Citi 5y €STR minus Bloomberg EESWE5 is
17 to 37bp in 2007 to 2012 and 0.1bp from 2013 on. Citi's own EONIA 5y minus €STR 5y is
negative before 2013, which cannot be. Whatever Citi back-filled there, it is not an OIS rate
on either fixing. Bloomberg is the OIS source for the whole history.

**4. Where the sources should agree, they do.** €STR 1y Citi vs Bloomberg: -0.1bp mean,
1.0bp standard deviation. EONIA 1y and 5y: 0.0bp mean. Citi EONIA minus €STR in 2019 to 2025:
8.5bp. The two providers are reading the same market for the OIS and 6m swap legs.

**5. Sovereign yields differ by construction, not by error.** Citi's constant-maturity (CMT)
yields against Bloomberg's generic benchmark bond yields:

| Point | Mean diff (bp) | Std (bp) | Worst years |
|---|---|---|---|
| France 1y | -3.2 | 6.7 | 2023: -16.8; 2011: +14.2 |
| France 5y | -1.2 | 6.0 | 2011-12: +10; 2018: -6.1 |
| Italy 1y | +3.4 | 8.5 | 2011: +20.7; 2013: +10.1 |
| Italy 5y | +3.7 | 7.6 | 2015-18: +8 to +12 |

A generic benchmark is one actual bond whose maturity drifts between rolls; a CMT yield is
fitted to exactly the tenor. The 1y point is where the drift matters most, and the 1y point is
the axis of the scenario slide. Which to use is decision 0004 (proposed).

**6. Moving from Euribor to €STR shifts the spread level by the basis.** On 2026-10-02:

| Point | OAT yield | 6m Euribor swap | €STR OIS | Spread vs Euribor | Spread vs €STR |
|---|---|---|---|---|---|
| 1y | 3.311 | 3.304 | 2.896 | -1bp | -41bp |
| 5y | 4.332 | 3.501 | 3.177 | -83bp | -115bp |

The draft deck's chart (-78bp at 5.4y, -4bp at 1y vs Euribor) is consistent with the Euribor
columns. On the €STR basis the whole history sits lower by the 6m Euribor / €STR basis, which
Bloomberg puts at 28bp today and 55 to 95bp in 2008 to 2012. Percentile ranks move with it.
This is the footnote decision 0003 asks for, and it is not a small one in the 2008-2012 window.

**7. The bond file (received later on 2026-10-05).** FRTR 3¼ 02/25/2032, Bloomberg mid yield
daily from 2026-05-15 (102 observations) and mid z-spread from 2026-07-14 (60 observations).
The z-spread is against the 6m Euribor swap curve, bond minus swap: it equals bond yield minus
the Bloomberg 5y 6m-Euribor swap to -1.3bp mean, 3.2bp standard deviation, while against €STR
OIS it would read 31bp wider. On 2026-10-02 the z-spread is 82bp; on the deck's basis (swap
minus bond, €STR OIS) the same bond is at about -115bp. The bond yields 9bp more than the Citi
5y CMT yield on average (1.5bp standard deviation), which is the 5.4-year versus 5-year
maturity pickup, and 2bp more than the Bloomberg 5y generic, which suggests the generic is this
bond or its neighbour. The 2026-10-05 row repeats the 2026-10-02 values and is treated as not
yet updated.

Sign convention throughout: swap minus bond, so a cheap OAT reads negative (decision 0002,
decided 2026-10-05).
