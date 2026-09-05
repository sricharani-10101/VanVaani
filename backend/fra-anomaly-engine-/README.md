# FRA Anomaly Detection Engine — 

**PS-7 — AI-powered Decision Support System for Forest Rights Act (FRA) Monitoring**

Turns `fra_data.json` (Member 2's format) into a scored, explained anomaly
feed: `anomalies.json`. No UI — pure CLI pipeline.

## ⚠️ Updated to match Member 2's real data (read this if you touched the old version)

This version was rebuilt against Member 2's **actual** `fra_data.json` and
`generate_analytics.py`, not an earlier guess. Two things changed:

1. **`fra_data.json` is wrapped**, not a flat list:
   ```json
   { "meta": {...}, "claims": [ {...}, {...} ] }
   ```
   This script reads `data["claims"]` directly. It still also accepts a
   plain flat list, so nothing breaks if you're testing with an unwrapped file.

2. **Field names and values changed:**
   - `status` is `"Approved"` / `"Pending"` / `"Rejected"` (Title Case), not upper case.
   - There is no `land_record_area` field. Real claims have
     `land_area_hectares` and `forest_area_hectares` instead.
   - The rule that used to be called `LAND_RECORD_MISMATCH` is now
     **`LAND_FOREST_MISMATCH`** — see below for what it checks now.
     **Member 4's dashboard has been updated to expect this new name.**

## Pipeline

```
fra_data.json (Member 2's real file, or self-mocked)
        │
        ▼
  data validation   (bad rows skipped + logged, never crash the run)
        │
        ▼
  rule / statistical checks
        │
        ▼
  anomaly flags + risk score + severity
        │
        ▼
  explanation layer (template-based by default, pluggable LLM)
        │
        ▼
  anomalies.json
```

## Rules implemented

| Flag | Rule |
|---|---|
| `DELAYED_CLAIM` | claim pending > 180 days (relative to an "as of" date — see below) |
| `LAND_FOREST_MISMATCH` | `forest_area_hectares` exceeds `land_area_hectares` (impossible), or covers less than 50% of it |
| `DATE_INCONSISTENCY` | `approval_date < claim_date` |
| `UNUSUAL_REJECTION_RATE` | a district's rejection rate is far above the state average |

Rules decide *whether* a claim is anomalous. The explanation layer only
describes *why*, after the fact — it never makes the anomaly call itself.

### A note on the "as of" date

Member 2's data is a static historical snapshot (claim dates 2010–2023). Using
the real wall-clock date for `DELAYED_CLAIM` would flag almost every pending
claim every single time this runs, regardless of when the hackathon happens
to be judged. Instead, the script defaults to the **latest date found in the
dataset itself** as its reference "today" — pass `--as-of YYYY-MM-DD` to
override.

### Honest heads-up about this specific mock dataset

Member 2's real generator always builds "normal" claims — `forest_area_hectares`
is always 85–100% of `land_area_hectares`, and `approval_date` is always
after `claim_date`. That means on the current `sample_data/fra_data.json`,
**`LAND_FOREST_MISMATCH` and `DATE_INCONSISTENCY` will correctly fire zero
times** — not because they're broken, but because this particular dataset
never contains a case that should trigger them. `DELAYED_CLAIM` and
`UNUSUAL_REJECTION_RATE` do fire (see the numbers below). If you want to
demo all four rules live, the honest way to do it is to manually add a
couple of deliberately inconsistent rows to a copy of `fra_data.json` and
clearly label them as hand-crafted edge cases for the demo — not to loosen
the thresholds until real data trips them by accident.

## Scoring

`risk_score` is a weighted sum of triggered rule hits, capped at 100:
`LOW` 0–39 · `MEDIUM` 40–69 · `HIGH` 70–100. Weights live in `RULE_WEIGHTS`
at the top of `anomaly_engine.py`.

## Output contract — `anomalies.json`

```json
[
  {
    "claim_id": "MP-SEO-0012",
    "state": "Madhya Pradesh",
    "district": "Seoni",
    "severity": "MEDIUM",
    "risk_score": 30,
    "type": "DELAYED_CLAIM",
    "explanation": "This claim has been pending significantly longer than the standard processing window. It may need administrative follow-up.",
    "recommendation": "Escalate for administrative review."
  }
]
```

Field names are fixed by team agreement — Member 4's dashboard reads this
file directly. Don't rename fields without telling them.

## Usage

```bash
# Run against Member 2's real data
python anomaly_engine.py --input fra_data.json --output anomalies.json

# Generate a small self-mock and run on it (schema-matched fallback)
python anomaly_engine.py --mock 30

# Override the reference date used for DELAYED_CLAIM
python anomaly_engine.py --as-of 2024-06-01

# Attempt a real LLM call for explanations (falls back to templates on any failure)
python anomaly_engine.py --use-llm
```

No dependencies beyond the Python standard library.

## Verified results on the real sample data (450 claims, 15 MP districts)

Running against the included `sample_data/fra_data.json`:

- **146 anomalies** flagged out of 450 claims
- `DELAYED_CLAIM`: 129 (every currently-pending claim — see note above)
- `UNUSUAL_REJECTION_RATE`: 17 (across districts with disproportionate rejections)
- All flagged claims currently land in the `LOW` band, because only one
  rule fires per claim on this dataset — a claim tripping two rules would
  score higher. This is expected and documented, not a bug.

## Wiring up a real LLM (optional)

Explanations default to a template per rule type — fast, free, and can't
fail live. To use a real free-tier LLM instead, implement `call_llm()` in
`anomaly_engine.py` (stub already there) and pass `--use-llm`. The template
fallback stays in place as a safety net if the API call fails or times out.

## Demo data disclosure

`sample_data/fra_data.json` is self-generated synthetic data (Member 2's
own generator) for development and demo purposes — it is not live claim
data and should be presented as such.
