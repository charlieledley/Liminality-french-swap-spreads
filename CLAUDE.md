# CLAUDE.md — Liminality French swap spreads

Read this first in every session. It holds the conventions for this repo; the personal rules
are in the global `~/.claude/CLAUDE.md`. Longer explanations live in `docs/decisions/` and the
memory folder. When a rule here and a decision file disagree, the decision file wins and this
file needs updating.

## What this repo is

The investor deck for a French swap-spread investment: a 4-year-expiry option on a ~5-year
OAT swap spread (long FRTR 3¼ 02/25/32, pay fixed on a 6m Euribor swap, 4-year non-recourse TRS
financing at €STR + 17bp), rolling into the 1-year point. The deliverable is a `.pptx` on
Jeff's template (since 2026-10-07; the put-writing house format before), built by script from analysis in this repo. Charlie's draft
of 2026-10-04 is in `docs/drafts/` and the plan that maps it onto the house format is
`docs/deck-plan-2026-10-04.md`.

- **The scenario analysis is on the 6m Euribor swap basis** (decision 0003, revised
  2026-10-05 evening), matching the trade and Charlie's IRR/MOIC spreadsheet. Working assumption:
  every spread chart in the deck is on the same basis, footnoted with the €STR financing leg and
  the current Euribor/€STR basis. The €STR OIS construction (Bloomberg EESWE, which embeds the
  8.5bp EONIA splice) is kept in `analysis/` and the workbook as the cross-check. Both bases are
  built by `analysis/spread_history.py`; `PRIMARY_BASIS` names the one the deck reads.
- **IRR and MOIC come from Charlie's spreadsheet**, not from this repo. The deck reads the uploaded
  output from `deck/data/` and states the model's inputs (floor, leverage, rate level, fee basis)
  beside the numbers. Do not rebuild the IRR engine here unless asked.
- The US belly deck in the draft is not an appendix; its slides are raw material to repurpose.
- **Spread sign is swap minus bond**: a cheap OAT reads negative (decided 2026-10-05).
- **Sovereign yields: Bloomberg generic benchmarks throughout** (decision 0004, reversed
  2026-10-05 evening after the CMT 1y read 6.6bp off the terminal on the quoted day). The 5y
  generic is the trade's own bond. Citi CMT stays as the `*_cmt_bp` cross-check. The OIS leg is
  Bloomberg EESWE throughout, which already embeds the 8.5bp splice.
- **Percentile window starts 2010-01-01** (decision 0005): the whole euro sovereign crisis,
  not the 2007-09 money-market blow-out. The draft's 2012 window is kept for comparison only.
- Still unconfirmed in `docs/decisions/0002-research-question.md`: the spreadsheet's inputs
  (floor, leverage, rate level, fee basis). Do not build a figure on an unconfirmed one without
  saying so.

- `analysis/` holds every script behind a quoted number. `analysis/data/` holds hand-supplied
  Bloomberg pulls (tracked, metered, with a `source` column). `analysis/_cache/` is ignored.
- `deck/` holds the builder, `dsl.py` (design system), `qa.py` (geometry QA), logos and
  `deck/data/` JSON written by `analysis/` scripts. Built decks go to `exports/`.
- `exports/` is the gitignored drop for `.pptx` and `.xlsx` deliverables.
- `tests/` pins any figure that will be quoted again. Empty until there is one.
- `tools/bbg-pull/` is a copy of the personal `bbg-pull` skill so the repo carries it.

## Environment

- Python lives in `.venv\Scripts\python.exe` (3.12). Packages are listed in `requirements.txt`;
  `blpapi` installs from Bloomberg's own index (command in that file). Do not install one-off
  tooling into it; use `pip install --target=<scratch>/pylibs` and `PYTHONPATH`.
- Bloomberg Desktop API is available on this PC through the `bbg-pull` skill. A missing series
  is a question for Charlie, not a reason to proxy or truncate.
- Tests: `.venv\Scripts\python.exe -m pytest` from the repo root. There is no CI.

## Git

- `main` is the integration branch; work on feature branches.
- Remote `origin` is Charlie's personal GitHub account (added and pushed 2026-10-09).
  **Never push without being asked, and only ever to Charlie's personal account.**
- Several Claude sessions may share this working tree. Before `git add`, run `git status` and
  stage only the files you changed, by path.
- `.claude/` is gitignored, so settings are per machine.
- Backup: `tools/backup-to-onedrive.ps1` runs hourly from the Windows scheduled task
  "Liminality french-swap-spreads backup to OneDrive" and copies the repo (minus `.venv` and
  caches) and this project's Claude transcript and memory folder into
  `OneDrive - Liminality Capital LP\Liminality-french-swap-spreads-backup-current\`. Copy-only,
  never deletes. Log is `backup.log` in that folder. Set up 2026-10-04, mirroring the
  put-writing repo's job.

## Where things go

- Anything needed to reproduce a number goes in the repo under `analysis/`, never in a
  scratchpad or temp folder. Two scratchpads have already been lost on the sibling project.
- Decisions that change a number, a method or a convention get a file in `docs/decisions/` at
  the time they are made. Numbered in the order opened; status proposed / decided / superseded.
- Reusable output templates go in personal skills at `~/.claude/skills/` (currently
  `xlsx-report`, `bbg-pull`, `checkpoint`). Check there before building a formatter.

## Naming

- Files and handles: what it is plus an ISO date or a version handle. Never `final`, `alt`,
  `v2`, `new`, `fixed` in a name. Good: `oat_swap_spread_history_2026-10-04.csv`.

## Measurement conventions (carried over from the sibling repo, each one has bitten there)

- **Total return series for every comparison.** Never benchmark against a price index.
- **Calendar-year mark-to-market for option P&L.** Never attribute by entry year.
- **Reporting window is a choice, not a by-product.** State the window with every figure.
- **Monthly joins use PeriodIndex.** Bloomberg stamps last trading day, pandas last calendar
  day; joining on timestamps drops months silently.
- **State the provenance of every number** in the message: window, real / re-run / proxied,
  and the script or cache that produced it.
- Swap-spread sign and quoting convention (bond yield minus swap rate, or the reverse; which
  swap curve, €STR or 6m Euribor) must be fixed in a decision file before the first chart.

## Deck

- Build with `python-pptx` through `deck/dsl.py`; every number on a slide comes from a JSON in
  `deck/data/` written by an `analysis/` script. No literal figures in slide prose.
- Charts are native wherever the data is ours. A pasted picture is only for a third-party chart
  (Polymarket, a bank research chart) and carries its source on the slide.
- Anything on a slide for Charlie rather than an investor goes through `internal_note()`;
  `INTERNAL_NOTES = False` strips them for the external build.
- No process language on investor slides ("earlier draft", "prior version", "what changed").
- **One function per slide, running order in a list** (since 2026-10-07, decision 0008): `ORDER` at
  the foot of `deck/build_deck.py` is the deck; `CUT` holds pages kept as raw material and not
  built. Pages are never deleted from the builder: add the name back to `ORDER` to restore one.
  `DECK_ALL=1` builds every page in the old 23-slide order. Shared data loads sit above the first
  slide function; a slide function only reads globals.
- **The deck is on Jeff's template** (decided 2026-10-07, decision 0008): `deck/dsl.py` opens
  `deck/template-liminality-2026-10-07.pptx` (his master, scaled to 13.33 x 7.5in), body pages use
  his "Title and Content" layout (navy band with the title placeholder and the subtitle inside the
  band, his logo bottom left), Garamond throughout. Slide functions keep their old content
  coordinates; the primitives shift them down by `SHIFT` to clear the band, and `raw=True` on
  `tbox` places a shape at its literal y (title zone, footnotes, page number). Footnotes live in the
  lane right of the logo (`FOOT_X`, `FOOT_W`). Garamond text metrics carry a width safety factor.
- **Two builds from one builder** (decision 0009, 2026-10-08): `DECK_MODE=memo` (default, the full
  text, to send out) and `DECK_MODE=outline` (Jeff's lean wording, to present). Pages with text
  variants branch on `OUTLINE`; figures come from the same JSON in both. Rebuild means both files.
- The forward-price view (`analysis/forward_price.py`, `deck/data/forward_price_2026-10-05.json`):
  the bond financed at EUR STR + 17bp, compounded, coupons reinvested; bond-only gains. Jeff's
  figures and the reconciliation are in decision 0009.
- Every page that quotes a hypothetical return carries the `HYPO` sentence in its footnote
  (Charlie, 2026-10-07); the investment is "the structure" (a total return swap with a floor), not
  "the option"; the premium is the floor's cost, part of the structure.
- Charlie sends edits by the slide numbers of the deck he has open; read them that way. Hold
  the rebuild until he says rebuild, then build once, run `deck/qa.py`, render with LibreOffice
  (`C:\Program Files\LibreOffice\program\soffice.exe`, rasterise with `pypdfium2`), look at
  the changed pages and send.
- **Check chart pages through PowerPoint itself** (PowerShell COM export of the slide to PNG)
  before sending: LibreOffice and PowerPoint disagree on details that matter. Bitten 2026-10-05:
  date axes rendered four years late in PowerPoint because python-pptx writes no `c:date1904`
  element; `xy_chart` now writes it. A QA build to a scratch path uses `DECK_OUT=<path>`.
- State the honest limit of a claim in the slide body, not a footnote.

## Output

- Tables and comparisons ship as `.xlsx` via the `xlsx-report` skill into `exports/`. No
  hand-rolled openpyxl, no bare CSV as a deliverable.
- Run the `checkpoint` skill at the end of every milestone and before closing a session.
