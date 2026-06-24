# Security

## Genomic data privacy

Human genomic data is privacy-sensitive by default in this project.

- Do not commit real patient or participant genomic data to this repository.
- Do not pass private genomic data to external services without explicit authorization and appropriate data governance agreements.
- Local tools (`tools/`) run entirely on-premises and do not transmit data externally.
- Official Anthropic Life Sciences skills should be evaluated for data handling policies before use with private data.

## No clinical claims

This project provides exploratory QC summaries only. No tool in this repository makes clinical claims, diagnoses, or medical recommendations. See `CLAUDE.md` for the full clinical safety guardrails.

## Reporting vulnerabilities

If you discover a security issue in this project, please report it by opening a GitHub issue marked **[SECURITY]**, or contact the repository maintainer directly before disclosure.

Do not open public issues for vulnerabilities that involve real genomic data.

## Scope

This repository contains code and configuration files only. No genomic data, patient records, or identifying information is included.
