"""Preserve source rows and nulls; validate and add typed analytical fields.
Run: python src/clean_csv.py --input data/raw/FILE.csv
Outputs cleaned CSV plus a JSON quality report. Requires pandas.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    source = args.input.resolve()
    root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(source, dtype='string', keep_default_na=False)
    original_rows = len(df)
    required = ['event_date', 'event_timestamp', 'event_name', 'user_pseudo_id', 'ga_session_id',
                'user_first_touch_timestamp', 'engagement_time_msec', 'session_engaged',
                'device_category', 'country', 'first_user_source', 'first_user_medium',
                'transaction_id', 'purchase_revenue_in_usd', 'refund_value_in_usd']
    absent = sorted(set(required) - set(df.columns))
    if absent:
        raise ValueError(f'Missing required columns: {absent}')
    report = {'source_file': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'input_rows': original_rows, 'changes': {}, 'invalid_values': {}}
    # Normalize whitespace; only empty cells become null. Preserve literal source placeholders.
    for col in df.columns:
        trimmed = df[col].str.strip()
        changed = int((df[col] != trimmed).sum())
        if changed:
            report['changes'][col + '_whitespace_trimmed'] = changed
        df[col] = trimmed.mask(trimmed.eq(''), pd.NA)
    df.insert(0, 'source_row_number', range(2, len(df) + 2))
    df.insert(0, 'source_file', source.name)
    for col in ['event_timestamp', 'user_first_touch_timestamp', 'ga_session_id', 'engagement_time_msec']:
        valid = df[col].isna() | df[col].str.fullmatch(r'\d+', na=False)
        report['invalid_values'][col] = int((~valid).sum())
    dates = pd.to_datetime(df['event_date'], format='%Y%m%d', errors='coerce')
    report['invalid_values']['event_date'] = int((df.event_date.notna() & dates.isna()).sum())
    for col in ['purchase_revenue_in_usd', 'refund_value_in_usd']:
        parsed = pd.to_numeric(df[col], errors='coerce')
        report['invalid_values'][col] = int((df[col].notna() & (parsed.isna() | parsed.isin([float('inf'), -float('inf')]))).sum())
    if any(report['invalid_values'].values()):
        raise ValueError(f'Invalid typed values; raw file unchanged: {report["invalid_values"]}')
    for col in ['event_timestamp', 'user_first_touch_timestamp', 'engagement_time_msec']:
        df[col] = pd.to_numeric(df[col], errors='raise').astype('Int64')
    # User/session/transaction identifiers stay strings, avoiding floating-point precision loss.
    for col in ['purchase_revenue_in_usd', 'refund_value_in_usd']:
        df[col] = pd.to_numeric(df[col], errors='raise').astype('Float64')
    df['event_date'] = dates.dt.strftime('%Y-%m-%d').astype('string')
    df['event_time_utc'] = pd.to_datetime(df.event_timestamp, unit='us', utc=True, errors='raise').dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # Unambiguous JSON tuple representation; unavailable if either component is missing.
    df['session_key'] = pd.Series([
        json.dumps([user, session], separators=(',', ':')) if pd.notna(user) and pd.notna(session) else pd.NA
        for user, session in zip(df.user_pseudo_id, df.ga_session_id)], dtype='string')
    purchase = df.event_name.eq('purchase').fillna(False)
    tx = df.loc[purchase, 'transaction_id'].dropna()
    report.update({
        'output_rows': len(df), 'rows_removed': 0,
        'date_min': df.event_date.min(), 'date_max': df.event_date.max(),
        'distinct_users': int(df.user_pseudo_id.nunique()),
        'distinct_sessions': int(df.session_key.nunique()),
        'missing_values': {col: int(df[col].isna().sum()) for col in required},
        'identical_source_rows': int(df[required].duplicated().sum()),
        'event_counts': {str(k): int(v) for k, v in df.event_name.value_counts().items()},
        'purchase_events': int(purchase.sum()),
        'purchase_rows_missing_transaction_id': int(df.loc[purchase, 'transaction_id'].isna().sum()),
        'repeated_purchase_transaction_rows': int(tx.duplicated().sum()),
        'purchase_rows_missing_revenue': int(df.loc[purchase, 'purchase_revenue_in_usd'].isna().sum()),
        'raw_purchase_revenue_usd': float(df.loc[purchase, 'purchase_revenue_in_usd'].sum()),
        'policies': ['No records deduplicated or removed.', 'Missing revenue, refunds and engagement values remain null.',
                     'Source placeholders are retained for investigation.', 'Event date is source reporting date; event_time_utc is UTC.',
                     'Event counts are not conversion rates.', 'CSV has no type metadata: read user_pseudo_id, ga_session_id and transaction_id as strings.'],
        'warnings': []})
    if report['event_counts'].get('add_to_cart', 0) < report['event_counts'].get('begin_checkout', 0):
        report['warnings'].append('Add-to-cart event count is below checkout count; investigate instrumentation/sample coverage before funnel interpretation.')
    if df.session_engaged.isna().any():
        report['warnings'].append('Session engagement flag is incomplete; null is not an explicit zero.')
    output_dir = root / 'data/processed'
    quality_dir = root / 'data/quality/daily_reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    quality_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f'google_store_events_cleaned_{report["date_min"]}.csv'
    if report['date_min'] != report['date_max']:
        raise ValueError('Expected one-day input for this cleaning step.')
    df.to_csv(output, index=False, na_rep='')
    check = pd.read_csv(output, dtype='string', keep_default_na=False)
    assert len(check) == original_rows
    assert check.user_pseudo_id.tolist() == df.user_pseudo_id.fillna('').tolist()
    assert check.ga_session_id.tolist() == df.ga_session_id.fillna('').tolist()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == report['source_sha256']
    report['output_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    report_path = quality_dir / f'data_quality_report_{report["date_min"]}.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'report': str(report_path), 'rows': len(df),
                      'sessions': report['distinct_sessions'], 'warnings': report['warnings']}, indent=2))

if __name__ == '__main__':
    main()
