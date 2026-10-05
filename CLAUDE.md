# CLAUDE.md — Liminality French swap spreads

Read this first in every session. It holds the conventions for this repo; the personal rules
are in the global `~/.claude/CLAUDE.md`. Longer explanations live in `docs/decisions/` and the
memory folder. When a rule here and a decision file disagree, the decision file wins and this
file needs updating.

## What this repo is

The investor deck for a French swap-spread investment: a 4-year-expiry option on a ~5-year
OAT swap spread (long FRTR 3¼ 02/25/32, pay fixed on a 6m Euribor swap, 4-year non-recourse TRS
financing at €STR + 17bp), rolling into the 1-year point. The deliverable is a `.pptx` in the
house format of the put-writing deck, built by script from analysis in this repo. Charlie's draft
of 2026-10-04 is in `docs/drafts/` and the plan that maps it onto the house format is
`docs/deck-plan-2026-10-04.md`.

- **Historical spreads are OAT vs €STR OIS, with EONIA OIS less 8.5bp spliced in before
  2019-10-02** (decision 0003; the shift is on the swap rate, pre-2019 dates only). The trade's
  own 6m Euribor swap is a later layer. Both substitutions are footnoted on every slide that
  uses the series.
- **IRR and MOIC come from Charlie's spreadsheet**, not from this repo. The deck reads the uploaded
  output from `deck/data/` and states the model's inputs (floor, leverage, rate level, fee basis)
  beside the numbers. Do not rebuild the IRR engine here unless asked.
- The US belly deck in the draft is not an appendix; its slides are raw material to repurpose.
- **Spread sign is swap minus bond**: a cheap OAT reads negative (decided 2026-10-05).
- **Sovereign yields: Citi CMT from 2012, Bloomberg generics before 2011-09-22** (decision
  0004). The OIS leg is Bloomberg EESWE throughout, which already embeds the 8.5bp splice.
- Still unconfirmed in `docs/decisions/0002-research-question.md`: the history start date for
  percentiles (draft says 2012) and the spreadsheet's inputs. Do not build a figure on an
  unconfirmed one without saying so.

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
- No remote yet. **Never add or push to a remote without being asked.**
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
- Charlie sends edits by the slide numbers of the deck he has open; read them that way. Hold
  the rebuild until he says rebuild, then build once, run `deck/qa.py`, render with LibreOffice
  (`C:\Program Files\LibreOffice\program\soffice.exe`, rasterise with `pypdfium2`), look at
  the changed pages and send.
- State the honest limit of a claim in the slide body, not a footnote.

## Output

- Tables and comparisons ship as `.xlsx` via the `xlsx-report` skill into `exports/`. No
  hand-rolled openpyxl, no bare CSV as a deliverable.
- Run the `checkpoint` skill at the end of every milestone and before closing a session.
