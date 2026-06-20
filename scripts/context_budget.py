#!/usr/bin/env python3
"""
context_budget.py — Token cost audit for all injectable context files.

Why this matters:
  Claude Code has a ~200K token window. Beyond 70% fill (~140K), decision
  quality degrades. Context engineering = maximizing signal per token.

  Rough token estimation: 1 token ≈ 3.5–4 chars (English/code mix).
  This script uses 3.8 as the divisor (conservative estimate).

Usage:
    python scripts/context_budget.py           → full audit table
    python scripts/context_budget.py <phase>   → budget for a specific phase
    python scripts/context_budget.py --all     → show all files + phase totals

Output columns:
    FILE          path relative to project root
    CHARS         raw character count
    ~TOKENS       estimated token count
    SIGNAL        tokens / total_tokens ratio (how much of budget this file uses)
    STATUS        OK | WARN (>500 tokens) | HEAVY (>1000 tokens)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHARS_PER_TOKEN = 3.8  # conservative estimate for mixed French/English/code


# ─── Phase context profiles ───────────────────────────────────────────────────
# Each phase: (files, description)
# These mirror the LECTURE OBLIGATOIRE / CONDITIONNELLE in CLAUDE.md
# "always" files are read at every session start.

ALWAYS = [
    "CLAUDE.md",
    "session/context.yaml",
]

PHASE_PROFILES: dict[str, dict] = {
    "survey": {
        "description": "Inventaire brut — lecture intensive du legacy",
        "files": [*ALWAYS, "prompts/system.md", "src/app.py"],
        "optional": [],
    },
    "map": {
        "description": "Cartographie — analyse des dépendances",
        "files": [*ALWAYS, "prompts/system.md", "logs/audit/survey.md"],
        "optional": ["src/app.py"],
    },
    "audit": {
        "description": "Scoring technique par domaine",
        "files": [*ALWAYS, "prompts/system.md", "logs/audit/survey.md", "logs/audit/map.md"],
        "optional": [],
    },
    "draft": {
        "description": "Plan d'intervention + contrats",
        "files": [
            *ALWAYS, "prompts/system.md", "prompts/conventions.md",
            "prompts/data_contract.md", "logs/audit/latest.md",
        ],
        "optional": [],
    },
    "stabilize": {
        "description": "Génération des tests de sécurité",
        "files": [
            *ALWAYS, "prompts/system.md", "logs/audit/draft.md", "src/app.py",
        ],
        "optional": [],
    },
    "derive": {
        "description": "Refacto module par module — contexte maximal",
        "files": [
            *ALWAYS, "prompts/system.md", "prompts/conventions.md",
            "prompts/coding_standards.md", "prompts/data_contract.md",
            "logs/audit/latest.md", "logs/audit/draft.md",
        ],
        "optional": ["session/history.md"],
    },
    "extend": {
        "description": "Nouvelles features post-refacto",
        "files": [
            *ALWAYS, "prompts/system.md", "prompts/conventions.md",
            "prompts/coding_standards.md",
        ],
        "optional": ["session/history.md"],
    },
    "compact": {
        "description": "Compression de session",
        "files": [*ALWAYS, "session/history.md"],
        "optional": [],
    },
    "doctor": {
        "description": "Diagnostic de blockers",
        "files": [*ALWAYS, "session/history.md"],
        "optional": [],
    },
}

# Token budget thresholds
WARN_TOKENS = 500
HEAVY_TOKENS = 1000
SESSION_BUDGET = 140_000   # 70% of 200K — degradation threshold
TARGET_CONTEXT = 8_000     # target for total injected context (tight budget)


# ─── Core logic ───────────────────────────────────────────────────────────────

def estimate_tokens(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        chars = len(path.read_text(encoding="utf-8", errors="ignore"))
        return max(1, int(chars / CHARS_PER_TOKEN))
    except OSError:
        return 0


def file_status(tokens: int) -> str:
    if tokens >= HEAVY_TOKENS:
        return "HEAVY ⚠️ "
    if tokens >= WARN_TOKENS:
        return "WARN  🟡"
    return "OK    ✅"


def audit_file(rel_path: str) -> tuple[str, int, int, str]:
    path = ROOT / rel_path
    exists = path.exists()
    chars = len(path.read_text(encoding="utf-8", errors="ignore")) if exists else 0
    tokens = max(1, int(chars / CHARS_PER_TOKEN)) if exists else 0
    status = file_status(tokens) if exists else "MISSING ❌"
    return rel_path, chars, tokens, status


def print_table(rows: list[tuple], phase_total: int) -> None:
    print(f"\n{'FILE':<45} {'CHARS':>7} {'~TOKENS':>8} {'STATUS'}")
    print("─" * 78)
    for rel_path, chars, tokens, status in rows:
        print(f"  {rel_path:<43} {chars:>7,} {tokens:>8,}   {status}")
    print("─" * 78)
    bar_fill = min(40, int(phase_total / TARGET_CONTEXT * 40))
    bar = "█" * bar_fill + "░" * (40 - bar_fill)
    pct = round(phase_total / TARGET_CONTEXT * 100)
    rating = "🟢 lean" if pct <= 80 else "🟡 acceptable" if pct <= 130 else "🔴 heavy"
    print(f"  {'TOTAL':<43} {'':>7} {phase_total:>8,}   {rating}")
    print(f"\n  Context budget: [{bar}] {pct}% of {TARGET_CONTEXT:,} target tokens")
    print(f"  Session window: {phase_total:,} / {SESSION_BUDGET:,} ({round(phase_total/SESSION_BUDGET*100)}% of degradation threshold)")


def run_phase(phase: str) -> None:
    if phase not in PHASE_PROFILES:
        print(f"Unknown phase: {phase}. Available: {', '.join(PHASE_PROFILES)}")
        sys.exit(1)

    profile = PHASE_PROFILES[phase]
    print(f"\n{'='*78}")
    print(f"  Phase: /{phase}  —  {profile['description']}")
    print(f"{'='*78}")

    rows = [audit_file(f) for f in profile["files"]]
    total = sum(r[2] for r in rows)

    print_table(rows, total)

    if profile["optional"]:
        print(f"\n  Optional (conditional):")
        opt_rows = [audit_file(f) for f in profile["optional"]]
        opt_total = sum(r[2] for r in opt_rows)
        for rel_path, chars, tokens, status in opt_rows:
            print(f"    + {rel_path:<41} {chars:>7,} {tokens:>8,}   {status}")
        print(f"    {'max with optionals':<41} {'':>7} {total + opt_total:>8,}")

    heavy = [r for r in rows if r[2] >= WARN_TOKENS]
    if heavy:
        print(f"\n  ⚠️  Files to slim down:")
        for rel_path, chars, tokens, _ in heavy:
            savings = tokens - WARN_TOKENS
            print(f"    • {rel_path} ({tokens} tokens — {savings} over target)")


def run_all() -> None:
    print(f"\n{'='*78}")
    print(f"  FULL CONTEXT BUDGET AUDIT — All injectable files")
    print(f"{'='*78}")

    all_files: dict[str, tuple] = {}
    for profile in PHASE_PROFILES.values():
        for f in [*profile["files"], *profile["optional"]]:
            if f not in all_files:
                all_files[f] = audit_file(f)

    rows = list(all_files.values())
    rows.sort(key=lambda r: r[2], reverse=True)
    total = sum(r[2] for r in rows)
    print_table(rows, total)

    print(f"\n{'─'*78}")
    print(f"  PER-PHASE TOTALS:")
    print(f"  {'PHASE':<15} {'TOKENS':>8}   BUDGET RATING")
    print(f"  {'─'*50}")
    for phase, profile in PHASE_PROFILES.items():
        phase_total = sum(audit_file(f)[2] for f in profile["files"])
        pct = round(phase_total / TARGET_CONTEXT * 100)
        rating = "🟢" if pct <= 80 else "🟡" if pct <= 130 else "🔴"
        print(f"  /{phase:<14} {phase_total:>8,}   {rating} {pct}% of target")


def main() -> None:
    args = sys.argv[1:]

    if not args or "--all" in args:
        run_all()
    elif args[0] in PHASE_PROFILES:
        run_phase(args[0])
    else:
        print(f"Usage: python scripts/context_budget.py [phase|--all]")
        print(f"Phases: {', '.join(PHASE_PROFILES)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
