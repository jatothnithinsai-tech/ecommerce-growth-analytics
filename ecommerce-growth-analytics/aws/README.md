# AWS deployment record and reproduction

The project was configured manually in the AWS console, not deployed by Terraform or CloudFormation. deployment_config.json records the configuration, without credentials. Workgroup is primary; region is eu-north-1.

## Recreate
1. Create a private general-purpose S3 bucket with ACLs disabled, public access blocked and SSE-S3 encryption. Use a unique name if the recorded name is unavailable.
2. Run src/prepare_parquet.py after validating the cleaned data. Upload the contents under Data/aws_ready/, preserving event_date=YYYY-MM-DD folders.
3. Set Athena result output to query-results/ in the same bucket, with SSE-S3.
4. Update the bucket in sql/athena/01_create_events.sql if needed.
5. Execute 00_create_database.sql, 01_create_events.sql, 01b_register_partitions.sql and 01c_verify_upload.sql one statement at a time. Expected: 4,295,584 rows across 92 dates.
6. Execute 02_sessions.sql then 03_ordered_funnel.sql; use remaining SELECT queries to export aggregate results. The 07_new_returning.sql file is an earlier alternative segmentation; 09_first_vs_subsequent_sessions.sql is the executed version represented in analytics outputs.

SQL defines Glue Data Catalog metadata through Athena; no crawler or paid Glue ETL job was required. Python upload.py is an earlier starter and does not implement this console-upload layout.

## Cleanup status
No resources have been deleted by the agent. Before cleanup, verify the GitHub push and local raw, processed and Parquet checksums. GitHub contains code and aggregate results, not the full event-level data backup. Keep a separate copy of local data if you require protection against disk loss.

After backup verification: empty and delete this project's S3 bucket (including query results), then drop only ga4_growth views/tables/database. These are project-specific resources; do not delete unrelated resources or the AWS account. Verify S3 is empty and check Billing across regions. Console sign-out does not stop storage usage. Actual cleanup must be recorded when performed.
