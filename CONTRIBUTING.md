# Contributing

## Setup

```bash
conda env create -f env/environment.yml
conda activate genomics-agent
pip install pytest pytest-cov
```

## Running tests

```bash
pytest tests/ -v
```

Tests are designed to run without samtools, bcftools, or bedtools installed. Parser tests use fixture files in `tests/fixtures/`. External-tool degradation is verified by checking that tools produce structured skip entries in JSON output.

## Adding a metric

1. Implement the computation as a pure function importable from the tool module.
2. Add a skipped-metric entry with `missing_biological_conclusion` and `enable_with` for cases where the metric cannot be computed.
3. Write fixture-based tests for the pure function.
4. Update `docs/IMPLEMENTATION_STATUS.md`.

## Biological reasoning requirement

Every new QC warning or skipped metric must address:

- What technical artifact could explain the observation?
- What biological state could also explain it?
- What metadata or validation would help distinguish the two?

This is enforced by tests in `tests/test_external_tools.py` and `tests/test_atac_qc_local.py`.

## Clinical safety

No tool in this repository may make clinical claims or recommend medical action. See `CLAUDE.md` and `SECURITY.md`.
