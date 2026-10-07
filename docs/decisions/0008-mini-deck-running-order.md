# 0008 · The mini-deck running order; the template question left open

**Status:** decided 2026-10-07 (Charlie: "Jeff cut the draft down to a mini-deck and made some
other changes. I added back a few slides and created a new one. Help me do another turn.")
Template choice: open (Charlie, same day: "I couldn't quite tell if I like his template better").

## What arrived

Three files, kept in `docs/drafts/`:

- `deck-jeff-edit-v4.2-received-2026-10-07.pptx`: Jeff's 9-slide cut, in a different template
  (10 x 5.625in, navy title band, Garamond, logo bottom left).
- `deck-jeff-turn-charlie-edits-received-2026-10-07.pptx`: Charlie's 13-slide version of it,
  with three of the built pages pasted back (why the dislocation, what is the trade, where the
  return comes from), a `[Risks]` placeholder and a new page on why France will not exit or default.
  This is the running order the builder now follows.
- `deck-proposed-replacements-received-2026-10-06.pptx`: a 12-page "reviewer draft, replacement
  pack" of 6 October, author not stated, with notes on each page. Not asked for; two of its points
  were adopted (below).

## Decision

1. **The builder follows the 13-slide running order** (`ORDER` at the foot of `deck/build_deck.py`):
   title, disclaimer, firm, executive summary, what is a swap spread, the current dislocation, why
   the dislocation, what is the trade, where the return comes from, scenario analysis, Italy and
   Spain in the euro crisis, risks, why no exit or default.
2. **The ten pages Jeff cut stay in the builder as functions** (`CUT`): not a credit spread, France
   is different, fiscal, politics, ECB and EU, base case, and the four appendices. `DECK_ALL=1`
   builds all 23 in the old order for comparison. Nothing is deleted; Charlie can put any page back
   by adding its name to `ORDER`.
3. **Each slide is a function** (`slide_<name>()`), so the order is a list rather than the file's
   layout. The refactor was checked by building all 23 pages and diffing every text run against
   the previous build: identical.
4. **Jeff's page edits are taken as written**: the executive summary's three numbered bullets with
   bold leads and the trade box; the swap-spread page's two statements over side-by-side charts;
   the dislocation page without its cards (today's readings become labels on the lines); the
   scenario page's rows level with its lines, the MOIC column and the 10th-percentile row dropped;
   the stress page's title and subtitle without its cards. The row alignment on the scenario page
   is computed from the axis scale, not placed by hand.
5. **Charlie's wording of 7 October**: "option" becomes "structure" for the investment and
   "floor" for the strike and its cost, because the trade is a total return swap with a floor; the
   premium is part of the structure, not a separate purchase; the non-recourse leverage is in the
   headline wording; and every page that quotes a hypothetical return carries "Please see the
   disclosures page regarding the hypothetical performance results listed above." (pages 4, 9, 10,
   12), with his new disclosure block on page 2.
6. **Two points from the reviewer pack adopted**: the scenario IRR at an off-grid level is now
   derived from the interpolated MOIC with the spreadsheet's own convention, not interpolated
   itself (the −350bp row moves from 14.0% to 14.5%; see `analysis/scenario_returns.py`); and the
   risks page says what the floor does not cover (the counterparty bank in the same crisis).

## Still open

- ~~Template.~~ **Decided 2026-10-07 afternoon: Jeff's band and serif** (Charlie, after the
  side-by-side `exports/template_comparison_2026-10-07.png`). The builder now opens
  `deck/template-liminality-2026-10-07.pptx`, an empty copy of Jeff's master scaled to 13.33 x
  7.5in through PowerPoint, and puts every body page on his "Title and Content" layout: the navy
  band (011C40, 1.68in) carries the title in the placeholder and the subtitle beneath it in the
  band; his logo sits bottom left on the layout; the page number is drawn bottom right. Garamond
  throughout (`HFONT = BFONT`), with a 3.5% width safety in the text metrics because PowerPoint
  sets Garamond a little wider than the TrueType metrics predict. Content coordinates in the slide
  functions are unchanged: the primitives shift them down by `SHIFT = 0.40in` to clear the band
  (`Y()` in `dsl.py`), and footnotes sit in the lane right of the logo. The title page is drawn to
  his (logo on white, navy block below). The old house format is one commit back.
- ~~The trade box on page 4 still carries Jeff's `[EUR x]` and `[EUR y]`.~~ Supplied by Charlie the
  same afternoon, as percent of notional: floor 0.84%, present value of the maximum loss 0.247%,
  total 1.09% (`deck/data/structure_terms_2026-10-07.json`).
- **Page 13's retirement-age bracket** is filled with the Cour des comptes' February 2025 arithmetic
  (65; up to €8.4bn a year by 2035 against a pension-system deficit of €6.6bn in 2024), which covers
  the pension system's own deficit, not the general deficit; the slide and footnote say so.
