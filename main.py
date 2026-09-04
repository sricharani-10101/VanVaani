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

#FRA Analytics
import json
import os
from collections import defaultdict
from datetime import date

# save/read files next to this script, no matter which folder we run it from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR
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

# FRA Data
import json
import os
import random
from datetime import date, timedelta

# -----------------------------------------------------------------------
# 1. SETTINGS  (change these numbers if you want to experiment)
# -----------------------------------------------------------------------

random.seed(42)
# ^ using a fixed "seed" means we get the SAME random data every time we run
#   this script. That makes our demo reproducible - useful when showing the
#   project to judges or teammates. Remove this line if you want fresh
#   random data on every run.

STATE_NAME = "Madhya Pradesh"
CLAIMS_PER_DISTRICT = 30

# district name -> short 3-letter code used inside each Claim ID
DISTRICTS = {
    "Mandla": "MAN",
    "Dindori": "DIN",
    "Balaghat": "BAL",
    "Seoni": "SEO",
    "Chhindwara": "CHH",
    "Shahdol": "SHA",
    "Umaria": "UMA",
    "Anuppur": "ANU",
    "Alirajpur": "ALI",
    "Jhabua": "JHA",
    "Barwani": "BAR",
    "Betul": "BET",
    "Sidhi": "SID",
    "Singrauli": "SIN",
    "Panna": "PAN",
}

STATUSES = ["Approved", "Pending", "Rejected"]
STATUS_WEIGHTS = [0.55, 0.30, 0.15]  # 55% approved, 30% pending, 15% rejected

APPLICANT_TYPES = ["Individual", "Community"]
APPLICANT_WEIGHTS = [0.7, 0.3]  # individual claims (IFR) are more common than
                                # community claims (CFR) in real FRA data

CLAIM_START_DATE = date(2010, 1, 1)
CLAIM_END_DATE = date(2023, 12, 31)


# -----------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# -----------------------------------------------------------------------

def random_date(start, end):
    """Pick a random date between start and end (both included)."""
    total_days = (end - start).days
    return start + timedelta(days=random.randint(0, total_days))


def make_claim(district, serial_number):
    """Build ONE mock FRA claim and return it as a dictionary."""

    code = DISTRICTS[district]
    claim_id = f"MP-{code}-{serial_number:04d}"

    claim_date = random_date(CLAIM_START_DATE, CLAIM_END_DATE)
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
    applicant_type = random.choices(APPLICANT_TYPES, weights=APPLICANT_WEIGHTS, k=1)[0]

    # only an APPROVED claim has an approval date
    if status == "Approved":
        processing_days = random.randint(30, 730)  # 1 month to ~2 years
        approval_date = claim_date + timedelta(days=processing_days)
    else:
        approval_date = None

    # individual claims are usually small plots, community claims are larger
    if applicant_type == "Individual":
        land_area = round(random.uniform(0.5, 4.0), 2)
    else:
        land_area = round(random.uniform(5.0, 150.0), 2)

    # the forest area is usually close to (but not more than) the land area
    forest_area = round(land_area * random.uniform(0.85, 1.0), 2)

    return {
        "claim_id": claim_id,
        "state": STATE_NAME,
        "district": district,
        "claim_date": claim_date.isoformat(),
        "approval_date": approval_date.isoformat() if approval_date else None,
        "status": status,
        "land_area_hectares": land_area,
        "forest_area_hectares": forest_area,
        "applicant_type": applicant_type,
    }


def generate_all_claims():
    """Create CLAIMS_PER_DISTRICT claims for every district in the list."""
    all_claims = []
    for district in DISTRICTS:
        for serial_number in range(1, CLAIMS_PER_DISTRICT + 1):
            all_claims.append(make_claim(district, serial_number))
    return all_claims


# -----------------------------------------------------------------------
# 3. MAIN
# -----------------------------------------------------------------------

def main():
    claims = generate_all_claims()

    output = {
        "meta": {
            "project": "PS-7 - AI-powered Decision Support System for FRA Monitoring",
            "prepared_by": "Team Member 2 - FRA Data & Analytics System",
            "state": STATE_NAME,
            "total_districts": len(DISTRICTS),
            "claims_per_district": CLAIMS_PER_DISTRICT,
            "total_claims": len(claims),
            "data_type": "SYNTHETIC / MOCK DATA",
            "disclaimer": (
                "This dataset is artificially generated using Python for "
                "hackathon prototype/demo purposes only. It does NOT "
                "represent real government FRA records."
            ),
        },
        "claims": claims,
    }

    # save the file next to this script, inside ../data/, no matter which
    # folder we happen to run this script from
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "fra_data.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Done! {len(claims)} mock FRA claims saved to: {output_path}")


if __name__ == "__main__":
    main()
