#!/usr/bin/env bash
set -euo pipefail

echo "VERIFY-RELEASE: CivicData Bridge v0.1.1"

PYTHON_CANDIDATES=()
if [[ -n "${CIVICDATA_RELEASE_PYTHON:-}" ]]; then
  PYTHON_CANDIDATES+=("$CIVICDATA_RELEASE_PYTHON")
fi
PYTHON_CANDIDATES+=(python python3 py "/mnt/c/Users/scott/AppData/Local/Microsoft/WindowsApps/python.exe")

PYTHON_BIN=""
for candidate in "${PYTHON_CANDIDATES[@]}"; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import build, pytest, ruff" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "[FAIL] python: no interpreter with build, pytest, and ruff available"
  exit 1
fi

echo "[INFO] python: $PYTHON_BIN"

bash scripts/verify-docs.sh
"$PYTHON_BIN" scripts/check-civiccore-placeholder-imports.py
"$PYTHON_BIN" -m pytest -q
"$PYTHON_BIN" -m ruff check .
rm -rf dist
"$PYTHON_BIN" -m build
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
import hashlib
expected = {"civicdata-0.1.1-py3-none-any.whl", "civicdata-0.1.1.tar.gz"}
dist = Path("dist")
found = {p.name for p in dist.iterdir() if p.is_file()}
missing = expected - found
if missing:
    raise SystemExit(f"missing artifacts: {sorted(missing)}")
lines = []
for name in sorted(expected):
    data = (dist / name).read_bytes()
    lines.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
(dist / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("[PASS] build artifacts and SHA256SUMS")
PY
"$PYTHON_BIN" - <<'PY'
import civicdata
assert civicdata.__version__ == "0.1.1"
print("[PASS] package version 0.1.1")
PY

echo "VERIFY-RELEASE: PASSED"
