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

## What this changes

- Decision 0002's "swap curve" row: €STR (EONIA before 2019-10-02), 6m Euribor as a later layer.
- Analysis items A1, A2 and A5 in the deck plan are specified against OIS, not Euribor swaps.
