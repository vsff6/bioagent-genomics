"""Tests for tools/report_builder.py."""
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TOOL = REPO_ROOT / "tools" / "report_builder.py"


def run_tool(*args):
    return subprocess.run(
        [sys.executable, str(TOOL)] + list(args),
        capture_output=True, text=True,
    )


class TestHelp:
    def test_help_exits_zero(self):
        r = run_tool("--help")
        assert r.returncode == 0


class TestEmptyReport:
    def test_empty_report_runs(self, tmp_path):
        r = run_tool(
            "--title", "Test Report",
            "--output-dir", str(tmp_path),
        )
        assert r.returncode == 0

    def test_report_file_created(self, tmp_path):
        run_tool("--title", "Test Report", "--output-dir", str(tmp_path))
        report = tmp_path / "final_report.md"
        assert report.exists()

    def test_report_has_required_sections(self, tmp_path):
        run_tool("--title", "Test Report", "--output-dir", str(tmp_path))
        content = (tmp_path / "final_report.md").read_text(encoding="utf-8")
        required = [
            "Dataset Summary",
            "File Provenance",
            "Metadata and Assumptions",
            "Official Claude Life Sciences Tools",
            "Local Tools Used",
            "Genome Build",
            "QC Metrics",
            "Biological Justification",
            "Technical Artifact vs. Plausible Biology",
            "Skipped Metrics",
            "Limitations",
            "Commands Run",
            "Software Versions",
        ]
        for section in required:
            assert section in content, f"Missing section: {section}"

    def test_artifact_biology_table_present(self, tmp_path):
        run_tool("--title", "Test Report", "--output-dir", str(tmp_path))
        content = (tmp_path / "final_report.md").read_text(encoding="utf-8")
        assert "Possible Technical Explanation" in content
        assert "Possible Biological Explanation" in content
        assert "Confidence" in content


class TestWithSections:
    def test_with_scrna_qc_dir(self, tmp_path):
        """Test that report picks up scRNA QC outputs if they exist."""
        qc_dir = tmp_path / "scrna_qc"
        qc_dir.mkdir()
        import json
        with open(qc_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump({"tool": "scrna_qc_local.py", "version": "1.0.0",
                       "n_cells": 100, "n_genes": 200, "plots": []}, f)
        (qc_dir / "qc_report.md").write_text("## scRNA QC\n\nTest content.", encoding="utf-8")

        r = run_tool(
            "--title", "Test Report",
            "--scrna-qc-dir", str(qc_dir),
            "--output-dir", str(tmp_path / "report"),
        )
        assert r.returncode == 0
        content = (tmp_path / "report" / "final_report.md").read_text(encoding="utf-8")
        assert "scRNA QC" in content or "scrna_qc_local.py" in content

    def test_custom_title(self, tmp_path):
        run_tool("--title", "My Unique QC Title", "--output-dir", str(tmp_path))
        content = (tmp_path / "final_report.md").read_text(encoding="utf-8")
        assert "My Unique QC Title" in content

    def test_custom_output_name(self, tmp_path):
        run_tool(
            "--title", "Test",
            "--output-dir", str(tmp_path),
            "--output-name", "my_custom_report.md",
        )
        assert (tmp_path / "my_custom_report.md").exists()

    def test_metadata_fields_present(self, tmp_path):
        run_tool(
            "--title", "Test",
            "--species", "human",
            "--tissue", "PBMC",
            "--disease", "healthy",
            "--genome-build", "GRCh38",
            "--output-dir", str(tmp_path),
        )
        content = (tmp_path / "final_report.md").read_text(encoding="utf-8")
        assert "human" in content
        assert "PBMC" in content
        assert "GRCh38" in content
