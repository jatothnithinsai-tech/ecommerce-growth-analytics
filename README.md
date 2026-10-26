# Ecommerce Growth & Customer Journey Analytics

GA4 ecommerce analysis with Python, SQL, AWS S3 and Athena, and a colorful Power BI report. The analysis covers 4,295,584 events across 92 days (November 2020–January 2021).

## Power BI dashboard

![All-in-one Power BI dashboard](ecommerce-growth-analytics/powerbi/ecommerce-growth-dashboard.png)

The report includes executive overview, customer journey, acquisition, weekly retention, daily trends, device performance, and an all-in-one summary page.

[Power BI files and documentation](ecommerce-growth-analytics/powerbi/) · [Download dashboard PDF](ecommerce-growth-analytics/powerbi/ecommerce-growth-dashboard.pdf) · [Project documentation](ecommerce-growth-analytics/README.md)

The Power BI folder contains the actual dashboard PNG/PDF exports, aggregate import CSV, optional DAX measures, and a report manifest. The interactive report remains in the authenticated Power BI workspace; a PBIX file is not included.

## Results at a glance

- 270,154 observed users and 360,129 sessions.
- 4,848 purchasing sessions: 1.35% overall session purchase rate.
- Ordered product-view funnel: 77,020 views → 14,380 carts → 5,187 checkouts → 2,778 purchases.

This project uses an obfuscated GA4 sample. Findings are observational; no A/B experiment was run. See the project documentation for definitions and limitations.
