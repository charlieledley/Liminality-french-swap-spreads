# 0001 · Repo layout and conventions

**Status:** proposed 2026-10-04 (Claude, at initialisation); Charlie to confirm or amend.

## Decision

The repo follows the layout of `C:\Liminality-put-writing-strategy`, so that the two projects
read the same way and the personal skills (`xlsx-report`, `bbg-pull`, `checkpoint`) work in
both without changes:

- `analysis/` for every script behind a quoted number; `analysis/data/` for metered Bloomberg
  pulls (tracked); `analysis/_cache/` for regenerable caches (ignored).
- `exports/` for `.xlsx` deliverables (ignored, because Office rewrites workbook metadata on
  every open and committed workbooks churn forever).
- `docs/decisions/` for this log. `tests/` for figure pins.
- `tools/bbg-pull/` carries a copy of the Bloomberg skill so the repo is self-contained.
- Python 3.12 virtual environment in `.venv`, packages in `requirements.txt`, `blpapi` from
  Bloomberg's index.
- `main` is the integration branch. Remote `origin` is Charlie's personal GitHub account,
  added 2026-10-09 (it was "no remote until Charlie names one" from initialisation).

## What was deliberately left out

- No `.githooks/pre-commit` pin yet: there is no figure to pin. Add it with the first test.
- No research scope: that is decision 0002, to be written in the first working session. The
  swap-spread sign convention and the swap curve (€STR vs 6m Euribor) belong in it.

## Alternatives considered

A flat folder with scripts at the root would be quicker to start but has already cost rework
on the sibling project once outputs, caches and data mixed. Mirroring the existing layout costs
nothing now.
