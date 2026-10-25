"""Run extract, clean, validate in that order. Raw data remains unchanged.
Uses Application Default Credentials for BigQuery, never embedded credentials.
"""
import argparse
import csv
from datetime import date, timedelta, datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['event_date','event_timestamp','event_name','user_pseudo_id','user_first_touch_timestamp',
            'ga_session_id','engagement_time_msec','session_engaged','device_category','country',
            'first_user_source','first_user_medium','transaction_id','purchase_revenue_in_usd','refund_value_in_usd']
METRICS = {'product_view_events':'view_item','add_to_cart_events':'add_to_cart',
           'checkout_events':'begin_checkout','purchase_events':'purchase'}


def coverage():
    path = ROOT/'data/quality/daily_event_coverage.csv'
    with path.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    result = {r['event_date']:r for r in rows}
    if len(result) != len(rows):
        raise ValueError('Coverage file has duplicate dates.')
    return result


def inspect(path, expected, cleaned=False):
    from collections import Counter
    counts = Counter()
    users=set()
    missing=0
    count=0
    dates=set()
    with path.open(newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not set(REQUIRED).issubset(reader.fieldnames or []):
            raise ValueError(f'Missing fields: {path.name}')
        for row in reader:
            count+=1
            counts[row['event_name']]+=1
            dates.add(row['event_date'].replace('-',''))
            if row['user_pseudo_id']: users.add(row['user_pseudo_id'])
            else: missing+=1
    actual={'total_events':count,'observed_users':len(users),'missing_user_ids':missing}
    actual.update({key:counts[event] for key,event in METRICS.items()})
    diffs={k:{'expected':int(expected[k]),'actual':v} for k,v in actual.items() if v!=int(expected[k])}
    if dates!={expected['event_date'].replace('-','')}: diffs['dates']=sorted(dates)
    if diffs: raise ValueError(f'Reconciliation failed for {path.name}: {diffs}')
    return actual


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):h.update(chunk)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['all','extract','clean','validate'], default='all')
    parser.add_argument('--start', type=date.fromisoformat, default=date(2020,11,1))
    parser.add_argument('--end', type=date.fromisoformat, default=date(2021,1,31))
    parser.add_argument('--project', default='axial-serenity-512520-r8')
    parser.add_argument('--max-daily-bytes',type=int,default=1_000_000_000)
    parser.add_argument('--max-total-bytes',type=int,default=10_000_000_000)
    args=parser.parse_args()
    if not date(2020,11,1)<=args.start<=args.end<=date(2021,1,31):
        parser.error('Dates must be ordered within the sample period.')
    expected=coverage()
    days=[args.start+timedelta(days=i) for i in range((args.end-args.start).days+1)]
    for day in days:
        if day.isoformat() not in expected:raise ValueError(f'Missing coverage for {day}')
    raw_dir=ROOT/'data/raw';raw_dir.mkdir(exist_ok=True,parents=True)
    quality=ROOT/'data/quality';quality.mkdir(exist_ok=True,parents=True)
    manifest_path=quality/'extraction_manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if args.stage in ('all','extract'):
        pending=[d for d in days if not (raw_dir/f'google_store_events_raw_{d}.csv').exists()]
        if pending:
            from google.cloud import bigquery
            from google.auth.exceptions import DefaultCredentialsError
            try:client=bigquery.Client(project=args.project,location='US')
            except DefaultCredentialsError:
                raise SystemExit('Google sign-in required: install Google Cloud CLI, then run gcloud auth application-default login. No data downloaded.')
            template=(ROOT/'sql/bigquery/04_extract_daily_events.sql').read_text()
            estimates={}
            for d in pending:
                sql=template.replace('{date_suffix}',d.strftime('%Y%m%d'))
                job=client.query(sql,job_config=bigquery.QueryJobConfig(dry_run=True,use_query_cache=False))
                estimates[str(d)]=job.total_bytes_processed or 0
            total=sum(estimates.values())
            print(f'Preflight: {len(pending)} dates, {total:,} estimated bytes',flush=True)
            if total>args.max_total_bytes or any(v>args.max_daily_bytes for v in estimates.values()):
                raise SystemExit('Estimated query bytes exceed configured limits. Review before increasing limits. No new exports downloaded.')
            for d in pending:
                sql=template.replace('{date_suffix}',d.strftime('%Y%m%d'))
                job=client.query(sql,job_config=bigquery.QueryJobConfig(maximum_bytes_billed=args.max_daily_bytes))
                result=job.result()
                output=raw_dir/f'google_store_events_raw_{d}.csv'
                temp=output.with_suffix('.csv.tmp')
                with temp.open('w',newline='') as f:
                    writer=csv.writer(f);writer.writerow([field.name for field in result.schema])
                    for row in result:writer.writerow(['' if v is None else v for v in row.values()])
                stats=inspect(temp,expected[str(d)])
                temp.replace(output)
                manifest[str(d)]={'job_id':job.job_id,'bytes_processed':job.total_bytes_processed,
                    'bytes_billed':job.total_bytes_billed,'cache_hit':job.cache_hit,
                    'source_sha256':digest(output),**stats}
                manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
                print(f'Downloaded and reconciled {d}: {stats["total_events"]:,} rows',flush=True)
        # Reconcile existing files as well; existing data is never silently overwritten.
        for d in days:inspect(raw_dir/f'google_store_events_raw_{d}.csv',expected[str(d)])
        print('Extraction stage complete.',flush=True)
    if args.stage in ('all','clean'):
        for d in days:
            source=raw_dir/f'google_store_events_raw_{d}.csv'
            inspect(source,expected[str(d)])
            subprocess.run([sys.executable,str(ROOT/'src/clean_csv.py'),'--input',str(source)],check=True)
        print('Cleaning stage complete.',flush=True)
    if args.stage in ('all','validate'):
        checks=[]
        for d in days:
            raw=raw_dir/f'google_store_events_raw_{d}.csv'
            clean=ROOT/f'data/processed/google_store_events_cleaned_{d}.csv'
            raw_stats=inspect(raw,expected[str(d)])
            clean_stats=inspect(clean,expected[str(d)],cleaned=True)
            report=json.loads((quality/'daily_reports'/f'data_quality_report_{d}.json').read_text())
            if report['source_sha256']!=digest(raw) or report['output_sha256']!=digest(clean):
                raise ValueError(f'Quality report checksum mismatch: {d}')
            checks.append({'event_date':str(d),'reconciled':True,**clean_stats})
        output=quality/'daily_reconciliation.csv'
        with output.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(checks[0]));writer.writeheader();writer.writerows(checks)
        summary={'generated_utc':datetime.now(timezone.utc).isoformat(),'start':str(args.start),'end':str(args.end),
            'validated_days':len(checks),'total_event_rows':sum(r['total_events'] for r in checks),
            'status':'counts_and_checksums_reconciled',
            'scope':'Date, row/event counts, observed users, missing users and file checksums. Warnings in daily quality reports still require review.'}
        (quality/'pipeline_validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
