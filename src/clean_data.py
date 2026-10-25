import pandas as pd
from pathlib import Path


def clean_hospital_data():
    input_path = Path("data/raw/hospital_event_log.csv")
    output_path = Path("data/processed/cleaned_event_log.csv")

    if not input_path.exists():
        raise FileNotFoundError(
            "Hospital event log not found. Run generate_data.py first."
        )

    df = pd.read_csv(input_path)

    # Normalize columns and data types
    df.columns = df.columns.str.strip()
    df["Case_ID"] = df["Case_ID"].astype(str).str.strip()
    df["Activity_Name"] = df["Activity_Name"].astype(str).str.strip()
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], errors="coerce"
    )

    # Remove invalid records and duplicates
    df = df.dropna(
        subset=["Case_ID", "Activity_Name", "Timestamp"]
    )
    df = df.drop_duplicates()

    # Sort events by patient and timestamp
    df = df.sort_values(
        ["Case_ID", "Timestamp"]
    ).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print("Data cleaning completed successfully!")
    print(f"Total cleaned events: {len(df)}")
    print(f"Unique patients: {df['Case_ID'].nunique()}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    clean_hospital_data()