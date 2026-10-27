# SQL analysis and validation

The project uses **BigQuery SQL for acquisition** and **Athena SQL for the session model and analysis**. Their dialects and object names differ; run each file in its intended engine.

## BigQuery

[bigquery/](bigquery/) contains source previews, parameterized extraction queries, complete-day exports and the daily coverage query for the 92-day source period. The Python pipeline uses `01_extract_events.sql` with date suffix parameters. Use your own authorized billing project and review query limits before execution.

## Athena

Run metadata and validation files before analytical SELECTs:

1. `00_create_database.sql`, `01_create_events.sql` and `01b_register_partitions.sql` define the catalog and date partitions.
2. `01c_verify_upload.sql`, `02_sessions.sql` and `02b_validate_sessions.sql` establish upload and session checks.
3. `03_ordered_funnel.sql` / `03b_funnel_summary.sql` define the chronological, same-session funnel.
4. The later files cover first-user acquisition, weekly cohorts, data quality, device funnels, session segmentation and daily trends.

`07_new_returning.sql` is an earlier alternative. `09_first_vs_subsequent_sessions.sql` is the version represented in the saved segmentation output.

## Evidence and execution scope

The repository retains [aggregate analysis exports](../data/analytics/), [quality outputs](../data/quality/) and an [AWS configuration record](../aws/deployment_config.json). These document the historical analysis; this portfolio documentation review did not execute cloud queries. The cloud setup is no longer required for reading the exported results.

Replace original bucket/project names with your own settings before reproducing. See the [AWS guide](../aws/README.md) and [pipeline guide](../docs/run_data_pipeline.md). Ordered-funnel purchasing sessions differ from all purchasing sessions, and first-user attribution is not session attribution.
