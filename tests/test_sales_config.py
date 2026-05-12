import subprocess
import sys
from pathlib import Path

import pytest


VERIFY_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "verify_sales_config.py"


def _run_verifier(config_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), str(config_dir)],
        capture_output=True,
        text=True,
    )


def test_example_fixture_validates(example_config_dir: Path) -> None:
    result = _run_verifier(example_config_dir)
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_required_file_reports_error(tmp_path: Path) -> None:
    config = tmp_path / ".sales"
    (config / "propositions").mkdir(parents=True)
    (config / "identity.md").write_text("## Company\nExample Co\n")
    result = _run_verifier(config)
    assert result.returncode != 0
    assert "icp.md" in result.stdout + result.stderr


def test_missing_required_section_reports_error(tmp_path: Path) -> None:
    config = tmp_path / ".sales"
    (config / "propositions").mkdir(parents=True)
    for name in ("identity.md", "icp.md", "pricing.md", "case-studies.md", "competitive.md", "objections.md"):
        (config / name).write_text("# placeholder with no H2\n")
    (config / "propositions" / "demo.md").write_text("# placeholder\n")
    result = _run_verifier(config)
    assert result.returncode != 0
