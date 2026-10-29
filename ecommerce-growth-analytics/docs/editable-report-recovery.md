# Editable report recovery audit

Checked 28 October 2026. Dashboard redesign remains blocked by the absence of a recovered genuine editable Power BI report. The existing PNG/PDF exports and verified analytical outputs are preserved. No replacement report was generated from the dashboard CSV.

## Evidence checked

- The public repository's complete fetched Git history, branches and tags contain no `.pbix`, `.pbip`, `.pbit`, `.pbir`, `.tmdl` or `.bim` report source. The only current remote branch is `main`.
- Local searches covered Desktop, Documents, Downloads, OneDrive, existing project workspaces, attachments, top-level ZIP archives and Power BI Desktop's AutoRecovery directory. Recovered PBIX files were inspected by report page inventories; they belong to the map exercise, Transit and financial complaints projects, rather than this report.
- The public report materials include the original Power BI Service PNG/PDF, a 205-row, 27-column dashboard CSV, a report manifest and reusable DAX definitions. These are useful analytical artifacts but do not recover the authored report's model, layout, interactions or full calculation context.
- No connected document session was available. The in-app browser connection failed during startup with missing `sandboxPolicy` metadata, before any authenticated Power BI page could be inspected.

## Remaining recovery route

The project documentation records that the report was authored in Power BI Service on macOS. Its authenticated workspace has not been inspected in this audit, so the report's continued availability there is unverified. If the original report remains accessible and its download settings allow it, download the genuine PBIX from that workspace and validate it before redesign. Credentials are not needed in this repository.

No editable source was found in the locations inspected. This does not establish that the source is unavailable in every cloud workspace or backup. Report calculations and exported visuals have not been replaced, and no new redesign or interaction test is claimed.
