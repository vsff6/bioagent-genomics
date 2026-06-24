"""Tests for tools/wgs_vcf_qc_local.py."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TOOL = REPO_ROOT / "tools" / "wgs_vcf_qc_local.py"
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


class TestVCF:
    def test_vcf_runs(self, tmp_path):
        r = run_tool(
            "--vcf", str(EXAMPLES / "tiny.vcf"),
            "--output-dir", str(tmp_path),
        )
        assert r.returncode == 0

    def test_json_written(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        json_file = tmp_path / "wgs_vcf_qc_summary.json"
        assert json_file.exists()
        with open(json_file) as f:
            data = json.load(f)
        assert data["tool"] == "wgs_vcf_qc_local.py"

    def test_markdown_written(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        md_file = tmp_path / "wgs_vcf_qc_report.md"
        assert md_file.exists()
        content = md_file.read_text(encoding="utf-8")
        assert "clinical" in content.lower()  # Must mention clinical disclaimer

    def test_snp_count(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        vcf_m = data["vcf_metrics"]
        # tiny.vcf has 6 SNPs (single-bp substitutions) and 1 indel
        assert vcf_m["n_snps"] >= 5

    def test_indel_count(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        vcf_m = data["vcf_metrics"]
        assert vcf_m["n_indels"] >= 1

    def test_titv_computed(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        ti_tv = data["vcf_metrics"].get("ti_tv_ratio")
        assert ti_tv is not None
        assert isinstance(ti_tv, (int, float))

    def test_het_hom_computed(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        het_hom = data["vcf_metrics"].get("het_hom_ratio")
        assert het_hom is not None

    def test_samples_detected(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        assert data["vcf_metrics"]["n_samples"] == 1
        assert "SAMPLE1" in data["vcf_metrics"]["samples"]

    def test_no_clinical_claims_in_report(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        md_file = tmp_path / "wgs_vcf_qc_report.md"
        content = md_file.read_text(encoding="utf-8").lower()
        # Report must not make clinical claims or diagnoses
        assert "diagnosis" not in content
        assert "you have" not in content
        # But it IS allowed to say what it does NOT do
        assert "no clinical" in content or "never" in content

    def test_clinical_disclaimer_present(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        assert "clinical_disclaimer" in data
        assert "No clinical claims" in data["clinical_disclaimer"]


class TestSkippedMetrics:
    def test_coverage_skipped_reported(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        skipped = {s["metric"] for s in data["skipped_metrics"]}
        assert any("coverage" in m.lower() or "Coverage" in m for m in skipped)

    def test_bam_skipped_reported(self, tmp_path):
        run_tool("--vcf", str(EXAMPLES / "tiny.vcf"), "--output-dir", str(tmp_path))
        with open(tmp_path / "wgs_vcf_qc_summary.json") as f:
            data = json.load(f)
        skipped = {s["metric"] for s in data["skipped_metrics"]}
        assert any("BAM" in m or "bam" in m.lower() for m in skipped)


class TestNoInputs:
    def test_no_input_exits_cleanly(self, tmp_path):
        r = run_tool("--output-dir", str(tmp_path))
        assert r.returncode == 0
        json_file = tmp_path / "wgs_vcf_qc_summary.json"
        assert json_file.exists()
