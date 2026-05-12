"""Lint a project-local .sales/ seller config folder.

Usage: python scripts/verify_sales_config.py <path-to-.sales-folder>

Exits 0 if the folder is well-formed, 1 otherwise. Errors print to stdout.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES: dict[str, list[str]] = {
    "identity.md": ["## Company", "## Senders", "## Voice and Tone", "## Signature", "## Company Bio"],
    "icp.md": ["## ICP Summary", "## Firmographic Criteria"],
    "pricing.md": ["## Tiers", "## Deal Size Benchmarks", "## Discount Rules", "## Contract Terms"],
    "case-studies.md": ["## "],
    "competitive.md": ["## Positioning Statement", "## Competitors"],
    "objections.md": ["## Top Objections"],
}


PROPOSITION_SECTIONS: list[str] = [
    "## Name",
    "## Slug",
    "## Value Prop",
    "## Target Persona",
    "## Key Features",
    "## Differentiators",
    "## Ideal Use Cases",
    "## Pricing Tier Reference",
    "## Success Metrics",
    "## Anti-Fit Signals",
]


def _check_sections(text: str, required: list[str]) -> list[str]:
    missing: list[str] = []
    for header in required:
        pattern = re.compile(rf"^{re.escape(header)}\b", re.MULTILINE)
        if not pattern.search(text):
            missing.append(header)
    return missing


def verify(config_dir: Path) -> list[str]:
    errors: list[str] = []
    if not config_dir.is_dir():
        return [f"not a directory: {config_dir}"]

    for filename, required_sections in REQUIRED_FILES.items():
        path = config_dir / filename
        if not path.is_file():
            errors.append(f"missing required file: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        for missing in _check_sections(text, required_sections):
            errors.append(f"{filename}: missing section '{missing}'")

    propositions_dir = config_dir / "propositions"
    if not propositions_dir.is_dir():
        errors.append("missing required folder: propositions/")
        return errors

    prop_files = sorted(p for p in propositions_dir.glob("*.md") if not p.name.startswith("_"))
    if not prop_files:
        errors.append("propositions/: at least one proposition file required")

    for prop in prop_files:
        text = prop.read_text(encoding="utf-8")
        for missing in _check_sections(text, PROPOSITION_SECTIONS):
            errors.append(f"propositions/{prop.name}: missing section '{missing}'")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_sales_config.py <path-to-.sales-folder>", file=sys.stderr)
        return 2
    errors = verify(Path(argv[1]))
    for err in errors:
        print(err)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
