# Demo Output Excerpts

Short synthetic excerpts showing the output structure of each tool. These are representative samples, not real genomic data.

---

## Environment check

`reports/env_check/environment_check.json` (excerpt):

```json
{
  "tool": "check_environment.py",
  "version": "1.0.0",
  "summary": {
    "n_ok": 8,
    "n_warnings": 16,
    "n_failures": 0,
    "ready": true
  }
}
```

---

## ATAC-seq QC

`reports/atac_qc/atac_qc_summary.json` (excerpt):

```json
{
  "tool": "atac_qc_local.py",
  "version": "2.0.0",
  "bedtools_available": false,
  "metrics": {
    "fragments": { "n_fragments": 4 },
    "insert_sizes": {
      "n_sampled": 4,
      "median": 225.0,
      "mean": 243.75
    },
    "frip": {
      "frip": 0.5,
      "n_total_fragments": 4,
      "n_fragments_in_peaks": 2,
      "note": "FRiP computed by local Python interval overlap (streaming fallback)."
    },
    "peaks": {
      "n_peaks": 3,
      "median_peak_width_bp": 350.0
    }
  },
  "skipped_metrics": [
    {
      "metric": "Blacklist fraction",
      "reason": "Blacklist BED not provided",
      "missing_biological_conclusion": "Cannot determine what fraction of reads overlap problematic genomic regions...",
      "enable_with": "--blacklist /path/to/blacklist.bed"
    },
    {
      "metric": "TSS enrichment",
      "reason": "GTF provided but TSS enrichment calculation not implemented in local tool.",
      "missing_biological_conclusion": "Cannot assess regulatory signal enrichment even though GTF was provided.",
      "enable_with": "conda install -c bioconda deeptools  +  --bam aligned.bam"
    }
  ]
}
```

---

## WGS/VCF QC

`reports/wgs_qc/wgs_vcf_qc_summary.json` (excerpt):

```json
{
  "tool": "wgs_vcf_qc_local.py",
  "version": "2.0.0",
  "samtools_available": false,
  "bcftools_available": false,
  "vcf_metrics": {
    "n_snps": 6,
    "n_indels": 1,
    "ti_tv_ratio": 2.0,
    "het_hom_ratio": 0.857,
    "n_samples": 1,
    "note": "Ti/Tv interpretation: WGS ~2.0-2.1, WES ~2.8-3.0. No clinical interpretation provided."
  },
  "clinical_disclaimer": "No clinical claims are made. Do not use for medical decisions."
}
```

---

## Reference validation

`reports/reference_check/reference_validation_summary.json` (excerpt):

```json
{
  "gtf": {
    "path": "examples/tiny.gtf",
    "exists": true,
    "chrom_style": "ucsc",
    "example_chroms": ["chr1"]
  }
}
```

---

## Skipped metric structure

Every unavailable metric follows this structure to ensure no biological conclusion is silently dropped:

```json
{
  "metric": "Coverage statistics",
  "reason": "Requires mosdepth or samtools depth with full BAM.",
  "missing_biological_conclusion": "Cannot determine whether sequencing depth is sufficient for confident variant calling...",
  "enable_with": "mosdepth --quantize 0:5:10:30: output.prefix input.bam"
}
```
