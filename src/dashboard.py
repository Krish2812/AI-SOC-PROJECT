
import streamlit as st
import altair as alt
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    :root {
        --bg: #0a0e17;
        --panel: #111827;
        --panel-2: #161f30;
        --border: #1f2a3d;
        --text: #e5e9f0;
        --muted: #8b97ad;
        --accent: #22d3ee;
        --accent-2: #6366f1;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(1200px 500px at 10% -10%, rgba(99,102,241,0.12), transparent 60%),
            radial-gradient(900px 400px at 100% 0%, rgba(34,211,238,0.08), transparent 60%),
            var(--bg);
    }

    [data-testid="stHeader"] { background: transparent; }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1322 0%, #0a0e17 100%);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] h1 {
        font-size: 20px;
        font-weight: 800;
        background: linear-gradient(90deg, var(--accent), var(--accent-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ---------- Hero banner ---------- */
    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #111a2e 0%, #0f172a 55%, #151a3a 100%);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 28px;
    }
    .hero::after {
        content: "";
        position: absolute;
        right: -60px; top: -60px;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(34,211,238,0.18), transparent 70%);
        pointer-events: none;
    }
    .hero-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }
    .dashboard-title {
        font-size: 32px;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }
    .dashboard-title span {
        background: linear-gradient(90deg, var(--accent), var(--accent-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .dashboard-subtitle {
        color: var(--muted);
        font-size: 14px;
        margin-top: 6px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(34,197,94,0.1);
        border: 1px solid rgba(34,197,94,0.35);
        color: #4ade80;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .status-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #22c55e;
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(34,197,94,0.6); }
        70%  { box-shadow: 0 0 0 10px rgba(34,197,94,0); }
        100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
    }
    .hero-meta {
        display: flex;
        gap: 22px;
        flex-wrap: wrap;
        margin-top: 18px;
        font-size: 12px;
        color: var(--muted);
    }
    .hero-meta b { color: var(--text); font-weight: 600; }
    .mono { font-family: 'JetBrains Mono', monospace; }

    /* ---------- Section titles ---------- */
    .section-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 21px;
        font-weight: 700;
        color: #f8fafc;
        margin: 26px 0 16px 0;
    }
    .section-title::before {
        content: "";
        width: 4px;
        height: 22px;
        border-radius: 4px;
        background: linear-gradient(180deg, var(--accent), var(--accent-2));
    }

    /* ---------- KPI cards ---------- */
    .kpi-card {
        background: linear-gradient(160deg, var(--panel-2), var(--panel));
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px 22px;
        transition: transform .15s ease, border-color .15s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: #2c3b57; }
    .kpi-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--muted);
        font-size: 13px;
        font-weight: 500;
    }
    .kpi-icon {
        width: 34px; height: 34px;
        display: grid; place-items: center;
        border-radius: 10px;
        font-size: 17px;
    }
    .kpi-value {
        font-size: 34px;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 10px;
        letter-spacing: -1px;
    }
    .kpi-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }

    /* ---------- Severity cards ---------- */
    .severity-card {
        background: linear-gradient(160deg, var(--panel-2), var(--panel));
        border-radius: 14px;
        padding: 18px 20px;
        border: 1px solid var(--border);
        transition: transform .15s ease;
    }
    .severity-card:hover { transform: translateY(-2px); }
    .severity-name {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 600;
        color: var(--text);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .severity-value {
        font-size: 32px;
        font-weight: 800;
        margin-top: 8px;
    }
    .severity-label { font-size: 12px; color: var(--muted); }
    .sev-bar {
        height: 6px;
        background: #1c2638;
        border-radius: 6px;
        margin-top: 12px;
        overflow: hidden;
    }
    .sev-bar > div { height: 100%; border-radius: 6px; }

    /* ---------- Native widgets ---------- */
    [data-testid="stMetric"] {
        background: linear-gradient(160deg, var(--panel-2), var(--panel));
        padding: 18px;
        border-radius: 14px;
        border: 1px solid var(--border);
    }
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    .stDownloadButton button, .stButton button {
        border-radius: 10px;
        border: 1px solid #2c3b57;
        background: linear-gradient(135deg, #1b2540, #141c30);
        font-weight: 600;
        transition: all .15s ease;
    }
    .stDownloadButton button:hover, .stButton button:hover {
        border-color: var(--accent);
        color: var(--accent);
    }
    [data-testid="stVegaLiteChart"] {
        background: linear-gradient(160deg, var(--panel-2), var(--panel));
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 12px;
    }
    hr { border-color: var(--border) !important; }
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

time_min = df["timestamp"].min()
time_max = df["timestamp"].max()
time_range = (
    f"{time_min:%d %b %Y %H:%M} → {time_max:%d %b %Y %H:%M} UTC"
    if pd.notna(time_min) and pd.notna(time_max) else "Unknown"
)

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-top">
            <div>
                <div class="dashboard-title">🛡️ AI-SOC <span>Security Operations</span></div>
                <div class="dashboard-subtitle">
                    AI-powered threat detection, alert prioritization and analyst workflow.
                    All alerts require human investigation.
                </div>
            </div>
            <div class="status-pill"><span class="status-dot"></span>MONITORING ACTIVE</div>
        </div>
        <div class="hero-meta">
            <div>📁 Source <b class="mono">{Path(loaded_file).name}</b></div>
            <div>🕒 Window <b>{time_range}</b></div>
            <div>🔄 Rendered <b>{datetime.now():%d %b %Y %H:%M}</b></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SECURITY OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">Security Overview</div>',
    unsafe_allow_html=True
)

total_events = len(filtered_df)

total_alerts = int(filtered_df["alert"].sum())

unique_hosts = filtered_df["host"].nunique()

unique_ips = filtered_df["source_ip"].nunique()

alert_rate = (total_alerts / total_events * 100) if total_events else 0

kpis = [
    ("Total Events", f"{total_events:,}", "Events in current view", "📡", "rgba(34,211,238,0.12)"),
    ("Active Alerts", f"{total_alerts:,}", f"{alert_rate:.1f}% of events flagged", "🚨", "rgba(239,68,68,0.14)"),
    ("Monitored Hosts", f"{unique_hosts:,}", "Unique endpoints", "🖥️", "rgba(99,102,241,0.15)"),
    ("Source IPs", f"{unique_ips:,}", "Distinct origins", "🌐", "rgba(34,197,94,0.12)"),
]

for column, (label, value, sub, icon, tint) in zip(st.columns(4), kpis):
    with column:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-head">
                    <span>{label}</span>
                    <span class="kpi-icon" style="background:{tint};">{icon}</span>
                </div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ALERT SEVERITY OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">Alert Severity</div>',
    unsafe_allow_html=True
)

severity_config = [
    ("Critical", "#ef4444"),
    ("High", "#f97316"),
    ("Medium", "#eab308"),
    ("Low", "#22c55e"),
    ("Review", "#3b82f6"),
    ("Informational", "#64748b")
]
severity_colors = dict(severity_config)

severity_counts = (
    filtered_df[filtered_df["alert"] == True]["priority"]
    .value_counts()
    .to_dict()
)

severity_total = max(sum(severity_counts.values()), 1)

for row_start in [0, 3]:

    for column, (severity, color) in zip(
        st.columns(3), severity_config[row_start:row_start + 3]
    ):

        count = severity_counts.get(severity, 0)
        share = count / severity_total * 100

        with column:
            st.markdown(
                f"""
                <div class="severity-card" style="border-top:3px solid {color};">
                    <div class="severity-name">
                        <span style="color:{color};">●</span>{severity}
                    </div>
                    <div class="severity-value" style="color:{color};">{count}</div>
                    <div class="severity-label">{share:.0f}% of alerts</div>
                    <div class="sev-bar"><div style="width:{share:.1f}%;background:{color};"></div></div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")


# ============================================================
# CHARTS
# ============================================================

alert_df = filtered_df[filtered_df["alert"] == True]

priority_order = [
    "Critical",
    "High",
    "Medium",
    "Low",
    "Review",
    "Informational"
]


def style_chart(chart):
    return (
        chart.configure_view(strokeWidth=0)
        .configure_axis(
            labelColor="#8b97ad",
            titleColor="#8b97ad",
            gridColor="#1f2a3d",
            domainColor="#1f2a3d"
        )
        .configure_legend(labelColor="#c7cfdc", titleColor="#8b97ad")
        .configure(background="transparent")
    )


st.markdown(
    '<div class="section-title">Activity Timeline</div>',
    unsafe_allow_html=True
)

timeline_df = filtered_df.dropna(subset=["timestamp"]).copy()

if not timeline_df.empty:
    timeline_df["Time"] = timeline_df["timestamp"].dt.tz_convert(None).dt.floor("h")
    timeline_df["Type"] = np.where(timeline_df["alert"], "Alerts", "Normal Events")
    timeline = (
        timeline_df.groupby(["Time", "Type"]).size().reset_index(name="Count")
    )
    timeline_chart = (
        alt.Chart(timeline)
        .mark_area(opacity=0.5, interpolate="monotone", line=True)
        .encode(
            x=alt.X("Time:T", title=None),
            y=alt.Y("Count:Q", title="Events per hour", stack=None),
            color=alt.Color(
                "Type:N",
                scale=alt.Scale(
                    domain=["Normal Events", "Alerts"],
                    range=["#22d3ee", "#ef4444"]
                ),
                legend=alt.Legend(orient="top", title=None)
            ),
            tooltip=["Time:T", "Type:N", "Count:Q"]
        )
        .properties(height=280)
    )
    st.altair_chart(style_chart(timeline_chart), use_container_width=True)
else:
    st.info("No timestamped events available for the selected filters.")


left_col, right_col = st.columns([1.4, 1])

with left_col:

    st.markdown(
        '<div class="section-title">Event Overview</div>',
        unsafe_allow_html=True
    )

    event_counts = (
        filtered_df["event_type"]
        .value_counts()
        .rename_axis("Event Type")
        .reset_index(name="Count")
    )

    if not event_counts.empty:
        event_chart = (
            alt.Chart(event_counts)
            .mark_bar(cornerRadiusEnd=6)
            .encode(
                y=alt.Y("Event Type:N", sort="-x", title=None),
                x=alt.X("Count:Q", title="Number of events"),
                color=alt.Color(
                    "Count:Q",
                    scale=alt.Scale(range=["#3b4a8f", "#22d3ee"]),
                    legend=None
                ),
                tooltip=["Event Type:N", "Count:Q"]
            )
            .properties(height=300)
        )
        st.altair_chart(style_chart(event_chart), use_container_width=True)
    else:
        st.info("No events available for the selected filters.")

with right_col:

    st.markdown(
        '<div class="section-title">Alert Priority Mix</div>',
        unsafe_allow_html=True
    )

    priority_counts = (
        alert_df["priority"]
        .value_counts()
        .reindex(priority_order, fill_value=0)
        .rename_axis("Priority")
        .reset_index(name="Alerts")
    )
    priority_counts = priority_counts[priority_counts["Alerts"] > 0]

    if not priority_counts.empty:
        donut = (
            alt.Chart(priority_counts)
            .mark_arc(innerRadius=70, outerRadius=120, cornerRadius=4, padAngle=0.02)
            .encode(
                theta=alt.Theta("Alerts:Q"),
                color=alt.Color(
                    "Priority:N",
                    sort=priority_order,
                    scale=alt.Scale(
                        domain=priority_order,
                        range=[severity_colors[p] for p in priority_order]
                    ),
                    legend=alt.Legend(orient="right", title=None)
                ),
                tooltip=["Priority:N", "Alerts:Q"]
            )
            .properties(height=300)
        )
        st.altair_chart(style_chart(donut), use_container_width=True)
    else:
        st.info("No alerts available for the selected filters.")


# ============================================================
# AI MODEL PERFORMANCE
# ============================================================

st.markdown(
    '<div class="section-title">AI Model Performance</div>',
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
    '<div class="section-title">Alert Investigation</div>',
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
    '<div class="section-title">All Security Events</div>',
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
    '<div class="section-title">Export Security Reports</div>',
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