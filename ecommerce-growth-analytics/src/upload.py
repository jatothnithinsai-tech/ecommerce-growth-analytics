"""Upload local processed Parquet to an existing S3 bucket."""
import argparse
import json
import boto3
from src.common import ROOT, config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    cfg = config()
    paths = sorted((ROOT / "data/processed/events").glob("event_date=*/*.parquet"))
    if not paths:
        raise SystemExit("No real data to upload.")
    report = ROOT / "data/quality/quality_report.json"
    if not report.exists() or json.loads(report.read_text())["hard_failure"]:
        raise SystemExit("Run src.quality successfully before upload.")
    if any(p.stat().st_mtime > report.stat().st_mtime for p in paths):
        raise SystemExit("Data changed since validation; rerun src.quality.")
    client = None if args.dry_run else boto3.client("s3", region_name=cfg["aws_region"])
    for path in paths:
        relative = path.relative_to(ROOT / "data/processed").as_posix()
        key = f'{cfg["s3_prefix"].strip("/")}/processed/{relative}'
        print(f'{path.name} -> s3://{cfg["s3_bucket"]}/{key}')
        if client:
            client.upload_file(str(path), cfg["s3_bucket"], key)

if __name__ == "__main__":
    main()
