"""
PS-7 FRA Monitoring — Decision Support Dashboard

Reads THREE files (all produced by the other project modules, or by the
bundled fallback generators in this repo if those files aren't ready yet):

  data/fra_data.json   <- produced by the data generation module. Shape:
                          {"meta": {...}, "claims": [...]}
                          Used here only to enrich the claim-detail view
                          (land_area_hectares, forest_area_hectares,
                          applicant_type) — the KPIs/tables/charts don't
                          need it.

  data/analytics.json  <- produced by the data generation module. Shape:
                          {
                            "meta": {...},
                            "overall": {total_claims, approved_claims,
                                        pending_claims, rejected_claims,
                                        approval_percentage, pending_percentage,
                                        rejected_percentage,
                                        average_processing_time_days},
                            "state_wise":    {"Madhya Pradesh": {...same shape...}},
                            "district_wise": {"Mandla": {...same shape...}, ...}
                          }
                          Note: this file has NO anomaly information in it —
                          that's the anomaly detection module's job, not the
                          data generation module's. This dashboard merges the
                          two itself (see summarize_anomalies() below).

  data/anomalies.json  <- produced by the anomaly detection module. A flat
                          list of:
                          {claim_id, state, district, severity, risk_score,
                           type, explanation, recommendation}
                          type is one of: DELAYED_CLAIM, LAND_FOREST_MISMATCH,
                          DATE_INCONSISTENCY, UNUSUAL_REJECTION_RATE.

Run with:  streamlit run app.py
"""

import json
import os
import subprocess
import sys
from collections import defaultdict

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FRA_DATA_PATH = os.path.join(DATA_DIR, "fra_data.json")
ANALYTICS_PATH = os.path.join(DATA_DIR, "analytics.json")
ANOMALIES_PATH = os.path.join(DATA_DIR, "anomalies.json")

SEVERITY_COLOR = {"HIGH": "#e74c3c", "MEDIUM": "#f39c12", "LOW": "#f1c40f"}
SEVERITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}


# ---------------------------------------------------------------------------
# Data loading + fallback generation
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_json(path):
    with open(path) as f:
        return json.load(f)


def ensure_data_files():
    """
    If the real files from the data generation / anomaly detection modules
    aren't in data/ yet, generate compatible ones so the dashboard still
    runs. fra_data.json and analytics.json are generated using the data
    generation module's OWN scripts, unmodified (bundled in this repo), so
    the fallback is guaranteed to match the real contract exactly — no
    separate mock format to keep in sync.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(FRA_DATA_PATH):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "scripts_data_generator", "generate_fra_data.py")
        subprocess.run([sys.executable, script], check=True)

    if not os.path.exists(ANALYTICS_PATH):
        script = os.path.join(DATA_DIR, "generate_analytics.py")
        subprocess.run([sys.executable, script], cwd=DATA_DIR, check=True)

    if not os.path.exists(ANOMALIES_PATH):
        # Minimal built-in fallback so the anomaly panel isn't empty before
        # the anomaly detection module's real anomalies.json is dropped in.
        # Matches that module's actual output contract exactly (including
        # the real district names).
        mock_anomalies = [
            {"claim_id": "MP-SEO-0012", "state": "Madhya Pradesh", "district": "Seoni",
             "severity": "MEDIUM", "risk_score": 55, "type": "DELAYED_CLAIM",
             "explanation": "This claim has been pending significantly longer than the standard processing window.",
             "recommendation": "Escalate for administrative review."},
            {"claim_id": "MP-BET-0004", "state": "Madhya Pradesh", "district": "Betul",
             "severity": "LOW", "risk_score": 25, "type": "UNUSUAL_REJECTION_RATE",
             "explanation": "This district shows a rejection rate well above the state average.",
             "recommendation": "District-level audit recommended."},
        ]
        with open(ANOMALIES_PATH, "w") as f:
            json.dump(mock_anomalies, f, indent=2)


def summarize_anomalies(anomalies):
    """
    analytics.json has no concept of anomalies (that's a separate anomaly
    detection module). This computes state/district/severity/type
    breakdowns directly from anomalies.json so the dashboard can merge them
    with the data generation module's approved/pending/rejected numbers.
    """
    by_state = defaultdict(int)
    by_district = defaultdict(int)
    by_severity = defaultdict(int)
    by_type = defaultdict(int)
    for a in anomalies:
        by_state[a["state"]] += 1
        by_district[(a["state"], a["district"])] += 1
        by_severity[a["severity"]] += 1
        by_type[a["type"]] += 1
    return by_state, by_district, by_severity, by_type


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

st.set_page_config(page_title="FRA Monitoring — Decision Support", layout="wide")
ensure_data_files()

fra_data = load_json(FRA_DATA_PATH)
analytics = load_json(ANALYTICS_PATH)
anomalies = load_json(ANOMALIES_PATH)
anomalies_sorted = sorted(anomalies, key=lambda a: a["risk_score"], reverse=True)

claims_by_id = {c["claim_id"]: c for c in fra_data.get("claims", [])}
by_state_count, by_district_count, by_severity, by_type = summarize_anomalies(anomalies)

st.title("Forest Rights Act — Decision Support Dashboard")
st.caption("Officer-facing monitoring panel — PS-7")

disclaimer = analytics.get("meta", {}).get("disclaimer")
if disclaimer:
    st.info(disclaimer, icon="ℹ️")

# ---------------------------------------------------------------------------
# 1. KPI cards
# ---------------------------------------------------------------------------

overall = analytics["overall"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Claims", f"{overall['total_claims']:,}")
col2.metric("Approved", f"{overall['approved_claims']:,}")
col3.metric("Pending", f"{overall['pending_claims']:,}")
col4.metric("Anomalies", f"{len(anomalies):,}")

st.divider()

# ---------------------------------------------------------------------------
# 2. State-wise / district-wise comparison tables
#    (data generation module's stats merged with anomaly detection module's
#    counts)
# ---------------------------------------------------------------------------

def build_summary_rows(wise_dict, is_district, state_lookup=None):
    rows = []
    for name, stats in wise_dict.items():
        row = dict(stats)
        if is_district:
            state = state_lookup.get(name, "Madhya Pradesh")
            row["state"] = state
            row["district"] = name
            row["anomalies"] = by_district_count.get((state, name), 0)
        else:
            row["state"] = name
            row["anomalies"] = by_state_count.get(name, 0)
        rows.append(row)
    return rows


# map district -> state, needed because district_wise is keyed by district
# name alone (the data generation module's format)
district_to_state = {c["district"]: c["state"] for c in fra_data.get("claims", [])}

state_rows = build_summary_rows(analytics["state_wise"], is_district=False)
district_rows = build_summary_rows(analytics["district_wise"], is_district=True,
                                    state_lookup=district_to_state)

state_df = pd.DataFrame(state_rows)
district_df = pd.DataFrame(district_rows)

state_tab, district_tab = st.tabs(["State-wise Progress", "District-wise Progress"])
with state_tab:
    if not state_df.empty:
        view = state_df[["state", "total_claims", "approved_claims", "pending_claims",
                          "rejected_claims", "anomalies"]].copy()
        view.columns = ["State", "Claims", "Approved", "Pending", "Rejected", "Anomalies"]
        view = view.sort_values("Anomalies", ascending=False)
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.write("No state-level data available yet.")

with district_tab:
    if not district_df.empty:
        view = district_df[["state", "district", "total_claims", "approved_claims",
                             "pending_claims", "rejected_claims", "anomalies"]].copy()
        view.columns = ["State", "District", "Claims", "Approved", "Pending", "Rejected", "Anomalies"]
        view = view.sort_values("Anomalies", ascending=False)
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.write("No district-level data available yet.")

st.divider()

# ---------------------------------------------------------------------------
# 3. Charts
# ---------------------------------------------------------------------------

st.subheader("Charts")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if not district_df.empty:
        rate_df = district_df.copy()
        rate_df["Approval Rate (%)"] = (
            rate_df["approved_claims"] / rate_df["total_claims"] * 100
        ).round(1)
        fig = px.bar(rate_df.sort_values("Approval Rate (%)"), x="district", y="Approval Rate (%)",
                     title="Approval Rate by District", color="Approval Rate (%)",
                     color_continuous_scale="Greens")
        fig.update_layout(xaxis_title="District")
        st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    if not district_df.empty:
        fig = px.bar(district_df.sort_values("pending_claims", ascending=False),
                      x="district", y="pending_claims", title="Pending Claims by District",
                      color_discrete_sequence=["#f39c12"])
        fig.update_layout(xaxis_title="District", yaxis_title="Pending")
        st.plotly_chart(fig, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)
with chart_col3:
    if by_severity:
        sev_df = pd.DataFrame({"Severity": list(by_severity.keys()), "Count": list(by_severity.values())})
        fig = px.pie(sev_df, names="Severity", values="Count", title="Anomaly Distribution by Severity",
                     color="Severity", color_discrete_map=SEVERITY_COLOR)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No anomalies to chart yet.")

with chart_col4:
    if by_type:
        type_df = pd.DataFrame({"Type": list(by_type.keys()), "Count": list(by_type.values())})
        fig = px.bar(type_df, x="Type", y="Count", title="Anomaly Distribution by Type")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No anomalies to chart yet.")

st.caption(f"Average processing time: **{overall['average_processing_time_days']} days** "
           f"(across all approved claims, per the data generation module's analytics).")

st.divider()

# ---------------------------------------------------------------------------
# 4. Anomaly panel + 5. Claim detail view
# ---------------------------------------------------------------------------

st.subheader("Anomaly Panel")

with st.sidebar:
    st.header("Filters")
    severity_filter = st.multiselect("Severity", options=["HIGH", "MEDIUM", "LOW"],
                                      default=["HIGH", "MEDIUM", "LOW"])
    search = st.text_input("Search claim ID or district")

filtered = [
    a for a in anomalies_sorted
    if a["severity"] in severity_filter
    and (search.lower() in a["claim_id"].lower() or search.lower() in a["district"].lower() if search else True)
]

if "selected_claim" not in st.session_state:
    st.session_state.selected_claim = None

if not filtered:
    st.write("No anomalies match the current filters.")
else:
    for a in filtered:
        emoji = SEVERITY_EMOJI.get(a["severity"], "⚪")
        label = a["type"].replace("_", " ").title()
        with st.container(border=True):
            left, right = st.columns([5, 1])
            with left:
                st.markdown(f"**{emoji} {a['severity']} — {label}**")
                st.caption(f"{a['district']}, {a['state']} — {a['claim_id']} · risk score {a['risk_score']}")
            with right:
                if st.button("View Details", key=f"view_{a['claim_id']}"):
                    st.session_state.selected_claim = a["claim_id"]

if st.session_state.selected_claim:
    selected = next((a for a in anomalies if a["claim_id"] == st.session_state.selected_claim), None)
    claim = claims_by_id.get(st.session_state.selected_claim)

    if selected:
        st.divider()
        st.subheader(f"Claim Detail — {selected['claim_id']}")

        d1, d2, d3 = st.columns(3)
        d1.metric("State", selected["state"])
        d2.metric("District", selected["district"])
        d3.metric("Risk Score", f"{selected['risk_score']} ({selected['severity']})")

        if claim:
            e1, e2, e3 = st.columns(3)
            e1.metric("Land Area", f"{claim['land_area_hectares']} ha")
            e2.metric("Forest Area", f"{claim['forest_area_hectares']} ha")
            e3.metric("Applicant Type", claim["applicant_type"])
            st.caption(f"Status: {claim['status']} · Claim date: {claim['claim_date']} · "
                       f"Approval date: {claim['approval_date'] or '—'}")
        else:
            st.caption("Full claim record not found in fra_data.json — showing anomaly data only.")

        st.markdown("**AI Analysis**")
        st.write(selected["explanation"])
        st.markdown("**Recommendation**")
        st.write(selected["recommendation"])

        if st.button("Close detail view"):
            st.session_state.selected_claim = None
            st.rerun()
