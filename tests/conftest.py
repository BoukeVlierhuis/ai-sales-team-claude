from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def example_config_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "sales-config-example" / ".sales"
