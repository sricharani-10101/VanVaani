# FRA Decision Support Dashboard — Member 4

**PS-7 — AI-powered Decision Support System for Forest Rights Act (FRA) Monitoring**

Officer-facing Streamlit dashboard: KPI cards, state/district progress
tables, charts, an anomaly panel, and a claim detail view.

## ⚠️ Updated to match Member 2 and Member 3's real files

This version reads the **actual** contracts, not earlier guesses:

- **`data/fra_data.json`** (Member 2) — wrapped as `{"meta": {...}, "claims": [...]}`.
  Used only to enrich the claim-detail view (land area, forest area,
  applicant type) — the KPIs/tables/charts don't need it directly.
- **`data/analytics.json`** (Member 2) — shape:
  ```json
  {
    "meta": {...},
    "overall": {"total_claims": 450, "approved_claims": 249, "pending_claims": 129,
                "rejected_claims": 72, "approval_percentage": 55.33, ...},
    "state_wise": {"Madhya Pradesh": {...same shape...}},
    "district_wise": {"Mandla": {...same shape...}, "Dindori": {...}, ...}
  }
  ```
  **This file has no anomaly data in it — that's not Member 2's job.**
  `app.py` computes anomaly counts by state/district/severity/type itself
  from `anomalies.json` and merges them with Member 2's numbers.
- **`data/anomalies.json`** (Member 3) — flat list of
  `{claim_id, state, district, severity, risk_score, type, explanation, recommendation}`.
  `type` is one of `DELAYED_CLAIM`, `LAND_FOREST_MISMATCH` (renamed from
  `LAND_RECORD_MISMATCH` to match what the real data actually contains —
  see Member 3's README), `DATE_INCONSISTENCY`, `UNUSUAL_REJECTION_RATE`.

## Why `scripts_member2/` and `data/generate_analytics.py` are in this repo

If Member 2's real files aren't ready yet, this dashboard needs *some*
`fra_data.json` and `analytics.json` to run against. Rather than writing a
second, separately-maintained mock generator that could drift out of sync
with Member 2's real format, this repo bundles **Member 2's own scripts,
completely unmodified**, as the fallback generator. That guarantees the
fallback data is always shaped exactly like the real thing.

The folder layout (`scripts_member2/` next to `data/`) exists only so those
two scripts' own internal file paths resolve correctly without editing a
single line of them:
- `generate_fra_data.py` writes to `../data/fra_data.json` relative to its
  own folder → lands in `data/`.
- `generate_analytics.py` reads/writes `fra_data.json`/`analytics.json` in
  its own folder → put it inside `data/` directly.

You never need to run these by hand — `app.py` calls them automatically
if the files are missing. Once Member 2 hands you the real files, just
drop them into `data/` and delete/ignore the bundled scripts if you like;
nothing else changes.

## What's built (from the original brief)

1. **KPI cards** — Total Claims, Approved, Pending, Anomalies
2. **State/district comparison table** — Member 2's per-region stats + Member 3's anomaly counts, in two tabs
3. **Charts** — approval rate by district, pending claims by district, anomaly distribution by severity, anomaly distribution by type
4. **Anomaly panel** — filterable by severity, searchable by claim ID/district, colored by severity
5. **Claim detail view** — on "View Details": risk score, severity, land area, forest area, applicant type, status/dates, AI explanation, recommendation

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

First run with no data present will auto-generate `data/fra_data.json` and
`data/analytics.json` via Member 2's bundled scripts, and a small built-in
`anomalies.json` fallback until Member 3's real file is dropped in.

## Swapping in real files

Drop Member 2's and Member 3's real `fra_data.json`, `analytics.json`, and
`anomalies.json` into `data/`, overwriting the generated ones. No code
changes needed — `app.py` just reads whatever's there.

## Verified against real data

This dashboard's data-processing logic (loading, joining Member 2's stats
with Member 3's anomaly counts, claim lookups) has been run end-to-end
against the actual 450-claim dataset and 146-anomaly output included in
`data/` — not just checked for syntax. Sample results:

- Total claims: 450 · Approved: 249 · Pending: 129 · Anomalies: 146
- Top anomaly districts: Shahdol (15), Umaria (14), Balaghat (12), Betul (12)

## Demo data disclosure

Data in `data/` is self-generated synthetic data (Member 2's own generator)
for development and demo purposes — it is not live claim data and should
be presented as such. The disclaimer from Member 2's own `meta` block is
shown directly in the dashboard UI.
