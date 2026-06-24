"""Tests for tools/scrna_qc_local.py."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TOOL = REPO_ROOT / "tools" / "scrna_qc_local.py"
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
        assert "scrna" in r.stdout.lower() or "input" in r.stdout.lower()


class TestMissingScanpy:
    """These tests verify the tool handles missing scanpy gracefully."""

    def test_csv_input_no_crash(self, tmp_path):
        """Tool should run on CSV without crashing, even if scanpy unavailable."""
        r = run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        # Tool should either succeed (scanpy available) or fail gracefully
        # returncode 0 = success; 1 = scanpy missing (graceful)
        assert r.returncode in (0, 1), f"Unexpected exit code: {r.returncode}\n{r.stderr}"

    def test_json_always_written(self, tmp_path):
        """JSON summary should always be written, even on scanpy-missing failure."""
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        json_file = tmp_path / "summary.json"
        assert json_file.exists(), "summary.json not created"
        with open(json_file) as f:
            data = json.load(f)
        assert "tool" in data


class TestWithScanpy:
    """Run only if scanpy is installed."""
    @pytest.fixture(autouse=True)
    def check_scanpy(self):
        try:
            import scanpy  # noqa
        except ImportError:
            pytest.skip("scanpy not installed")

    def test_csv_qc_runs(self, tmp_path):
        r = run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        assert r.returncode == 0, f"Tool failed:\n{r.stderr}"

    def test_qc_metrics_csv_written(self, tmp_path):
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        csv_file = tmp_path / "qc_metrics.csv"
        assert csv_file.exists(), "qc_metrics.csv not written"

    def test_markdown_report_written(self, tmp_path):
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        md_file = tmp_path / "qc_report.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "# scRNA-seq QC Report" in content
        assert "Biological" in content or "biological" in content

    def test_json_has_cells_and_genes(self, tmp_path):
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        with open(tmp_path / "summary.json") as f:
            data = json.load(f)
        assert data["n_cells"] == 10
        assert data["n_genes"] == 13

    def test_mito_genes_detected(self, tmp_path):
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        with open(tmp_path / "summary.json") as f:
            data = json.load(f)
        # tiny_counts.csv has MT-CO1, MT-ND1, MT-ATP6
        assert data.get("n_mito_genes", 0) >= 3, "Mitochondrial genes not detected"

    def test_filters_not_applied_with_recommend_only(self, tmp_path):
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        with open(tmp_path / "summary.json") as f:
            data = json.load(f)
        # With --recommend-only, all 10 cells should still be reported
        assert data["n_cells"] == 10

    def test_filter_suggestions_have_biological_notes(self, tmp_path):
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        with open(tmp_path / "summary.json") as f:
            data = json.load(f)
        for s in data.get("filter_suggestions", []):
            assert "biological_note" in s, f"Missing biological_note in suggestion: {s}"
            assert len(s["biological_note"]) > 10
            # Verify all 7 required filter decision elements are present
            fdf = s.get("filter_decision_framework", {})
            assert fdf, f"Missing filter_decision_framework in suggestion: {s['metric']}"
            for bound, details in fdf.items():
                assert "technical_artifact" in details, f"{s['metric']}/{bound} missing technical_artifact"
                assert "biological_signal" in details, f"{s['metric']}/{bound} missing biological_signal"
                assert "evidence_for_filtering" in details, f"{s['metric']}/{bound} missing evidence_for_filtering"
                assert "evidence_against_filtering" in details, f"{s['metric']}/{bound} missing evidence_against_filtering"
                action_key = f"recommended_action_{bound}"
                assert action_key in details, f"{s['metric']}/{bound} missing {action_key}"
            assert "validation_note" in s, f"{s['metric']} missing validation_note"

    def test_json_has_fallback_note_and_primary_path(self, tmp_path):
        """JSON summary must declare fallback status and official primary path."""
        run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "human",
            "--tissue", "pbmc",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        with open(tmp_path / "summary.json") as f:
            data = json.load(f)
        assert "fallback_note" in data, "summary.json missing fallback_note"
        assert data["fallback_note"], "fallback_note must be non-empty"
        assert "single-cell-rna-qc@life-sciences" in data["fallback_note"], (
            "fallback_note must reference the official skill"
        )
        assert "primary_path" in data, "summary.json missing primary_path"
        assert "single-cell-rna-qc@life-sciences" in data["primary_path"], (
            "primary_path must name the official skill"
        )

    def test_mouse_mito_prefix(self, tmp_path):
        r = run_tool(
            "--input", str(EXAMPLES / "tiny_counts.csv"),
            "--species", "mouse",
            "--tissue", "unknown",
            "--output-dir", str(tmp_path),
            "--recommend-only",
        )
        assert r.returncode == 0
        with open(tmp_path / "summary.json") as f:
            data = json.load(f)
        # Mouse uses mt- prefix; tiny_counts.csv has MT- prefix, so 0 expected
        assert "mito_prefixes_used" in data
        assert any("mt-" in p.lower() for p in data["mito_prefixes_used"])
