# Genomics QC Report

**Title**: {TITLE}  
**Generated**: {TIMESTAMP}  
**Analyst**: {ANALYST}

---

## Dataset Summary

- **Sample ID(s)**: {SAMPLE_IDS}
- **Species**: {SPECIES}
- **Tissue**: {TISSUE}
- **Disease/condition**: {DISEASE}
- **Protocol**: {PROTOCOL}
- **Chemistry**: {CHEMISTRY}
- **Genome build**: {GENOME_BUILD}
- **Annotation version**: {ANNOTATION_VERSION}
- **n_cells** (if single-cell): {N_CELLS}
- **n_genes** (if single-cell): {N_GENES}

---

## File Provenance

| File | Type | Size (MB) | Source | Hash |
|------|------|-----------|--------|------|
| {FILE_PATH} | {FILE_TYPE} | {FILE_SIZE} | {FILE_SOURCE} | {FILE_HASH} |

---

## Metadata and Assumptions

List all metadata provided and all assumptions made when metadata was missing.

| Field | Value | Source | Assumption? |
|-------|-------|--------|-------------|
| Species | {SPECIES} | {SPECIES_SOURCE} | {SPECIES_ASSUMED} |
| Tissue | {TISSUE} | {TISSUE_SOURCE} | {TISSUE_ASSUMED} |
| Genome build | {GENOME_BUILD} | {BUILD_SOURCE} | {BUILD_ASSUMED} |

---

## Official Claude Life Sciences Tools Used

| Tool | Purpose | Version | Status |
|------|---------|---------|--------|
| {OFFICIAL_TOOL} | {TOOL_PURPOSE} | {TOOL_VERSION} | {TOOL_STATUS} |

---

## Local Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| `inspect_file.py` | v1.0.0 | File inspection |
| `scrna_qc_local.py` | v1.0.0 | scRNA-seq QC fallback |
| `atac_qc_local.py` | v2.0.0 | ATAC QC (bedtools integration, chrom-mismatch detection) |
| `wgs_vcf_qc_local.py` | v2.0.0 | WGS/VCF QC (samtools/bcftools integration) |
| `reference_validator.py` | v1.0.0 | Reference file validation |

---

## Genome Build and Annotation Version

- **Genome build**: {GENOME_BUILD}
- **Annotation version**: {ANNOTATION_VERSION}
- **Chromosome naming style**: {CHROM_STYLE} (UCSC chr-prefix / Ensembl no-prefix)
- **Source**: {BUILD_SOURCE}

> ⚠️ Always confirm genome build from file headers or provider metadata. Never assume.

---

## Reference Files Used

| Reference | Path | Checksum (partial) | Validated |
|-----------|------|--------------------|-----------|
| Genome FASTA | {FASTA_PATH} | {FASTA_MD5} | {FASTA_OK} |
| GTF/GFF | {GTF_PATH} | {GTF_MD5} | {GTF_OK} |
| Blacklist BED | {BLACKLIST_PATH} | {BLACKLIST_MD5} | {BLACKLIST_OK} |
| Known sites VCF | {KNOWN_VCF_PATH} | {KNOWN_VCF_MD5} | {KNOWN_VCF_OK} |

---

## QC Metrics

### scRNA-seq

| Metric | Value | Flag |
|--------|-------|------|
| Total cells | {N_CELLS} | |
| Median total counts | {MEDIAN_COUNTS} | |
| Median genes per cell | {MEDIAN_GENES} | |
| Median mitochondrial % | {MEDIAN_MITO} | |

### ATAC-seq

| Metric | Value | Flag |
|--------|-------|------|
| Total fragments | {N_FRAGMENTS} | |
| FRiP | {FRIP} | |
| Median insert size | {MEDIAN_INSERT} | |
| Number of peaks | {N_PEAKS} | |

### WGS/WES

| Metric | Value | Flag |
|--------|-------|------|
| Total variants | {N_VARIANTS} | |
| SNPs | {N_SNPS} | |
| Indels | {N_INDELS} | |
| Ti/Tv ratio | {TITV} | |
| Het/hom ratio | {HET_HOM} | |

---

## Plots Generated

- {PLOT_LIST}

---

## Recommended Filtering Parameters

> **These are recommendations only.** Do not apply without biological review.

| Metric | Suggested Threshold | Basis | Cells Affected |
|--------|--------------------|----|---------------|
| {METRIC} | {THRESHOLD} | {BASIS} | {N_AFFECTED} |

---

## Biological Justification

For every recommended filter:

1. What was observed?
2. What technical artifact could explain it?
3. What biological state could also explain it?
4. What metadata would help distinguish artifact from biology?
5. What validation should be done?
6. Should data be filtered, flagged, stratified, or preserved?

---

## Technical Artifact vs. Plausible Biology

| Observation | Possible Technical Explanation | Possible Biological Explanation | Evidence Supporting Artifact | Evidence Supporting Biology | Recommended Follow-up | Confidence |
|-------------|-------------------------------|--------------------------------|------------------------------|-----------------------------|-----------------------|------------|
| {OBSERVATION} | {TECH_EXPLANATION} | {BIO_EXPLANATION} | {ARTIFACT_EVIDENCE} | {BIO_EVIDENCE} | {FOLLOWUP} | {CONFIDENCE} |

Confidence scale: `low` / `moderate` / `high`  
Use `high` only when evidence is strong and specific to this dataset.

---

## Skipped Metrics and Missing Inputs

| Metric | Reason Skipped | Required Input | Impact |
|--------|---------------|----------------|--------|
| TSS enrichment | GTF not provided | `--gtf annotation.gtf` | Cannot assess regulatory enrichment |
| Blacklist fraction | Blacklist BED not provided | `--blacklist regions.bed` | Cannot remove artifactual peaks |
| Coverage | samtools/mosdepth not run | External tool | Cannot assess sequencing uniformity |

---

## Limitations

- {LIMITATION_1}
- {LIMITATION_2}

---

## Suggested Next Analyses

- [ ] {NEXT_ANALYSIS_1}
- [ ] {NEXT_ANALYSIS_2}

---

## Commands Run

```bash
{COMMANDS}
```

---

## Software Versions

| Tool | Version |
|------|---------|
| Python | {PYTHON_VERSION} |
| scanpy | {SCANPY_VERSION} |
| anndata | {ANNDATA_VERSION} |
| pysam | {PYSAM_VERSION} |
| numpy | {NUMPY_VERSION} |
| pandas | {PANDAS_VERSION} |
| matplotlib | {MATPLOTLIB_VERSION} |
