import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

# ============================================================
# CAREFLOW | CLINICAL PATHWAY PROCESS MINING
# ============================================================
st.set_page_config(
    page_title="CareFlow | Clinical Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------- THEME ---------------------------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp {
    background: radial-gradient(ellipse at top left, #172554 0%, #0b1220 42%, #080d17 100%);
    color: #e5edf8;
}
.block-container { max-width: 1700px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #111827; border-right: 1px solid #263449; }
h1, h2, h3 { color: #f8fafc !important; letter-spacing: -0.02em; }
p, label, .stCaption { color: #cbd5e1; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(30, 58, 138, .62), rgba(15, 23, 42, .96));
    border: 1px solid #334b70; border-radius: 16px; padding: 19px 20px;
    box-shadow: 0 8px 28px rgba(0,0,0,.20); min-height: 115px;
}
div[data-testid="stMetricLabel"] { color: #cbd5e1 !important; }
div[data-testid="stMetricValue"] { color: #67e8f9 !important; font-weight: 750; }
div[data-testid="stMetricDelta"] { color: #a7f3d0 !important; }
hr { border-color: #263449; }
section[data-testid="stMain"] div[data-testid="stPlotlyChart"] { border-radius: 14px; }
div[data-testid="stAlert"] { border-radius: 12px; }
.small-note { color: #94a3b8; font-size: .85rem; }
.hero {
    padding: 1.25rem 1.5rem; border-radius: 18px; margin-bottom: 1rem;
    background: linear-gradient(110deg, rgba(14,165,233,.18), rgba(99,102,241,.12), rgba(15,23,42,.3));
    border: 1px solid rgba(125,211,252,.22);
}
</style>
""", unsafe_allow_html=True)

# --------------------------- HEADER -------------------------
st.markdown("""
<div class="hero">
  <h1>🏥 CareFlow</h1>
  <h3>Clinical Pathway Process Mining</h3>
  <p>Interactive workflow analytics • Process discovery • Patient journey exploration</p>
  <p class="small-note">Educational prototype using simulated hospital event data — not real patient records.</p>
</div>
""", unsafe_allow_html=True)

# --------------------------- DATA ---------------------------
DATA_PATH = Path("data/processed/cleaned_event_log.csv")
RAW_PATH = Path("data/raw/hospital_event_log.csv")

if not DATA_PATH.exists():
    st.error(f"Processed dataset not found: `{DATA_PATH}`")
    st.info("From your project folder, run `python main.py` first to generate and clean the dataset.")
    st.stop()

try:
    df = pd.read_csv(DATA_PATH)
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.stop()

required = {"Case_ID", "Activity_Name", "Timestamp"}
missing = required - set(df.columns)
if missing:
    st.error(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    st.stop()

df["Case_ID"] = df["Case_ID"].astype(str)
df["Activity_Name"] = df["Activity_Name"].astype(str)
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df = df.dropna(subset=["Case_ID", "Activity_Name", "Timestamp"])
df = df.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)

if df.empty:
    st.error("The dataset contains no valid events.")
    st.stop()

# --------------------------- SIDEBAR ------------------------
st.sidebar.markdown("## 🔎 Explore event log")
st.sidebar.caption("Filter the simulated patient records.")

patient_ids = sorted(df["Case_ID"].unique().tolist())
activity_names = sorted(df["Activity_Name"].unique().tolist())

patient_mode = st.sidebar.radio(
    "Patient selection",
    ["All patients", "Choose patients"],
    horizontal=False
)
if patient_mode == "Choose patients":
    chosen_patients = st.sidebar.multiselect(
        "Patient IDs", patient_ids, default=patient_ids[:1],
        placeholder="Search patient IDs"
    )
else:
    chosen_patients = patient_ids

chosen_activities = st.sidebar.multiselect(
    "Activities",
    activity_names,
    default=activity_names,
    placeholder="Choose activities"
)

date_min = df["Timestamp"].min().date()
date_max = df["Timestamp"].max().date()
date_range = st.sidebar.date_input(
    "Event date range",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max
)

filtered = df[
    df["Case_ID"].isin(chosen_patients)
    & df["Activity_Name"].isin(chosen_activities)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["Timestamp"].dt.date.between(start_date, end_date)
    ]

if filtered.empty:
    st.warning("No events match the selected filters. Change the patient, activity, or date filters.")
    st.stop()

filtered = filtered.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)

# --------------------------- KPIs ---------------------------
patient_count = filtered["Case_ID"].nunique()
event_count = len(filtered)
activity_count = filtered["Activity_Name"].nunique()
avg_events = event_count / patient_count if patient_count else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Simulated patients", f"{patient_count:,}")
k2.metric("📋 Events in view", f"{event_count:,}")
k3.metric("🏥 Activities in view", f"{activity_count:,}")
k4.metric("📈 Avg. events / patient", f"{avg_events:.1f}")

st.caption(f"Showing {event_count:,} events across {patient_count:,} patient cases after filtering.")
st.divider()

# --------------------- SEQUENCES + EDGES --------------------
sequences = {}
transition_counts = Counter()
for case_id, group in filtered.groupby("Case_ID", sort=True):
    group = group.sort_values("Timestamp")
    acts = group["Activity_Name"].tolist()
    sequences[case_id] = group
    for source, target in zip(acts[:-1], acts[1:]):
        transition_counts[(source, target)] += 1

# ----------------------- ACTIVITY ANALYTICS -----------------
st.header("📊 Activity Analytics")
left, right = st.columns(2)

activity_counts = (
    filtered["Activity_Name"].value_counts()
    .rename_axis("Activity").reset_index(name="Events")
    .sort_values("Events", ascending=True)
)

with left:
    st.subheader("Activity distribution")
    fig = px.bar(
        activity_counts, x="Events", y="Activity", orientation="h",
        text="Events", color="Events", color_continuous_scale="Blues",
        template="plotly_dark", title="Events recorded by activity"
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Events: %{x}<extra></extra>",
        marker_line_width=0
    )
    fig.update_layout(
        height=430, margin=dict(l=10, r=25, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False, xaxis_title="Event count", yaxis_title="",
        font=dict(color="#e2e8f0")
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Most frequent transitions")
    if transition_counts:
        trans_df = pd.DataFrame([
            {"Transition": f"{a} → {b}", "Frequency": n}
            for (a, b), n in transition_counts.items()
        ]).sort_values("Frequency", ascending=True).tail(10)
        fig_t = px.bar(
            trans_df, x="Frequency", y="Transition", orientation="h",
            text="Frequency", color="Frequency", color_continuous_scale="Teal",
            template="plotly_dark", title="Most common consecutive activities"
        )
        fig_t.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Transitions: %{x}<extra></extra>",
            marker_line_width=0
        )
        fig_t.update_layout(
            height=430, margin=dict(l=10, r=25, t=55, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, xaxis_title="Transition count", yaxis_title="",
            font=dict(color="#e2e8f0")
        )
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("No transitions available for the selected filters.")

# --------------------- 3D PROCESS NETWORK -------------------
st.divider()
st.header("🌐 Interactive 3D Patient Pathway")
st.write("Rotate with your mouse, scroll to zoom, and hover over a node to inspect its activity count.")

# Place nodes on a spacious layered ring for readability.
node_activities = activity_counts.sort_values("Events", ascending=False)["Activity"].tolist()
n_nodes = len(node_activities)
angles = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False) if n_nodes else []
radius = 8.0
positions = {}
for idx, act in enumerate(node_activities):
    # Alternate node heights, while preserving a consistent ring.
    z = [0.0, 2.3, 0.7, 3.0, 1.2, 2.6, 0.2][idx % 7]
    positions[act] = (
        float(radius * np.cos(angles[idx])),
        float(radius * np.sin(angles[idx])),
        float(z)
    )

node_counts = filtered["Activity_Name"].value_counts().to_dict()
max_count = max(node_counts.values()) if node_counts else 1

# Transition line segments: width varies with observed frequency.
edge_x, edge_y, edge_z = [], [], []
for (source, target), count in transition_counts.items():
    if source not in positions or target not in positions:
        continue
    x0, y0, z0 = positions[source]
    x1, y1, z1 = positions[target]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    edge_z.extend([z0, z1, None])

fig_3d = go.Figure()

# Base network edges.
fig_3d.add_trace(go.Scatter3d(
    x=edge_x, y=edge_y, z=edge_z,
    mode="lines",
    line=dict(color="rgba(56,189,248,0.58)", width=5),
    hoverinfo="skip",
    name="Observed transitions"
))

# Nodes and readable labels.
nx = [positions[a][0] for a in node_activities]
ny = [positions[a][1] for a in node_activities]
nz = [positions[a][2] for a in node_activities]
nv = [node_counts.get(a, 0) for a in node_activities]
sizes = [max(13, min(28, 12 + 15 * (v / max_count))) for v in nv]

fig_3d.add_trace(go.Scatter3d(
    x=nx, y=ny, z=nz,
    mode="markers+text",
    text=node_activities,
    textposition="top center",
    textfont=dict(size=12, color="#f8fafc"),
    customdata=nv,
    marker=dict(
        size=sizes, color=nv, colorscale="Turbo", opacity=1.0,
        showscale=True,
        colorbar=dict(title=dict(text="Event count"), thickness=13, len=0.72),
        line=dict(color="#e0f2fe", width=2),
        symbol="circle"
    ),
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Events: %{customdata}<br>"
        "3D layout coordinates: (%{x:.1f}, %{y:.1f}, %{z:.1f})"
        "<extra></extra>"
    ),
    name="Hospital activities"
))

fig_3d.update_layout(
    template="plotly_dark",
    height=760,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=15, b=0),
    scene=dict(
        bgcolor="rgba(9,16,32,0.65)",
        xaxis=dict(visible=False, range=[-11, 11]),
        yaxis=dict(visible=False, range=[-11, 11]),
        zaxis=dict(visible=False, range=[-2, 6]),
        camera=dict(eye=dict(x=1.55, y=1.55, z=1.15)),
        aspectmode="manual",
        aspectratio=dict(x=1.35, y=1.35, z=0.72)
    ),
    legend=dict(orientation="h", yanchor="bottom", y=0.99, xanchor="left", x=0.01),
    font=dict(color="#e2e8f0")
)
st.plotly_chart(fig_3d, use_container_width=True)
st.caption("Node size and color reflect event counts. Connections represent consecutive activities observed in the filtered simulated event log. The 3D positions are illustrative, not physical hospital locations.")

# --------------------------- SANKEY -------------------------
st.divider()
st.header("🔀 Patient Flow — Sankey Diagram")
st.write("Connection width represents the number of observed consecutive activity transitions.")

if transition_counts:
    sankey_activities = node_activities
    index_map = {name: i for i, name in enumerate(sankey_activities)}
    sankey_sources, sankey_targets, sankey_values, sankey_labels = [], [], [], []
    for (source, target), count in transition_counts.items():
        if source in index_map and target in index_map:
            sankey_sources.append(index_map[source])
            sankey_targets.append(index_map[target])
            sankey_values.append(int(count))
            sankey_labels.append(f"{source} → {target}: {count}")

    sankey = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=32, thickness=24,
            line=dict(color="rgba(226,232,240,.7)", width=1),
            label=sankey_activities,
            color=["#38bdf8", "#818cf8", "#2dd4bf", "#fbbf24", "#fb7185", "#a78bfa", "#34d399"][:len(sankey_activities)],
            hovertemplate="<b>%{label}</b><extra></extra>"
        ),
        link=dict(
            source=sankey_sources, target=sankey_targets, value=sankey_values,
            label=sankey_labels,
            color=["rgba(56,189,248,0.34)" for _ in sankey_values],
            hovertemplate="%{label}<extra></extra>"
        )
    ))
    sankey.update_layout(
        template="plotly_dark", height=620,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=25, b=20),
        font=dict(size=13, color="#f1f5f9")
    )
    st.plotly_chart(sankey, use_container_width=True)
else:
    st.info("No transitions available for the selected filters.")

# ------------------- PATIENT JOURNEY TIMELINE ----------------
st.divider()
st.header("🧭 Patient Journey Timeline")
timeline_patient = st.selectbox(
    "Choose a patient to inspect",
    options=sorted(filtered["Case_ID"].unique()),
    key="timeline_patient"
)
journey = filtered[filtered["Case_ID"] == timeline_patient].sort_values("Timestamp").copy()

if not journey.empty:
    journey["Event order"] = np.arange(1, len(journey) + 1)
    journey["Time label"] = journey["Timestamp"].dt.strftime("%d %b %Y, %H:%M:%S")
    fig_journey = px.scatter(
        journey, x="Timestamp", y="Activity_Name",
        color="Activity_Name", size_max=16,
        hover_data={"Case_ID": True, "Time label": True, "Event order": True, "Timestamp": False},
        template="plotly_dark", title=f"Activity timeline for {timeline_patient}"
    )
    fig_journey.update_traces(marker=dict(size=15, line=dict(width=1, color="#f8fafc")))
    fig_journey.update_layout(
        height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, xaxis_title="Event timestamp", yaxis_title="Activity",
        margin=dict(l=10, r=15, t=55, b=20)
    )
    st.plotly_chart(fig_journey, use_container_width=True)
    st.dataframe(
        journey[["Event order", "Timestamp", "Activity_Name"]].rename(
            columns={"Timestamp": "Timestamp", "Activity_Name": "Activity"}
        ),
        use_container_width=True, hide_index=True
    )
else:
    st.info("No events for this patient under the current filters.")

# ----------------------- REPEATED ACTIVITIES ----------------
st.divider()
st.header("🔁 Repeated Activity Analysis")
repeated_rows = []
for case_id, group in filtered.groupby("Case_ID"):
    counts = group["Activity_Name"].value_counts()
    for activity, count in counts.items():
        if count > 1:
            repeated_rows.append({
                "Patient ID": case_id,
                "Repeated activity": activity,
                "Occurrences": int(count)
            })

if repeated_rows:
    repeated_df = pd.DataFrame(repeated_rows).sort_values(
        ["Occurrences", "Patient ID"], ascending=[False, True]
    )
    a, b = st.columns(2)
    a.metric("Repeated patient/activity pairs", len(repeated_df))
    b.metric("Patients with repeated activities", repeated_df["Patient ID"].nunique())
    st.dataframe(repeated_df, use_container_width=True, hide_index=True)
else:
    st.success("No repeated activities were found in the filtered event log.")

# ---------------------- PROCESS MODEL IMAGES ----------------
st.divider()
st.header("🗺️ Discovered Process Models")
image_left, image_right = st.columns(2)
with image_left:
    st.subheader("NetworkX Process Graph")
    graph_path = Path("outputs/process_graph.png")
    if graph_path.exists():
        st.image(str(graph_path), use_container_width=True)
    else:
        st.info("Image not found. Run `python main.py` to generate the process graph.")
with image_right:
    st.subheader("PM4Py Process Model")
    petri_path = Path("outputs/pm4py_process_model.png")
    if petri_path.exists():
        st.image(str(petri_path), use_container_width=True)
    else:
        st.info("Image not found. Run `python main.py` to generate the PM4Py model.")

# -------------------------- EVENT LOG -----------------------
st.divider()
st.header("📁 Event Log Explorer")
with st.expander("Open filtered event log"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)

st.download_button(
    "⬇️ Download filtered event log (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="careflow_filtered_event_log.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("CareFlow Clinical Pathway Process Mining • Educational prototype • All records are simulated.")
# ============================================================
# WEEK 3: PROCESS PERFORMANCE ANALYSIS
# ============================================================

st.markdown("---")
st.header("⏱️ Process Performance Analysis")

try:
    from src.performance_analysis import (
        load_event_log,
        calculate_patient_journey,
        calculate_activity_timing,
        calculate_activity_frequency,
    )

    performance_df = load_event_log()

    patient_journey = calculate_patient_journey(performance_df)

    transitions, transition_summary = calculate_activity_timing(
        performance_df
    )

    activity_frequency = calculate_activity_frequency(performance_df)

    st.caption(
        "Analysis uses simulated hospital event data. "
        "Elapsed time represents the interval between recorded events."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Patients Analysed",
        f"{patient_journey['Case_ID'].nunique():,}"
    )

    col2.metric(
        "Average Journey Duration",
        f"{patient_journey['Journey_Duration_Hours'].mean():.2f} hrs"
    )

    col3.metric(
        "Longest Journey",
        f"{patient_journey['Journey_Duration_Hours'].max():.2f} hrs"
    )

    st.subheader("Patient Journey Duration")

    journey_fig = px.histogram(
        patient_journey,
        x="Journey_Duration_Hours",
        nbins=15,
        title="Distribution of Recorded Patient Journey Durations",
        labels={
            "Journey_Duration_Hours": "Duration (hours)"
        },
    )

    st.plotly_chart(journey_fig, width="stretch")

    st.subheader("Average Time Between Activities")

    if not transition_summary.empty:
        transition_summary = transition_summary.copy()

        transition_summary["Transition"] = (
            transition_summary["Previous_Activity"]
            + " → "
            + transition_summary["Activity_Name"]
        )

        transition_fig = px.bar(
            transition_summary.sort_values(
                "Average_Elapsed_Hours"
            ),
            x="Average_Elapsed_Hours",
            y="Transition",
            orientation="h",
            title="Average Elapsed Time Between Consecutive Activities",
            labels={
                "Average_Elapsed_Hours": "Average elapsed time (hours)",
                "Transition": "Activity transition",
            },
        )

        st.plotly_chart(transition_fig, width="stretch")

        st.subheader("Transition Performance Details")

        st.dataframe(
            transition_summary[
                [
                    "Previous_Activity",
                    "Activity_Name",
                    "Transition_Count",
                    "Average_Elapsed_Hours",
                    "Median_Elapsed_Hours",
                    "Maximum_Elapsed_Hours",
                ]
            ].round(2),
            width="stretch",
            hide_index=True,
        )

    st.subheader("Activity Frequency")

    activity_fig = px.bar(
        activity_frequency.sort_values("Event_Count"),
        x="Event_Count",
        y="Activity_Name",
        orientation="h",
        title="Recorded Events by Activity",
        labels={
            "Event_Count": "Number of events",
            "Activity_Name": "Hospital activity",
        },
    )

    st.plotly_chart(activity_fig, width="stretch")

    st.subheader("Patient Journey Details")

    st.dataframe(
        patient_journey.round(2),
        width="stretch",
        hide_index=True,
    )

except Exception as error:
    st.error(f"Unable to load process performance analysis: {error}")