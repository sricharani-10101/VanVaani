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

**PS-7 – AI-powered Decision Support System for Forest Rights Act (FRA) Monitoring**

The project was developed by a student team with separate work on the anomaly detection and dashboard components.
