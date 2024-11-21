import pickle
import glob
import pandas as pd
import networkx as nx
import os

# Create the output directory if it doesn't exist
output_dir = "data/graphs/"
os.makedirs(output_dir, exist_ok=True)

graphs = []

normal_first_graphs = glob.glob("data/eth_transactions/Normal first-order nodes/*.csv")
phishing_first_graphs = glob.glob("data/eth_transactions/Phishing first-order nodes/*.csv")

y = []  # Labels for graphs
i = 0
cnt = 0

# Helper function to process a single CSV file into a graph
def process_csv_to_graph(file_path, label):
    graph = nx.Graph()
    node_list = {}
    node_idx = 0

    # Load the CSV with pandas
    df = pd.read_csv(file_path, index_col=0)

    for _, row in df.iterrows():
        from_wallet = row['From']  # Assuming the CSV has a "From" column
        to_wallet = row['To']      # Assuming the CSV has a "To" column
        tx_hash = row['TxHash']
        value = float(row['Value'])
        timestamp = int(row['TimeStamp'])

        # Print all values with labels
        print(f"From: {from_wallet}, To: {to_wallet}, TxHash: {tx_hash}, Value: {value}, Timestamp: {timestamp}")

        # Add from_wallet as a node with an attribute
        if from_wallet not in node_list:
            node_list[from_wallet] = node_idx
            graph.add_node(node_idx, address=from_wallet)  # Store wallet address as node attribute
            node_idx += 1

        # Add to_wallet as a node with an attribute
        if to_wallet not in node_list:
            node_list[to_wallet] = node_idx
            graph.add_node(node_idx, address=to_wallet)  # Store wallet address as node attribute
            node_idx += 1

        # Add edge with attributes: weight, TxHash, Value, and TimeStamp
        graph.add_edge(
            node_list[from_wallet], node_list[to_wallet],
            weight=value, TxHash=tx_hash, Value=value, TimeStamp=timestamp
        )

    return graph

# Process normal first-order graphs
for f in normal_first_graphs:
    file_name = os.path.basename(f)
    if file_name == "0x0000000000000000000000000000000000000000.csv":
        continue
    graph = process_csv_to_graph(f, label=0)
    graphs.append([graph, 0])  # 0 for normal graph
    y.append(0)  # Label for normal graph
    i += 1

print(f"Processed {i} normal first-order graphs.")
i = 0

# Process phishing first-order graphs
for f in phishing_first_graphs:
    file_name = os.path.basename(f)
    if file_name == "0x0000000000000000000000000000000000000000.csv":
        continue
    graph = process_csv_to_graph(f, label=1)
    graphs.append([graph, 1])  # 1 for phishing graph
    y.append(1)  # Label for phishing graph
    i += 1

print(f"Processed {i} phishing first-order graphs.")

# Save the graphs to a pickle file
pickle_file_path = os.path.join(output_dir, "graphs.pickle")
with open(pickle_file_path, "wb") as f:
    pickle.dump(graphs, f)

print(f"Graphs saved to {pickle_file_path}")
