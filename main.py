from data.generate_mock_claims import generate_claims, save_csv
from scripts.build_map import build_map


def run():
    print("Step 1/2: Generating simulated FRA claim data...")
    claims = generate_claims(num_claims_per_district=40)
    save_csv(claims)

    print("\nStep 2/2: Building interactive map...")
    build_map()

    print("\nAll done! Open output/mp_fra_map.html in your browser to see the map.")


if __name__ == "__main__":
    run()
