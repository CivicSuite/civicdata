from pathlib import Path
import re
import sys

PLACEHOLDERS = (
    "audit",
    "auth",
    "catalog",
    "connectors",
    "exemptions",
    "ingest",
    "notifications",
    "onboarding",
    "scaffold",
    "search",
    "verification",
)
SOURCE_ROOT = Path("civicdata")
pattern = re.compile(r"^\s*(?:from|import)\s+civiccore\.(" + "|".join(PLACEHOLDERS) + r")\b")
violations: list[str] = []
for path in SOURCE_ROOT.rglob("*.py"):
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = pattern.search(line)
        if match:
            name = match.group(1)
            violations.append(
                f"{path}:{lineno}: civiccore.{name} is a placeholder package in v0.3.0. See AGENTS.md section 3.1."
            )
if violations:
    print("PLACEHOLDER-IMPORT-CHECK: FAILED")
    print("\n".join(violations))
    sys.exit(1)
print(f"PLACEHOLDER-IMPORT-CHECK: PASSED ({len(list(SOURCE_ROOT.rglob('*.py')))} source files scanned)")
