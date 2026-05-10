#!/bin/bash
set -eo pipefail

# Sync GitHub issues to local issues/ directory
# Usage: ./ralph/sync-issues.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ISSUES_DIR="$PROJECT_ROOT/issues"

cd "$PROJECT_ROOT"

# Read issue tracker config
if [ ! -f .opencode/issue-tracker.json ]; then
  echo "Error: .opencode/issue-tracker.json not found"
  exit 1
fi

REPO=$(python3 -c "import json; d=json.load(open('.opencode/issue-tracker.json')); print(d['issue_tracker']['repo'])")
TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$TOKEN" ]; then
  echo "Error: GITHUB_TOKEN not set"
  echo "Run: export GITHUB_TOKEN=ghp_..."
  exit 1
fi

echo "Syncing issues from github.com/$REPO..."

TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

# Fetch open issues
curl -s -X GET \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$REPO/issues?state=open&per_page=100" > "$TMPFILE"

# Check for errors
if grep -q '"message"' "$TMPFILE" 2>/dev/null; then
  echo "Error from GitHub API:"
  cat "$TMPFILE" | python3 -m json.tool 2>/dev/null || cat "$TMPFILE"
  exit 1
fi

# Save each issue as a markdown file
python3 << PYTHON
import json, os, re

issues_dir = "$ISSUES_DIR"

with open("$TMPFILE") as f:
    issues = json.load(f)

if not isinstance(issues, list):
    print(f"Error: expected list, got {type(issues).__name__}")
    exit(1)

count = 0
for issue in issues:
    if 'pull_request' in issue:
        continue
    
    number = issue['number']
    title = issue['title']
    body = issue.get('body', '')
    labels = [l['name'] for l in issue.get('labels', [])]
    
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    
    filename = f"{number:03d}-{safe_title}.md"
    filepath = os.path.join(issues_dir, filename)
    
    content = f"""# {title}

**GitHub Issue:** #{number}
**Labels:** {', '.join(labels)}
**State:** {issue.get('state', 'unknown')}

{body}
"""
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"  Saved: {filename}")
    count += 1

print(f"\nSynced {count} issues to {issues_dir}/")
PYTHON
