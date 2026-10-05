# 0003 · Swap curve for the historical analysis: €STR, with EONIA spliced in before €STR exists

**Status:** decided 2026-10-04 (Charlie, in chat). Splice adjustment: **option A decided
2026-10-05** (Charlie, in chat): EONIA OIS rates before 2019-10-02 are shifted down by 8.5bp.

## Decision

The historical OAT swap-spread analysis is run against the **€STR OIS curve**. Before €STR data
exists, **EONIA** OIS is substituted. Charlie's reasons:

- The financing leg of the trade is itself €STR-based (TRS at €STR + 17bp), so a €STR spread is
  conceptually the easier one for an investor to follow.
- The actual trade currently contemplates a **6-month Euribor** swap, which the firm prefers
  because 6m Euribor widens against €STR in a stress scenario, which helps the trade. Euribor is
  layered in afterwards as a further step and/or footnoted; it is not the base case of the history.

Both substitutions are footnoted on every slide that uses the series: EONIA for €STR before
€STR exists, and €STR for the 6m Euribor swap the trade actually uses.

Data will come from several sources uploaded by Charlie (not a single Bloomberg pull). Every file
lands in `analysis/data/` with a `source` column; see `analysis/data/README.md`.

## The splice (option A decided 2026-10-05)

€STR was first published on 2 October 2019. From that date until EONIA was discontinued on
3 January 2022, EONIA was fixed by definition as **€STR + 8.5bp**. Two ways to join the series:

| Option | What it does | Effect |
|---|---|---|
| A. Adjusted splice (**decided**) | EONIA OIS rates before 2019-10-02 shifted down by 8.5bp, then €STR OIS from 2019-10-02 | continuous series on an €STR basis; the swap spread before 2019 moves by +8.5bp relative to a raw EONIA spread |
| B. Raw splice | EONIA OIS as published, €STR OIS from 2019-10-02 | an 8.5bp step at the join; the pre-2019 spread is on the EONIA basis the market quoted at the time |

Option A is the recalibration the ECB itself defined, so it is the natural choice when the
question is "where is the €STR spread versus its own history". Option B is what a Bloomberg
chart of the time would have shown. The slide footnote names the adjustment: "OIS leg is €STR;
before 2 October 2019, EONIA OIS less 8.5bp (the ECB's EONIA = €STR + 8.5bp recalibration)."

Implementation rule for `analysis/`: the shift applies to the OIS swap rate, not to the spread,
and only to observations dated before 2019-10-02. Where both EONIA and €STR OIS exist for the
same date (October 2019 to January 2022), €STR is used and EONIA is kept only as a check that
the difference is 8.5bp.

## Update 2026-10-05 (evening): the scenario analysis is on 6m Euribor

**Decided (Charlie, in chat):** the scenario analysis, meaning the IRR and MOIC table and the
1-year percentile ladder its at-expiry spread levels are read against, uses the **6m Euribor
swap** basis, the curve the trade and the spreadsheet are on. On that basis the 1y spread today
is +6bp, its median since 2012 is +28bp, and the 5y point is -71bp (`spread_history.py`,
data to 2026-10-02).

Consequence for the rest of the deck, stated as Claude's working assumption until Charlie says
otherwise: every spread chart in the deck goes on the same Euribor basis, so one number means
one thing throughout, and the footnote says the financing leg is €STR and names the current
Euribor / €STR basis (41bp at 1y, 32bp at 5y). The €STR construction stays in the analysis
and the workbook as the cross-check, and can go in the appendix if wanted. The original
reasoning for €STR (easier to follow because the financing leg is €STR) is answered on the
"what is the trade" slide rather than in the history charts.

## Update 2026-10-05 (later): both bases built in parallel for now

Charlie's IRR and MOIC spreadsheet is built on the 6m Euribor swap, the curve the trade
actually uses, and the choice of basis for the deck's history is not settled. Decision: build
every spread history, percentile ladder and chart **on both bases**, €STR OIS and 6m Euribor,
side by side, until the deck's basis is chosen. `analysis/spread_history.py` produces both;
the workbook and the deck data carry both; nothing is quoted from one without the other being
available. The €STR footnote wording above applies if the €STR basis is chosen; if Euribor is
chosen, the footnote instead names the 6m Euribor swap and that the financing leg is €STR.

## Update 2026-10-05: Bloomberg has already done the splice

Bloomberg's €STR OIS tickers (EESWE1, EESWE5) run from 2007-01-02 and equal the EONIA OIS
tickers (EUSWE1, EUSWE5) less 8.50bp on every day of 2007 to 2021, with a 0.12bp standard
deviation (`docs/data-inventory-2026-10-05.md`, finding 1). That is option A exactly.
`analysis/load_rates.py` therefore uses EESWE as the OIS leg for the whole history and applies
no further shift. The `estr_spliced()` function stays for any series that does not embed it
(Citi's do not). The slide footnote wording above is unchanged, because it describes what the
series is, whichever party did the arithmetic.

## What this changes

- Decision 0002's "swap curve" row: €STR (EONIA before 2019-10-02), 6m Euribor as a later layer.
- Analysis items A1, A2 and A5 in the deck plan are specified against OIS, not Euribor swaps.
