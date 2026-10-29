from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CAREFLOW | CLINICAL PATHWAY ANALYTICS
# Redesigned Streamlit dashboard
# ============================================================

st.set_page_config(
    page_title="CareFlow | Clinical Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
CLEAN_LOG = ROOT / "data" / "processed" / "cleaned_event_log.csv"
RAW_LOG = ROOT / "data" / "raw" / "hospital_event_log.csv"

# ------------------------- Theme ----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(20,184,166,0.09), transparent 28%),
            linear-gradient(135deg, #07111f 0%, #0b1424 55%, #0d1829 100%);
        color: #e8eef8;
    }
    .block-container {
        max-width: 1500px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101d30 0%, #0b1525 100%);
        border-right: 1px solid rgba(148,163,184,0.16);
    }
    [data-testid="stSidebar"] * { color: #dce7f5; }
    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.025em;
    }
    h1 { color: #f4f8ff; font-weight: 800 !important; }
    h2, h3 { color: #edf5ff; font-weight: 700 !important; }
    .hero {
        padding: 1.55rem 1.7rem;
        border: 1px solid rgba(94,234,212,0.20);
        border-radius: 22px;
        background: linear-gradient(115deg, rgba(17,54,72,0.94), rgba(18,31,53,0.96) 60%, rgba(30,41,74,0.94));
        box-shadow: 0 18px 50px rgba(0,0,0,0.18);
        margin-bottom: 1.25rem;
    }
    .eyebrow {
        color: #5eead4;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }
    .hero-title {
        color: #f8fbff;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(1.7rem, 3vw, 2.65rem);
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 0.5rem;
    }
    .hero-sub {
        color: #b7c8dc;
        font-size: 1rem;
        max-width: 850px;
        line-height: 1.6;
    }
    .section-note {
        color: #94a9c3;
        font-size: 0.9rem;
        margin-top: -0.55rem;
        margin-bottom: 1rem;
    }
    .kpi {
        min-height: 132px;
        padding: 1.15rem 1.2rem;
        border-radius: 18px;
        border: 1px solid rgba(148,163,184,0.16);
        background: linear-gradient(145deg, rgba(21,37,59,0.96), rgba(14,26,44,0.96));
        box-shadow: 0 10px 28px rgba(0,0,0,0.12);
    }
    .kpi-label {
        color: #9db2ca;
        font-size: 0.84rem;
        font-weight: 600;
        margin-bottom: 0.65rem;
    }
    .kpi-value {
        color: #f5f9ff;
        font-family: 'Manrope', sans-serif;
        font-size: 2rem;
        line-height: 1.1;
        font-weight: 800;
    }
    .kpi-foot {
        color: #5eead4;
        font-size: 0.78rem;
        margin-top: 0.55rem;
    }
    .panel {
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 18px;
        background: rgba(15,28,47,0.62);
        padding: 1rem 1.1rem 0.5rem 1.1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid rgba(148,163,184,0.15);
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(19,35,56,0.8);
        border-radius: 10px 10px 0 0;
        padding: 0.7rem 1rem;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 12px;
        overflow: hidden;
    }
    div.stDownloadButton > button {
        background: linear-gradient(90deg, #0f9f91, #0e7490);
        color: white;
        border: 0;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.55rem 1rem;
    }
    div.stDownloadButton > button:hover {
        border: 1px solid #5eead4;
        color: white;
    }
    .footnote {
        border-top: 1px solid rgba(148,163,184,0.15);
        margin-top: 2rem;
        padding-top: 1rem;
        color: #8298b2;
        font-size: 0.82rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------- Data loading -----------------------
@st.cache_data
def load_event_log():
    path = CLEAN_LOG if CLEAN_LOG.exists() else RAW_LOG
    if not path.exists():
        return pd.DataFrame(columns=["Case_ID", "Activity_Name", "Timestamp"])

    df = pd.read_csv(path)
    rename_map = {}

    for col in df.columns:
        key = col.strip().lower().replace(" ", "_")
        if key in {"case_id", "caseid", "patient_id", "patientid", "case"}:
            rename_map[col] = "Case_ID"
        elif key in {"activity_name", "activity", "activityname", "event"}:
            rename_map[col] = "Activity_Name"
        elif key in {"timestamp", "time", "event_time", "datetime", "event_timestamp"}:
            rename_map[col] = "Timestamp"

    df = df.rename(columns=rename_map)
    required = {"Case_ID", "Activity_Name", "Timestamp"}
    if not required.issubset(df.columns):
        raise ValueError(
            "Event log needs Case_ID, Activity_Name, and Timestamp. "
            f"Found columns: {list(df.columns)}"
        )

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Case_ID", "Activity_Name", "Timestamp"]).copy()
    df["Case_ID"] = df["Case_ID"].astype(str)
    df["Activity_Name"] = df["Activity_Name"].astype(str)
    return df.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)


def build_analysis(df):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    journey = (
        df.groupby("Case_ID")
        .agg(
            First_Activity=("Timestamp", "min"),
            Last_Activity=("Timestamp", "max"),
            Total_Events=("Activity_Name", "size"),
            Unique_Activities=("Activity_Name", "nunique"),
        )
        .reset_index()
    )
    journey["Journey_Duration_Hours"] = (
        (journey["Last_Activity"] - journey["First_Activity"])
        .dt.total_seconds() / 3600
    )

    activity_frequency = (
        df.groupby("Activity_Name")
        .agg(
            Event_Count=("Activity_Name", "size"),
            Patient_Count=("Case_ID", "nunique"),
        )
        .reset_index()
        .sort_values("Event_Count", ascending=False)
    )

    ordered = df.sort_values(["Case_ID", "Timestamp"]).copy()
    ordered["Previous_Activity"] = ordered.groupby("Case_ID")["Activity_Name"].shift(1)
    ordered["Previous_Timestamp"] = ordered.groupby("Case_ID")["Timestamp"].shift(1)
    ordered["Elapsed_Hours"] = (
        (ordered["Timestamp"] - ordered["Previous_Timestamp"])
        .dt.total_seconds() / 3600
    )

    transitions = ordered.dropna(
        subset=["Previous_Activity", "Previous_Timestamp", "Elapsed_Hours"]
    ).copy()
    transitions = transitions[transitions["Elapsed_Hours"] >= 0].copy()

    if transitions.empty:
        summary = pd.DataFrame()
    else:
        summary = (
            transitions.groupby(["Previous_Activity", "Activity_Name"])
            .agg(
                Transition_Count=("Elapsed_Hours", "size"),
                Average_Elapsed_Hours=("Elapsed_Hours", "mean"),
                Median_Elapsed_Hours=("Elapsed_Hours", "median"),
                Maximum_Elapsed_Hours=("Elapsed_Hours", "max"),
            )
            .reset_index()
        )
        summary["Transition"] = (
            summary["Previous_Activity"] + " → " + summary["Activity_Name"]
        )
        transitions["Transition"] = (
            transitions["Previous_Activity"] + " → " + transitions["Activity_Name"]
        )

    return journey, activity_frequency, summary, transitions


def plotly_theme(fig, height=390):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#dce8f7", size=12),
        title=dict(font=dict(size=16, color="#f3f7ff"), x=0.02, xanchor="left"),
        margin=dict(l=15, r=20, t=65, b=30),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#b9cbe0"),
        ),
        hoverlabel=dict(
            bgcolor="#13243a",
            bordercolor="#2dd4bf",
            font=dict(color="#f8fafc"),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.12)",
        zerolinecolor="rgba(148,163,184,0.15)",
        linecolor="rgba(148,163,184,0.2)",
    )
    fig.update_yaxes(
        showgrid=False,
        linecolor="rgba(148,163,184,0.2)",
    )
    return fig


def metric_card(label, value, foot):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------- Header --------------------------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Clinical process intelligence</div>
        <div class="hero-title">CareFlow <span style="color:#5eead4;">/</span> Clinical Analytics</div>
        <div class="hero-sub">
            Explore patient pathways, compare activity transitions, and identify
            time-intensive steps in the care journey through an interactive process-mining workspace.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    event_log = load_event_log()
except Exception as exc:
    st.error(f"Could not load the event log: {exc}")
    st.stop()

if event_log.empty:
    st.warning(
        "No event log found. Run `python main.py` in the CareFlow project folder, "
        "then refresh this dashboard."
    )
    st.stop()

# ------------------------- Sidebar -------------------------
st.sidebar.markdown("## 🔎 Explore data")
st.sidebar.caption("Use the filters to focus the analysis.")

all_patients = sorted(event_log["Case_ID"].unique().tolist())
all_activities = sorted(event_log["Activity_Name"].unique().tolist())
min_date = event_log["Timestamp"].min().date()
max_date = event_log["Timestamp"].max().date()

patient_choice = st.sidebar.radio(
    "Patient cohort",
    ["All patients", "Choose patients"],
    index=0,
)
if patient_choice == "Choose patients":
    selected_patients = st.sidebar.multiselect(
        "Patients",
        all_patients,
        default=all_patients[:min(10, len(all_patients))],
    )
else:
    selected_patients = all_patients

selected_activities = st.sidebar.multiselect(
    "Activities",
    all_activities,
    default=all_activities,
)

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

filtered = event_log[event_log["Case_ID"].isin(selected_patients)].copy()
filtered = filtered[filtered["Activity_Name"].isin(selected_activities)].copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[filtered["Timestamp"].dt.date.between(start_date, end_date)].copy()

st.sidebar.markdown("---")
st.sidebar.caption("Source: CareFlow event log")
st.sidebar.caption("Data type: simulated / demonstration")

if filtered.empty:
    st.warning("No events match these filters. Adjust the sidebar selections.")
    st.stop()

filtered = filtered.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)
journey, activity_frequency, transition_summary, transition_events = build_analysis(filtered)

# ------------------------- KPI row -------------------------
total_events = len(filtered)
patient_count = filtered["Case_ID"].nunique()
activity_count = filtered["Activity_Name"].nunique()
avg_duration = journey["Journey_Duration_Hours"].mean() if not journey.empty else 0.0
median_duration = journey["Journey_Duration_Hours"].median() if not journey.empty else 0.0

st.markdown("### At a glance")
k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    metric_card("RECORDED EVENTS", f"{total_events:,}", "Events in current selection")
with k2:
    metric_card("PATIENTS ANALYSED", f"{patient_count:,}", "Unique patient cases")
with k3:
    metric_card("ACTIVITIES", f"{activity_count:,}", "Distinct activity types")
with k4:
    metric_card("AVG. JOURNEY", f"{avg_duration:.2f} h", f"Median: {median_duration:.2f} h")

st.markdown("<br>", unsafe_allow_html=True)

# --------------------- Overview charts --------------------
st.markdown("### 📊 Activity overview")
st.markdown(
    '<div class="section-note">Compare activity volume and understand how long recorded patient journeys span.</div>',
    unsafe_allow_html=True,
)
left, right = st.columns([1.05, 1], gap="large")

with left:
    freq = activity_frequency.sort_values("Event_Count", ascending=True).copy()
    fig_freq = px.bar(
        freq,
        x="Event_Count",
        y="Activity_Name",
        orientation="h",
        text="Event_Count",
        hover_data={"Patient_Count": True, "Event_Count": ":,d"},
        labels={
            "Event_Count": "Recorded events",
            "Activity_Name": "Hospital activity",
            "Patient_Count": "Patients",
        },
        title="Events by hospital activity",
        color="Event_Count",
        color_continuous_scale=["#164e63", "#0d9488", "#5eead4"],
    )
    fig_freq.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Events: %{x:,}<br><extra></extra>",
    )
    fig_freq.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Number of recorded events",
        yaxis_title="",
        bargap=0.32,
    )
    plotly_theme(fig_freq, 400)
    st.plotly_chart(fig_freq, width="stretch", config={"displaylogo": False})

with right:
    if not journey.empty:
        journey_plot = journey.copy()
        journey_plot["Journey_Duration_Hours"] = journey_plot["Journey_Duration_Hours"].round(2)
        fig_duration = px.histogram(
            journey_plot,
            x="Journey_Duration_Hours",
            nbins=14,
            marginal="box",
            title="Patient journey duration distribution",
            labels={"Journey_Duration_Hours": "Recorded journey duration (hours)", "count": "Patients"},
            color_discrete_sequence=["#38bdf8"],
            hover_data=["Journey_Duration_Hours"],
        )
        fig_duration.update_traces(
            marker_line_color="#7dd3fc",
            marker_line_width=1,
            opacity=0.9,
        )
        fig_duration.update_layout(
            xaxis_title="Journey duration (hours)",
            yaxis_title="Number of patients",
            bargap=0.12,
            showlegend=False,
        )
        plotly_theme(fig_duration, 400)
        st.plotly_chart(fig_duration, width="stretch", config={"displaylogo": False})
    else:
        st.info("Journey duration is not available for the selected records.")

# -------------------- Journey table -----------------------
st.markdown("### 🧭 Patient journey details")
st.markdown(
    '<div class="section-note">Each row summarizes the first and last recorded event for a patient in the current selection.</div>',
    unsafe_allow_html=True,
)
journey_display = journey.copy()
if not journey_display.empty:
    for col in ["First_Activity", "Last_Activity"]:
        journey_display[col] = journey_display[col].dt.strftime("%d %b %Y, %H:%M")
    journey_display["Journey_Duration_Hours"] = journey_display["Journey_Duration_Hours"].round(2)
    journey_display = journey_display.rename(
        columns={
            "Case_ID": "Patient ID",
            "First_Activity": "First recorded event",
            "Last_Activity": "Last recorded event",
            "Total_Events": "Events",
            "Unique_Activities": "Unique activities",
            "Journey_Duration_Hours": "Journey duration (h)",
        }
    )
    st.dataframe(
        journey_display,
        width="stretch",
        hide_index=True,
        height=300,
        column_config={
            "Journey duration (h)": st.column_config.NumberColumn(format="%.2f h"),
            "Events": st.column_config.NumberColumn(format="%d"),
            "Unique activities": st.column_config.NumberColumn(format="%d"),
        },
    )
    st.download_button(
        "Download patient journey table",
        journey_display.to_csv(index=False).encode("utf-8"),
        file_name="careflow_patient_journeys.csv",
        mime="text/csv",
    )

# ------------------ Transition analysis --------------------
st.markdown("---")
st.markdown("### ⏱️ Transition performance")
st.markdown(
    '<div class="section-note">Elapsed time is calculated between consecutive recorded activities for each patient.</div>',
    unsafe_allow_html=True,
)

if transition_summary.empty:
    st.info("No consecutive activity transitions are available for the selected filters.")
else:
    trans_left, trans_right = st.columns([1.1, 0.9], gap="large")
    with trans_left:
        trans_plot = transition_summary.sort_values("Average_Elapsed_Hours", ascending=True).copy()
        fig_trans = px.bar(
            trans_plot,
            x="Average_Elapsed_Hours",
            y="Transition",
            orientation="h",
            text=trans_plot["Average_Elapsed_Hours"].map(lambda v: f"{v:.2f} h"),
            labels={
                "Average_Elapsed_Hours": "Average elapsed time (hours)",
                "Transition": "Activity transition",
            },
            title="Average time between activities",
            color="Average_Elapsed_Hours",
            color_continuous_scale=["#155e75", "#0891b2", "#67e8f9"],
            hover_data={
                "Transition_Count": True,
                "Median_Elapsed_Hours": ":.2f",
                "Maximum_Elapsed_Hours": ":.2f",
            },
        )
        fig_trans.update_traces(
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
        )
        fig_trans.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Average elapsed time (hours)",
            yaxis_title="",
            bargap=0.3,
        )
        plotly_theme(fig_trans, max(390, 38 * len(trans_plot) + 100))
        st.plotly_chart(fig_trans, width="stretch", config={"displaylogo": False})

    with trans_right:
        st.markdown("#### Transition summary")
        trans_table = transition_summary[
            [
                "Previous_Activity",
                "Activity_Name",
                "Transition_Count",
                "Average_Elapsed_Hours",
                "Median_Elapsed_Hours",
                "Maximum_Elapsed_Hours",
            ]
        ].copy()
        trans_table = trans_table.rename(
            columns={
                "Previous_Activity": "From",
                "Activity_Name": "To",
                "Transition_Count": "Count",
                "Average_Elapsed_Hours": "Average (h)",
                "Median_Elapsed_Hours": "Median (h)",
                "Maximum_Elapsed_Hours": "Maximum (h)",
            }
        )
        for col in ["Average (h)", "Median (h)", "Maximum (h)"]:
            trans_table[col] = trans_table[col].round(2)
        trans_table = trans_table.sort_values("Average (h)", ascending=False)
        st.dataframe(
            trans_table,
            width="stretch",
            hide_index=True,
            height=390,
            column_config={
                "Average (h)": st.column_config.NumberColumn(format="%.2f"),
                "Median (h)": st.column_config.NumberColumn(format="%.2f"),
                "Maximum (h)": st.column_config.NumberColumn(format="%.2f"),
            },
        )

    # ---------------- Bottleneck detection ----------------
    st.markdown("#### 🚦 Bottleneck watchlist")
    st.markdown(
        '<div class="section-note">Ranked by average elapsed time. Severity labels are configurable demonstration indicators, not clinical standards.</div>',
        unsafe_allow_html=True,
    )

    bottlenecks = transition_summary.nlargest(
        min(10, len(transition_summary)),
        "Average_Elapsed_Hours",
    ).copy()

    # Relative categories make more sense than hard-coded 1.0-hour thresholds:
    # classify against the distribution of transitions in this filtered dataset.
    if len(transition_summary) == 1:
        bottlenecks["Severity"] = "Review"
    else:
        q75 = transition_summary["Average_Elapsed_Hours"].quantile(0.75)
        q40 = transition_summary["Average_Elapsed_Hours"].quantile(0.40)
        bottlenecks["Severity"] = np.select(
            [
                bottlenecks["Average_Elapsed_Hours"] >= q75,
                bottlenecks["Average_Elapsed_Hours"] >= q40,
            ],
            ["High", "Moderate"],
            default="Lower",
        )

    sev_order = {"High": 0, "Moderate": 1, "Lower": 2, "Review": 0}
    bottlenecks["_sev_order"] = bottlenecks["Severity"].map(sev_order).fillna(3)
    bottlenecks = bottlenecks.sort_values(
        ["_sev_order", "Average_Elapsed_Hours"],
        ascending=[True, False],
    )

    bleft, bright = st.columns([1.1, 0.9], gap="large")
    with bleft:
        fig_bottle = px.bar(
            bottlenecks.sort_values("Average_Elapsed_Hours", ascending=True),
            x="Average_Elapsed_Hours",
            y="Transition",
            orientation="h",
            text=bottlenecks.sort_values("Average_Elapsed_Hours", ascending=True)[
                "Average_Elapsed_Hours"
            ].map(lambda v: f"{v:.2f} h"),
            color="Severity",
            category_orders={"Severity": ["High", "Moderate", "Lower", "Review"]},
            color_discrete_map={
                "High": "#fb7185",
                "Moderate": "#fbbf24",
                "Lower": "#2dd4bf",
                "Review": "#a78bfa",
            },
            title="Transitions needing attention",
            labels={"Average_Elapsed_Hours": "Average elapsed time (hours)", "Transition": ""},
        )
        fig_bottle.update_traces(textposition="outside", cliponaxis=False)
        fig_bottle.update_layout(
            xaxis_title="Average elapsed time (hours)",
            yaxis_title="",
            legend_title="Relative category",
            bargap=0.28,
        )
        plotly_theme(fig_bottle, max(390, 38 * len(bottlenecks) + 100))
        st.plotly_chart(fig_bottle, width="stretch", config={"displaylogo": False})

    with bright:
        bottle_table = bottlenecks[
            [
                "Transition",
                "Transition_Count",
                "Average_Elapsed_Hours",
                "Median_Elapsed_Hours",
                "Maximum_Elapsed_Hours",
                "Severity",
            ]
        ].copy().rename(
            columns={
                "Transition": "Transition",
                "Transition_Count": "Occurrences",
                "Average_Elapsed_Hours": "Average (h)",
                "Median_Elapsed_Hours": "Median (h)",
                "Maximum_Elapsed_Hours": "Maximum (h)",
            }
        )
        for col in ["Average (h)", "Median (h)", "Maximum (h)"]:
            bottle_table[col] = bottle_table[col].round(2)
        st.dataframe(
            bottle_table,
            width="stretch",
            hide_index=True,
            height=390,
            column_config={
                "Average (h)": st.column_config.NumberColumn(format="%.2f"),
                "Median (h)": st.column_config.NumberColumn(format="%.2f"),
                "Maximum (h)": st.column_config.NumberColumn(format="%.2f"),
            },
        )
        st.download_button(
            "Download bottleneck report",
            bottle_table.to_csv(index=False).encode("utf-8"),
            file_name="careflow_bottleneck_report.csv",
            mime="text/csv",
        )

# -------------------- Activity pathways --------------------
st.markdown("---")
st.markdown("### 🔗 Patient activity pathways")
st.markdown(
    '<div class="section-note">The Sankey diagram shows how often one recorded activity follows another.</div>',
    unsafe_allow_html=True,
)

if transition_events.empty:
    st.info("Pathway flow is unavailable for the selected records.")
else:
    pathway_counts = (
        transition_events.groupby(["Previous_Activity", "Activity_Name"])
        .size()
        .reset_index(name="Transition_Count")
    )
    labels = list(
        dict.fromkeys(
            pathway_counts["Previous_Activity"].tolist()
            + pathway_counts["Activity_Name"].tolist()
        )
    )
    label_index = {label: idx for idx, label in enumerate(labels)}

    sankey = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    label=labels,
                    pad=22,
                    thickness=20,
                    line=dict(color="rgba(148,163,184,0.35)", width=0.8),
                    color=[
                        "#0f766e",
                        "#0891b2",
                        "#2563eb",
                        "#7c3aed",
                        "#d97706",
                        "#be123c",
                        "#475569",
                    ][:len(labels)],
                ),
                link=dict(
                    source=pathway_counts["Previous_Activity"].map(label_index).tolist(),
                    target=pathway_counts["Activity_Name"].map(label_index).tolist(),
                    value=pathway_counts["Transition_Count"].tolist(),
                    color="rgba(94,234,212,0.28)",
                    hovertemplate=(
                        "%{source.label} → %{target.label}"
                        "<br>Recorded transitions: %{value}<extra></extra>"
                    ),
                ),
            )
        ]
    )
    sankey.update_layout(
        title="Flow between hospital activities",
        height=470,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#e2e8f0", size=12),
        margin=dict(l=20, r=20, t=65, b=25),
    )
    st.plotly_chart(sankey, width="stretch", config={"displaylogo": False})

    # ---------------------- 3D workflow --------------------
    st.markdown("### 🌐 3D workflow network")
    st.markdown(
        '<div class="section-note">Interactive network layout for exploring connections between activity types. Drag to rotate and use the toolbar to zoom.</div>',
        unsafe_allow_html=True,
    )

    # Use the full activity transition network from current filtered records.
    node_names = labels
    angles = np.linspace(0, 2 * np.pi, len(node_names), endpoint=False)
    coordinates = {
        name: (
            float(np.cos(angle)),
            float(np.sin(angle)),
            float((idx % 3) * 0.8),
        )
        for idx, (name, angle) in enumerate(zip(node_names, angles))
    }

    edge_x, edge_y, edge_z = [], [], []
    for row in pathway_counts.itertuples(index=False):
        src, dst = row[0], row[1]
        x0, y0, z0 = coordinates[src]
        x1, y1, z1 = coordinates[dst]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    node_x = [coordinates[name][0] for name in node_names]
    node_y = [coordinates[name][1] for name in node_names]
    node_z = [coordinates[name][2] for name in node_names]

    workflow = go.Figure()
    workflow.add_trace(
        go.Scatter3d(
            x=edge_x,
            y=edge_y,
            z=edge_z,
            mode="lines",
            line=dict(color="rgba(45,212,191,0.65)", width=4),
            hoverinfo="skip",
            name="Transitions",
        )
    )
    workflow.add_trace(
        go.Scatter3d(
            x=node_x,
            y=node_y,
            z=node_z,
            mode="markers+text",
            marker=dict(
                size=9,
                color=list(range(len(node_names))),
                colorscale="Teal",
                line=dict(color="#e0f2fe", width=1),
                opacity=0.95,
            ),
            text=node_names,
            textposition="top center",
            textfont=dict(size=11, color="#eaf6ff"),
            customdata=node_names,
            hovertemplate="<b>%{customdata}</b><extra></extra>",
            name="Activities",
        )
    )
    workflow.update_layout(
        height=560,
        title="Activity connection map",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#dce8f7", size=12),
        margin=dict(l=0, r=0, t=65, b=0),
        scene=dict(
            xaxis=dict(title="", showbackground=False, showticklabels=False, zeroline=False, showgrid=False),
            yaxis=dict(title="", showbackground=False, showticklabels=False, zeroline=False, showgrid=False),
            zaxis=dict(title="", showbackground=False, showticklabels=False, zeroline=False, showgrid=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    )
    st.plotly_chart(workflow, width="stretch", config={"displaylogo": False})

# ----------------------- Event explorer --------------------
st.markdown("---")
st.markdown("### 🗂️ Event log explorer")
st.markdown(
    '<div class="section-note">Inspect the filtered event records, search activities, and export the current view.</div>',
    unsafe_allow_html=True,
)

search_term = st.text_input(
    "Search patient ID or activity",
    placeholder="Example: CASE_0001 or Diagnosis",
)
event_view = filtered.copy()
if search_term.strip():
    term = search_term.strip().lower()
    mask = (
        event_view["Case_ID"].str.lower().str.contains(term, na=False)
        | event_view["Activity_Name"].str.lower().str.contains(term, na=False)
    )
    event_view = event_view[mask]

event_display = event_view.copy()
event_display["Timestamp"] = event_display["Timestamp"].dt.strftime("%d %b %Y, %H:%M:%S")
event_display = event_display.rename(
    columns={
        "Case_ID": "Patient ID",
        "Activity_Name": "Activity",
        "Timestamp": "Event timestamp",
    }
)
st.caption(f"Showing {len(event_display):,} of {len(filtered):,} filtered event records.")
st.dataframe(
    event_display,
    width="stretch",
    hide_index=True,
    height=360,
)
st.download_button(
    "Download filtered event log",
    event_view.to_csv(index=False).encode("utf-8"),
    file_name="careflow_filtered_event_log.csv",
    mime="text/csv",
)

# -------------------------- Footer -------------------------
st.markdown(
    """
    <div class="footnote">
        <strong style="color:#b6c8dc;">CareFlow Clinical Pathway Process Mining</strong><br>
        Demonstration dashboard using simulated event data. Transition elapsed times are calculated
        from timestamps in the event log and should not be treated as verified hospital waiting times
        or clinical performance standards.
    </div>
    """,
    unsafe_allow_html=True,
)
