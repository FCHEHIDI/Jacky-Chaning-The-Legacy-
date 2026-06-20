# Makefile — Project Jacky
# Cross-platform targets for common dev operations
# Usage: make <target>

PYTHON := python
SRC    := src
TESTS  := tests

.DEFAULT_GOAL := help

# ─── Setup ────────────────────────────────────────────────────────────────────

.PHONY: setup
setup: ## Initialize project: create state DB + install deps
	$(PYTHON) scripts/init_state.py
	$(PYTHON) -m pip install -r requirements.txt

.PHONY: verify
verify: ## Pre-flight check — run before opening Claude Code
	$(PYTHON) scripts/verify_env.py

.PHONY: verify-fix
verify-fix: ## Pre-flight check + auto-fix what can be fixed
	$(PYTHON) scripts/verify_env.py --fix

.PHONY: validate-compact
validate-compact: ## Validate context.yaml has all survival fields
	$(PYTHON) scripts/validate_compact.py

.PHONY: state-init
state-init: ## (Re)initialize the SQLite state database
	$(PYTHON) scripts/init_state.py

.PHONY: state-reset
state-reset: ## DANGER: reset all state (phases, decisions, smells, metrics)
	$(PYTHON) scripts/init_state.py --reset

.PHONY: dump
dump: ## Export DB to session/state.sql (commit this file, not state.db)
	$(PYTHON) scripts/state.py export sql
	$(PYTHON) scripts/state.py export yaml

.PHONY: state-restore
state-restore: ## Restore DB from session/state.sql (use after git clone)
	$(PYTHON) scripts/state.py import sql

# ─── State queries ─────────────────────────────────────────────────────────────

.PHONY: status
status: ## Show current phase and summary
	@$(PYTHON) scripts/state.py phase list
	@echo ""
	@$(PYTHON) scripts/state.py export summary

.PHONY: dashboard
dashboard: ## Show inter-session metrics trends (feedback loops)
	$(PYTHON) scripts/metrics_dashboard.py

.PHONY: dashboard-health
dashboard-health: ## Exit 0 if healthy, 1 if regression detected (use in CI)
	$(PYTHON) scripts/metrics_dashboard.py --health

.PHONY: decisions
decisions: ## List all decisions recorded in state.db
	@$(PYTHON) scripts/state.py decision list

.PHONY: budget
budget: ## Show token cost audit for all context files
	$(PYTHON) scripts/context_budget.py --all

.PHONY: budget-phase
budget-phase: ## Show token budget for a specific phase (usage: make budget-phase PHASE=derive)
	$(PYTHON) scripts/context_budget.py $(PHASE)

.PHONY: smells
smells: ## List all open smells
	@$(PYTHON) scripts/state.py smell list --open

.PHONY: metrics
metrics: ## Show all recorded metrics
	@$(PYTHON) scripts/state.py metric show

.PHONY: context
context: ## Regenerate and print session/context.yaml from DB
	@$(PYTHON) scripts/state.py export yaml

# ─── Testing ──────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run full test suite
	$(PYTHON) -m pytest $(TESTS)/ -v

.PHONY: test-fast
test-fast: ## Run tests without verbose output
	$(PYTHON) -m pytest $(TESTS)/ -q

.PHONY: coverage
coverage: ## Run tests with coverage report
	$(PYTHON) -m pytest $(TESTS)/ --cov=$(SRC) --cov-report=term-missing

# ─── Linting / type checking ──────────────────────────────────────────────────

.PHONY: lint
lint: ## Run ruff linter
	$(PYTHON) -m ruff check $(SRC)/

.PHONY: format
format: ## Format code with ruff
	$(PYTHON) -m ruff format $(SRC)/

.PHONY: typecheck
typecheck: ## Run mypy strict type checking
	$(PYTHON) -m mypy $(SRC)/ --strict --ignore-missing-imports

.PHONY: check
check: lint typecheck ## Run all static checks (lint + types)

# ─── Gate validation ──────────────────────────────────────────────────────────

.PHONY: gate-survey
gate-survey: ## Check if /survey phase criteria are met
	$(PYTHON) scripts/check_gate.py survey

.PHONY: gate-map
gate-map: ## Check if /map phase criteria are met
	$(PYTHON) scripts/check_gate.py map

.PHONY: gate-audit
gate-audit: ## Check if /audit phase criteria are met
	$(PYTHON) scripts/check_gate.py audit

.PHONY: gate-draft
gate-draft: ## Check if /draft phase criteria are met
	$(PYTHON) scripts/check_gate.py draft

.PHONY: gate-stabilize
gate-stabilize: ## Check if /stabilize phase criteria are met
	$(PYTHON) scripts/check_gate.py stabilize

.PHONY: gate-derive
gate-derive: ## Check if /derive phase criteria are met
	$(PYTHON) scripts/check_gate.py derive

.PHONY: gate-extend
gate-extend: ## Check if /extend phase criteria are met
	$(PYTHON) scripts/check_gate.py extend

# ─── Utility ──────────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove Python caches and temp files
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]"
	$(PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').glob('export_*.json')]"
	$(PYTHON) -c "import shutil; [shutil.rmtree(d, ignore_errors=True) for d in ['.pytest_cache','.mypy_cache','.ruff_cache','htmlcov']]"

.PHONY: help
help: ## Show this help
	@$(PYTHON) -c "import re; [print(f'  {m.group(1):<22}{m.group(2)}') for line in open('Makefile') for m in [re.match(r'^([a-zA-Z_-]+):.*?## (.+)', line)] if m]"
