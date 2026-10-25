# Power BI build specification

No .pbix has been generated. Use Power BI Desktop on Windows.

## Initial import
Export Athena query results as CSV into data/analytics. Import sessions, session_funnel, acquisition results and retention results. Keep aggregate result tables independent unless a verified relationship is needed. Use distinct user/session pairs as keys; do not relate tables on ga_session_id alone.

For a first report, start with CSV import. Direct Athena connectivity requires the supported driver/DSN setup in Microsoft's connector documentation. Scheduled service refresh can require a configured gateway and credentials.

## Pages
1. Executive: observed users, eligible sessions, purchase sessions, purchase rate, daily trend. Add validated revenue only after transaction reconciliation.
2. Journey: ordered stages, stage losses, device segments. Filter funnel through a session dimension with a collision-safe user/session key.
3. Acquisition: first-user source/medium, sessions, engagement coverage, engagement rate and purchase rate. Do not label as session channels.
4. Retention: cohort-week heatmap, cohort sizes, complete-week availability, observed new/subsequent session comparison.

Format percentages consistently; display denominators and date filters. Show unavailable retention cells as blank. Include a visible sample-data limitation note.

Reference: https://learn.microsoft.com/en-us/power-query/connectors/amazon-athena
