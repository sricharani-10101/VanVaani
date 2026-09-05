import json
import os
from collections import defaultdict
from datetime import datetime

def load_claims(path='sample_data/fra_data.json'):
    """
    Member 2's real fra_data.json is wrapped: {"meta": {...}, "claims": [...]}.
    This still accepts a plain flat list too, so it keeps working with any
    older-format mock file.
    """
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'claims' in data:
        return data['claims']
    return data

def load_anomalies(path='sample_data/anomalies.json'):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def aggregate_by_district(claims, anomalies=None):
    anomalies = anomalies or []
    raw = defaultdict(lambda: {'total': 0, 'approved': 0, 'pending': 0, 'rejected': 0, 'processing_days_sum': 0, 'processing_days_count': 0})
    for row in claims:
        d = raw[row['district']]
        d['total'] += 1
        status = row['status']
        if status == 'Approved':
            d['approved'] += 1
        elif status == 'Pending':
            d['pending'] += 1
        elif status == 'Rejected':
            d['rejected'] += 1
        if row.get('approval_date'):
            claim_date = datetime.strptime(row['claim_date'], '%Y-%m-%d')
            approval_date = datetime.strptime(row['approval_date'], '%Y-%m-%d')
            days = (approval_date - claim_date).days
            if days >= 0:
                d['processing_days_sum'] += days
                d['processing_days_count'] += 1
    anomaly_counts = defaultdict(lambda: {'total': 0, 'high': 0, 'medium': 0, 'low': 0})
    for a in anomalies:
        bucket = anomaly_counts[a['district']]
        bucket['total'] += 1
        if a['severity'] == 'HIGH':
            bucket['high'] += 1
        elif a['severity'] == 'MEDIUM':
            bucket['medium'] += 1
        elif a['severity'] == 'LOW':
            bucket['low'] += 1
    final = {}
    for district, d in raw.items():
        avg_days = None
        if d['processing_days_count']:
            avg_days = round(d['processing_days_sum'] / d['processing_days_count'], 1)
        approval_rate = round(d['approved'] / d['total'] * 100, 1) if d['total'] else 0.0
        a_counts = anomaly_counts.get(district, {'total': 0, 'high': 0, 'medium': 0, 'low': 0})
        final[district] = {'total_claims': d['total'], 'approved': d['approved'], 'pending': d['pending'], 'rejected': d['rejected'], 'approval_rate_pct': approval_rate, 'avg_processing_days': avg_days, 'anomalies_total': a_counts['total'], 'anomalies_high': a_counts['high'], 'anomalies_medium': a_counts['medium'], 'anomalies_low': a_counts['low']}
    return final
if __name__ == '__main__':
    claims = load_claims()
    anomalies = load_anomalies()
    stats = aggregate_by_district(claims, anomalies)
    for district, s in stats.items():
        print(district, '->', s)
