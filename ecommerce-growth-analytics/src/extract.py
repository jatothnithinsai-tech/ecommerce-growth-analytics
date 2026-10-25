"""Extract flattened real GA4 events, one date per file. Requires GCP authentication."""
import argparse
from datetime import date, timedelta
from google.cloud import bigquery
from src.common import ROOT, config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not date(2020, 11, 1) <= args.start <= args.end <= date(2021, 1, 31):
        parser.error("Dates must be ordered and within 2020-11-01 through 2021-01-31.")
    cfg = config()
    client = bigquery.Client(project=cfg["gcp_project_id"], location=cfg["bigquery_location"])
    sql = (ROOT / "sql/bigquery/01_extract_events.sql").read_text()
    day = args.start
    while day <= args.end:
        output = ROOT / "data/processed/events" / f"event_date={day.isoformat()}" / "events.parquet"
        if output.exists() and not args.overwrite:
            print(f"Skipping existing {output}")
            day += timedelta(days=1)
            continue
        params = [bigquery.ScalarQueryParameter(name, "STRING", day.strftime("%Y%m%d"))
                  for name in ("start_suffix", "end_suffix")]
        preview = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params, dry_run=True, use_query_cache=False))
        estimated = preview.total_bytes_processed or 0
        print(f"{day}: estimated scan {estimated:,} bytes")
        if estimated > cfg["maximum_bytes_billed"]:
            raise SystemExit("Estimated scan exceeds configured per-query byte limit.")
        job = client.query(sql, job_config=bigquery.QueryJobConfig(
            query_parameters=params, maximum_bytes_billed=cfg["maximum_bytes_billed"]))
        frame = job.result().to_dataframe(create_bqstorage_client=False)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Date is encoded in the Hive partition folder, not repeated in file schema.
        temp = output.with_suffix(".parquet.tmp")
        frame.drop(columns=["event_date"]).to_parquet(temp, index=False)
        temp.replace(output)
        print(f"Saved {len(frame):,} real event rows to {output}")
        day += timedelta(days=1)

if __name__ == "__main__":
    main()
