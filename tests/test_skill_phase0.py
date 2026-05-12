import subprocess
import sys
from pathlib import Path


VERIFY_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "verify_skill_phase0.py"


def _run() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT)],
        capture_output=True,
        text=True,
    )


def test_phase0_verifier_runs() -> None:
    result = _run()
    # Before any skills are migrated, the verifier should report missing
    # Phase 0 sections; that is the expected starting state. We assert the
    # output mentions the contract so an engineer reading the failure knows
    # what to do.
    assert "Phase 0" in result.stdout + result.stderr
