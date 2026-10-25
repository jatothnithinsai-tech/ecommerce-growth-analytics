# Ecommerce Growth Analytics

## Status
All 92 dates (2020-11-01 to 2021-01-31) are extracted, cleaned and reconciled: 4,295,584 event rows preserved. AWS S3/Athena setup and aggregate SQL exports are complete. Python statistical analysis and Power BI remain pending. AWS cleanup has not been performed.

## Folder guide
- data/raw/: 92 original daily CSVs. Preserve unchanged.
- data/processed/: 92 cleaned daily CSVs.
- data/aws_ready/: 92 verified Snappy Parquet files, partitioned by event_date, prepared for S3 upload.
- data/quality/daily_reports/: detailed daily validation JSON files.
- data/quality/logs/: technical run logs.
- data/quality/: expected coverage, reconciliation, overall summary and extraction manifest.
- data/analytics/: future analysis results; currently empty.
- sql/bigquery/: extraction/coverage SQL and saved-query web shortcuts.
- sql/athena/: planned AWS SQL, not yet executed.
- src/: Python scripts.
- docs/run_data_pipeline.md: pipeline run instructions.
- aws/: AWS setup guide.
- powerbi/: dashboard specification and DAX starters.

## Active pipeline
Run from this project directory:

```bash
.venv/bin/python src/run_data_pipeline.py --stage extract
.venv/bin/python src/run_data_pipeline.py --stage clean
.venv/bin/python src/run_data_pipeline.py --stage validate
```

run_data_pipeline.py orchestrates the active CSV workflow; clean_csv.py performs daily cleaning. extract.py, quality.py and upload.py are earlier Parquet workflow starters, not active CSV commands. Review them during AWS preparation before use.

## Limitations
Engagement flags are incomplete on all 92 days. Cart-event counts are below checkout counts on 26 dates. Preserve warnings and investigate before funnel interpretation. Missing values remain missing and identifiers are text. Validation reconciles counts and checksums; it does not establish instrumentation completeness or validated net revenue.

Google obfuscated historical source: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset

First-user acquisition is distinct from session attribution. First observed users are not verified first-ever customers. No real controlled experiment is present. Raw data and credentials remain excluded from Git. Cloud costs depend on usage. Power BI Desktop requires Windows.

## Prepare AWS files
Run `python src/prepare_parquet.py` with pandas and pyarrow installed. Schema and conversion checks are in `data/quality/parquet_conversion_report.json`. The date is stored in the partition path. Identifiers remain strings; review the earlier Athena table schema before use. No upload is performed.

## Results available now
- 360,129 observed sessions; 270,154 pseudonymous users.
- 4,848 purchasing sessions across all observed sessions.
- Strict funnel: 77,020 product-view sessions → 14,380 cart → 5,187 checkout → 2,778 purchases (3.61%). This is a different denominator from overall session purchase rate.
- Acquisition, device, first/subsequent session, daily trend and cohort summaries are in data/analytics/.

## Reproduce and inspect
See docs/run_data_pipeline.md and aws/README.md. Aggregate CSVs and selected quality reports are committed for review. Full raw, cleaned and Parquet event files, local environments, logs and credentials are excluded. No passwords, tokens or cloud credential files are required to review the repository. Cloud execution requires your own authorized accounts.

## Portfolio status
This is an in-progress project. The Power BI directory contains specifications and starter measures, not a completed dashboard. No A/B intervention was performed and no causal effect is claimed. Do not describe the current work as a finished production system.
