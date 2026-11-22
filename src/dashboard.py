
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import hashlib

# ============================================================
# AI-SOC | SECURITY OPERATIONS DASHBOARD
# Complete Streamlit Dashboard
# ============================================================

st.set_page_config(
    page_title="AI-SOC Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .dashboard-title {
        font-size: 38px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 35px;
    }

    .section-title {
        font-size: 27px;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .severity-card {
        background: #1e2531;
        border-radius: 12px;
        padding: 22px;
        border: 1px solid #303846;
        min-height: 155px;
    }

    .severity-name {
        font-size: 23px;
        font-weight: 700;
        color: white;
    }

    .severity-label {
        font-size: 13px;
        color: #b8c4d6;
        margin-top: 18px;
    }

    .severity-value {
        font-size: 34px;
        font-weight: 700;
        margin-top: 5px;
    }

    .critical { border-left: 5px solid #ff3333; }
    .high { border-left: 5px solid #ff7043; }
    .medium { border-left: 5px solid #ffb74d; }
    .low { border-left: 5px solid #4caf50; }
    .review { border-left: 5px solid #42a5f5; }
    .informational { border-left: 5px solid #78909c; }

    .stMetric {
        background: #171c26;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #303846;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #303846;
        border-radius: 8px;
    }

    hr {
        border-color: #303846;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATHS = [
    BASE_DIR / "outputs" / "alerts.csv",
    BASE_DIR / "data" / "sample_events.csv"
]


@st.cache_data
def load_data():

    for path in DATA_PATHS:

        if path.exists():

            try:
                df = pd.read_csv(path)

                if not df.empty:
                    return df, str(path)

            except Exception as error:
                st.error(f"Error reading {path}: {error}")

    return pd.DataFrame(), None


df, loaded_file = load_data()


# ============================================================
# SAMPLE DATA FALLBACK
# ============================================================

if df.empty:

    st.error(
        "No event data found. Please check outputs/alerts.csv "
        "or data/sample_events.csv."
    )

    st.stop()


# ============================================================
# DATA PREPROCESSING
# ============================================================

df.columns = df.columns.str.strip().str.lower()

# Handle alternate column names

column_aliases = {
    "source_ip": ["src_ip", "sourceip", "ip_address"],
    "event_type": ["event", "type"],
    "host": ["hostname", "device"],
    "timestamp": ["time", "date"],
    "priority": ["severity"],
    "alert": ["is_alert", "detected_alert"]
}

for standard, alternatives in column_aliases.items():

    if standard not in df.columns:

        for alternative in alternatives:

            if alternative in df.columns:
                df.rename(columns={alternative: standard}, inplace=True)
                break


# Ensure required columns exist

required_columns = [
    "timestamp",
    "host",
    "source_ip",
    "event_type",
    "priority",
    "alert",
    "alert_source",
    "investigation_note"
]

for column in required_columns:

    if column not in df.columns:

        if column == "alert":
            df[column] = False

        elif column == "priority":
            df[column] = "Informational"

        elif column == "investigation_note":
            df[column] = "No investigation note available."

        elif column == "alert_source":
            df[column] = "None"

        elif column == "timestamp":
            df[column] = pd.Timestamp.now()

        else:
            df[column] = "Unknown"


# Convert timestamps

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce",
    utc=True
)


# Convert boolean values safely

def convert_boolean(value):

    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    return str(value).strip().lower() in [
        "true", "1", "yes", "y", "alert", "detected"
    ]


# Determine alerts

if "alert" in df.columns:

    df["alert"] = df["alert"].apply(convert_boolean)

    if "rule_alert" in df.columns:

        df["alert"] = (
            df["alert"] |
            df["rule_alert"].apply(convert_boolean)
        )

    if "ml_anomaly" in df.columns:

        df["alert"] = (
            df["alert"] |
            df["ml_anomaly"].apply(convert_boolean)
        )


# Normalize priorities

def normalize_priority(value):

    value = str(value).strip().lower()

    priority_mapping = {
        "critical": "Critical",
        "severe": "Critical",
        "high": "High",
        "medium": "Medium",
        "moderate": "Medium",
        "low": "Low",
        "review": "Review",
        "informational": "Informational",
        "info": "Informational"
    }

    return priority_mapping.get(value, "Informational")


df["priority"] = df["priority"].apply(normalize_priority)


# Fill missing values

for column in ["host", "source_ip", "event_type", "alert_source"]:

    df[column] = df[column].fillna("Unknown").astype(str)


df["investigation_note"] = (
    df["investigation_note"]
    .fillna("No investigation note available.")
    .astype(str)
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🛡️ AI-SOC Controls")

st.sidebar.markdown("---")

st.sidebar.subheader("Event Filters")

available_hosts = sorted(df["host"].unique().tolist())

selected_hosts = st.sidebar.multiselect(
    "Select Hosts",
    available_hosts,
    default=available_hosts
)

available_priorities = [
    "Critical",
    "High",
    "Medium",
    "Low",
    "Review",
    "Informational"
]

selected_priorities = st.sidebar.multiselect(
    "Alert Severity",
    available_priorities,
    default=available_priorities
)

available_events = sorted(df["event_type"].unique().tolist())

selected_events = st.sidebar.multiselect(
    "Event Type",
    available_events,
    default=available_events
)

alert_filter = st.sidebar.selectbox(
    "Alert Status",
    ["All Events", "Alerts Only", "Non-Alert Events"]
)

search_ip = st.sidebar.text_input(
    "Search Source IP"
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "AI-SOC Security Monitoring System"
)

st.sidebar.caption(
    "Educational prototype | Human verification required"
)


# Apply filters

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["host"].isin(selected_hosts)
]

filtered_df = filtered_df[
    filtered_df["priority"].isin(selected_priorities)
]

filtered_df = filtered_df[
    filtered_df["event_type"].isin(selected_events)
]

if alert_filter == "Alerts Only":

    filtered_df = filtered_df[filtered_df["alert"] == True]

elif alert_filter == "Non-Alert Events":

    filtered_df = filtered_df[filtered_df["alert"] == False]


if search_ip:

    filtered_df = filtered_df[
        filtered_df["source_ip"].str.contains(
            search_ip,
            case=False,
            na=False
        )
    ]


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">🛡️ AI-SOC | Security Operations Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Educational AI-powered Security Operations Center prototype. '
    'All alerts require human investigation.'
    '</div>',
    unsafe_allow_html=True
)

st.caption(f"Data source: {loaded_file}")


# ============================================================
# SECURITY OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📊 Security Overview</div>',
    unsafe_allow_html=True
)

total_events = len(filtered_df)

total_alerts = int(filtered_df["alert"].sum())

unique_hosts = filtered_df["host"].nunique()

unique_ips = filtered_df["source_ip"].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Events", total_events)

with col2:
    st.metric("Total Alerts", total_alerts)

with col3:
    st.metric("Unique Hosts", unique_hosts)

with col4:
    st.metric("Source IPs", unique_ips)


st.divider()


# ============================================================
# ALERT SEVERITY OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">🚨 Alert Severity Overview</div>',
    unsafe_allow_html=True
)

severity_config = [
    ("Critical", "#ff3333", "critical"),
    ("High", "#ff7043", "high"),
    ("Medium", "#ffb74d", "medium"),
    ("Low", "#4caf50", "low"),
    ("Review", "#42a5f5", "review"),
    ("Informational", "#78909c", "informational")
]

severity_counts = (
    filtered_df[filtered_df["alert"] == True]["priority"]
    .value_counts()
    .to_dict()
)

for row_start in [0, 3]:

    cols = st.columns(3)

    for i, (severity, color, css_class) in enumerate(
        severity_config[row_start:row_start + 3]
    ):

        count = severity_counts.get(severity, 0)

        with cols[i]:

            st.markdown(
                f"""
                <div class="severity-card {css_class}">
                    <div class="severity-name">
                        <span style="color:{color};">●</span>
                        {severity}
                    </div>
                    <div class="severity-label">
                        {severity} Alerts
                    </div>
                    <div class="severity-value" style="color:{color};">
                        {count}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")


st.divider()


# ============================================================
# EVENT OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📈 Event Overview</div>',
    unsafe_allow_html=True
)

event_counts = (
    filtered_df["event_type"]
    .value_counts()
    .rename_axis("Event Type")
    .to_frame("Count")
)

if not event_counts.empty:

    st.bar_chart(
        event_counts,
        x_label="Event Type",
        y_label="Number of Events",
        height=350
    )

else:

    st.info("No events available for the selected filters.")


st.divider()


# ============================================================
# ALERT PRIORITY DISTRIBUTION
# ============================================================

st.markdown(
    '<div class="section-title">📊 Alert Priority Distribution</div>',
    unsafe_allow_html=True
)

alert_df = filtered_df[filtered_df["alert"] == True]

priority_order = [
    "Critical",
    "High",
    "Medium",
    "Low",
    "Review",
    "Informational"
]

priority_counts = (
    alert_df["priority"]
    .value_counts()
    .reindex(priority_order, fill_value=0)
)

if priority_counts.sum() > 0:

    st.bar_chart(
        priority_counts,
        x_label="Priority",
        y_label="Number of Alerts",
        height=350
    )

else:

    st.info("No alerts available for the selected filters.")


st.divider()



# ============================================================
# AI MODEL PERFORMANCE
# ============================================================

st.divider()
st.markdown(
    '<div class="section-title">🤖 AI Model Performance</div>',
    unsafe_allow_html=True
)

EVALUATION_PATH = BASE_DIR / "outputs" / "hybrid_evaluation_results.csv"

if EVALUATION_PATH.exists():
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        confusion_matrix
    )

    try:
        evaluation_df = pd.read_csv(EVALUATION_PATH)
        evaluation_df.columns = evaluation_df.columns.str.strip().str.lower()

        needed_columns = {"label", "ml_anomaly", "rule_alert", "alert"}
        if not needed_columns.issubset(evaluation_df.columns):
            st.warning(
                "The evaluation file is missing required columns. "
                "Run `python src/evaluate_hybrid.py` to regenerate it."
            )
        else:
            evaluation_df["label"] = (
                evaluation_df["label"].astype(str).str.strip().str.lower()
            )
            evaluation_df = evaluation_df[
                evaluation_df["label"].isin(["benign", "suspicious"])
            ].copy()

            def as_bool(series):
                return series.astype(str).str.strip().str.lower().isin(
                    ["true", "1", "yes", "y"]
                )

            y_true = (evaluation_df["label"] == "suspicious").astype(int)
            predictions = {
                "Isolation Forest": as_bool(evaluation_df["ml_anomaly"]).astype(int),
                "Rule-Based Detection": as_bool(evaluation_df["rule_alert"]).astype(int),
                "Hybrid Detection": as_bool(evaluation_df["alert"]).astype(int),
            }

            metric_rows = []
            for model_name, y_pred in predictions.items():
                metric_rows.append({
                    "Model": model_name,
                    "Accuracy": accuracy_score(y_true, y_pred),
                    "Precision": precision_score(y_true, y_pred, zero_division=0),
                    "Recall": recall_score(y_true, y_pred, zero_division=0),
                    "F1-score": f1_score(y_true, y_pred, zero_division=0),
                })

            performance_df = pd.DataFrame(metric_rows)
            st.caption(
                f"Evaluation records: {len(evaluation_df)}. "
                "These are diagnostic results on the dataset used by the current "
                "pipeline, not independent test-set performance."
            )

            st.subheader("Performance Comparison")
            st.dataframe(
                performance_df.style.format({
                    "Accuracy": "{:.2%}",
                    "Precision": "{:.2%}",
                    "Recall": "{:.2%}",
                    "F1-score": "{:.2%}",
                }),
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Model Metrics Comparison")
            chart_df = performance_df.set_index("Model")[
                ["Accuracy", "Precision", "Recall", "F1-score"]
            ]
            st.bar_chart(chart_df, y_label="Score", height=350)

            selected_model = st.selectbox(
                "View confusion matrix",
                list(predictions.keys()),
                key="performance_confusion_model"
            )
            matrix = confusion_matrix(
                y_true, predictions[selected_model], labels=[0, 1]
            )
            matrix_df = pd.DataFrame(
                matrix,
                index=["Actual Benign", "Actual Suspicious"],
                columns=["Predicted Benign", "Predicted Suspicious"]
            )
            st.dataframe(matrix_df, use_container_width=True)

            st.download_button(
                "⬇️ Download Model Performance Report",
                data=performance_df.to_csv(index=False).encode("utf-8"),
                file_name="ai_soc_model_performance.csv",
                mime="text/csv",
                key="download_model_performance"
            )
    except Exception as error:
        st.error(f"Could not load model evaluation results: {error}")
else:
    st.info(
        "Model evaluation results are not available yet. Run "
        "`python src/evaluate_hybrid.py` in the VS Code terminal, "
        "then refresh this dashboard."
    )


# ============================================================
# ALERT INVESTIGATION WORKFLOW
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Alert Investigation</div>',
    unsafe_allow_html=True
)

investigation_df = filtered_df[
    filtered_df["alert"] == True
].copy()

# Store analyst statuses separately from alerts.csv so that running
# the detection pipeline does not erase investigation progress.
STATUS_PATH = BASE_DIR / "outputs" / "alert_status.json"
STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)

STATUS_OPTIONS = ["Open", "Investigating", "Resolved"]

def make_alert_id(row):
    identity_parts = [
        str(row.get("timestamp", "")),
        str(row.get("host", "")),
        str(row.get("source_ip", "")),
        str(row.get("event_type", "")),
        str(row.get("alert_source", "")),
        str(row.get("investigation_note", "")),
        str(row.name)
    ]
    identity = "|".join(identity_parts)
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]

def load_investigation_statuses():
    if STATUS_PATH.exists():
        try:
            with STATUS_PATH.open("r", encoding="utf-8") as file:
                saved = json.load(file)
            return saved if isinstance(saved, dict) else {}
        except (json.JSONDecodeError, OSError):
            st.warning("Could not read saved investigation statuses. Starting with Open statuses.")
    return {}

def save_investigation_statuses(statuses):
    temporary_path = STATUS_PATH.with_suffix(".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(statuses, file, indent=2, ensure_ascii=False)
    temporary_path.replace(STATUS_PATH)

if not investigation_df.empty:
    investigation_df = investigation_df.sort_values(
        "timestamp",
        ascending=False
    ).copy()

    saved_statuses = load_investigation_statuses()
    investigation_df["Alert ID"] = investigation_df.apply(make_alert_id, axis=1)
    investigation_df["Investigation Status"] = investigation_df["Alert ID"].map(
        lambda alert_id: saved_statuses.get(alert_id, "Open")
    )

    status_counts = investigation_df["Investigation Status"].value_counts()
    status_cols = st.columns(3)
    for column, status, color in zip(
        status_cols,
        STATUS_OPTIONS,
        ["#ff7043", "#ffb74d", "#4caf50"]
    ):
        with column:
            st.metric(f"{status} Alerts", int(status_counts.get(status, 0)))

    st.caption("Change an alert's status directly in the table. Changes are saved locally and remain available after dashboard refreshes or reruns of the detection pipeline.")

    investigation_columns = [
        "Alert ID",
        "timestamp",
        "host",
        "source_ip",
        "event_type",
        "priority",
        "alert_source",
        "investigation_note",
        "Investigation Status"
    ]
    investigation_columns = [
        column for column in investigation_columns
        if column in investigation_df.columns
    ]

    editable_df = investigation_df[investigation_columns].copy()
    edited_df = st.data_editor(
        editable_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        key="alert_investigation_editor",
        disabled=[column for column in editable_df.columns if column != "Investigation Status"],
        column_config={
            "Alert ID": st.column_config.TextColumn("Alert ID", help="Stable identifier for this alert"),
            "Investigation Status": st.column_config.SelectboxColumn(
                "Investigation Status",
                help="Select the current analyst workflow status",
                options=STATUS_OPTIONS,
                required=True
            )
        }
    )

    updated_statuses = saved_statuses.copy()
    for _, row in edited_df.iterrows():
        status = row["Investigation Status"]
        if status not in STATUS_OPTIONS:
            status = "Open"
        updated_statuses[row["Alert ID"]] = status

    if updated_statuses != saved_statuses:
        try:
            save_investigation_statuses(updated_statuses)
            st.success("Investigation statuses saved successfully.")
        except OSError as error:
            st.error(f"Could not save investigation statuses: {error}")

else:
    st.info("No alerts require investigation under the current filters.")


st.divider()


# ============================================================
# ALL SECURITY EVENTS
# ============================================================

st.markdown(
    '<div class="section-title">📋 All Security Events</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Showing {len(filtered_df)} events after applying filters."
)

display_df = filtered_df.sort_values(
    "timestamp",
    ascending=False
).copy()

if not display_df.empty:

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=450
    )

else:

    st.warning("No events match the selected filters.")


# ============================================================
# CSV EXPORT
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">📥 Export Security Reports</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download All Filtered Events",
        data=csv_data,
        file_name="ai_soc_security_events.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:

    alert_csv = alert_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Alert Report",
        data=alert_csv,
        file_name="ai_soc_alert_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#8994a5;
        padding:20px;
        font-size:13px;
    ">
        🛡️ AI-SOC Security Operations Dashboard<br>
        AI-based Security Monitoring | Anomaly Detection |
        Alert Prioritization<br>
        <br>
        Educational Prototype — Alerts must be verified by a human analyst.
    </div>
    """,
    unsafe_allow_html=True
)