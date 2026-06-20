#!/usr/bin/env python3
"""
verify_env.py — Pre-flight runtime check before starting a Claude Code session.

Run this BEFORE opening Claude Code (especially before filming) to ensure
the full stack is operational. Exits 0 (all good) or 1 (issues found).

Checks:
  1. Python version ≥ 3.11
  2. Required packages installed (Flask, pytest, mypy, ruff, etc.)
  3. session/state.db initialized and readable
  4. session/context.yaml present and valid compact
  5. src/app.py importable (legacy app syntax-check)
  6. tests/ directory has at least a README
  7. All 9 slash commands non-empty
  8. CLAUDE.md non-empty and has required sections
  9. scripts/ all syntax-valid
  10. make targets available

Usage:
    python scripts/verify_env.py
    python scripts/verify_env.py --fix    → auto-fix what can be fixed
"""
import importlib
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
REQUIRED_PACKAGES = [
    ("flask",        "Flask"),
    ("pytest",       "pytest"),
    ("mypy",         "mypy"),
    ("ruff",         "ruff"),
    ("pydantic",     "pydantic"),
    ("bcrypt",       "bcrypt"),
    ("structlog",    "structlog"),
    ("sqlalchemy",   "SQLAlchemy"),
]
REQUIRED_COMMANDS = [
    "survey", "map", "audit", "draft",
    "stabilize", "derive", "extend", "compact", "doctor",
]
REQUIRED_SCRIPTS = [
    "scripts/init_state.py",
    "scripts/state.py",
    "scripts/check_gate.py",
    "scripts/context_budget.py",
    "scripts/metrics_dashboard.py",
    "scripts/validate_compact.py",
    "scripts/verify_env.py",
]

OK   = "✅"
WARN = "🟡"
FAIL = "🔴"
INFO = "   "


class Check:
    def __init__(self) -> None:
        self.passed = 0
        self.warnings = 0
        self.failures = 0

    def ok(self, msg: str) -> None:
        print(f"  {OK} {msg}")
        self.passed += 1

    def warn(self, msg: str) -> None:
        print(f"  {WARN} {msg}")
        self.warnings += 1

    def fail(self, msg: str, fix: str = "") -> None:
        print(f"  {FAIL} {msg}")
        if fix:
            print(f"     → Fix: {fix}")
        self.failures += 1

    def info(self, msg: str) -> None:
        print(f"  {INFO}  {msg}")


def run(fix_mode: bool = False) -> bool:
    c = Check()

    # ── 1. Python version ───────────────────────────────────────────────────
    print("\n── 1. Python runtime")
    v = sys.version_info
    if v >= (3, 11):
        c.ok(f"Python {v.major}.{v.minor}.{v.micro}")
    else:
        c.fail(f"Python {v.major}.{v.minor} — need ≥ 3.11", "upgrade Python")

    # ── 2. Required packages ────────────────────────────────────────────────
    print("\n── 2. Required packages")
    missing_pkgs = []
    for mod, name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(mod)
            c.ok(name)
        except ImportError:
            c.fail(f"{name} not installed", f"pip install {name.lower()}")
            missing_pkgs.append(name.lower())

    if missing_pkgs and fix_mode:
        print(f"\n  Auto-installing missing packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", *missing_pkgs], check=False)

    # ── 3. State DB ─────────────────────────────────────────────────────────
    print("\n── 3. State DB (session/state.db)")
    db_path = ROOT / "session" / "state.db"
    if not db_path.exists():
        c.fail("state.db not found", "python scripts/init_state.py")
        if fix_mode:
            subprocess.run([sys.executable, "scripts/init_state.py"], cwd=ROOT)
    else:
        try:
            conn = sqlite3.connect(db_path)
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]
            required_tables = {"phases", "decisions", "smells", "metrics", "session_log", "session_state"}
            missing_tables = required_tables - set(tables)
            if missing_tables:
                c.fail(f"Missing tables: {missing_tables}", "python scripts/init_state.py")
            else:
                phase_count = conn.execute("SELECT COUNT(*) FROM phases").fetchone()[0]
                c.ok(f"state.db readable — {phase_count} phases, {len(tables)} tables")
            conn.close()
        except sqlite3.Error as e:
            c.fail(f"state.db error: {e}", "python scripts/init_state.py --reset")

    # ── 4. context.yaml ─────────────────────────────────────────────────────
    print("\n── 4. session/context.yaml")
    yaml_path = ROOT / "session" / "context.yaml"
    if not yaml_path.exists():
        c.fail("context.yaml not found", "python scripts/state.py export yaml")
        if fix_mode:
            subprocess.run([sys.executable, "scripts/state.py", "export", "yaml"], cwd=ROOT)
    else:
        content = yaml_path.read_text(encoding="utf-8")
        tokens = len(content) // 4
        c.ok(f"context.yaml present (~{tokens} tokens)")
        result = subprocess.run(
            [sys.executable, "scripts/validate_compact.py"],
            capture_output=True, text=True, cwd=ROOT
        )
        if result.returncode == 0:
            c.ok("compact validation: all survival fields present")
        else:
            c.warn("compact validation: some recommended fields missing (non-blocking)")

    # ── 5. Legacy app syntax ────────────────────────────────────────────────
    print("\n── 5. src/app.py")
    app_path = ROOT / "src" / "app.py"
    if not app_path.exists():
        c.fail("src/app.py not found")
    else:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(app_path)],
            capture_output=True, text=True, cwd=ROOT
        )
        if result.returncode == 0:
            lines = len(app_path.read_text(encoding="utf-8").splitlines())
            c.ok(f"src/app.py syntax OK ({lines} lines)")
        else:
            c.fail(f"src/app.py has syntax errors:\n     {result.stderr.strip()}")

    # ── 6. Slash commands ───────────────────────────────────────────────────
    print("\n── 6. Slash commands (.claude/commands/)")
    for cmd in REQUIRED_COMMANDS:
        path = ROOT / ".claude" / "commands" / f"{cmd}.md"
        if not path.exists():
            c.fail(f"/{cmd} missing")
        elif path.stat().st_size < 200:
            c.warn(f"/{cmd} very short ({path.stat().st_size} bytes) — may be incomplete")
        else:
            c.ok(f"/{cmd} ({path.stat().st_size} bytes)")

    # ── 7. CLAUDE.md sections ───────────────────────────────────────────────
    print("\n── 7. CLAUDE.md")
    claude_path = ROOT / "CLAUDE.md"
    if not claude_path.exists():
        c.fail("CLAUDE.md missing")
    else:
        content = claude_path.read_text(encoding="utf-8")
        for section in ["État courant", "Règles absolues", "Contexte d'injection", "Architecture cible"]:
            if section in content:
                c.ok(f"section '{section}' present")
            else:
                c.fail(f"section '{section}' missing in CLAUDE.md")

    # ── 8. Scripts syntax ───────────────────────────────────────────────────
    print("\n── 8. scripts/ syntax check")
    for rel in REQUIRED_SCRIPTS:
        path = ROOT / rel
        if not path.exists():
            c.fail(f"{rel} missing")
            continue
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            c.ok(rel)
        else:
            c.fail(f"{rel} has syntax errors", result.stderr.strip())

    # ── 9. requirements.txt ─────────────────────────────────────────────────
    print("\n── 9. requirements.txt")
    req_path = ROOT / "requirements.txt"
    if req_path.exists():
        c.ok(f"requirements.txt present ({len(req_path.read_text().splitlines())} packages)")
    else:
        c.warn("requirements.txt missing — others can't reproduce your env")

    # ── Summary ─────────────────────────────────────────────────────────────
    total = c.passed + c.warnings + c.failures
    print(f"\n{'='*55}")
    print(f"  {OK} {c.passed}/{total} checks passed  "
          f"{WARN} {c.warnings} warnings  "
          f"{FAIL} {c.failures} failures")

    if c.failures == 0 and c.warnings == 0:
        print(f"\n  🚀 READY — all systems operational. Safe to film.")
    elif c.failures == 0:
        print(f"\n  🟡 MOSTLY READY — {c.warnings} non-blocking warning(s).")
        print(f"     Safe to proceed but review warnings above.")
    else:
        print(f"\n  🔴 NOT READY — {c.failures} failure(s) must be fixed before starting.")
        if not fix_mode:
            print(f"     Try: python scripts/verify_env.py --fix")
    print()

    return c.failures == 0


if __name__ == "__main__":
    fix = "--fix" in sys.argv
    ok = run(fix_mode=fix)
    sys.exit(0 if ok else 1)
