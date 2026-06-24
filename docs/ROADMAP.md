# Roadmap

## v0.3 (planned)

### Higher-priority items

- **MCP wrappers**: Thin MCP server adapters around the existing CLI tools, enabling Claude Code to call them as structured tools rather than via shell commands. The CLI tools are the implementation; MCP is the interface layer.
- **mosdepth integration**: Structured coverage summary from mosdepth output, analogous to the samtools/bcftools integration in v2.0. Include coverage uniformity, low-coverage region reporting, and WES target enrichment metrics.
- **scRNA-seq h5ad support in local fallback**: Extend `scrna_qc_local.py` to handle `.h5ad` and 10x `.h5` inputs via anndata when scanpy is installed. The official skill remains the preferred path.
- **VCF allele frequency distribution**: Improve AF histogram and summary in the local VCF parser, with notes on somatic vs. germline AF expectations.

### Lower-priority items

- **R workflow documentation**: Add a `docs/R_WORKFLOWS.md` guide covering Seurat, Signac, and DESeq2 integration points with nf-core outputs.
- **Samplesheet generator**: A small utility to build nf-core-compatible samplesheets from a directory of FASTQ or BAM files.
- **Report HTML export**: An optional HTML version of the final report with embedded plots.

## Not planned

The following will remain delegated to dedicated tools:

- Variant annotation (VEP, ANNOVAR)
- Doublet detection (scrublet, scDblFinder)
- Ambient RNA removal (SoupX, DecontX)
- Full alignment pipelines (nf-core/rnaseq, nf-core/sarek, nf-core/atacseq)
- Batch integration and downstream modeling (scvi-tools@life-sciences)
- Clinical interpretation (never)
