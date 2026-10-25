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
