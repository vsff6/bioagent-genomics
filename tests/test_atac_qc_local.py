"""Tests for tools/atac_qc_local.py."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TOOL = REPO_ROOT / "tools" / "atac_qc_local.py"
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


class TestFragmentsOnly:
    def test_fragments_only_runs(self, tmp_path):
        r = run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        assert r.returncode == 0

    def test_json_written(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        json_file = tmp_path / "atac_qc_summary.json"
        assert json_file.exists()
        with open(json_file) as f:
            data = json.load(f)
        assert data["tool"] == "atac_qc_local.py"

    def test_markdown_written(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        md_file = tmp_path / "atac_qc_report.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "ATAC" in content

    def test_fragments_counted(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        with open(tmp_path / "atac_qc_summary.json") as f:
            data = json.load(f)
        assert data["metrics"]["fragments"]["n_fragments"] == 10

    def test_barcodes_counted(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        with open(tmp_path / "atac_qc_summary.json") as f:
            data = json.load(f)
        assert data["metrics"]["barcodes"]["n_barcodes"] == 3  # 3 unique barcodes in tiny_fragments.tsv


class TestFRiP:
    def test_frip_computed_with_peaks(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--peaks", str(EXAMPLES / "tiny_peaks.bed"),
            "--output-dir", str(tmp_path),
        )
        with open(tmp_path / "atac_qc_summary.json") as f:
            data = json.load(f)
        frip = data["metrics"]["frip"]["frip"]
        assert frip is not None
        assert 0 <= frip <= 1

    def test_frip_skipped_without_peaks(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        with open(tmp_path / "atac_qc_summary.json") as f:
            data = json.load(f)
        # frip should be None or have skipped_reason
        frip_data = data["metrics"].get("frip", {})
        assert frip_data.get("frip") is None or "skipped_reason" in frip_data


class TestSkippedMetrics:
    def test_tss_skipped_without_gtf(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        with open(tmp_path / "atac_qc_summary.json") as f:
            data = json.load(f)
        skipped = {s["metric"] for s in data["skipped_metrics"]}
        assert any("TSS" in m for m in skipped)

    def test_blacklist_skipped_without_blacklist(self, tmp_path):
        run_tool(
            "--fragments", str(EXAMPLES / "tiny_fragments.tsv"),
            "--output-dir", str(tmp_path),
        )
        with open(tmp_path / "atac_qc_summary.json") as f:
            data = json.load(f)
        skipped = {s["metric"] for s in data["skipped_metrics"]}
        assert any("blacklist" in m.lower() or "Blacklist" in m for m in skipped)


class TestNoInputs:
    def test_no_fragments_exits_cleanly(self, tmp_path):
        r = run_tool("--output-dir", str(tmp_path))
        assert r.returncode == 0  # should not crash, just report skipped
        json_file = tmp_path / "atac_qc_summary.json"
        assert json_file.exists()
