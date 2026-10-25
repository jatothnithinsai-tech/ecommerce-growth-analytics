# Full-period data pipeline

Status: 92 dates extracted, cleaned and reconciled. Existing raw files are preserved.

## Authentication (once)
Install Google Cloud CLI from https://cloud.google.com/sdk/docs/install and run:

```bash
gcloud auth application-default login
```

Use the account with access to axial-serenity-512520-r8. Credentials remain outside the repository. Browser console login alone does not authenticate Python.

## Run in order from this project directory

```bash
.venv/bin/python src/run_data_pipeline.py --stage extract
.venv/bin/python src/run_data_pipeline.py --stage clean
.venv/bin/python src/run_data_pipeline.py --stage validate
```

Or execute all three in sequence:

```bash
.venv/bin/python src/run_data_pipeline.py
```

Extraction performs dry runs before downloading and enforces 1 GB per query and 10 GB total estimated bytes for pending dates. These are query limits, not monetary spending caps. Review before changing them. Exports are saved atomically, existing raw files are checked and reused, and each date reconciles against daily_event_coverage.csv. A rerun retries missing dates. Inspect any failed temporary export before removing it.

Cleaning writes daily CSV files directly to data/processed without an events subfolder. It preserves rows and nulls and writes daily quality JSON reports in data/quality/daily_reports/. Validation reconciles every date's counts and checksums and creates daily_reconciliation.csv and pipeline_validation_summary.json in data/quality. These results do not resolve instrumentation limitations or establish causal claims.

The .venv currently uses system site packages; requirements.txt describes dependencies, not an exact reproducible lock file. No GitHub push is performed.
