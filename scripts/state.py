#!/usr/bin/env python3
"""
state.py — CLI for reading and writing project state to SQLite.
Claude Code uses this to persist phase transitions, decisions, smells and metrics
across sessions without relying on markdown files alone.

Usage:
    python scripts/state.py phase list
    python scripts/state.py phase set <name> <status>
    python scripts/state.py phase current

    python scripts/state.py decision add <phase> <content> [justification]
    python scripts/state.py decision list [phase]

    python scripts/state.py smell add <name> <location> <severity>
    python scripts/state.py smell fix <id> <phase>
    python scripts/state.py smell list [--open|--fixed]

    python scripts/state.py metric record <phase> <key> <value> [unit]
    python scripts/state.py metric show [phase]

    python scripts/state.py log <LEVEL> <message> [phase]

    python scripts/state.py export yaml     → prints context.yaml to stdout
    python scripts/state.py export summary  → prints compact markdown summary
    python scripts/state.py export sql      → writes session/state.sql (commit this file)
    python scripts/state.py import sql      → restores DB from session/state.sql

    python scripts/state.py set next_action "description of next concrete action"
    python scripts/state.py set active_file "src/routes/auth.py"
    python scripts/state.py get next_action
    python scripts/state.py turn            → increment turn counter, warn if compact due
"""
import sqlite3
import sys
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "session" / "state.db"
YAML_PATH = Path(__file__).parent.parent / "session" / "context.yaml"
SQL_PATH = Path(__file__).parent.parent / "session" / "state.sql"

PHASE_ORDER = ["survey", "map", "audit", "draft", "stabilize", "derive", "extend"]


def _conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        print(f"ERROR: state.db not found at {DB_PATH}")
        print("Run: python scripts/init_state.py")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── PHASE ────────────────────────────────────────────────────────────────────

def phase_list() -> None:
    conn = _conn()
    rows = conn.execute(
        "SELECT name, status, started_at, completed_at FROM phases ORDER BY id"
    ).fetchall()
    icons = {"not_started": "⬜", "in_progress": "🔵", "completed": "✅", "skipped": "⏭️"}
    for r in rows:
        icon = icons.get(r["status"], "?")
        print(f"{icon} {r['name']:<12} {r['status']}")
    conn.close()


def phase_set(name: str, status: str) -> None:
    valid = ("not_started", "in_progress", "completed", "skipped")
    if status not in valid:
        print(f"ERROR: status must be one of {valid}")
        sys.exit(1)
    conn = _conn()
    now = datetime.utcnow().isoformat()
    updates: dict = {"status": status}
    if status == "in_progress":
        updates["started_at"] = now
    elif status == "completed":
        updates["completed_at"] = now
    set_clause = ", ".join(f"{k}=?" for k in updates)
    conn.execute(
        f"UPDATE phases SET {set_clause} WHERE name=?",
        [*updates.values(), name]
    )
    conn.commit()
    conn.close()
    _log("INFO", f"Phase '{name}' → {status}", name)
    _update_yaml()
    print(f"✅ phase {name} = {status}")


def phase_current() -> None:
    conn = _conn()
    row = conn.execute(
        "SELECT name, status FROM phases WHERE status='in_progress' LIMIT 1"
    ).fetchone()
    if row:
        print(f"🔵 {row['name']} (in_progress)")
    else:
        row = conn.execute(
            "SELECT name FROM phases WHERE status='not_started' ORDER BY id LIMIT 1"
        ).fetchone()
        if row:
            print(f"⬜ next: {row['name']} (not_started)")
        else:
            print("✅ all phases completed")
    conn.close()


# ─── DECISIONS ────────────────────────────────────────────────────────────────

def decision_add(phase: str, content: str, justification: str = "") -> None:
    conn = _conn()
    conn.execute(
        "INSERT INTO decisions (phase, content, justification) VALUES (?,?,?)",
        [phase, content, justification]
    )
    conn.commit()
    conn.close()
    _log("DECISION", content, phase)
    _update_yaml()
    print(f"✅ decision recorded in phase {phase}")


def decision_list(phase: str | None = None) -> None:
    conn = _conn()
    if phase:
        rows = conn.execute(
            "SELECT id, phase, content, justification, created_at FROM decisions WHERE phase=? ORDER BY id",
            [phase]
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, phase, content, justification, created_at FROM decisions ORDER BY id"
        ).fetchall()
    for r in rows:
        print(f"[{r['id']}] [{r['phase']}] {r['content']}")
        if r["justification"]:
            print(f"      → {r['justification']}")
    conn.close()


# ─── SMELLS ───────────────────────────────────────────────────────────────────

def smell_add(name: str, location: str, severity: str) -> None:
    valid = ("critical", "high", "medium", "low")
    if severity not in valid:
        print(f"ERROR: severity must be one of {valid}")
        sys.exit(1)
    conn = _conn()
    conn.execute(
        "INSERT INTO smells (name, location, severity) VALUES (?,?,?)",
        [name, location, severity]
    )
    conn.commit()
    conn.close()
    _log("RISK", f"Smell catalogued: {name} @ {location} ({severity})", "survey")
    _update_yaml()
    print(f"✅ smell added: {name} ({severity})")


def smell_fix(smell_id: int, phase: str) -> None:
    conn = _conn()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE smells SET status='fixed', fixed_in=?, fixed_at=? WHERE id=?",
        [phase, now, smell_id]
    )
    conn.commit()
    conn.close()
    _log("DONE", f"Smell #{smell_id} fixed in phase {phase}", phase)
    _update_yaml()
    print(f"✅ smell #{smell_id} marked as fixed")


def smell_list(filter_status: str | None = None) -> None:
    conn = _conn()
    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    fix_icon = {"open": "⬜", "fixed": "✅", "wontfix": "🚫"}
    query = "SELECT id, name, location, severity, status FROM smells"
    params: list = []
    if filter_status:
        query += " WHERE status=?"
        params = [filter_status]
    query += " ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END"
    rows = conn.execute(query, params).fetchall()
    for r in rows:
        sev = icons.get(r["severity"], "?")
        sta = fix_icon.get(r["status"], "?")
        print(f"{sta} [{r['id']:>2}] {sev} {r['name']:<35} @ {r['location']}")
    print(f"\nTotal: {len(rows)}")
    conn.close()


# ─── METRICS ──────────────────────────────────────────────────────────────────

def metric_record(phase: str, key: str, value: float, unit: str = "") -> None:
    conn = _conn()
    conn.execute(
        "INSERT INTO metrics (phase, key, value, unit) VALUES (?,?,?,?)",
        [phase, key, value, unit]
    )
    conn.commit()
    conn.close()
    _update_yaml()
    print(f"✅ metric: {phase}.{key} = {value} {unit}")


def metric_show(phase: str | None = None) -> None:
    conn = _conn()
    query = "SELECT phase, key, value, unit, recorded_at FROM metrics"
    params: list = []
    if phase:
        query += " WHERE phase=?"
        params = [phase]
    query += " ORDER BY recorded_at DESC"
    rows = conn.execute(query, params).fetchall()
    for r in rows:
        unit = f" {r['unit']}" if r["unit"] else ""
        print(f"[{r['phase']}] {r['key']} = {r['value']}{unit}  ({r['recorded_at'][:10]})")
    conn.close()


# ─── LOG ──────────────────────────────────────────────────────────────────────

def _log(level: str, message: str, phase: str | None = None) -> None:
    conn = _conn()
    conn.execute(
        "INSERT INTO session_log (level, message, phase) VALUES (?,?,?)",
        [level, message, phase]
    )
    conn.commit()
    conn.close()


def log_write(level: str, message: str, phase: str | None = None) -> None:
    valid = ("INFO", "DECISION", "WARN", "RISK", "DONE")
    if level not in valid:
        print(f"ERROR: level must be one of {valid}")
        sys.exit(1)
    _log(level, message, phase)
    print(f"✅ [{level}] logged")


# ─── EXPORT ───────────────────────────────────────────────────────────────────

def _update_yaml() -> None:
    """Write compact YAML context snapshot from current DB state."""
    conn = _conn()

    # Phase info
    in_progress = conn.execute(
        "SELECT name FROM phases WHERE status='in_progress' LIMIT 1"
    ).fetchone()
    current_phase = in_progress["name"] if in_progress else "none"

    phases = conn.execute(
        "SELECT name, status FROM phases ORDER BY id"
    ).fetchall()

    # Recent decisions (last 5)
    decisions = conn.execute(
        "SELECT phase, content, justification FROM decisions ORDER BY id DESC LIMIT 5"
    ).fetchall()

    # Smell counts
    smell_open = conn.execute("SELECT COUNT(*) FROM smells WHERE status='open'").fetchone()[0]
    smell_fixed = conn.execute("SELECT COUNT(*) FROM smells WHERE status='fixed'").fetchone()[0]

    # Latest metrics
    test_total = _latest_metric(conn, "tests_total") or 0
    test_pass = _latest_metric(conn, "tests_passing") or 0
    coverage = _latest_metric(conn, "coverage_pct") or 0
    modules_done = _latest_metric(conn, "modules_migrated") or 0
    modules_total = _latest_metric(conn, "modules_total") or 5

    # Open risks
    risks = conn.execute(
        "SELECT message FROM session_log WHERE level='RISK' ORDER BY id DESC LIMIT 3"
    ).fetchall()

    conn.close()

    lines = [
        f"# context.yaml — auto-generated by state.py — do NOT edit manually",
        f"snapshot: \"{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}\"",
        "",
        "phase:",
        f"  current: {current_phase}",
        "  all:",
    ]
    for p in phases:
        icon = {"not_started": "-", "in_progress": ">", "completed": "x", "skipped": "s"}.get(p["status"], "?")
        lines.append(f"    [{icon}] {p['name']}")

    # Session continuity — the 3 fields that make a compact truly useful
    conn2 = sqlite3.connect(DB_PATH)
    conn2.row_factory = sqlite3.Row
    next_action = conn2.execute(
        "SELECT value FROM session_state WHERE key='next_action'"
    ).fetchone()
    active_file = conn2.execute(
        "SELECT value FROM session_state WHERE key='active_file'"
    ).fetchone()
    turn_count = conn2.execute(
        "SELECT value FROM session_state WHERE key='turn_count'"
    ).fetchone()
    compact_threshold = conn2.execute(
        "SELECT value FROM session_state WHERE key='compact_every_n_turns'"
    ).fetchone()
    conn2.close()

    turns = int(turn_count[0]) if turn_count else 0
    threshold = int(compact_threshold[0]) if compact_threshold else 15
    turns_until_compact = threshold - (turns % threshold) if turns % threshold != 0 else 0

    lines += [
        "",
        "# --- SESSION CONTINUITY (critical for cold-start) ---",
        f"next_action: \"{next_action[0] if next_action else 'run /survey'}\"",
        f"active_file:  \"{active_file[0] if active_file else 'src/app.py'}\"",
        f"turn_count: {turns}",
        f"compact_due: {'true  # ⚠️ run /compact now' if turns_until_compact == 0 and turns > 0 else f'false  # {turns_until_compact} turns remaining'}",
        "",
    ]

    lines += ["decisions_recent:"]
    for d in decisions:
        lines.append(f"  - phase: {d['phase']}")
        lines.append(f"    what: \"{d['content']}\"")
        if d["justification"]:
            lines.append(f"    why: \"{d['justification']}\"")

    lines += [
        "",
        "smells:",
        f"  open: {smell_open}",
        f"  fixed: {smell_fixed}",
        "",
        "tests:",
        f"  total: {int(test_total)}",
        f"  passing: {int(test_pass)}",
        f"  coverage_pct: {coverage}",
        "",
        "progress:",
        f"  modules_migrated: {int(modules_done)}",
        f"  modules_total: {int(modules_total)}",
        "",
        "risks:",
    ]
    for r in risks:
        lines.append(f"  - \"{r['message']}\"")

    # Knowledge stack — derived artifacts that progressively replace raw code.
    # Each phase output is denser than its input: src/app.py (3224 tokens)
    # is eventually replaced by draft.md (~500 tokens of distilled knowledge).
    knowledge_files = [
        ("src/app.py",           "raw legacy code"),
        ("logs/audit/survey.md", "derived: smell inventory"),
        ("logs/audit/map.md",    "derived: dependency map"),
        ("logs/audit/latest.md", "derived: technical scoring"),
        ("logs/audit/draft.md",  "derived: refactor plan"),
    ]
    lines += ["", "knowledge_stack:"]
    for rel, label in knowledge_files:
        path = YAML_PATH.parent.parent / rel
        if path.exists() and path.stat().st_size > 10:
            tokens = max(1, int(len(path.read_text(encoding="utf-8", errors="ignore")) / 3.8))
            lines.append(f"  [x] {rel:<35} # ~{tokens} tokens — {label}")
        else:
            lines.append(f"  [ ] {rel:<35} # missing — {label}")

    lines += [
        "",
        "# context_profiles: which files to inject per phase",
        "context_profiles:",
        "  survey:    [CLAUDE.md, context.yaml, system.md, src/app.py]",
        "  map:       [CLAUDE.md, context.yaml, system.md, survey.md]",
        "  audit:     [CLAUDE.md, context.yaml, system.md, survey.md, map.md]",
        "  draft:     [CLAUDE.md, context.yaml, system.md, conventions.md, data_contract.md, latest.md]",
        "  stabilize: [CLAUDE.md, context.yaml, system.md, draft.md, src/app.py]",
        "  derive:    [CLAUDE.md, context.yaml, system.md, conventions.md, coding_standards.md, data_contract.md, latest.md, draft.md]",
        "  compact:   [CLAUDE.md, context.yaml, history.md]",
        "  doctor:    [CLAUDE.md, context.yaml, history.md]",
    ]

    YAML_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _latest_metric(conn: sqlite3.Connection, key: str) -> float | None:
    row = conn.execute(
        "SELECT value FROM metrics WHERE key=? ORDER BY id DESC LIMIT 1", [key]
    ).fetchone()
    return row[0] if row else None


def snapshot() -> None:
    """Record a full metrics snapshot — called by /compact to build time-series data.

    Captures: coverage_pct, tests_passing, tests_total, smells_open, smells_fixed,
    modules_migrated. Each compact creates one snapshot row per metric, enabling
    the dashboard to render inter-session trends.
    """
    conn = _conn()
    # Get current phase
    row = conn.execute("SELECT name FROM phases WHERE status='in_progress' LIMIT 1").fetchone()
    phase = row["name"] if row else "unknown"

    # Snapshot from latest values already in metrics table
    keys_to_snapshot = [
        "tests_total", "tests_passing", "coverage_pct", "mypy_errors", "modules_migrated"
    ]
    now = datetime.utcnow().isoformat()
    snapped = 0
    for key in keys_to_snapshot:
        latest = _latest_metric(conn, key)
        if latest is not None:
            conn.execute(
                "INSERT INTO metrics (phase, key, value, recorded_at) VALUES (?,?,?,?)",
                [phase, f"snapshot_{key}", latest, now]
            )
            snapped += 1

    # Also snapshot smell counts directly
    open_c = conn.execute("SELECT COUNT(*) FROM smells WHERE status='open'").fetchone()[0]
    fixed_c = conn.execute("SELECT COUNT(*) FROM smells WHERE status='fixed'").fetchone()[0]
    conn.execute("INSERT INTO metrics (phase, key, value, recorded_at) VALUES (?,?,?,?)",
                 [phase, "snapshot_smells_open", open_c, now])
    conn.execute("INSERT INTO metrics (phase, key, value, recorded_at) VALUES (?,?,?,?)",
                 [phase, "snapshot_smells_fixed", fixed_c, now])
    conn.commit()
    conn.close()

    _log("INFO", f"Metrics snapshot recorded ({snapped} series + smells)", phase)
    _update_yaml()
    print(f"✅ Snapshot recorded for phase '{phase}' ({snapped + 2} values captured)")


def export_sql() -> None:
    conn = _conn()

    tables = [
        "phases", "decisions", "smells",
        "metrics", "session_log", "files_touched",
    ]

    lines = [
        "-- state.sql — Project Jacky state dump",
        f"-- Generated: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}",
        "-- Source of truth: state.db  (excluded from git via .gitignore)",
        "-- Restore with: python scripts/state.py import sql",
        "-- Or:           make state-restore",
        "",
        "PRAGMA foreign_keys=OFF;",
        "",
    ]

    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        cols = [d[1] for d in conn.execute(f"PRAGMA table_info({table})").fetchall()]

        lines.append(f"-- {table} ({len(rows)} rows)")
        lines.append(f"DELETE FROM {table};")

        if rows:
            col_list = ", ".join(cols)
            for row in rows:
                values = ", ".join(
                    "NULL" if v is None else f"'{str(v).replace(chr(39), chr(39)*2)}'"
                    for v in row
                )
                lines.append(f"INSERT INTO {table} ({col_list}) VALUES ({values});")
        lines.append("")

    lines.append("PRAGMA foreign_keys=ON;")

    SQL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    conn.close()
    print(f"✅ SQL dump written to {SQL_PATH}")
    print(f"   Commit with: git add session/state.sql && git commit -m 'chore: update state dump'")


def import_sql() -> None:
    """Restore DB from session/state.sql. Runs init_state.py first to ensure schema."""
    if not SQL_PATH.exists():
        print(f"ERROR: {SQL_PATH} not found. Nothing to import.")
        sys.exit(1)

    # Ensure schema exists
    import importlib.util
    init_path = Path(__file__).parent / "init_state.py"
    spec = importlib.util.spec_from_file_location("init_state", init_path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        mod.init(reset=False)

    conn = sqlite3.connect(DB_PATH)
    sql = SQL_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()
    conn.close()

    _update_yaml()
    print(f"✅ DB restored from {SQL_PATH}")
    print(f"   Run: python scripts/state.py export yaml  to refresh context.yaml")


def export_yaml() -> None:
    _update_yaml()
    print(YAML_PATH.read_text(encoding="utf-8"))


def export_summary() -> None:
    conn = _conn()
    in_prog = conn.execute("SELECT name FROM phases WHERE status='in_progress' LIMIT 1").fetchone()
    current = in_prog["name"] if in_prog else "none"
    smell_open = conn.execute("SELECT COUNT(*) FROM smells WHERE status='open'").fetchone()[0]
    smell_fixed = conn.execute("SELECT COUNT(*) FROM smells WHERE status='fixed'").fetchone()[0]
    dec_count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    conn.close()
    print(f"Phase: {current} | Smells open/fixed: {smell_open}/{smell_fixed} | Decisions: {dec_count}")


# ─── SESSION STATE (next_action, active_file, turn_count) ─────────────────────

def _get_state(key: str) -> str | None:
    conn = _conn()
    row = conn.execute("SELECT value FROM session_state WHERE key=?", [key]).fetchone()
    conn.close()
    return row[0] if row else None


def _set_state(key: str, value: str) -> None:
    now = datetime.utcnow().isoformat()
    conn = _conn()
    conn.execute(
        "INSERT INTO session_state (key, value, updated_at) VALUES (?,?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        [key, value, now]
    )
    conn.commit()
    conn.close()


def state_set(key: str, value: str) -> None:
    allowed = {"next_action", "active_file", "compact_every_n_turns"}
    if key not in allowed:
        print(f"ERROR: key must be one of {allowed}")
        sys.exit(1)
    _set_state(key, value)
    _update_yaml()
    print(f"✅ {key} = {value!r}")


def state_get(key: str) -> None:
    val = _get_state(key)
    if val is None:
        print(f"(not set)")
    else:
        print(val)


def turn_increment() -> None:
    """Increment turn counter. Warn when compact is due."""
    raw = _get_state("turn_count") or "0"
    count = int(raw) + 1
    _set_state("turn_count", str(count))

    threshold = int(_get_state("compact_every_n_turns") or "15")
    remaining = threshold - (count % threshold)

    if count % threshold == 0:
        print(f"⚠️  COMPACT DUE — turn {count} reached threshold ({threshold})")
        print(f"   Run: /compact  or  python scripts/state.py snapshot")
    else:
        print(f"Turn {count} | next compact in {remaining} turns")

    _update_yaml()


# ─── ROUTER ───────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    sub = args[1] if len(args) > 1 else ""

    match (cmd, sub):
        # phase
        case ("phase", "list"):   phase_list()
        case ("phase", "current"): phase_current()
        case ("phase", "set"):    phase_set(args[2], args[3])
        # decision
        case ("decision", "add"):  decision_add(args[2], args[3], args[4] if len(args) > 4 else "")
        case ("decision", "list"): decision_list(args[2] if len(args) > 2 else None)
        # smell
        case ("smell", "add"):   smell_add(args[2], args[3], args[4])
        case ("smell", "fix"):   smell_fix(int(args[2]), args[3])
        case ("smell", "list"):
            f = args[2].lstrip("-") if len(args) > 2 else None
            smell_list(f)
        # metric
        case ("metric", "record"): metric_record(args[2], args[3], float(args[4]), args[5] if len(args) > 5 else "")
        case ("metric", "show"):  metric_show(args[2] if len(args) > 2 else None)
        # log
        case ("log", _):          log_write(sub, args[2], args[3] if len(args) > 3 else None)
        # export
        case ("export", "yaml"):    export_yaml()
        case ("export", "summary"): export_summary()
        case ("export", "sql"):     export_sql()
        case ("import", "sql"):     import_sql()
        case ("snapshot", _) | ("snapshot",): snapshot()
        # session state
        case ("set", _):            state_set(sub, args[2])
        case ("get", _):            state_get(sub)
        case ("turn", _) | ("turn",): turn_increment()
        case _:
            print(f"Unknown command: {' '.join(args)}")
            print("Run: python scripts/state.py --help")
            sys.exit(1)


if __name__ == "__main__":
    main()
