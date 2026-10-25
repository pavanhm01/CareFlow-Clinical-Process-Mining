from src.generate_data import generate_hospital_data
from src.clean_data import clean_hospital_data
from src.process_mining import discover_process


def main():
    print("=" * 50)
    print("CAREFLOW: CLINICAL PATHWAY PROCESS MINING")
    print("=" * 50)

    print("\nSTEP 1: Generating simulated hospital data...")
    generate_hospital_data(num_patients=100)

    print("\nSTEP 2: Cleaning hospital event logs...")
    clean_hospital_data()

    print("\nSTEP 3: Discovering patient pathways...")
    discover_process()

    print("\n" + "=" * 50)
    print("CAREFLOW PIPELINE COMPLETED SUCCESSFULLY!")
    print("Check the data and outputs folders for results.")
    print("=" * 50)


if __name__ == "__main__":
    main()
