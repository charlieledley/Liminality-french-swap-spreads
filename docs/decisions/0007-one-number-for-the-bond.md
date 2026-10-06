# 0007 · One number for the bond's spread: the model's entry spread

**Status:** decided 2026-10-05 (Charlie, round 2: "we say -83 is the 5y today and the bond is the 5y
at -82; seems odd").

## The problem

Three sources give three readings for the same bond on 2026-10-02, versus the 6m Euribor swap,
swap minus bond: the Bloomberg 5y generic benchmark yield, -83.1bp; the bond's own mid yield,
-82.5bp; the model's entry spread on the matched-maturity swap, -82.9bp. The deck showed two of
them, rounded to -83 and -82, and read as inconsistent.

## Decision

The deck shows **one number for the bond: the model's entry spread, -82.9bp, displayed as -83bp**
(`BOND_BP` in `deck/build_deck.py`). The 5y generic point is this bond, so the 5-year point and the
bond are the same figure. The 1y-to-5y gap (the roll-down available) replaced the duplicate bond
card on the dislocation page.

## Consequences

- Slide 4's bullet reads "83bp", the roll card "+82bp" (-1.3 less -82.9).
- The history charts still plot the generic 5y series, which ends at -83.1bp; the half-basis-point
  difference is invisible at chart scale.
- When the trade date or the model's entry spread changes, `BOND_BP` follows the model file.
