# Power BI — Ecommerce Growth & Customer Journey

![Colorful all-in-one Power BI dashboard](ecommerce-growth-dashboard.png)

[Download the one-page dashboard PDF](ecommerce-growth-dashboard.pdf)

## Completed report

The report was authored and saved in Power BI Service on a Mac. It contains six detail pages and a final **All-in-One Dashboard** combining every section:

1. Executive Overview
2. Customer Journey
3. Acquisition
4. Weekly Retention
5. Daily Trends
6. Device Performance
7. All-in-One Dashboard

The PNG and PDF are exports of the actual Power BI report, not a Python mockup. The interactive report remains in its authenticated Power BI workspace. No `.pbix` file has been exported or included.

## Files

- `ecommerce-growth-dashboard.png`: colorful combined page for the GitHub portfolio.
- `ecommerce-growth-dashboard.pdf`: the same dashboard on one PDF page.
- `dashboard_data.csv`: the 205-row, 27-column aggregate presentation dataset imported into Power BI as `DashboardData`.
- `measures.dax`: reusable measure definitions; the completed browser report uses explicit visual-level filters and precomputed aggregate fields. This file is a reproducibility aid, not a claim that every listed measure was installed in the model.
- `report_manifest.json`: page inventory, dataset summary, display palette, and model safeguards.

## Verified metrics

Period: **1 November 2020–31 January 2021** (92 days).

| Metric | Value |
|---|---:|
| Event rows | 4,295,584 |
| Observed pseudonymous users | 270,154 |
| Sessions | 360,129 |
| Purchasing sessions | 4,848 |
| Overall session purchase rate | 1.35% |
| Ordered funnel: product view | 77,020 |
| Ordered funnel: add to cart | 14,380 |
| Ordered funnel: checkout | 5,187 |
| Ordered funnel: purchase | 2,778 |
| Ordered view-to-purchase rate | 3.61% |

Overall purchase rate and ordered-funnel conversion have different denominators.

## Rebuild and interpret

Import `dashboard_data.csv` into Power BI and name its table `DashboardData`. Counts should be whole numbers, dates should be dates, rates should be decimal numbers formatted as percentages, and WeekNumber should be a categorical key when used as matrix columns.

The flat dataset combines different aggregate grains. **Do not sum across RowType values.** Scope each visual to the applicable RowType: Overview, Daily, Funnel, Acquisition, Device, or Cohort. Cards use Overview; the daily line uses Daily; the ordered funnel uses Funnel; acquisition uses Acquisition; device conversion uses Device. The cohort matrix uses CohortWeek rows, WeekNumber columns and RetentionRate values. Disable row, column and grand totals for retention. Each cohort/week cell has one precomputed rate. Unavailable future weeks stay blank; observed zero-return weeks remain zero.

First-user source is acquisition attribution, not session attribution. Do not add distinct-user counts across categories or dates. When regrouping rates, calculate ratios from the correct numerator and denominator rather than summing precomputed percentages. Unrelated RowTypes should not cross-filter each other.

The display uses Power BI's Electric color palette, pastel blue/pink/orange/cyan KPI backgrounds, purple/pink/orange/mint funnel stages, pink acquisition bars, orange device bars and a soft lavender canvas. The final summary uses a 1920 × 1080 canvas; the six detail pages use 1280 × 720 canvases.

## Statistical and data limits

Mobile's ordered conversion is 3.77%, desktop's 3.50%, and tablet's 3.59%. The mobile–desktop difference is approximately +0.274 percentage points; a user-cluster bootstrap 95% interval is approximately [−0.004, +0.545] points and includes zero. The device comparison is exploratory and does not establish a causal effect. No A/B experiment was run.

The source is Google's obfuscated historical GA4 ecommerce sample. Users are observed pseudonymous identifiers, not verified people or first-ever customers. Engagement flags are incomplete. No validated net revenue metric is included. AWS resources are not required to view these aggregate exports.
