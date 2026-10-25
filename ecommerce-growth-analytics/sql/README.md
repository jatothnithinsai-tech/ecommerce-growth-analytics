# SQL queries

## BigQuery: data acquisition and validation
- `bigquery/00_preview_events.sql`: original 1,000-row preview, already run manually.
- `bigquery/01_extract_events.sql`: parameterized extraction used by the Python pipeline; requires start_suffix/end_suffix parameters. Not the manual CSV export.
- `bigquery/02_export_complete_day.sql`: complete November 1 export, already run manually.
- `bigquery/03_daily_event_coverage.sql`: three-month daily coverage check; inspect the downloaded results before conclusions.

## Athena: later analysis
The numbered files in `athena/` are starter queries for the planned AWS stage. They have not been validated against a deployed dataset. Run in numeric order after setting up the S3 table. These use Athena SQL, not BigQuery SQL.

Keep future queries here with descriptive filenames and comments describing their purpose. Saving a query does not mean it has been executed or its output validated.
