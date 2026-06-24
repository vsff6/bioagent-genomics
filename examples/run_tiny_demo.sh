#!/usr/bin/env bash
# run_tiny_demo.sh — End-to-end toy workflow for the genomics-agent workspace.
#
# Runs all six local tools on the tiny example files in examples/ and assembles
# a final report at reports/demo/final_report.md.
#
# Usage:
#   bash examples/run_tiny_demo.sh
#
# Requirements:
#   Python 3.11+ with numpy, pandas, scipy, matplotlib, seaborn, h5py in PATH.
#   Run from the repository root.
#   scanpy/anndata optional — scRNA QC step degrades gracefully without them.
#
# This demo exercises the LOCAL FALLBACK path only.
# In production, use single-cell-rna-qc@life-sciences for scRNA QC
# and nextflow-development@life-sciences for full pipelines.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DEMO_DIR="reports/demo"
mkdir -p "$DEMO_DIR"

PYTHON="${PYTHON:-python}"

echo "============================================================"
echo "  genomics-agent tiny demo"
echo "  $(date)"
echo "  Repo: $REPO_ROOT"
echo "  Output: $DEMO_DIR"
echo "============================================================"
echo ""

# ── Step 1: Environment check ────────────────────────────────────
echo "[1/7] Environment check..."
"$PYTHON" tools/check_environment.py \
  --output-dir "$DEMO_DIR/env_check"
echo ""

# ── Step 2: File inspection ──────────────────────────────────────
echo "[2/7] Inspecting example files..."
"$PYTHON" tools/inspect_file.py \
  --input examples/tiny_counts.csv \
  --output-dir "$DEMO_DIR/inspect"
echo "      → examples/tiny.vcf"
"$PYTHON" tools/inspect_file.py \
  --input examples/tiny.vcf \
  --output-dir "$DEMO_DIR/inspect_vcf"
echo ""

# ── Step 3: Reference validation ────────────────────────────────
echo "[3/7] Validating reference files..."
"$PYTHON" tools/reference_validator.py \
  --gtf examples/tiny.gtf \
  --blacklist examples/tiny.bed \
  --output-dir "$DEMO_DIR/reference_check"
echo ""

# ── Step 4: scRNA-seq QC (local fallback) ───────────────────────
echo "[4/7] scRNA-seq QC (local fallback — official single-cell-rna-qc@life-sciences preferred)..."
"$PYTHON" tools/scrna_qc_local.py \
  --input examples/tiny_counts.csv \
  --species human \
  --tissue unknown \
  --protocol "10x_v3" \
  --chemistry v3 \
  --genome-build GRCh38 \
  --recommend-only \
  --output-dir "$DEMO_DIR/scrna_qc"
echo ""

# ── Step 5: ATAC-seq QC ─────────────────────────────────────────
echo "[5/7] ATAC-seq QC..."
"$PYTHON" tools/atac_qc_local.py \
  --fragments examples/tiny_fragments.tsv \
  --peaks examples/tiny_peaks.bed \
  --gtf examples/tiny.gtf \
  --output-dir "$DEMO_DIR/atac_qc"
echo ""

# ── Step 6: WGS/VCF QC ──────────────────────────────────────────
echo "[6/7] WGS/VCF QC..."
"$PYTHON" tools/wgs_vcf_qc_local.py \
  --vcf examples/tiny.vcf \
  --output-dir "$DEMO_DIR/wgs_qc"
echo ""

# ── Step 7: Final report ────────────────────────────────────────
echo "[7/7] Assembling final report..."
"$PYTHON" tools/report_builder.py \
  --title "Genomics-Agent Tiny Demo Report" \
  --species human \
  --tissue "PBMC (toy data)" \
  --genome-build GRCh38 \
  --scrna-qc-dir "$DEMO_DIR/scrna_qc" \
  --output-dir "$DEMO_DIR" \
  --output-name "final_report.md"
echo ""

echo "============================================================"
echo "  Demo complete."
echo "  Final report: $DEMO_DIR/final_report.md"
echo ""
echo "  NOTE: This demo used the LOCAL FALLBACK tools only."
echo "  For production analysis, prefer:"
echo "    single-cell-rna-qc@life-sciences  (scRNA QC)"
echo "    nextflow-development@life-sciences  (full pipelines)"
echo "    biology-interpretation-reviewer agent (QC review)"
echo "============================================================"
