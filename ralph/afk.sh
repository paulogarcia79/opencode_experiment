#!/bin/bash
set -eo pipefail

if [ -z "$1" ]; then
  echo "Usage: $0 <iterations>"
  echo "Example: $0 10"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

for ((i=1; i<=$1; i++)); do
  echo ""
  echo "═══════════════════════════════════════════════"
  echo "  RALPH ITERATION $i/$1"
  echo "═══════════════════════════════════════════════"
  echo ""

  # Run once.sh and capture output
  if ! "$SCRIPT_DIR/once.sh"; then
    echo "Ralph iteration $i failed."
    exit 1
  fi

  # Check if all tasks are done
  issues_remaining=$(ls issues/*.md 2>/dev/null | wc -l)
  if [ "$issues_remaining" -eq 0 ]; then
    echo ""
    echo "✅ Ralph complete after $i iterations. No more AFK issues."
    exit 0
  fi

done

echo ""
echo "⏹️  Ralph completed $1 iterations. Issues remaining:"
ls issues/*.md 2>/dev/null || echo "  (none)"
