Write-Host "🔧 Initializing Claude Code environment..."

# --- folders ---
$folders = @(
  "prompts",
  "src/ingestion",
  "src/etl",
  "src/db",
  "src/api",
  "src/analytics",
  "data/mock",
  "data/raw",
  ".claude/commands",
  "session"
)

foreach ($f in $folders) {
  if (-not (Test-Path $f)) {
    New-Item -ItemType Directory -Path $f | Out-Null
    Write-Host "📁 Created folder: $f"
  }
}

# --- files ---
$files = @(
  "CLAUDE.md",
  "prompts/system.md",
  "prompts/data_contract.md",
  "prompts/conventions.md",
  "prompts/coding_standards.md",
  "data/mock/users.json",
  "data/raw/events.json",
  "session/context.md",
  "session/history.md"
)

foreach ($file in $files) {
  if (-not (Test-Path $file)) {
    New-Item -ItemType File -Path $file | Out-Null
    Write-Host "📄 Created file: $file"
  }
}

# --- .claude settings ---
$settingsPath = ".claude/settings.local.json"
if (-not (Test-Path $settingsPath)) {
@"
{
  "permissions": {
    "allowFileSystem": true,
    "allowNetwork": false
  },
  "tools": {
    "sqlite": true
  }
}
"@ | Out-File $settingsPath -Encoding utf8
  Write-Host "⚙️ Created .claude/settings.local.json"
}

# --- default slash commands ---
$commands = @(
  "survey.md",
  "map.md",
  "derive.md",
  "draft.md",
  "extend.md",
  "stabilize.md",
  "audit.md",
  "doctor.md",
  "compact.md"
)

foreach ($cmd in $commands) {
  $path = ".claude/commands/$cmd"
  if (-not (Test-Path $path)) {
    "# $cmd — custom Claude Code command" | Out-File $path -Encoding utf8
    Write-Host "🛠️ Created command: $cmd"
  }
}

Write-Host "✨ Claude Code environment ready."
