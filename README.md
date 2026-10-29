# CareFlow: Clinical Pathway Process Mining

## 1. Project Overview

CareFlow analyzes simulated hospital event logs to discover patient treatment pathways and identify potential workflow inefficiencies.

## 2. Objectives

* Generate simulated hospital event logs.
* Clean and preprocess event data.
* Discover hospital workflows using PM4Py.
* Visualize patient pathways and activity transitions.
* Demonstrate repeated activities and possible workflow inefficiencies.

## 3. Technologies Used

* Python 3.11
* Pandas and NumPy
* PM4Py
* NetworkX
* Matplotlib
* Graphviz

## 4. Project Workflow

1. Generate simulated hospital event data.
2. Clean and normalize the event logs.
3. Discover process models using PM4Py.
4. Generate visualizations of activity transitions and process structure.

## 5. Dataset

The project uses simulated data representing 100 patients and 750 hospital events.

Activities include Registration, Initial Assessment, Doctor Consultation, Lab Test, Diagnosis, Treatment, and Discharge.

**Note:** The dataset is simulated and does not contain real patient records.

## 6. Project Structure

```text
CareFlow-Clinical-Process-Mining/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── generate_data.py
│   ├── clean_data.py
│   └── process_mining.py
├── outputs/
│   ├── process_graph.png
│   └── pm4py_process_model.png
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 7. Installation and Execution

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the complete pipeline:

```bash
python main.py
```

Graphviz must also be installed and available on the system PATH for the PM4Py Petri net visualization.

## 8. Outputs

* `data/raw/hospital_event_log.csv`: Generated event data.
* `data/processed/cleaned_event_log.csv`: Cleaned event data.
* `outputs/process_graph.png`: Patient activity transition graph.
* `outputs/pm4py_process_model.png`: PM4Py-discovered Petri net model.

## 9. Limitations

This is an educational prototype using simulated hospital data. Its results do not establish actual hospital performance or clinical outcomes.

## 10. Future Enhancements

* Analyze real, appropriately de-identified hospital event logs.
* Measure activity durations and waiting times.
* Identify bottlenecks and frequent workflow loops.
* Improve process visualization and reporting.




## Week 3 – Day 1: Process Performance Analysis

### Overview

Analyzed the CareFlow clinical event log to understand patient activity patterns, journey durations, and transition performance using process mining techniques.

### Features

* **Activity Frequency Analysis:** Analyzes how frequently each clinical activity occurs.
* **Patient Journey Analysis:** Examines patient pathways and total journey durations.
* **Transition Time Analysis:** Calculates elapsed time between consecutive activities.
* **Performance Summary:** Generates statistical summaries of activity transitions.
* **CSV Reports:** Exports activity frequency, transition times, patient journeys, and transition performance summaries.
* **Dashboard Integration:** Presents process performance information through interactive visualizations.

### Output Files

* `outputs/activity_frequency_analysis.csv`
* `outputs/activity_transition_times.csv`
* `outputs/patient_journey_analysis.csv`
* `outputs/transition_performance_summary.csv`

### Dataset Summary

* **Total Events:** 750
* **Total Patients:** 100
* **Unique Activities:** 7

*Note: These results are generated using simulated patient activity data and do not represent verified hospital performance measurements.*




## Week 3 – Day 2: Process Bottleneck Detection

### Overview

The CareFlow Clinical Process Mining project analyzes patient activity pathways to identify transitions that may contribute to delays in hospital workflows.

### Features

* **Transition Time Analysis:** Calculates elapsed time between consecutive patient activities.
* **Bottleneck Detection:** Identifies transitions with higher average elapsed times.
* **Performance Summary:** Reports average, median, and maximum transition times.
* **Visual Analytics:** Displays activity frequency, patient journey duration, and transition performance.
* **Patient Journey Analysis:** Examines the sequence of activities followed by patients.
* **Interactive Dashboard:** Uses Streamlit and Plotly to explore process performance.
* **Data Export:** Supports downloading analysis results for further examination.

### Technologies Used

* Python
* Pandas and NumPy
* PM4Py
* Streamlit
* Plotly
* Matplotlib
* NetworkX

### How to Run

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the process mining pipeline:

```bash
python main.py
```

Launch the dashboard:

```bash
python -m streamlit run dashboard.py
```

### Note

The current dataset contains simulated patient activity events. Bottleneck results are exploratory and should not be interpreted as verified clinical performance measurements.
