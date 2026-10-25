import pandas as pd
import pm4py
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
from collections import Counter


def discover_process():
    input_path = Path("data/processed/cleaned_event_log.csv")
    output_path = Path("outputs/process_graph.png")

    if not input_path.exists():
        raise FileNotFoundError(
            "Cleaned event log not found. Run src/clean_data.py first."
        )

    df = pd.read_csv(input_path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Prepare the event log for PM4Py.
    event_log = pm4py.format_dataframe(
        df,
        case_id="Case_ID",
        activity_key="Activity_Name",
        timestamp_key="Timestamp"
    )

    # Discover a process model using the Inductive Miner.
    process_tree = pm4py.discover_process_tree_inductive(event_log)

    # Convert the process tree into a Petri net.
    net, initial_marking, final_marking = (
        pm4py.convert_to_petri_net(process_tree)
    )

    # Export the discovered Petri net as a PNG.
    pm4py.save_vis_petri_net(
        net,
        initial_marking,
        final_marking,
        str(output_path.with_name("pm4py_process_model.png"))
    )

    # Build a directly-follows graph for transition frequencies.
    graph = nx.DiGraph()
    transition_counts = Counter()

    for _, patient_data in df.groupby("Case_ID"):
        activities = patient_data.sort_values(
            "Timestamp"
        )["Activity_Name"].tolist()

        for activity in activities:
            graph.add_node(activity)

        for i in range(len(activities) - 1):
            transition_counts[
                (activities[i], activities[i + 1])
            ] += 1

    for (source, target), count in transition_counts.items():
        graph.add_edge(source, target, weight=count)

    plt.figure(figsize=(14, 9))
    positions = nx.spring_layout(graph, seed=42, k=1.5)

    nx.draw_networkx(
        graph,
        positions,
        node_size=2800,
        font_size=8,
        arrows=True,
        arrowsize=18
    )

    nx.draw_networkx_edge_labels(
        graph,
        positions,
        edge_labels={
            (source, target): count
            for (source, target), count in transition_counts.items()
        },
        font_size=8
    )

    plt.title("CareFlow: Patient Process Map")
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    print("PM4Py process discovery completed successfully!")
    print(f"Activities: {graph.number_of_nodes()}")
    print(f"Transitions: {graph.number_of_edges()}")
    print(f"Process graph: {output_path}")
    print("PM4Py Petri net: outputs/pm4py_process_model.png")


if __name__ == "__main__":
    discover_process()