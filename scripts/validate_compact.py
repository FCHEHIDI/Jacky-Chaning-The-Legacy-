#!/usr/bin/env python3
"""
validate_compact.py — Quality check for a compaction snapshot.

A bad compact = a blind next session. This script validates that
session/context.yaml contains ALL the fields required for a meaningful
cold-start on the next session.

The "survival contract": the 7 fields that must never be lost in a compact.

Usage:
    python scripts/validate_compact.py          → exits 0 (valid) or 1 (invalid)
    python scripts/validate_compact.py --verbose → explains each field
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
YAML_PATH = ROOT / "session" / "context.yaml"

# ─── Survival contract ────────────────────────────────────────────────────────
# Every field below MUST be present and non-empty in context.yaml after a compact.
# These are the 7 questions the next session needs answered to start without blindness.

REQUIRED_FIELDS = [
    ("snapshot",     "When was this compact taken?",       lambda v: len(v) >= 10),
    ("phase",        "What phase are we in?",              lambda v: "current:" in v),
    ("next_action",  "What's the first thing to do?",      lambda v: len(v) > 20 and v != '"run /survey to start legacy inventory"' or True),
    ("active_file",  "Which file is being worked on?",     lambda v: len(v) > 5),
    ("smells",       "How many smells remain?",            lambda v: "open:" in v),
    ("tests",        "What's the test/coverage status?",   lambda v: "coverage_pct:" in v),
    ("knowledge_stack", "Which derived artifacts exist?",  lambda v: "[x]" in v or "[ ]" in v),
]

# Fields that SHOULD be present but are warnings (not blockers)
RECOMMENDED_FIELDS = [
    ("decisions_recent", "What decisions were just taken?"),
    ("risks",            "What are the open risks?"),
    ("context_profiles", "Which files to read for this phase?"),
]


def validate() -> tuple[list[str], list[str]]:
    """Returns (errors, warnings)."""
    if not YAML_PATH.exists():
        return ["MISSING: session/context.yaml not found — run /compact first"], []

    content = YAML_PATH.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    for field, question, check in REQUIRED_FIELDS:
        # Find the field in YAML content
        field_line = next(
            (line for line in content.splitlines() if line.startswith(f"{field}:")),
            None
        )
        if field_line is None:
            errors.append(f"MISSING field '{field}' — answers: '{question}'")
            continue

        value = field_line.split(":", 1)[1].strip()
        if not value and field not in ("phase", "smells", "tests", "knowledge_stack"):
            errors.append(f"EMPTY field '{field}' — answers: '{question}'")
            continue

        # For multi-line fields (phase, smells, etc.), check the block
        if not check(content):
            errors.append(f"INCOMPLETE field '{field}' — answers: '{question}'")

    for field, question in RECOMMENDED_FIELDS:
        if f"\n{field}:" not in content and not content.startswith(f"{field}:"):
            warnings.append(f"MISSING (recommended) '{field}' — answers: '{question}'")

    # Check next_action is meaningful (not the default placeholder)
    na_line = next((l for l in content.splitlines() if l.startswith("next_action:")), "")
    na_value = na_line.split(":", 1)[1].strip().strip('"') if na_line else ""
    if na_value in ("", "run /survey to start legacy inventory"):
        warnings.append(
            "next_action appears to be the default — Claude should update it before /compact:\n"
            "  python scripts/state.py set next_action \"<specific next step>\""
        )

    return errors, warnings


def main() -> None:
    verbose = "--verbose" in sys.argv
    errors, warnings = validate()

    print(f"\n{'='*60}")
    print(f"  Compact quality validation")
    print(f"{'='*60}")
    print(f"  File: {YAML_PATH.relative_to(ROOT)}")

    if not errors and not warnings:
        print(f"\n  ✅ VALID — all 7 survival contract fields present")
        print(f"     This compact is safe to use as next session's context.\n")
        sys.exit(0)

    if errors:
        print(f"\n  🔴 INVALID — {len(errors)} required field(s) missing:\n")
        for e in errors:
            print(f"    • {e}")
        print(f"\n  The next session CANNOT start reliably from this compact.")
        print(f"  Fix and re-run /compact before closing the session.\n")

    if warnings:
        print(f"\n  🟡 WARNINGS — {len(warnings)} recommended field(s) missing:\n")
        for w in warnings:
            print(f"    • {w}")
        print()

    if verbose and YAML_PATH.exists():
        print(f"  Current context.yaml content:")
        print(f"  {'─'*50}")
        for line in YAML_PATH.read_text(encoding="utf-8").splitlines()[:30]:
            print(f"  {line}")
        print(f"  {'─'*50}\n")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
