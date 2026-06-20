#!/usr/bin/env python3
"""
metrics_dashboard.py — Inter-session trend visualization.

Reads time-series data from state.db and renders ASCII sparklines
to detect progress, stagnation, and regressions across sessions.

The "slow feedback loop": are we improving session over session?

Usage:
    python scripts/metrics_dashboard.py
    python scripts/metrics_dashboard.py --verbose
    python scripts/metrics_dashboard.py --health     → exits 0 (healthy) or 1 (regression)
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "session" / "state.db"

# Sparkline chars: 8 levels from empty to full
SPARK = " ▁▂▃▄▅▆▇█"


def _conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        print("ERROR: state.db not found. Run: python scripts/init_state.py")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sparkline(values: list[float], width: int = 20) -> str:
    """Render a list of values as an ASCII sparkline."""
    if not values:
        return "─" * width
    if len(values) == 1:
        return "•"

    min_v, max_v = min(values), max(values)
    rng = max_v - min_v or 1

    chars = []
    for v in values[-width:]:  # last N points
        idx = int((v - min_v) / rng * (len(SPARK) - 1))
        chars.append(SPARK[idx])
    return "".join(chars)


def trend_arrow(values: list[float], higher_is_better: bool = True) -> str:
    """Return trend arrow and health signal."""
    if len(values) < 2:
        return "  ·"
    delta = values[-1] - values[-2]
    if abs(delta) < 0.5:
        return " →  (stable)"
    if (delta > 0) == higher_is_better:
        return f" ↑  (+{abs(delta):.1f})"
    return f" ↓  (-{abs(delta):.1f}) ⚠️"


def health_signal(values: list[float], threshold: float, higher_is_better: bool) -> str:
    if not values:
        return "⬜ no data"
    last = values[-1]
    if higher_is_better:
        if last >= threshold:
            return f"🟢 {last:.1f} (≥{threshold})"
        if last >= threshold * 0.85:
            return f"🟡 {last:.1f} (<{threshold})"
        return f"🔴 {last:.1f} (far below {threshold})"
    else:
        if last == 0:
            return f"🟢 {last:.0f}"
        if last <= threshold:
            return f"🟡 {last:.0f}"
        return f"🔴 {last:.0f} (>{threshold})"


def fetch_series(conn: sqlite3.Connection, key: str) -> tuple[list[float], list[str]]:
    """Fetch all recorded values for a metric key, ordered by time."""
    rows = conn.execute(
        "SELECT value, recorded_at FROM metrics WHERE key=? ORDER BY recorded_at",
        [key]
    ).fetchall()
    if not rows:
        return [], []
    values = [r["value"] for r in rows]
    dates = [r["recorded_at"][:10] for r in rows]
    return values, dates


def fetch_snapshot_series(conn: sqlite3.Connection) -> list[dict]:
    """Fetch all compact snapshots ordered by time."""
    rows = conn.execute(
        "SELECT * FROM metrics WHERE key LIKE 'snapshot_%' ORDER BY recorded_at"
    ).fetchall()
    return [dict(r) for r in rows]


def render_metric_row(
    label: str,
    values: list[float],
    threshold: float,
    higher_is_better: bool,
    unit: str = "",
) -> None:
    spark = sparkline(values)
    arrow = trend_arrow(values, higher_is_better)
    health = health_signal(values, threshold, higher_is_better)
    last = f"{values[-1]:.1f}{unit}" if values else "—"
    print(f"  {label:<22} {spark:<22} {last:>8}   {health}{arrow}")


def render_dashboard(verbose: bool = False) -> bool:
    """Render the full dashboard. Returns True if healthy, False if regression."""
    conn = _conn()

    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  PROJECT JACKY — Metrics Dashboard (inter-session feedback loops)   ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # ── Phase progress ──────────────────────────────────────────────────────
    phases = conn.execute(
        "SELECT name, status FROM phases ORDER BY id"
    ).fetchall()
    icons = {"not_started": "⬜", "in_progress": "🔵", "completed": "✅", "skipped": "⏭️"}
    phase_line = "  ".join(f"{icons.get(p['status'], '?')}{p['name']}" for p in phases)
    print(f"  Phases: {phase_line}")
    print()

    # ── Smell tracking ──────────────────────────────────────────────────────
    open_smells = conn.execute("SELECT COUNT(*) FROM smells WHERE status='open'").fetchone()[0]
    fixed_smells = conn.execute("SELECT COUNT(*) FROM smells WHERE status='fixed'").fetchone()[0]
    total_smells = open_smells + fixed_smells

    if total_smells > 0:
        fix_pct = round(fixed_smells / total_smells * 100)
        bar_len = 30
        filled = int(fix_pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  Smells    [{bar}] {fix_pct}%   {fixed_smells}/{total_smells} fixed")
    else:
        print(f"  Smells    [{'─'*30}] no data yet")
    print()

    # ── Time series metrics ─────────────────────────────────────────────────
    print(f"  {'METRIC':<22} {'TREND (oldest → latest)':<22} {'LAST':>8}   HEALTH")
    print(f"  {'─'*70}")

    regressions = []

    # Coverage
    cov_vals, _ = fetch_series(conn, "coverage_pct")
    render_metric_row("Coverage %", cov_vals, threshold=80, higher_is_better=True, unit="%")
    if len(cov_vals) >= 2 and cov_vals[-1] < cov_vals[-2]:
        regressions.append(f"coverage dropped {cov_vals[-2]:.1f}% → {cov_vals[-1]:.1f}%")

    # Tests passing
    test_vals, _ = fetch_series(conn, "tests_passing")
    render_metric_row("Tests passing", test_vals, threshold=1, higher_is_better=True)
    if len(test_vals) >= 2 and test_vals[-1] < test_vals[-2]:
        regressions.append(f"tests_passing dropped {test_vals[-2]:.0f} → {test_vals[-1]:.0f}")

    # mypy errors
    mypy_vals, _ = fetch_series(conn, "mypy_errors")
    render_metric_row("mypy errors", mypy_vals, threshold=0, higher_is_better=False)
    if len(mypy_vals) >= 2 and mypy_vals[-1] > mypy_vals[-2]:
        regressions.append(f"mypy errors increased {mypy_vals[-2]:.0f} → {mypy_vals[-1]:.0f}")

    # Modules migrated
    mod_vals, _ = fetch_series(conn, "modules_migrated")
    render_metric_row("Modules migrated", mod_vals, threshold=5, higher_is_better=True)

    print()

    # ── Decision velocity ───────────────────────────────────────────────────
    dec_count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    sessions = conn.execute("SELECT COUNT(DISTINCT DATE(created_at)) FROM session_log").fetchone()[0]
    velocity = round(dec_count / max(sessions, 1), 1)
    print(f"  Decisions total: {dec_count}  |  Sessions: {sessions}  |  Velocity: {velocity}/session")
    print()

    # ── Regression report ───────────────────────────────────────────────────
    if regressions:
        print(f"  ⚠️  REGRESSIONS DETECTED ({len(regressions)}):")
        for r in regressions:
            print(f"     • {r}")
        print(f"  → Run /doctor to diagnose")
        print()
    else:
        if cov_vals or test_vals:
            print(f"  ✅ No regressions detected across {max(len(cov_vals), len(test_vals))} data point(s)")
        else:
            print(f"  ⬜ No metric data yet — run /stabilize and /derive to populate")
        print()

    if verbose and (cov_vals or test_vals):
        print(f"  Raw data (last 5 snapshots):")
        for i, (v, d) in enumerate(zip(cov_vals[-5:], _[-5:])):
            print(f"    [{d}] coverage: {v:.1f}%")
        print()

    conn.close()
    return len(regressions) == 0


def main() -> None:
    args = sys.argv[1:]
    verbose = "--verbose" in args
    health_check = "--health" in args

    healthy = render_dashboard(verbose=verbose)

    if health_check:
        sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()
