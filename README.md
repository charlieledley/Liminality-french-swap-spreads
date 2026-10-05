# Liminality French swap spreads

Investor deck and supporting analysis for a French OAT vs Euribor swap-spread investment.
Initialised 2026-10-04. Scope and open conventions: `docs/decisions/0002-research-question.md`;
deck plan: `docs/deck-plan-2026-10-04.md`.

## Layout

| Path | What it holds | Tracked |
|---|---|---|
| `analysis/` | scripts behind every quoted number | yes |
| `analysis/data/` | hand-supplied Bloomberg pulls, CSV with a `source` column | yes (metered) |
| `analysis/_cache/` | script caches | no |
| `docs/decisions/` | numbered decision log | yes |
| `exports/` | `.xlsx` deliverables | no |
| `tests/` | pins for quoted figures | yes |
| `deck/` | deck builder, design system, QA script, data JSON | yes |
| `docs/drafts/` | Charlie's draft decks as received | yes |
| `tools/bbg-pull/` | copy of the Bloomberg pull skill | yes |

## Environment

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/ blpapi
.venv\Scripts\python.exe -m pytest
```

Working conventions are in `CLAUDE.md`.
