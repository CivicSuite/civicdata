#!/usr/bin/env bash
set -euo pipefail

required=(
  README.md
  README.txt
  USER-MANUAL.md
  USER-MANUAL.txt
  CHANGELOG.md
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  SECURITY.md
  SUPPORT.md
  LICENSE
  LICENSE-CODE
  LICENSE-DOCS
  AGENTS.md
  docs/index.html
  docs/IMPLEMENTATION_PLAN.md
  docs/MILESTONES.md
  docs/RECONCILIATION.md
  docs/github-discussions-seed.md
)

for path in "${required[@]}"; do
  if [[ ! -s "$path" ]]; then
    echo "VERIFY-DOCS: FAILED missing or empty $path"
    exit 1
  fi
done

current_files=(README.md README.txt USER-MANUAL.md USER-MANUAL.txt CHANGELOG.md docs/index.html AGENTS.md MILESTONE_0_7_DONE.md)
stale_patterns=(
  CivicComms civiccomms Civic311 civic311 CivicNotice civicnotice Open311
  "campaign content" "autonomous publication" "live CKAN publishing ships" "data warehouse ships"
  "0.1.1.dev0" "~=0.2" "MIT"
)

for file in "${current_files[@]}"; do
  for pattern in "${stale_patterns[@]}"; do
    if grep -Fq "$pattern" "$file"; then
      echo "VERIFY-DOCS: FAILED stale marker '$pattern' found in $file"
      exit 1
    fi
  done
done

if ! grep -Fq "civiccore==0.3.0" README.md; then
  echo "VERIFY-DOCS: FAILED README.md must mention civiccore==0.3.0"
  exit 1
fi
if ! grep -Fq "No live CKAN publication" docs/index.html; then
  echo "VERIFY-DOCS: FAILED docs/index.html must state live CKAN publication boundary"
  exit 1
fi

echo "VERIFY-DOCS: PASSED"
