"""Tests for tools/inspect_file.py."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TOOL = REPO_ROOT / "tools" / "inspect_file.py"
EXAMPLES = REPO_ROOT / "examples"


def run_tool(*args):
    result = subprocess.run(
        [sys.executable, str(TOOL)] + list(args),
        capture_output=True,
        text=True,
    )
    return result


class TestHelp:
    def test_help_exits_zero(self):
        r = run_tool("--help")
        assert r.returncode == 0
        assert "inspect" in r.stdout.lower() or "inspect" in r.stderr.lower()


class TestFasta:
    def test_fasta_detected(self, tmp_path, examples_dir):
        r = run_tool("--input", str(examples_dir / "tiny.fa"), "--output-dir", str(tmp_path))
        assert r.returncode == 0

    def test_json_written(self, tmp_path, examples_dir):
        run_tool("--input", str(examples_dir / "tiny.fa"), "--output-dir", str(tmp_path))
        json_file = tmp_path / "file_inventory.json"
        assert json_file.exists(), "JSON output not created"
        with open(json_file) as f:
            data = json.load(f)
        assert "files" in data
        assert data["files"][0]["type"] == "FASTA"

    def test_markdown_written(self, tmp_path, examples_dir):
        run_tool("--input", str(examples_dir / "tiny.fa"), "--output-dir", str(tmp_path))
        md_file = tmp_path / "file_inventory.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "FASTA" in content


class TestFastq:
    def test_fastq_detected(self, tmp_path, examples_dir):
        r = run_tool("--input", str(examples_dir / "tiny.fastq"), "--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        assert data["files"][0]["type"] == "FASTQ"


class TestCSV:
    def test_csv_detected(self, tmp_path, examples_dir):
        r = run_tool("--input", str(examples_dir / "tiny_counts.csv"), "--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        assert data["files"][0]["type"] == "CSV"
        dims = data["files"][0]["details"]["dims"]
        assert dims["cols"] == 11  # gene column + 10 cells
        assert isinstance(dims["rows"], (int, str))


class TestVCF:
    def test_vcf_detected(self, tmp_path, examples_dir):
        r = run_tool("--input", str(examples_dir / "tiny.vcf"), "--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        assert data["files"][0]["type"] == "VCF"
        assert data["files"][0]["details"]["n_samples"] == 1

    def test_vcf_header_sample(self, tmp_path, examples_dir):
        run_tool("--input", str(examples_dir / "tiny.vcf"), "--output-dir", str(tmp_path))
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        samples = data["files"][0]["details"]["samples"]
        assert "SAMPLE1" in samples


class TestBED:
    def test_bed_detected(self, tmp_path, examples_dir):
        r = run_tool("--input", str(examples_dir / "tiny.bed"), "--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        assert data["files"][0]["type"] == "BED"


class TestGTF:
    def test_gtf_detected(self, tmp_path, examples_dir):
        r = run_tool("--input", str(examples_dir / "tiny.gtf"), "--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        assert data["files"][0]["type"] == "GTF"


class TestFragments:
    def test_fragments_detected(self, tmp_path, examples_dir):
        r = run_tool("--input", str(examples_dir / "tiny_fragments.tsv"), "--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        assert "Fragment" in data["files"][0]["type"]


class TestMissingFile:
    def test_missing_file_reported(self, tmp_path):
        r = run_tool("--input", "/nonexistent/path/file.h5ad", "--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "file_inventory.json"
        with open(json_file) as f:
            data = json.load(f)
        assert not data["files"][0]["exists"]
        assert len(data["files"][0]["warnings"]) > 0


class TestJsonValid:
    def test_json_always_valid(self, tmp_path, examples_dir):
        for fname in ["tiny.fa", "tiny.fastq", "tiny.vcf", "tiny.bed", "tiny.gtf",
                      "tiny_counts.csv", "tiny_fragments.tsv", "tiny_peaks.bed"]:
            fpath = examples_dir / fname
            if fpath.exists():
                run_tool("--input", str(fpath), "--output-dir", str(tmp_path / fname))
                json_file = tmp_path / fname / "file_inventory.json"
                assert json_file.exists(), f"JSON not created for {fname}"
                with open(json_file) as f:
                    data = json.load(f)  # Must not raise
                assert "files" in data
