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


def test_phase0_verifier_passes() -> None:
    result = _run()
    assert result.returncode == 0, (
        "Phase 0 verifier reported skills missing the Phase 0 contract.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
