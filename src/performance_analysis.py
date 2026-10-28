from pathlib import Path

import pandas as pd


def load_event_log(file_path="data/processed/cleaned_event_log.csv"):
    """Load and validate the cleaned hospital event log."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Event log not found: {path}. Run python main.py first."
        )

    df = pd.read_csv(path)

    required_columns = {"Case_ID", "Activity_Name", "Timestamp"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    df["Case_ID"] = df["Case_ID"].astype(str).str.strip()
    df["Activity_Name"] = df["Activity_Name"].astype(str).str.strip()
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], errors="coerce"
    )

    df = df.dropna(
        subset=["Case_ID", "Activity_Name", "Timestamp"]
    )

    return df.sort_values(
        ["Case_ID", "Timestamp"]
    ).reset_index(drop=True)


def calculate_patient_journey(df):
    """Calculate the observed event-log span for each patient."""

    patient_journey = (
        df.groupby("Case_ID")
        .agg(
            First_Activity=("Timestamp", "min"),
            Last_Activity=("Timestamp", "max"),
            Total_Events=("Activity_Name", "size"),
            Unique_Activities=("Activity_Name", "nunique")
        )
        .reset_index()
    )

    patient_journey["Journey_Duration_Hours"] = (
        patient_journey["Last_Activity"]
        - patient_journey["First_Activity"]
    ).dt.total_seconds() / 3600

    return patient_journey


def calculate_activity_timing(df):
    """Calculate elapsed time between consecutive recorded activities."""

    result = df.copy()

    result["Previous_Activity"] = (
        result.groupby("Case_ID")["Activity_Name"].shift(1)
    )

    result["Previous_Timestamp"] = (
        result.groupby("Case_ID")["Timestamp"].shift(1)
    )

    result["Elapsed_Hours"] = (
        result["Timestamp"] - result["Previous_Timestamp"]
    ).dt.total_seconds() / 3600

    transitions = result.dropna(
        subset=["Previous_Activity", "Elapsed_Hours"]
    ).copy()

    transition_summary = (
        transitions.groupby(
            ["Previous_Activity", "Activity_Name"]
        )
        .agg(
            Transition_Count=("Case_ID", "size"),
            Average_Elapsed_Hours=("Elapsed_Hours", "mean"),
            Median_Elapsed_Hours=("Elapsed_Hours", "median"),
            Maximum_Elapsed_Hours=("Elapsed_Hours", "max")
        )
        .reset_index()
        .sort_values(
            "Average_Elapsed_Hours", ascending=False
        )
    )

    return transitions, transition_summary


def calculate_activity_frequency(df):
    """Summarize how frequently each activity occurs."""

    return (
        df.groupby("Activity_Name")
        .agg(
            Event_Count=("Case_ID", "size"),
            Patient_Count=("Case_ID", "nunique")
        )
        .reset_index()
        .sort_values("Event_Count", ascending=False)
    )


def generate_performance_report():
    """Run the performance analysis and save CSV reports."""

    df = load_event_log()

    patient_journey = calculate_patient_journey(df)
    transitions, transition_summary = calculate_activity_timing(df)
    activity_frequency = calculate_activity_frequency(df)

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    patient_journey.to_csv(
        output_dir / "patient_journey_analysis.csv", index=False
    )

    transitions.to_csv(
        output_dir / "activity_transition_times.csv", index=False
    )

    transition_summary.to_csv(
        output_dir / "transition_performance_summary.csv", index=False
    )

    activity_frequency.to_csv(
        output_dir / "activity_frequency_analysis.csv", index=False
    )

    print("\n=== CAREFLOW PROCESS PERFORMANCE REPORT ===")
    print(f"Total recorded events: {len(df)}")
    print(f"Unique patients: {df['Case_ID'].nunique()}")

    print("\nPatient Journey Duration (hours):")
    print(
        patient_journey["Journey_Duration_Hours"]
        .describe()
        .round(2)
    )

    print("\nActivity Frequency:")
    print(activity_frequency.to_string(index=False))

    print("\nTransitions with Highest Average Elapsed Time:")
    print(transition_summary.head(10).to_string(index=False))

    print("\nReports saved in the outputs folder.")

    return patient_journey, transitions, transition_summary, activity_frequency


if __name__ == "__main__":
    generate_performance_report()