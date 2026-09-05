# FRA Monitoring : GIS / Map System

**Part of:** AI-Powered Decision Support System for Forest Rights Act (FRA) Monitoring
**This module's job (PS-7 requirement):** an interactive WebGIS-style map of FRA claim data, by district, for Madhya Pradesh.

**Scope for this build:** Madhya Pradesh, 15 districts —
Mandla, Dindori, Balaghat, Seoni, Chhindwara, Shahdol, Umaria, Anuppur,
Alirajpur, Jhabua, Barwani, Betul, Sidhi, Singrauli, Panna.

---

## Shared data contract

⚠️ **Updated to match Member 2's real generator output** (previously this
assumed a flat list with different field names — that guess has been
replaced with the actual contract below; `aggregate_stats.py` was updated
to match).

- `sample_data/fra_data.json` — the claim records (Member 2's real output,
  or this module's own self-generated mock copy in the meantime)
- `sample_data/anomalies.json` — Member 3's anomaly output (optional; the
  map degrades gracefully to an approval-rate heuristic if it's missing)

`fra_data.json` is **wrapped**, not a flat list — `{"meta": {...}, "claims": [...]}`.
`aggregate_stats.py` reads `data["claims"]` (it also still accepts a plain
flat list, so older mock files keep working). Each claim looks like:

```json
{
  "claim_id": "MP-SEO-0012",
  "state": "Madhya Pradesh",
  "district": "Seoni",
  "claim_date": "2015-08-11",
  "approval_date": null,
  "status": "Pending",
  "land_area_hectares": 3.01,
  "forest_area_hectares": 2.85,
  "applicant_type": "Individual"
}
```

Note `status` is Title Case (`Approved`/`Pending`/`Rejected`), not upper
case — this module's district totals are keyed off that exact casing.

`anomalies.json` row shape (Member 3's exact contract — note `type` no
longer includes `LAND_RECORD_MISMATCH`; that's now `LAND_FOREST_MISMATCH`,
though this module only reads `severity`, so it's unaffected either way):

```json
{
  "claim_id": "MP-SEO-0012",
  "state": "Madhya Pradesh",
  "district": "Seoni",
  "severity": "MEDIUM",
  "risk_score": 30,
  "type": "DELAYED_CLAIM",
  "explanation": "This claim has been pending significantly longer than the standard processing window.",
  "recommendation": "Escalate for administrative review."
}
```

## About the data

The FRA claim numbers used here are simulated/synthetic when self-generated
by `generate_mock_claims.py`, using Python's `random` module with a fixed
seed. They are not real government figures, and are not presented as such —
the map always shows a "DEMO MODE" banner plus a note on whether it's
coloring districts from real anomaly data or the approval-rate fallback.

The district location coordinates in `district_coordinates.py` are real,
public geographic reference points — only the claim statistics are
simulated.

## What this module produces

`output/mp_fra_map.html` — an interactive map you can open in any browser.
Each district is a circle:

- **Bigger circle** = more total FRA claims in that district
- **Color** = risk level. If `anomalies.json` is present, color is driven
  by real anomaly severity/density from Member 3's engine. If it's not
  present yet, color falls back to a simple approval-rate heuristic
  (green/amber/red) so the map still works stand-alone.
- **Click a circle** → popup with total claims, approved/pending/rejected
  counts, approval rate, average processing time, and anomaly counts by
  severity.

## Folder structure

```
fra-gis-map/
├── sample_data/
│   ├── fra_data.json
│   └── anomalies.json
├── output/
│   └── mp_fra_map.html
├── district_coordinates.py
├── generate_mock_claims.py
├── aggregate_stats.py
├── build_map.py
├── main.py
├── requirements.txt
└── README.md
```

## How to run it

You need Python 3. Nothing else — the core pipeline uses only Python's
standard library.

```bash
python main.py
```

This will:

1. Use `sample_data/fra_data.json` if present, otherwise generate one
2. Build `output/mp_fra_map.html`, colored using `sample_data/anomalies.json`
   if it's there

Then open `output/mp_fra_map.html` in your browser (internet access needed
in the browser, since it loads Leaflet.js and map tiles from a free CDN).

### Running the pieces individually

```bash
python generate_mock_claims.py
python aggregate_stats.py
python build_map.py
```

## Swapping in real team files

No code changes needed — overwrite the two files:

- `sample_data/fra_data.json` ← Member 2's real output
- `sample_data/anomalies.json` ← Member 3's real output

## How this connects to the rest of the team

- **Member 2 (Data & Analytics):** produces the real `fra_data.json` this
  module reads.
- **Member 3 (AI Anomaly Detection):** produces the real `anomalies.json`
  this module reads to color districts by actual risk instead of the
  approval-rate fallback.
- **Member 4 (Decision Support Dashboard):** reads the same `fra_data.json`
  / `anomalies.json` (via its own `analytics.json` build step) — both
  modules stay consistent since they're reading identical source files.
- **Member 5 (Frontend/UI):** `output/mp_fra_map.html` is self-contained —
  embed it with `<iframe src="mp_fra_map.html">`, or adapt the HTML/JS
  into a React/HTML component.

## Upgrade path (optional, if there's extra time)

Districts are currently shown as circles at district-HQ points. For a more
"real GIS" look, swap points for actual district boundary polygons:

1. Download India district boundaries (free) from Bhuvan (ISRO), data.gov.in,
   or DataMeet's open India maps repository.
2. Filter down to the 15 MP districts (e.g. with `geopandas`).
3. In `build_map.py`, add the polygons as a Leaflet `L.geoJSON(...)` layer,
   colored the same way the circles are now.

This is a nice-to-have, not required — the point-marker map already
satisfies PS-7's ask for a "WebGIS-style map view of mock FRA claim data by
district."

## Credits / data sources

- District coordinate reference: publicly known geographic data.
- Map rendering: Leaflet.js (open-source, free) + OpenStreetMap tiles
  (free, open data).
- Claim statistics: simulated for this demo unless real team files are
  swapped in (see disclaimer above).
- Original code written for this project — no code copied from an existing
  product or repository.
