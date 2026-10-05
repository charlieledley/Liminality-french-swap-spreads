# 0002 · The investment, the research question and the conventions behind the deck

**Status:** proposed 2026-10-04 (Claude, read off Charlie's draft deck of 2026-10-04,
`docs/drafts/investor-deck-draft-received-2026-10-04.pptx`); Charlie to confirm each item.

## The investment, as the draft states it

Buy a 4-year-expiry option on a ~5-year-maturity France vs Euribor swap spread: long the OAT
FRTR 3¼ 02/25/32 against paying fixed on the matching euro swap, financed for four years through
a total return swap at €STR + 17bp, non-recourse through an embedded floor. In 4.4 years the bond
rolls into the ~1-year point of the curve, where the spread has sat near zero for fourteen years
while the 5.4-year point has dislocated to about -78bp (draft slide 5, as at early October 2026).

## The research question

What is the distribution of 4-year IRRs on that package across at-expiry spread levels, where is
break-even and where is 100% impairment, and how does the history of the 1-year OAT/Euribor spread
since 2012 (and Italy in 2011-12 as the stress analogue) locate those levels?

## Conventions to fix before the first chart (each needs Charlie's yes)

| Item | Draft's implicit choice | Alternative | Status |
|---|---|---|---|
| Spread sign | swap minus bond: negative when OATs are cheap to swaps (5.4y at -78bp) | bond minus swap, positive when cheap | **decided 2026-10-05** |
| Swap curve | €STR OIS for the history, EONIA before 2019-10-02; the trade's actual 6m Euribor swap layered in later and footnoted (decision 0003) | 6m Euribor throughout | **decided 2026-10-04** |
| Bond | FRTR 3¼ 02/25/32 | another OAT near 5y | in use; Charlie supplied its history 2026-10-05 |
| History window | from 2012 ("last 14y", percentiles "since 2012") on Citi CMT yields; Bloomberg generics for anything earlier (decision 0004) | from 2007 or 2010 | yields decided 2026-10-05; start date still to confirm |
| Financing | €STR + 17bp for 4 years, TRS | term sheet to confirm | open |
| Floor strike | not stated in the French draft (the US deck used 45bp out of the money) | | **missing** |
| Leverage / notional per unit of capital | not stated (US deck: 50-60x) | | **missing** |
| Rate level for the scenario | not stated | | **missing** |

## Why this needs to be written down

The three headline IRRs in the draft (43% at the 50th-percentile spread, 42% roll to spot,
36% no roll) have no construction behind them in the file. The scenario slide is a picture and a
list of labels. Every figure on the rebuilt deck will come from a script in `analysis/` that
reads the inputs above, so the inputs have to be decided first.

## Update 2026-10-04 (Charlie, in chat)

- The IRRs are calculated in Charlie's spreadsheet, not in this repo. Charlie will upload the
  output; the live Excel model may later be shared for joint work. The deck reads the output
  from `deck/data/`, with the model's inputs recorded beside the numbers. The floor, leverage and
  rate-level rows above are therefore inputs to that spreadsheet, and the deck states them as
  given.
- The scenario page shows **MOIC alongside IRR** at each at-expiry spread level.
- The US belly deck is **not** kept in the appendix. Several of its slides are repurposed
  (what is a swap spread, what is the trade, the TRS diagram, why the dislocation, risks).
- Historical data will arrive from several sources uploaded by Charlie, not a single pull.
