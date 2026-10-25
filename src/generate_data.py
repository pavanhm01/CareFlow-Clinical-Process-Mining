import pandas as pd
import numpy as np
from pathlib import Path


def generate_hospital_data(num_patients=100):
    """Generate simulated hospital event logs with realistic process delays."""

    np.random.seed(42)

    activities = [
        "Registration",
        "Initial Assessment",
        "Doctor Consultation",
        "Lab Test",
        "Diagnosis",
        "Treatment",
        "Discharge"
    ]

    records = []
    start_date = pd.Timestamp("2026-01-01")

    for patient_num in range(1, num_patients + 1):
        case_id = f"CASE_{patient_num:04d}"
        current_time = start_date + pd.Timedelta(
            days=int(np.random.randint(0, 90))
        )

        patient_activities = activities.copy()

        # Introduce operational inefficiencies and loop-backs.
        if np.random.random() < 0.30:
            patient_activities.insert(
                patient_activities.index("Doctor Consultation") + 1,
                "Initial Assessment"
            )

        if np.random.random() < 0.25:
            patient_activities.insert(
                patient_activities.index("Treatment"),
                "Lab Test"
            )

        for activity in patient_activities:
            current_time += pd.Timedelta(
                minutes=int(np.random.randint(10, 121))
            )

            records.append({
                "Case_ID": case_id,
                "Activity_Name": activity,
                "Timestamp": current_time
            })

    df = pd.DataFrame(records)

    output_path = Path("data/raw/hospital_event_log.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} events for {num_patients} patients.")
    print(f"Saved to: {output_path}")

    return df


if __name__ == "__main__":
    generate_hospital_data()