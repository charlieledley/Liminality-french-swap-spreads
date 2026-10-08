# 0009 · Two builds of one deck (memo and outline); the forward-price view of the return

**Status:** proposed 2026-10-08 (Charlie: colleagues find the deck "more of a memo deck to send out for
people to read, too much on the page for a presentation"; Jeff drafted a leaner outline version and
three alternatives to the "where the return comes from" page; "help me edit and conform the two
decks; his numbers are slightly different than mine").

## Decision

1. **One builder, two builds.** `DECK_MODE=memo` (the default) builds the full-text deck;
   `DECK_MODE=outline` builds the presentation version with Jeff's shortened wording (received
   2026-10-08 as `docs/drafts/deck-jeff-outline-edit-v2-received-2026-10-08.pptx`, with Charlie's own
   small changes). Every figure on both comes from the same JSON, so the two cannot disagree on a
   number. Output files: `exports/Liminality_French_Swap_Spreads_memo_<date>.pptx` and
   `..._outline_<date>.pptx`. Pages whose text differs by mode carry both variants in the slide
   function (`OUTLINE` branches); pages with charts only are identical.
2. **The forward-price view** (Jeff's versions 2, 3 and 4) is rebuilt from the repo's data in
   `analysis/forward_price.py`, which writes `deck/data/forward_price_2026-10-05.json`:
   - the bond's clean price on the trade date (Bloomberg) plus accrued, financed at a flat term rate
     of EUR STR OIS interpolated to the expiry tenor plus the 17bp funding spread, compounded annually
     to the model's expiry (2031-02-25), coupons received reinvested at the same rate;
   - the forward clean price is the all-in cost of the bond at expiry; the bond then has one year
     left and is worth (100 + coupon) / (1 + y);
   - expiry yields are today's 1-year 6m Euribor swap (the curve assumed unchanged) less each named
     scenario spread; the forward row uses the 4.4y1y forward swap from the par curve;
   - the gain is "just the bonds": the floor's cost, the swap's own P&L, the floating-leg basis and
     bid-offer are not in it; the model's break-even nets all of them.
3. **The three candidate pages are built in both decks after the existing page 9**, titled
   "version 2/3/4" as Jeff had them, for Charlie to choose from; the losers come out of `ORDER`.

## Reconciliation with Jeff's figures (his pages 9 to 11 of 2026-10-08)

| Item | Jeff | Repo | Why they differ |
|---|---|---|---|
| Financing rate | 3.33% (EUR STR + 17bp) | 3.30% (OIS 3.13% interpolated to expiry + 17bp) | same construction; his EUR STR point is the 5-year 3.17%, ours is interpolated to the 4.4-year expiry. Charlie first thought the forward should be at EUR STR alone (3.17%) and then agreed with Jeff that the all-in financing rate belongs in it (2026-10-08) |
| Forward date | 2/20/2031 | 2/25/2031 | the model's expiry is the coupon date |
| Forward clean price | 94.72 | 94.39 | compounding: his figure is reproduced to 0.1 point by simple interest on the dirty price with the coupons taken at face (94.8), the usual repo-forward quote; the repo compounds the financing and reinvests the coupons, which is what a 4.4-year TRS at daily EUR STR does |
| Forward-implied 1-year yield | 8.93% | 9.38% | follows from the forward price |
| 4.4y1y forward swap | 3.52% | 3.52% | same |
| Spot 1-year swap at expiry | 3.33% | 3.30% | ours is the Bloomberg 1-year 6m Euribor swap on the trade date |
| Forward-implied spread | −540bp | −586bp | follows from the above |
| Roll to spot | −3bp | −1.3bp | the model's interpolated 1-year point (decision 0002) |
| Gain, roll to spot | +€5.2m | +€5.5m | lower forward price here |
| Gain, break-even | +€1.0m | +€1.4m | same; less the floor's 0.84% leaves 0.16 (Jeff) or 0.59 (repo) points for the swap P&L, basis and bid-offer |
| Basis on the return page | 33bp (4.4y) | 32bp (5y) | his interpolated to the expiry tenor; ours the 5-year point in the data |

The compounding convention is the one that matters and is Charlie's to confirm against his
model: his spreadsheet's break-even of −445bp reconciles more closely with a simple-interest
forward (residual 0.16 points after the floor's cost) than with the compounded one (0.59 points).
Until he says, the pages show the repo's construction and the footnote states it.

## Consequences

- Two files in `exports/` per rebuild; the edits log records which mode an edit applies to.
- `docs/drafts/deck-as-sent-to-jeff-2026-10-08.pptx` is the memo build Jeff worked from.
