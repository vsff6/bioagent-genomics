"""Tests for tools/reference_validator.py."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TOOL = REPO_ROOT / "tools" / "reference_validator.py"
EXAMPLES = REPO_ROOT / "examples"


def run_tool(*args):
    return subprocess.run(
        [sys.executable, str(TOOL)] + list(args),
        capture_output=True, text=True,
    )


class TestHelp:
    def test_help_exits_zero(self):
        r = run_tool("--help")
        assert r.returncode == 0


class TestGTF:
    def test_gtf_validated(self, tmp_path):
        r = run_tool(
            "--gtf", str(EXAMPLES / "tiny.gtf"),
            "--output-dir", str(tmp_path),
        )
        # Should succeed (rc=0) or warn (rc=1) but not crash
        assert r.returncode in (0, 1)

    def test_json_written(self, tmp_path):
        run_tool("--gtf", str(EXAMPLES / "tiny.gtf"), "--output-dir", str(tmp_path))
        json_file = tmp_path / "reference_validation.json"
        assert json_file.exists()
        with open(json_file) as f:
            data = json.load(f)
        assert "results" in data

    def test_markdown_written(self, tmp_path):
        run_tool("--gtf", str(EXAMPLES / "tiny.gtf"), "--output-dir", str(tmp_path))
        md_file = tmp_path / "reference_validation.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "Reference File Validation" in content

    def test_chrom_style_detected(self, tmp_path):
        run_tool("--gtf", str(EXAMPLES / "tiny.gtf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "reference_validation.json") as f:
            data = json.load(f)
        result = data["results"][0]
        assert "chrom_style" in result
        assert "UCSC" in result["chrom_style"]  # tiny.gtf uses chr1, chr2


class TestBlacklist:
    def test_blacklist_bed_validated(self, tmp_path):
        r = run_tool(
            "--blacklist", str(EXAMPLES / "tiny.bed"),
            "--output-dir", str(tmp_path),
        )
        assert r.returncode in (0, 1)

    def test_blacklist_chrom_style(self, tmp_path):
        run_tool("--blacklist", str(EXAMPLES / "tiny.bed"), "--output-dir", str(tmp_path))
        with open(tmp_path / "reference_validation.json") as f:
            data = json.load(f)
        result = data["results"][0]
        assert "chrom_style" in result


class TestMissingFile:
    def test_missing_fasta_reported(self, tmp_path):
        r = run_tool(
            "--genome-fasta", "/nonexistent/genome.fa",
            "--output-dir", str(tmp_path),
        )
        assert r.returncode == 1  # issues found
        with open(tmp_path / "reference_validation.json") as f:
            data = json.load(f)
        assert data["results"][0]["status"] == "MISSING"


class TestChromConflict:
    def test_chrom_conflict_detected(self, tmp_path, examples_dir):
        """GTF has chr prefix; if we had an Ensembl-style file we'd get a conflict.
        Here just test that the conflict check runs without crash."""
        run_tool(
            "--gtf", str(examples_dir / "tiny.gtf"),
            "--blacklist", str(examples_dir / "tiny.bed"),
            "--output-dir", str(tmp_path),
        )
        with open(tmp_path / "reference_validation.json") as f:
            data = json.load(f)
        assert "conflicts" in data  # key always present


class TestNoInput:
    def test_no_input_warns(self, tmp_path):
        r = run_tool("--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "reference_validation.json"
        assert json_file.exists()
