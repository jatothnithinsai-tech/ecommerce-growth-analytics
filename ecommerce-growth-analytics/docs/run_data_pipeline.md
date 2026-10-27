# Full-period data pipeline

Status: 92 dates extracted, cleaned and reconciled. Existing raw files are preserved.

## Authentication (once)
Install Google Cloud CLI from https://cloud.google.com/sdk/docs/install and run:

```bash
gcloud auth application-default login
```

Use your own authorized Google Cloud project and put its ID in `config.json`. The original project ID is historical configuration, not an account that a new user should request access to. Credentials remain outside the repository. Browser console login alone does not authenticate Python.

## Run in order from the nested project directory

From the cloned repository root, first run `cd ecommerce-growth-analytics`. Install `requirements.txt` into your virtual environment and copy `config.example.json` to an ignored `config.json`. Align project, region and bucket settings with your own resources.

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

The original environment used system site packages. For a new setup, create a dedicated virtual environment and install `requirements.txt`; it describes dependency ranges, not an exact lock file. This pipeline does not publish to GitHub.
