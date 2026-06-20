#!/usr/bin/env python3
"""
check_gate.py — Validates that a phase's completion criteria are met.
Returns exit code 0 (gate open) or 1 (gate blocked).

Claude Code calls this at the end of each phase to enforce the
"never pass to N+1 without validating N" rule.
Coverage metrics are captured automatically from coverage.json on each run.

Usage:
    python scripts/check_gate.py survey
    python scripts/check_gate.py map
    python scripts/check_gate.py audit
    python scripts/check_gate.py draft
    python scripts/check_gate.py stabilize
    python scripts/check_gate.py derive
    python scripts/check_gate.py extend
"""
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "session" / "state.db"
COVERAGE_JSON = ROOT / "coverage.json"

def _record_metric(phase: str, key: str, value: float, unit: str = "") -> None:
    """Persist a metric to state.db and refresh context.yaml."""
    if not DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO metrics (phase, key, value, unit) VALUES (?,?,?,?)",
        [phase, key, value, unit],
    )
    conn.commit()
    conn.close()
    # Refresh YAML so next session injection is up to date
    subprocess.run(
        [sys.executable, "scripts/state.py", "export", "yaml"],
        capture_output=True,
        cwd=ROOT,
    )


def _run_pytest_with_coverage(phase: str) -> tuple[int, list[str], float]:
    """Run pytest + coverage JSON, record metrics automatically.

    Returns (exit_code, failure_lines, coverage_pct).
    """
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", str(ROOT / "tests"), "-q",
            "--tb=line",
            f"--cov={ROOT / 'src'}",
            "--cov-report=json",          # → coverage.json at ROOT
            f"--cov-config={ROOT / 'setup.cfg'}" if (ROOT / "setup.cfg").exists() else "--cov-report=json",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    # Parse test counts from output
    total, passing = 0, 0
    for line in result.stdout.splitlines():
        # pytest -q: "5 passed, 2 failed in 0.42s" or "7 passed in 0.42s"
        if "passed" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "passed" and i > 0:
                    try:
                        passing = int(parts[i - 1])
                    except ValueError:
                        pass
                if p in ("failed", "error") and i > 0:
                    try:
                        total += int(parts[i - 1])
                    except ValueError:
                        pass
            total += passing

    # Parse coverage.json
    coverage_pct = 0.0
    if COVERAGE_JSON.exists():
        try:
            data = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
            coverage_pct = round(data["totals"]["percent_covered"], 1)
        except (KeyError, json.JSONDecodeError):
            pass

    # Auto-record metrics
    if DB_PATH.exists():
        _record_metric(phase, "tests_total", total)
        _record_metric(phase, "tests_passing", passing)
        _record_metric(phase, "coverage_pct", coverage_pct, "%")
        print(f"  📊 Metrics recorded: {passing}/{total} tests passing, coverage {coverage_pct}%")

    failures = [l.strip() for l in result.stdout.splitlines() if "FAILED" in l or "ERROR" in l]
    return result.returncode, failures, coverage_pct


# ─── Gate definitions ─────────────────────────────────────────────────────────

def gate_survey() -> list[str]:
    """Survey gate: audit file exists and smells are catalogued."""
    errors = []
    survey_file = ROOT / "logs" / "audit" / "survey.md"
    if not survey_file.exists():
        errors.append("MISSING: logs/audit/survey.md — run /survey first")
    elif survey_file.stat().st_size < 500:
        errors.append("INCOMPLETE: logs/audit/survey.md is too short (< 500 bytes)")

    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        smell_count = conn.execute("SELECT COUNT(*) FROM smells").fetchone()[0]
        conn.close()
        if smell_count < 5:
            errors.append(f"INSUFFICIENT: only {smell_count} smells in DB (minimum 5 expected)")
    else:
        errors.append("MISSING: session/state.db — run: python scripts/init_state.py")

    return errors


def gate_map() -> list[str]:
    """Map gate: map file exists with risk zones."""
    errors = []
    map_file = ROOT / "logs" / "audit" / "map.md"
    if not map_file.exists():
        errors.append("MISSING: logs/audit/map.md — run /map first")
    elif map_file.stat().st_size < 300:
        errors.append("INCOMPLETE: logs/audit/map.md is too short (< 300 bytes)")
    return errors


def gate_audit() -> list[str]:
    """Audit gate: latest.md exists with scoring."""
    errors = []
    latest = ROOT / "logs" / "audit" / "latest.md"
    if not latest.exists():
        errors.append("MISSING: logs/audit/latest.md — run /audit first")
    elif latest.stat().st_size < 500:
        errors.append("INCOMPLETE: logs/audit/latest.md seems empty")
    return errors


def gate_draft() -> list[str]:
    """Draft gate: draft plan + data_contract filled."""
    errors = []
    draft_file = ROOT / "logs" / "audit" / "draft.md"
    if not draft_file.exists():
        errors.append("MISSING: logs/audit/draft.md — run /draft first")
    elif draft_file.stat().st_size < 500:
        errors.append("INCOMPLETE: logs/audit/draft.md is too short")

    contract = ROOT / "prompts" / "data_contract.md"
    if contract.exists():
        content = contract.read_text(encoding="utf-8")
        if "NON DÉFINI" in content or "À remplir" in content:
            errors.append("INCOMPLETE: prompts/data_contract.md still contains placeholder text")
    return errors


def gate_stabilize() -> list[str]:
    """Stabilize gate: all tests must pass on legacy code."""
    errors = []
    tests_dir = ROOT / "tests"

    test_files = list(tests_dir.glob("test_*.py"))
    if not test_files:
        errors.append("MISSING: no test_*.py files in tests/ — run /stabilize first")
        return errors

    conftest = tests_dir / "conftest.py"
    if not conftest.exists():
        errors.append("MISSING: tests/conftest.py — run /stabilize first")

    print("  Running pytest + coverage...")
    exit_code, failures, coverage_pct = _run_pytest_with_coverage("stabilize")

    if exit_code != 0:
        errors.append("FAILING: pytest did not exit 0 — all tests must pass before /derive")
        for f in failures:
            errors.append(f"  → {f}")
    else:
        print(f"  ✅ All tests passing")

    return errors


def gate_derive() -> list[str]:
    """Derive gate: all tests still pass + mypy clean + coverage ≥ 80% + no regression."""
    errors = []

    print("  Running pytest + coverage...")
    exit_code, failures, coverage_pct = _run_pytest_with_coverage("derive")

    if exit_code != 0:
        errors.append("FAILING: pytest — tests broken after /derive")
        for f in failures:
            errors.append(f"  → {f}")

    if coverage_pct < 80:
        errors.append(f"COVERAGE: {coverage_pct}% < 80% minimum required")
    else:
        print(f"  ✅ Coverage: {coverage_pct}%")

    # Regression check — coverage cannot decrease between /derive runs
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        prev = conn.execute(
            "SELECT value FROM metrics WHERE key='coverage_pct' ORDER BY id DESC LIMIT 2"
        ).fetchall()
        conn.close()
        if len(prev) >= 2:
            current_pct, previous_pct = prev[0][0], prev[1][0]
            if current_pct < previous_pct:
                errors.append(
                    f"REGRESSION: coverage dropped {previous_pct:.1f}% → {current_pct:.1f}%"
                    f" — run /doctor before proceeding"
                )

    # mypy
    src_dir = ROOT / "src"
    print("  Running mypy --strict...")
    result_mypy = subprocess.run(
        [sys.executable, "-m", "mypy", str(src_dir), "--strict", "--ignore-missing-imports"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result_mypy.returncode != 0:
        error_lines = [l for l in result_mypy.stdout.splitlines() if "error:" in l]
        errors.append(f"FAILING: mypy --strict ({len(error_lines)} errors)")
        for line in error_lines[:5]:
            errors.append(f"  → {line.strip()}")
        _record_metric("derive", "mypy_errors", len(error_lines))
    else:
        print("  ✅ mypy --strict: clean")
        _record_metric("derive", "mypy_errors", 0)

    return errors


def gate_extend() -> list[str]:
    """Extend gate: all derive modules completed + full test suite green."""
    errors = []
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        open_smells = conn.execute(
            "SELECT COUNT(*) FROM smells WHERE status='open' AND severity IN ('critical','high')"
        ).fetchone()[0]
        conn.close()
        if open_smells > 0:
            errors.append(
                f"OPEN: {open_smells} critical/high smells still open — fix before /extend"
            )
    return errors


# ─── Runner ───────────────────────────────────────────────────────────────────

GATES = {
    "survey":    gate_survey,
    "map":       gate_map,
    "audit":     gate_audit,
    "draft":     gate_draft,
    "stabilize": gate_stabilize,
    "derive":    gate_derive,
    "extend":    gate_extend,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in GATES:
        print(f"Usage: python scripts/check_gate.py <phase>")
        print(f"Phases: {', '.join(GATES.keys())}")
        sys.exit(1)

    phase = sys.argv[1]
    print(f"\n{'='*50}")
    print(f"  Gate check: /{phase}")
    print(f"{'='*50}")

    errors = GATES[phase]()

    if not errors:
        print(f"\n✅ GATE OPEN — /{phase} criteria met. You may proceed to next phase.\n")
        sys.exit(0)
    else:
        print(f"\n🔴 GATE BLOCKED — {len(errors)} issue(s) to resolve:\n")
        for e in errors:
            print(f"  • {e}")
        print(f"\nFix the above before proceeding. Then re-run:\n  python scripts/check_gate.py {phase}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
