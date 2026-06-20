# Jacky Chaning The Legacy

> **Chaning** = *chaining* Claude's reasoning steps through a legacy Flask monolith — Jackie Chan style.  
> Not a vibe-coding experiment — a disciplined, state-driven workflow.

[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-orange)](https://fchehidi.github.io/Jacky-Chaning-The-Legacy-/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Anthropic-D97757?logo=anthropic&logoColor=white)](https://docs.anthropic.com/en/docs/claude-code)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What this is

A complete runtime built **around** Claude Code to refactor a 367-line Flask legacy app with intentional security smells (SQL injection, MD5 passwords, no auth on admin routes, hardcoded secrets).

The rule: **never touch `src/` before `/stabilize` completes with all tests green.**

---

## Project structure

```
src/app.py              ← legacy Flask monolith (the target)
.claude/commands/       ← 9 slash commands (the REPL interface)
scripts/                ← state machine CLI, gates, dashboard, audit tools
prompts/                ← Claude persona + coding conventions
session/                ← context.yaml (auto-generated) + state.sql (committed)
logs/audit/             ← per-phase audit outputs
tests/                  ← populated by /stabilize
docs/                   ← GitHub Pages dashboard
CLAUDE.md               ← project brain — read at every session start
Makefile                ← all dev operations
```

---

## The 7 phases

| Phase | Command | Gate |
|---|---|---|
| 1 | `/survey` | smells catalogued in DB |
| 2 | `/map` | risk zones documented |
| 3 | `/audit` | OWASP score recorded |
| 4 | `/draft` | interface contracts written |
| 5 | `/stabilize` | pytest green + coverage ≥ 80% |
| 6 | `/derive` | refactor module by module |
| 7 | `/extend` | new features post-refactor |

Transversal: `/compact` (session compression) · `/doctor` (blocker diagnosis)

---

## Quickstart

```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Initialize state DB
make state-init

# 3. Pre-flight check
make verify

# 4. Open Claude Code and run /survey
```

> Windows: requires GNU make via `winget install GnuWin32.Make`

---

## Key design decisions

- **SQLite state machine** — 7 tables tracking phases, smells, decisions, metrics, session continuity
- **YAML context injection** — ~422 tokens injected at every session start, auto-generated from DB
- **Phase gates** — `check_gate.py` validates exit criteria before any phase transition
- **Option B git strategy** — `state.db` excluded, `session/state.sql` committed (human-readable)
- **Regression detection** — `gate_derive` checks coverage can't decrease between sessions
- **Context budget** — `make budget` audits token costs per file and per phase

---

## Make targets

```bash
make verify          # pre-flight check (33 verifications)
make status          # current phase + summary
make smells          # open smells
make dashboard       # inter-session metrics trends
make budget          # token cost audit
make gate-<phase>    # validate phase exit criteria
make dump            # export DB to session/state.sql + context.yaml
make test            # run pytest
make check           # lint + mypy --strict
```

---

## The legacy smells (intentional)

| Smell | Location | Severity |
|---|---|---|
| SQL injection | `get_tasks` query builder | 🔴 Critical |
| MD5 password | `register` route | 🔴 Critical |
| Global DB connection | module level `conn` | 🔴 Critical |
| Hardcoded secret key | `app.secret_key` | 🔴 Critical |
| Admin routes no auth | `/admin/users` `/admin/reset` | 🔴 Critical |

---

## Target architecture

```
src/app.py        → create_app() only
src/config.py     · src/db.py
src/models/       user · project · task · comment    (SQLAlchemy)
src/schemas/      user · project · task              (Pydantic)
src/routes/       auth · projects · tasks · admin    (Blueprints)
src/services/     auth · task · project              (business logic)
src/utils/        logger · security
tests/            conftest · test_auth · test_tasks · test_projects · test_admin
```

**Stack:** Flask 3.x · SQLAlchemy 2 · Pydantic 2 · bcrypt · structlog · pytest-cov · mypy --strict · ruff

---

## Current state

```
Phase:   survey → not started
Smells:  5 open / 0 fixed
Tests:   0 (populated by /stabilize)
Coverage: — (no data yet)
```

> State is tracked in `session/state.sql` — regenerate DB with `make state-restore`
