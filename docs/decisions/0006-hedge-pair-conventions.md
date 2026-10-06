# 0006 · The low-coupon / high-coupon OAT pair: sizing, recovery and carry assumptions

**Status:** decided 2026-10-05 (Charlie, in chat, rounds 3 to 5).

## The pair

Buy FRTR 0½ 05/25/2040, sell FRTR 4½ 04/25/2041 (Charlie's idea). On 2026-10-02 the two yielded
within 2.3bp of each other while the low coupon traded at 59% of the high coupon's price. If the
market prices an actual sovereign default, bonds trade on price rather than yield and the two
converge; the pair pays.

## Conventions

| Item | Decision | Alternative kept in the data |
|---|---|---|
| Sizing | **DV01-neutral**: 1.41 face of the 0½ per 100 face of the 4½ sold (DV01 0.0689 vs 0.0969 per 100 face) | equal face; equal market value |
| Recovery for the headline | **75**, both bonds converging to a price of 75 | ladder 90 to 40 shown on the page |
| Durations | computed from the quoted yields, annual coupons, ACT/ACT, settlement 2026-10-05; the computed clean prices tie to the quoted ones within 0.006 | Bloomberg's own durations, not pulled |
| Carry | total-return carry of each leg (yield × market value), not coupon only | coupon-only gap also in the JSON |
| Excess cash | the 15.5 of market value released (94 sold less 78 bought) earns **2.2%**, €STR less a spread (Charlie) | |
| Bid-offer | **10 through the middle** on the pair, taken as **0.08 points a year** over the hold (Charlie) | |
| All-in carry | 0.81 − 0.34 + 0.08 = **0.55 points a year** per 100 sold | |

All in `analysis/hedge_pair.py`; inputs transcribed from Charlie's Bloomberg screen
(`analysis/data/hedge_pair_2026-10-02.csv`), histories pulled through the Desktop API
(`analysis/data/hedge_pair_history_bbg_2026-10-05.csv`).

## What it changes

The appendix hedge page: +46 points per 100 sold at a 75 recovery (+27 long, +19 short), positive
at any common price down to 40, carry about 0.55 a year. The page lives in the appendix because
Charlie's view is that the floor already provides the hedge and this is optional.
