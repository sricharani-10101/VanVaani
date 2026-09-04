#map-system
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

#FRA Data and Analytics
import json
import os
from collections import defaultdict
from datetime import date

# save/read files next to this script, no matter which folder we run it from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
INPUT_PATH = os.path.join(DATA_DIR, "fra_data.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "analytics.json")


def load_claims():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["claims"], data["meta"]


def days_between(start_str, end_str):
    """Number of days between two ISO-format date strings."""
    start = date.fromisoformat(start_str)
    end = date.fromisoformat(end_str)
    return (end - start).days


def calculate_stats(claims):
    """
    Take a list of claims (could be all 450, or just one district's claims)
    and return a dictionary of statistics for that list.
    """
    total = len(claims)
    approved = [c for c in claims if c["status"] == "Approved"]
    pending = [c for c in claims if c["status"] == "Pending"]
    rejected = [c for c in claims if c["status"] == "Rejected"]

    def percent(count):
        return round((count / total) * 100, 2) if total > 0 else 0.0

    # average processing time only makes sense for APPROVED claims, since
    # those are the only ones that have both a claim_date and an approval_date
    processing_days = [
        days_between(c["claim_date"], c["approval_date"]) for c in approved
    ]
    avg_processing_time = (
        round(sum(processing_days) / len(processing_days), 1)
        if processing_days
        else 0
    )

    return {
        "total_claims": total,
        "approved_claims": len(approved),
        "pending_claims": len(pending),
        "rejected_claims": len(rejected),
        "approval_percentage": percent(len(approved)),
        "pending_percentage": percent(len(pending)),
        "rejected_percentage": percent(len(rejected)),
        "average_processing_time_days": avg_processing_time,
    }


def group_by(claims, field_name):
    """Split a list of claims into groups based on one field, e.g. 'district'."""
    groups = defaultdict(list)
    for claim in claims:
        groups[claim[field_name]].append(claim)
    return groups


def main():
    claims, meta = load_claims()

    overall_stats = calculate_stats(claims)

    # state-wise progress (only Madhya Pradesh right now, but this code
    # would automatically handle more states if they get added later)
    state_wise = {
        state_name: calculate_stats(state_claims)
        for state_name, state_claims in group_by(claims, "state").items()
    }

    # district-wise progress
    district_wise = {
        district_name: calculate_stats(district_claims)
        for district_name, district_claims in group_by(claims, "district").items()
    }

    analytics_output = {
        "meta": {
            "project": meta["project"],
            "prepared_by": meta["prepared_by"],
            "based_on_file": "fra_data.json",
            "data_type": "SYNTHETIC / MOCK DATA - statistics calculated from it",
            "disclaimer": meta["disclaimer"],
        },
        "overall": overall_stats,
        "state_wise": state_wise,
        "district_wise": district_wise,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(analytics_output, f, indent=2, ensure_ascii=False)

    print(f"Done! Analytics saved to: {OUTPUT_PATH}")
    print(f"Total claims analyzed: {overall_stats['total_claims']}")
    print(f"Approved: {overall_stats['approved_claims']} "
          f"({overall_stats['approval_percentage']}%)")
    print(f"Pending:  {overall_stats['pending_claims']} "
          f"({overall_stats['pending_percentage']}%)")
    print(f"Rejected: {overall_stats['rejected_claims']} "
          f"({overall_stats['rejected_percentage']}%)")


if __name__ == "__main__":
    main()
