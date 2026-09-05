import json
import random
from datetime import datetime, timedelta
from district_coordinates import DISTRICT_COORDS
STATE = 'Madhya Pradesh'
DISTRICTS = list(DISTRICT_COORDS.keys())

def generate_claims(num_claims_per_district=30, seed=42):
    random.seed(seed)
    rows = []
    today = datetime(2026, 9, 4)
    claim_id = 1
    for district in DISTRICTS:
        for _ in range(num_claims_per_district):
            claim_date = today - timedelta(days=random.randint(10, 400))
            status = random.choices(['Pending', 'Approved', 'Rejected'], weights=[0.3, 0.55, 0.15])[0]
            if status != 'Approved':
                approval_date = None
            elif random.random() < 0.08:
                approval_date = claim_date - timedelta(days=random.randint(1, 20))
            else:
                approval_date = claim_date + timedelta(days=random.randint(5, 200))
            land_area = round(random.uniform(0.5, 10.0), 2)
            forest_area = round(land_area * random.uniform(0.85, 1.0), 2)
            rows.append({'claim_id': f'MP-MOCK-{claim_id:04d}', 'state': STATE, 'district': district, 'claim_date': claim_date.strftime('%Y-%m-%d'), 'approval_date': approval_date.strftime('%Y-%m-%d') if approval_date else None, 'status': status, 'land_area_hectares': land_area, 'forest_area_hectares': forest_area, 'applicant_type': random.choice(['Individual', 'Community'])})
            claim_id += 1
    return rows

def save_json(rows, path='sample_data/fra_data.json'):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2)
    print(f'Saved {len(rows)} simulated claims to {path}')
if __name__ == '__main__':
    claims = generate_claims()
    save_json(claims)
