"""
PS-7 FRA Monitoring — Member 3: AI Anomaly Detection Engine
Consumes fra_data.json (Member 2's format) -> produces anomalies.json

Usage:
    python anomaly_engine.py                        # uses fra_data.json if present
    python anomaly_engine.py --input path.json       # run on a specific file
    python anomaly_engine.py --mock 30               # generate a small self-mock and run on it
    python anomaly_engine.py --as-of 2024-01-01       # override the "today" reference date

No UI. No browser needed. Pure CLI.

COMPATIBILITY NOTE (read this first):
Member 2's real fra_data.json looks like this:
    {
      "meta": {... project info, disclaimer, etc ...},
      "claims": [
        {
          "claim_id": "MP-MAN-0001",
          "state": "Madhya Pradesh",
          "district": "Mandla",
          "claim_date": "2012-07-01",
          "approval_date": "2013-03-16" | null,
          "status": "Approved" | "Pending" | "Rejected",   <- Title Case, not upper
          "land_area_hectares": 0.99,
          "forest_area_hectares": 0.86,
          "applicant_type": "Individual" | "Community"
        },
        ...
      ]
    }
This script reads that wrapped shape directly (data["claims"]). It also still
accepts a plain flat list of claim dicts, so this file keeps working
standalone if you ever get handed unwrapped data.

There is no "land_record_area" field in the real data (that was a guess made
before Member 2's actual generator existed). The rule that used to be called
LAND_RECORD_MISMATCH is now LAND_FOREST_MISMATCH and compares land_area_hectares
against forest_area_hectares instead — see check_land_forest_mismatch() below
for the reasoning. Everything downstream (Member 4's dashboard) has been
updated to expect this new type name.
"""

import json
import random
import argparse
import os
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# 0. CONFIG — agree on these once, don't change mid-build
# ---------------------------------------------------------------------------

RULE_WEIGHTS = {
    "DELAYED_CLAIM": 30,
    "LAND_FOREST_MISMATCH": 40,
    "DATE_INCONSISTENCY": 35,
    "UNUSUAL_REJECTION_RATE": 25,
}

DELAYED_CLAIM_DAYS = 180
# forest_area_hectares is generated as 85%-100% of land_area_hectares for
# normal claims. Below this ratio (or forest area exceeding land area,
# which is physically impossible) gets flagged.
FOREST_RATIO_MIN = 0.5
REJECTION_RATE_STD_MULTIPLIER = 1.5  # how many x above district baseline counts as unusual

SEVERITY_BANDS = [
    (70, 100, "HIGH"),
    (40, 69, "MEDIUM"),
    (0, 39, "LOW"),
]

# Real 15-district set (Madhya Pradesh), grouped for reference / consistency
# with the rest of the team's map and dashboard.
DISTRICT_GROUPS = {
    "Central & Eastern Forest Belt": ["Mandla", "Dindori", "Balaghat", "Seoni", "Chhindwara"],
    "Shahdol Region": ["Shahdol", "Umaria", "Anuppur"],
    "Western Tribal Belt": ["Alirajpur", "Jhabua", "Barwani"],
    "Southern / Forest-Connected": ["Betul", "Sidhi", "Singrauli", "Panna"],
}
STATES_DISTRICTS = {
    "Madhya Pradesh": [d for districts in DISTRICT_GROUPS.values() for d in districts]
}

STATUS_APPROVED = "Approved"
STATUS_PENDING = "Pending"
STATUS_REJECTED = "Rejected"

REQUIRED_FIELDS = ["claim_id", "state", "district", "claim_date", "status",
                   "land_area_hectares", "forest_area_hectares"]


# ---------------------------------------------------------------------------
# 1. LOADING — accepts Member 2's wrapped {"meta":..., "claims":[...]} shape,
#    or a plain flat list, so this still works standalone.
# ---------------------------------------------------------------------------

def load_claims(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "claims" in data:
        return data["claims"]
    if isinstance(data, list):
        return data
    raise ValueError(
        f"{path}: expected a claims list or a {{'meta':..., 'claims':[...]}} object"
    )


# ---------------------------------------------------------------------------
# 2. MOCK DATA GENERATOR (only used with --mock, e.g. if Member 2's file
#    isn't ready yet — matches the real schema so the swap-in is seamless)
# ---------------------------------------------------------------------------

def generate_mock_data(n=25, seed=42):
    random.seed(seed)
    rows = []
    today = datetime(2023, 12, 31)  # matches Member 2's real claim date range

    for i in range(1, n + 1):
        district = random.choice(STATES_DISTRICTS["Madhya Pradesh"])
        claim_date = today - timedelta(days=random.randint(10, 400))
        status = random.choices(
            [STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED], weights=[0.3, 0.55, 0.15]
        )[0]

        if status != STATUS_APPROVED:
            approval_date = None
        elif random.random() < 0.08:
            approval_date = claim_date - timedelta(days=random.randint(1, 20))
        else:
            approval_date = claim_date + timedelta(days=random.randint(5, 200))

        land_area = round(random.uniform(0.5, 10.0), 2)
        if random.random() < 0.15:
            forest_area = round(land_area * random.uniform(0.1, 0.4), 2)  # bad ratio
        else:
            forest_area = round(land_area * random.uniform(0.85, 1.0), 2)  # normal

        rows.append({
            "claim_id": f"MP-MOCK-{1000 + i:04d}",
            "state": "Madhya Pradesh",
            "district": district,
            "claim_date": claim_date.strftime("%Y-%m-%d"),
            "approval_date": approval_date.strftime("%Y-%m-%d") if approval_date else None,
            "status": status,
            "land_area_hectares": land_area,
            "forest_area_hectares": forest_area,
            "applicant_type": random.choice(["Individual", "Community"]),
        })

    return rows


# ---------------------------------------------------------------------------
# 3. VALIDATION — never crash on bad rows, just skip + log
# ---------------------------------------------------------------------------

def validate_row(row):
    for field in REQUIRED_FIELDS:
        if field not in row or row[field] is None:
            return False, f"missing field: {field}"
    try:
        datetime.strptime(row["claim_date"], "%Y-%m-%d")
        if row.get("approval_date"):
            datetime.strptime(row["approval_date"], "%Y-%m-%d")
    except (ValueError, TypeError):
        return False, "bad date format"
    return True, None


# ---------------------------------------------------------------------------
# 4. RULE ENGINE — rules decide IF something is anomalous
# ---------------------------------------------------------------------------

def check_delayed_claim(row, as_of):
    if row["status"] != STATUS_PENDING:
        return None
    claim_date = datetime.strptime(row["claim_date"], "%Y-%m-%d")
    days_pending = (as_of - claim_date).days
    if days_pending > DELAYED_CLAIM_DAYS:
        return {
            "type": "DELAYED_CLAIM",
            "detail": f"Claim has been pending for {days_pending} days (threshold: {DELAYED_CLAIM_DAYS})."
        }
    return None


def check_land_forest_mismatch(row):
    """
    forest_area_hectares should normally be 85-100% of land_area_hectares
    (that's how Member 2's generator builds "normal" claims). This flags:
      - forest area exceeding land area (not physically possible), or
      - forest area covering less than FOREST_RATIO_MIN of the claimed land
        (may indicate the claimed area was inflated, or forest cover data
        doesn't support the claim as filed).
    """
    land_area = row["land_area_hectares"]
    forest_area = row["forest_area_hectares"]
    if land_area <= 0:
        return None
    ratio = forest_area / land_area
    if forest_area > land_area:
        return {
            "type": "LAND_FOREST_MISMATCH",
            "detail": f"Forest area ({forest_area} ha) exceeds claimed land area ({land_area} ha), which is not possible."
        }
    if ratio < FOREST_RATIO_MIN:
        return {
            "type": "LAND_FOREST_MISMATCH",
            "detail": f"Forest area ({forest_area} ha) covers only {ratio*100:.1f}% of the claimed land area ({land_area} ha)."
        }
    return None


def check_date_inconsistency(row):
    if not row.get("approval_date"):
        return None
    claim_date = datetime.strptime(row["claim_date"], "%Y-%m-%d")
    approval_date = datetime.strptime(row["approval_date"], "%Y-%m-%d")
    if approval_date < claim_date:
        return {
            "type": "DATE_INCONSISTENCY",
            "detail": f"Approval date ({row['approval_date']}) is before claim date ({row['claim_date']})."
        }
    return None


def check_unusual_rejection_rate(all_rows):
    """District-level check: flags every REJECTED claim in a district whose
    rejection rate is far above the state average."""
    from collections import defaultdict

    state_totals = defaultdict(lambda: {"total": 0, "rejected": 0})
    district_totals = defaultdict(lambda: {"total": 0, "rejected": 0})

    for row in all_rows:
        key_state = row["state"]
        key_district = (row["state"], row["district"])
        state_totals[key_state]["total"] += 1
        district_totals[key_district]["total"] += 1
        if row["status"] == STATUS_REJECTED:
            state_totals[key_state]["rejected"] += 1
            district_totals[key_district]["rejected"] += 1

    flagged_districts = set()
    for (state, district), stats in district_totals.items():
        if stats["total"] < 3:
            continue  # not enough data to judge
        district_rate = stats["rejected"] / stats["total"]
        state_rate = (state_totals[state]["rejected"] / state_totals[state]["total"]
                      if state_totals[state]["total"] else 0)
        if district_rate > state_rate * REJECTION_RATE_STD_MULTIPLIER and district_rate > 0.2:
            flagged_districts.add((state, district))

    return flagged_districts


def run_rules(rows, as_of):
    """Returns a dict: claim_id -> list of triggered rule hits."""
    hits_by_claim = {}

    flagged_districts = check_unusual_rejection_rate(rows)

    for row in rows:
        hits = []
        d = check_delayed_claim(row, as_of)
        if d:
            hits.append(d)
        m = check_land_forest_mismatch(row)
        if m:
            hits.append(m)
        c = check_date_inconsistency(row)
        if c:
            hits.append(c)

        if row["status"] == STATUS_REJECTED and (row["state"], row["district"]) in flagged_districts:
            hits.append({
                "type": "UNUSUAL_REJECTION_RATE",
                "detail": f"{row['district']} district's rejection rate is significantly "
                          f"above the {row['state']} state average."
            })

        if hits:
            hits_by_claim[row["claim_id"]] = hits

    return hits_by_claim


# ---------------------------------------------------------------------------
# 5. SCORING
# ---------------------------------------------------------------------------

def compute_score_and_severity(hits):
    score = min(100, sum(RULE_WEIGHTS.get(h["type"], 10) for h in hits))
    for low, high, label in SEVERITY_BANDS:
        if low <= score <= high:
            return score, label
    return score, "LOW"


# ---------------------------------------------------------------------------
# 6. EXPLANATION LAYER — LLM explains AFTER the rule engine has decided.
#    Falls back to a template if no API key / network / rate limit — this
#    keeps your demo alive even if a free LLM tier hiccups live.
# ---------------------------------------------------------------------------

TEMPLATE_EXPLANATIONS = {
    "DELAYED_CLAIM": "This claim has been pending significantly longer than the standard processing window. It may need administrative follow-up.",
    "LAND_FOREST_MISMATCH": "The recorded forest area does not line up with the claimed land area for this plot. This claim may require manual verification.",
    "DATE_INCONSISTENCY": "The recorded approval date precedes the claim date, which is not possible under normal processing. This suggests a data entry error worth checking.",
    "UNUSUAL_REJECTION_RATE": "This claim's district shows a rejection rate well above the state average, which may indicate inconsistent review practices worth auditing.",
}

TEMPLATE_RECOMMENDATIONS = {
    "DELAYED_CLAIM": "Escalate for administrative review.",
    "LAND_FOREST_MISMATCH": "Manual verification recommended.",
    "DATE_INCONSISTENCY": "Data entry correction recommended.",
    "UNUSUAL_REJECTION_RATE": "District-level audit recommended.",
}


def generate_explanation(claim_id, hits, use_llm=False):
    """
    Set use_llm=True and fill in call_llm() below to use a real free LLM API
    (e.g. Groq, Gemini free tier, HuggingFace inference). Defaults to
    template mode, which is fast, free, and never fails during a demo.
    """
    primary_type = hits[0]["type"]

    if use_llm:
        try:
            return call_llm(claim_id, hits)
        except Exception:
            pass  # fall through to template

    explanation = TEMPLATE_EXPLANATIONS.get(primary_type, "This claim was flagged by the rule engine for review.")
    recommendation = TEMPLATE_RECOMMENDATIONS.get(primary_type, "Manual review recommended.")
    return explanation, recommendation


def call_llm(claim_id, hits):
    """
    Plug in a real free LLM call here if you have time, e.g.:

    import requests
    prompt = f"Explain in one plain-English sentence why claim {claim_id} was " \\
             f"flagged for: {[h['type'] for h in hits]}. Details: {[h['detail'] for h in hits]}. " \\
             f"Then give a one-line recommendation."
    resp = requests.post("<free LLM endpoint>", json={...}, timeout=5)
    text = resp.json()[...]
    # split text into explanation / recommendation and return both
    raise NotImplementedError("Wire up your free LLM API here")
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 7. MAIN PIPELINE
# ---------------------------------------------------------------------------

def build_anomalies(rows, as_of, use_llm=False):
    valid_rows = []
    for row in rows:
        ok, reason = validate_row(row)
        if ok:
            valid_rows.append(row)
        else:
            print(f"[skip] {row.get('claim_id', '?')}: {reason}")

    hits_by_claim = run_rules(valid_rows, as_of)
    row_lookup = {r["claim_id"]: r for r in valid_rows}

    anomalies = []
    for claim_id, hits in hits_by_claim.items():
        row = row_lookup[claim_id]
        score, severity = compute_score_and_severity(hits)
        explanation, recommendation = generate_explanation(claim_id, hits, use_llm=use_llm)
        primary_hit = max(hits, key=lambda h: RULE_WEIGHTS.get(h["type"], 0))

        anomalies.append({
            "claim_id": claim_id,
            "state": row["state"],
            "district": row["district"],
            "severity": severity,
            "risk_score": score,
            "type": primary_hit["type"],
            "explanation": explanation,
            "recommendation": recommendation,
        })

    anomalies.sort(key=lambda a: a["risk_score"], reverse=True)
    return anomalies


def resolve_as_of_date(rows, override=None):
    """
    DELAYED_CLAIM needs a reference "today". Member 2's data is a static
    historical snapshot (claim dates 2010-2023), so using the real wall-clock
    date would flag almost every pending claim as delayed, every single
    time this runs. Instead default to the latest date found in the dataset
    itself (the effective "as of" date of this data snapshot), unless the
    user passes --as-of explicitly.
    """
    if override:
        return datetime.strptime(override, "%Y-%m-%d")
    latest = None
    for row in rows:
        for key in ("claim_date", "approval_date"):
            val = row.get(key)
            if not val:
                continue
            try:
                d = datetime.strptime(val, "%Y-%m-%d")
            except (ValueError, TypeError):
                continue
            if latest is None or d > latest:
                latest = d
    return latest or datetime.now()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="fra_data.json", help="path to claim data (Member 2's format)")
    parser.add_argument("--output", default="anomalies.json", help="path to write output")
    parser.add_argument("--mock", type=int, default=0, help="generate N mock rows instead of reading --input")
    parser.add_argument("--use-llm", action="store_true", help="attempt real LLM call for explanations")
    parser.add_argument("--as-of", default=None, help="reference date (YYYY-MM-DD) for DELAYED_CLAIM; defaults to the latest date found in the data")
    args = parser.parse_args()

    if args.mock:
        rows = generate_mock_data(n=args.mock)
        with open("fra_data.json", "w") as f:
            json.dump(rows, f, indent=2)
        print(f"Generated {len(rows)} mock rows -> fra_data.json")
    elif os.path.exists(args.input):
        rows = load_claims(args.input)
        print(f"Loaded {len(rows)} rows from {args.input}")
    else:
        print(f"No {args.input} found — generating 25 mock rows instead.")
        rows = generate_mock_data(n=25)
        with open("fra_data.json", "w") as f:
            json.dump(rows, f, indent=2)

    as_of = resolve_as_of_date(rows, args.as_of)
    anomalies = build_anomalies(rows, as_of, use_llm=args.use_llm)

    with open(args.output, "w") as f:
        json.dump(anomalies, f, indent=2)

    print(f"\nUsing as-of date: {as_of.strftime('%Y-%m-%d')}")
    print(f"{len(anomalies)} anomalies flagged out of {len(rows)} claims -> {args.output}")
    for a in anomalies[:5]:
        print(f"  [{a['severity']:6}] {a['claim_id']} — {a['type']} (score {a['risk_score']})")


if __name__ == "__main__":
    main()
