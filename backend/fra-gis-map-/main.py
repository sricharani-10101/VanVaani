import os
from generate_mock_claims import generate_claims, save_json
from build_map import build_map
CLAIMS_PATH = 'sample_data/fra_data.json'
ANOMALIES_PATH = 'sample_data/anomalies.json'

def run():
    if not os.path.exists(CLAIMS_PATH):
        print('No sample_data/fra_data.json found - generating simulated claims...')
        claims = generate_claims()
        save_json(claims, CLAIMS_PATH)
    else:
        print(f'Using existing {CLAIMS_PATH}')
    if os.path.exists(ANOMALIES_PATH):
        print(f'Found {ANOMALIES_PATH} - map will color districts by real anomaly data.')
    else:
        print(f'No {ANOMALIES_PATH} found - map will fall back to approval-rate coloring.')
    build_map(claims_path=CLAIMS_PATH, anomalies_path=ANOMALIES_PATH)
    print('\nAll done! Open output/mp_fra_map.html in your browser to see the map.')
if __name__ == '__main__':
    run()
