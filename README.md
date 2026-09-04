# VanVaani
VanVaani is a specialized WebGIS and intelligent analytical platform designed to streamline, track, and optimize the implementation of the Forest Rights Act (FRA) across India.
# Forest Rights Act (FRA) Monitoring & Decision Support System

A simple AI-assisted decision support system for monitoring Forest Rights Act (FRA) claims.

The project brings claim data, land records and anomaly detection together in one dashboard. It helps identify claims that may need attention, such as long-pending claims, differences between claimed and recorded land area, and inconsistent dates.

> **Hackathon Project – PS-7: AI-powered Decision Support System for Forest Rights Act (FRA) Monitoring**

---

## What problem are we trying to solve?

FRA claim information can be difficult to monitor when the data is spread across different records and administrative levels.

Because of this, it can be difficult to quickly answer questions like:

* Which claims are still pending for a long time?
* Are there differences between claimed land and land records?
* Are there possible errors in claim dates?
* Which districts have unusual rejection patterns?
* Which claims should be checked first?

Our project tries to make this process easier by combining the data into a single monitoring dashboard and automatically flagging cases that look unusual.

---

## What does the project do?

The system has two main parts:

### 1. Anomaly Detection Engine

The Python-based anomaly engine checks FRA claim data and looks for predefined patterns.

Currently, it checks for:

* **Delayed Claims** – pending claims older than the defined threshold
* **Land Record Mismatch** – significant difference between claimed land area and recorded land area
* **Date Inconsistency** – approval date appearing before the claim date
* **Unusual Rejection Rate** – districts with rejection rates considerably higher than the state-level rate

Each detected anomaly is given a **risk score** and a severity level:

| Severity | Risk Score |
| -------- | ---------: |
| LOW      |       0–39 |
| MEDIUM   |      40–69 |
| HIGH     |     70–100 |

The engine also generates a short explanation and recommendation for each flagged claim.

---

### 2. Decision Support Dashboard

The dashboard provides a simple view of the overall FRA data.

It currently includes:

* Total number of claims
* Approved claims
* Pending claims
* Number of detected anomalies
* State-wise progress
* District-wise breakdown
* Approval rate charts
* Pending claim comparison
* Anomaly distribution
* Anomaly filtering by severity
* Search by claim ID or district
* Individual claim details
* Explanation and recommendation for flagged claims

The dashboard is designed mainly for an officer/administrator who needs a quick overview instead of going through every claim manually.

---

## Project Structure

```text
fra-decision-support/
│
├── fra-anomaly-engine/
│   ├── anomaly_engine.py
│   ├── fra_data.json
│   ├── anomalies.json
│   ├── requirements.txt
│   └── sample_data/
│       ├── fra_data.json
│       └── anomalies.json
│
└── fra-decision-dashboard/
    ├── app.py
    ├── build_analytics.py
    ├── requirements.txt
    └── sample_data/
        ├── analytics.json
        └── anomalies.json
```

---

## Tech Stack

* **Python**
* **Streamlit** – dashboard
* **Pandas** – data processing
* **Plotly** – charts
* **JSON** – sample/mock data
* **Python standard library** – anomaly detection engine

The current prototype is intentionally lightweight so that it can be run locally without requiring a complicated setup.

---

## How the system works

The basic flow is:

```text
FRA Claim Data
      │
      ▼
Data Validation
      │
      ▼
Anomaly Detection
      │
      ├── Delayed Claim
      ├── Land Record Mismatch
      ├── Date Inconsistency
      └── Unusual Rejection Rate
      │
      ▼
Risk Score + Severity
      │
      ▼
Anomaly Results
      │
      ▼
Decision Support Dashboard
```

The anomaly engine is responsible for deciding whether a claim should be flagged. The dashboard then presents those results in a form that is easier to understand.

---

## Running the Anomaly Engine

Go into the anomaly engine folder:

```bash
cd fra-anomaly-engine
```

Run it using the existing data:

```bash
python anomaly_engine.py
```

To generate mock data and run the engine:

```bash
python anomaly_engine.py --mock 30
```

You can also provide your own JSON input:

```bash
python anomaly_engine.py --input path/to/data.json
```

The generated anomaly information is stored in:

```text
anomalies.json
```

---

## Running the Dashboard

Go into the dashboard folder:

```bash
cd fra-decision-dashboard
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the Streamlit application:

```bash
streamlit run app.py
```

The dashboard will open in the browser.

---

## Sample Data

For the hackathon prototype, the project uses **self-generated mock FRA claim data**.

The sample records contain information such as:

```text
Claim ID
State
District
Claim Date
Approval Date
Status
Land Area
Land Record Area
```

The mock data is used to demonstrate how the system behaves when different types of anomalies are present.

It should not be treated as actual government FRA claim data.

---

## Example Anomaly

A claim may look like this:

```text
Claim ID: FRA1004
District: Betul
Status: APPROVED

Claimed Land Area: 4.03 ha
Recorded Land Area: 1.73 ha
```

Since the difference is significant, the system flags it as:

```text
Type: LAND_RECORD_MISMATCH
Severity: MEDIUM
Risk Score: 40
```

The dashboard then shows an explanation and suggests that the claim should be manually verified.

---

## Why use an anomaly score?

The idea is not to automatically reject or approve a claim.

Instead, the system acts as a **screening and decision-support tool**.

A high-risk or unusual claim is simply brought to the officer's attention so that it can be reviewed manually.

This is important because an anomaly does not necessarily mean that a claim is wrong. It only means that the claim has characteristics that are worth checking.

---

## Current Scope

The current version is a working prototype built around mock data.

At this stage, the main focus is:

* FRA claim monitoring
* Data validation
* Rule-based anomaly detection
* Risk scoring
* State/district summaries
* Decision-support dashboard

The project can later be extended with real FRA datasets, geographic boundaries and a proper map-based interface.

---

## Future Improvements

Some features we would like to add are:

* Interactive GIS map showing claims by district
* Real FRA/open government datasets
* Integration with land and forest boundary data
* More advanced anomaly detection using machine learning
* LLM-based explanations for detected anomalies
* Historical trend analysis
* More detailed district-level comparisons
* Role-based access for different types of users
* Exportable reports for flagged claims

---

## Important Note

This project is a **hackathon prototype**.

The data currently included in the repository is mock/sample data created for demonstration purposes. The anomaly results are also intended to demonstrate the working of the system and should not be used for actual administrative decisions.

---

## Team

Built as part of a hackathon project for:

**PROBLEM STATEMENT -7 – AI-powered Decision Support System for Forest Rights Act (FRA) Monitoring**

The project was developed by a student team with separate work on the anomaly detection and dashboard components.

(shivani)

## FRA Data & Analytics System
This module is independent — it does not need the map, AI, or dashboard code to run.
---
This is mock / synthetic data, generated with Python's `random` module — not
copied from a real dataset, not hand-typed fake numbers. Real, claim-level FRA
data isn't publicly available in a usable format, so we generate realistic
placeholder data instead.
Both output files clearly say `"data_type": "SYNTHETIC / MOCK DATA"` and
carry a disclaimer. This is a working prototype using programmatically generated mock data, standing in for real government data until it's integrated.
---
Folder structure
```
fra-data-analytics/
├── README.md
├── requirements.txt
├── scripts/
│   ├── generate_fra_data.py   # creates data/fra_data.json
│   └── analytics.py           # reads fra_data.json, creates data/analytics.json
└── data/
    ├── fra_data.json          # 450 mock claims (15 MP districts x 30 claims)
    └── analytics.json         # calculated statistics
```
---
Data schema (what's inside `fra_data.json`)
Each of the 450 claims looks like this:
```json
{
  "claim_id": "MP-MAN-0001",
  "state": "Madhya Pradesh",
  "district": "Mandla",
  "claim_date": "2012-07-01",
  "approval_date": "2013-03-16",
  "status": "Approved",
  "land_area_hectares": 0.99,
  "forest_area_hectares": 0.86,
  "applicant_type": "Individual"
}
```
`status` is one of `"Approved"`, `"Pending"`, `"Rejected"`.
`approval_date` is only filled in for `"Approved"` claims — otherwise it's `null`.
`applicant_type` is `"Individual"` (IFR-style, small plot) or `"Community"` (CFR-style, larger area).
`analytics.json` contains three sections: `overall` (all 450 claims), `state_wise`
(currently just Madhya Pradesh), and `district_wise` (all 15 districts) — each with
the same set of numbers: total/approved/pending/rejected claims, approval %,
pending %, rejected %, and average processing time in days.
---
Step-by-step roadmap (beginner-friendly)
Step 1 — Get your tools ready
Install Python 3 if you don't already have it: https://www.python.org/downloads/
Install a code editor: https://code.visualstudio.com/ (VS Code — free, beginner-friendly)
Install Git (needed to push to GitHub): https://git-scm.com/downloads
Make a free GitHub account if you don't have one: https://github.com/
No other installs are needed — both scripts use only Python's built-in
libraries (`json`, `random`, `datetime`, `os`, `collections`). Nothing to
`pip install`.
Step 2 — Get the files onto your laptop
Download the files below and put them in a folder exactly like the structure
shown above (`scripts/` and `data/` as sibling folders).
Step 3 — Run the data generator
Open a terminal (VS Code has one built in: Terminal → New Terminal), go into
the `scripts` folder, and run:
```bash
cd scripts
python generate_fra_data.py
```
You should see:
```
Done! 450 mock FRA claims saved to: .../data/fra_data.json
```
Step 4 — Run the analytics script
Still inside `scripts/`, run:
```bash
python analytics.py
```
You should see something like:
```
Done! Analytics saved to: .../data/analytics.json
Total claims analyzed: 450
Approved: 249 (55.33%)
Pending:  129 (28.67%)
Rejected: 72 (16.0%)
```
Step 5 — Check the output
Open `data/fra_data.json` and `data/analytics.json` in VS Code (or drag them
into https://jsonformatter.org/json-viewer) and just skim through — make sure
the numbers look sensible and every district shows up.
Step 6 — Push to GitHub
From the top-level project folder (the one with `README.md` in it):
```bash
git init                       # only if this repo isn't already a git repo
git add .
git commit -m "Add FRA mock data generator and analytics scripts (Member 2)"
git branch -M main
git remote add origin <your-team-repo-URL>
git push -u origin main
```
If your team already has a shared repo, instead do:
```bash
git checkout -b member2-data-analytics
git add .
git commit -m "Add FRA mock data generator and analytics scripts (Member 2)"
git push -u origin member2-data-analytics
```
...then open a Pull Request on GitHub so your teammates can review and merge it.
Step 7 — Hand off to your teammates
Tell them:
Member 1 (Map): load `data/fra_data.json`, plot claims by `district` — you'll
probably want to add real district boundary shapes from Bhuvan
(https://bhuvan.nrsc.gov.in) or Natural Earth (https://www.naturalearthdata.com)
and match them by district name.
Member 3 (AI anomaly detection): `status`, `claim_date`, and `approval_date`
in `fra_data.json` are enough to flag things like "pending for a very long time"
or "processing time much higher than the district average" (which you can pull
straight from `analytics.json`).
Member 4 (Dashboard): `analytics.json` already has everything pre-calculated
— `overall`, `state_wise`, and `district_wise` — so the dashboard just needs to
read and display it, no extra math needed.
Step 8 (optional, if you have extra time)
Swap the random `land_area`/`forest_area` ranges for numbers based on real FRA
reports you find on https://tribal.nic.in (Ministry of Tribal Affairs) or
https://data.gov.in, so the mock data is grounded in real-world ranges.
Add a command-line option to `generate_fra_data.py` (e.g. `--seed 7`) so
teammates can generate a different sample set for testing.
Add unit tests with Python's built-in `unittest` to check that percentages
always add up to (roughly) 100%.
---
Why this won't trip the "fake data as live results" rule
The data is generated by a script you can show anyone, not hand-typed —
anyone can re-run `generate_fra_data.py` and see how it works.
Every output file says in plain text that it is synthetic/mock data.
In your pitch, always describe it as "a working prototype demonstrated on
realistic mock data" — never as real claim records.
