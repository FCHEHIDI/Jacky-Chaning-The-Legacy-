#!/usr/bin/env python3
"""
init_state.py — Initialize the project state SQLite database.
Run once at project start, or to reset state (use --reset flag).

Usage:
    python scripts/init_state.py
    python scripts/init_state.py --reset
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "session" / "state.db"

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS phases (
    id          INTEGER PRIMARY KEY,
    name        TEXT    UNIQUE NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'not_started',
    started_at  TEXT,
    completed_at TEXT,
    CHECK (status IN ('not_started', 'in_progress', 'completed', 'skipped'))
);

CREATE TABLE IF NOT EXISTS decisions (
    id            INTEGER PRIMARY KEY,
    phase         TEXT    NOT NULL,
    content       TEXT    NOT NULL,
    justification TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS smells (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    location    TEXT    NOT NULL,
    severity    TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'open',
    fixed_in    TEXT,
    fixed_at    TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    CHECK (status IN ('open', 'fixed', 'wontfix'))
);

CREATE TABLE IF NOT EXISTS metrics (
    id          INTEGER PRIMARY KEY,
    phase       TEXT    NOT NULL,
    key         TEXT    NOT NULL,
    value       REAL    NOT NULL,
    unit        TEXT,
    recorded_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS session_log (
    id          INTEGER PRIMARY KEY,
    level       TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    phase       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK (level IN ('INFO', 'DECISION', 'WARN', 'RISK', 'DONE'))
);

CREATE TABLE IF NOT EXISTS files_touched (
    id          INTEGER PRIMARY KEY,
    phase       TEXT    NOT NULL,
    filepath    TEXT    NOT NULL,
    change_type TEXT    NOT NULL,
    description TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK (change_type IN ('created', 'modified', 'deleted'))
);

-- Key-value store for session state (next_action, active_file, turn_count)
CREATE TABLE IF NOT EXISTS session_state (
    key         TEXT    PRIMARY KEY,
    value       TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO session_state (key, value) VALUES
    ('next_action', 'run /survey to start legacy inventory'),
    ('active_file',  'src/app.py'),
    ('turn_count',   '0'),
    ('compact_every_n_turns', '15');

-- Seed phase definitions (ordered)
INSERT OR IGNORE INTO phases (name, status) VALUES
    ('survey',    'not_started'),
    ('map',       'not_started'),
    ('audit',     'not_started'),
    ('draft',     'not_started'),
    ('stabilize', 'not_started'),
    ('derive',    'not_started'),
    ('extend',    'not_started');
"""

RESET_SQL = """
DELETE FROM phases;
DELETE FROM decisions;
DELETE FROM smells;
DELETE FROM metrics;
DELETE FROM session_log;
DELETE FROM files_touched;
"""


def init(reset: bool = False) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    if reset:
        print("⚠️  Resetting state database...")
        conn.executescript(RESET_SQL)

    conn.executescript(SCHEMA)
    conn.close()
    print(f"✅ State DB ready: {DB_PATH}")


if __name__ == "__main__":
    init(reset="--reset" in sys.argv)
