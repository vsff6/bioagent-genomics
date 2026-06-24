"""Shared fixtures for genomics-agent tests."""
import os
import sys
from pathlib import Path

import pytest

# Add tools/ to path for direct imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

EXAMPLES_DIR = REPO_ROOT / "examples"
TOOLS_DIR = REPO_ROOT / "tools"


@pytest.fixture
def examples_dir():
    return EXAMPLES_DIR


@pytest.fixture
def tmp_out(tmp_path):
    return tmp_path / "output"
