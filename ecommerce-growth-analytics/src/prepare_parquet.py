"""Convert validated cleaned CSVs to date-partitioned Parquet for S3/Athena.
Run from the project: python src/prepare_parquet.py
Preserves input CSVs and uses one explicit schema across all dates.
"""
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
import hashlib
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = pa.schema([
    ('source_file', pa.string()), ('source_row_number', pa.int64()),
    ('event_timestamp', pa.int64()), ('event_name', pa.string()),
    ('user_pseudo_id', pa.string()), ('user_first_touch_timestamp', pa.int64()),
    ('ga_session_id', pa.string()), ('engagement_time_msec', pa.int64()),
    ('session_engaged', pa.string()), ('device_category', pa.string()),
    ('country', pa.string()), ('first_user_source', pa.string()),
    ('first_user_medium', pa.string()), ('transaction_id', pa.string()),
    ('purchase_revenue_in_usd', pa.float64()), ('refund_value_in_usd', pa.float64()),
    ('event_time_utc', pa.string()), ('session_key', pa.string())
])


def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024), b''):h.update(chunk)
    return h.hexdigest()


def main():
    quality=ROOT/'data/quality'
    validation=json.loads((quality/'pipeline_validation_summary.json').read_text())
    if validation.get('validated_days')!=92 or validation.get('status')!='counts_and_checksums_reconciled':
        raise ValueError('Run full-period validation before Parquet conversion.')
    expected=pd.read_csv(quality/'daily_event_coverage.csv',dtype='string').set_index('event_date')
    csv_dir=ROOT/'data/processed'
    output_dir=ROOT/'data/aws_ready'
    days=[date(2020,11,1)+timedelta(days=i) for i in range(92)]
    required={f'google_store_events_cleaned_{day}.csv' for day in days}
    if {p.name for p in csv_dir.glob('google_store_events_cleaned_*.csv')}!=required:
        raise ValueError('Expected exactly 92 cleaned daily files.')
    records=[]
    for day in days:
        source=csv_dir/f'google_store_events_cleaned_{day}.csv'
        source_hash=sha256(source)
        report=json.loads((quality/'daily_reports'/f'data_quality_report_{day}.json').read_text())
        if source_hash!=report['output_sha256']:
            raise ValueError(f'Cleaned file checksum mismatch: {day}')
        frame=pd.read_csv(source,dtype='string',keep_default_na=False)
        frame=frame.mask(frame.eq(''),pd.NA)
        if set(frame.columns)!=set(SCHEMA.names)|{'event_date'}:
            raise ValueError(f'Unexpected columns: {day}')
        if set(frame.event_date.dropna())!={str(day)} or frame.event_date.isna().any():
            raise ValueError(f'Partition date mismatch: {day}')
        if len(frame)!=int(expected.loc[str(day),'total_events']):
            raise ValueError(f'Coverage count mismatch: {day}')
        for field in SCHEMA:
            if pa.types.is_int64(field.type):
                frame[field.name]=pd.to_numeric(frame[field.name],errors='raise').astype('Int64')
            elif pa.types.is_float64(field.type):
                frame[field.name]=pd.to_numeric(frame[field.name],errors='raise').astype('Float64')
        table=pa.Table.from_pandas(frame[SCHEMA.names],schema=SCHEMA,preserve_index=False,safe=True).replace_schema_metadata(None)
        output=output_dir/f'event_date={day}'/'events.parquet'
        output.parent.mkdir(parents=True,exist_ok=True)
        temp=output.with_suffix('.parquet.tmp')
        pq.write_table(table,temp,compression='snappy',row_group_size=100_000)
        restored=pq.ParquetFile(temp).read()
        if not restored.equals(table,check_metadata=True):
            raise ValueError(f'Parquet round-trip changed data: {day}')
        if sha256(source)!=source_hash:
            raise ValueError(f'Input changed during conversion: {day}')
        temp.replace(output)
        records.append({'event_date':str(day),'rows':table.num_rows,'csv_bytes':source.stat().st_size,
                        'parquet_bytes':output.stat().st_size,'source_sha256':source_hash,
                        'parquet_sha256':sha256(output),'parquet_file':str(output.relative_to(ROOT)),
                        'round_trip_equal':True})
        print(f'{day}: {table.num_rows:,} rows verified',flush=True)
    total=sum(r['rows'] for r in records)
    if total!=validation['total_event_rows']:raise ValueError('Total row count mismatch')
    before=sum(r['csv_bytes'] for r in records);after=sum(r['parquet_bytes'] for r in records)
    summary={'generated_utc':datetime.now(timezone.utc).isoformat(),'days':len(records),'rows':total,
             'csv_bytes':before,'parquet_bytes':after,'size_reduction_pct':round((1-after/before)*100,2),
             'compression':'snappy','partition_column':'event_date','all_round_trips_equal':True,
             'schema':{field.name:str(field.type) for field in SCHEMA},
             'notes':['event_date is encoded in folder names, not repeated in Parquet files.',
                      'All identifier columns remain strings. No rows were removed.',
                      'Instrument coverage and engagement warnings remain unresolved.',
                      'No files uploaded to AWS by this script.'], 'files':records}
    (quality/'parquet_conversion_report.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('files','schema','notes')},indent=2))

if __name__=='__main__':main()
