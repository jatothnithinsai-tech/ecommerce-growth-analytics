"""Validate each local event partition without loading all dates into memory."""
import json
from datetime import datetime, timezone
import pandas as pd
from src.common import ROOT


def main():
    paths = sorted((ROOT / "data/processed/events").glob("event_date=*/*.parquet"))
    if not paths:
        raise SystemExit("No real data found. Run src.extract first.")
    required = {"event_name", "event_timestamp", "user_pseudo_id", "ga_session_id", "transaction_id", "purchase_revenue_in_usd"}
    reports = []
    failed = False
    for path in paths:
        df = pd.read_parquet(path)
        missing = sorted(required - set(df.columns))
        row = {"file": str(path.relative_to(ROOT)), "rows": len(df), "missing_columns": missing}
        if not missing:
            row.update({
                "null_event_names": int(df.event_name.isna().sum()),
                "null_event_timestamps": int(df.event_timestamp.isna().sum()),
                "missing_user_ids": int(df.user_pseudo_id.isna().sum()),
                "missing_session_ids": int(df.ga_session_id.isna().sum()),
                "purchase_events": int(df.event_name.eq("purchase").sum()),
                "purchase_revenue_usd_raw": float(df.loc[df.event_name.eq("purchase"), "purchase_revenue_in_usd"].sum()),
                "repeated_purchase_transaction_rows_within_partition": int(df.loc[
                    df.event_name.eq("purchase") & df.transaction_id.notna(), "transaction_id"].duplicated().sum())
            })
        row["hard_failure"] = bool(missing or not len(df) or row.get("null_event_names", 0) or row.get("null_event_timestamps", 0))
        failed |= row["hard_failure"]
        reports.append(row)
    output = ROOT / "data/quality/quality_report.json"
    output.write_text(json.dumps({"generated_utc": datetime.now(timezone.utc).isoformat(), "hard_failure": failed,
        "note": "Missing identifiers and repeated transaction rows require review; they are not automatically removed. Run Athena checks for duplicates across dates.",
        "partitions": reports}, indent=2))
    print(f"Quality report: {output}")
    if failed:
        raise SystemExit("Quality checks failed. Review report before upload.")

if __name__ == "__main__":
    main()
