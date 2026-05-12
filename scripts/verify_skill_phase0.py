"""Lint that each sales SKILL.md has a Phase 0: Load Seller Context block
mentioning the files the skill is required to load (per the design spec).

Usage: python scripts/verify_skill_phase0.py

Exits 0 if every skill in the contract passes, 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


SKILL_CONTRACT: dict[str, list[str]] = {
    "skills/sales-contacts/SKILL.md": ["identity.md", "propositions/<slug>.md"],
    "skills/sales-contacts-batch/SKILL.md": ["identity.md", "propositions/<slug>.md"],
    "skills/sales-qualify/SKILL.md": ["icp.md", "propositions/<slug>.md"],
    "skills/sales-outreach/SKILL.md": [
        "identity.md",
        "propositions/<slug>.md",
        "case-studies.md",
        "competitive.md",
    ],
    "skills/sales-followup/SKILL.md": ["identity.md", "propositions/<slug>.md"],
    "skills/sales-prep/SKILL.md": [
        "propositions/<slug>.md",
        "objections.md",
        "competitive.md",
    ],
    "skills/sales-proposal/SKILL.md": [
        "propositions/<slug>.md",
        "pricing.md",
        "case-studies.md",
        "identity.md",
    ],
    "skills/sales-objections/SKILL.md": [
        "objections.md",
        "competitive.md",
        "propositions/<slug>.md",
    ],
    "skills/sales-prospect/SKILL.md": [
        "identity.md",
        "icp.md",
        "pricing.md",
        "case-studies.md",
        "competitive.md",
        "objections.md",
        "propositions/<slug>.md",
    ],
    "skills/sales-report/SKILL.md": ["identity.md"],
    "skills/sales-report-pdf/SKILL.md": ["identity.md"],
}


PHASE0_HEADER = "## Phase 0: Load Seller Context"


def verify() -> list[str]:
    errors: list[str] = []
    for relpath, required_files in SKILL_CONTRACT.items():
        path = REPO_ROOT / relpath
        if not path.is_file():
            errors.append(f"{relpath}: file not found")
            continue
        text = path.read_text(encoding="utf-8")
        if PHASE0_HEADER not in text:
            errors.append(f"{relpath}: missing '{PHASE0_HEADER}' section")
            continue
        # Locate Phase 0 block: from its header to the next ## header or EOF.
        start = text.index(PHASE0_HEADER)
        rest = text[start + len(PHASE0_HEADER):]
        next_header = rest.find("\n## ")
        block = rest if next_header == -1 else rest[:next_header]
        for filename in required_files:
            if filename not in block:
                errors.append(f"{relpath}: Phase 0 must mention '{filename}'")
    return errors


def main() -> int:
    errors = verify()
    for err in errors:
        print(err)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
