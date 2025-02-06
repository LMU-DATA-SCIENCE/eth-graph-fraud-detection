import pickle
import glob
import pandas as pd
import networkx as nx
import os

# Create the output directory if it doesn't exist
output_dir = "data/graphs/"
os.makedirs(output_dir, exist_ok=True)

def process_transactions_to_graph(df, label=None):
    """
    Process a DataFrame of transactions into a NetworkX graph.
    
    Args:
        df (pd.DataFrame): DataFrame containing transactions with columns ['From', 'To', 'TxHash', 'Value', 'TimeStamp'].
        label (int, optional): Label for the graph. Only used for training graphs.
    
    Returns:
        nx.Graph: The resulting graph object.
    """
    graph = nx.Graph()
    node_list = {}
    node_idx = 0

    for _, row in df.iterrows():
        from_wallet = row['From']
        to_wallet = row['To']
        tx_hash = row['TxHash']
        value = float(row['Value'])
        timestamp = int(row['TimeStamp'])

        # Debugging output for each transaction
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

def main():
    graphs = []  # List to store graph objects
    y = []  # Labels for graphs

    # Define directories for normal and phishing transaction files
    normal_first_graphs = glob.glob("data/eth_transactions/Normal first-order nodes/*.csv")
    phishing_first_graphs = glob.glob("data/eth_transactions/Phishing first-order nodes/*.csv")

    # Process normal first-order graphs
    for f in normal_first_graphs:
        file_name = os.path.basename(f)
        if file_name == "0x0000000000000000000000000000000000000000.csv":
            continue
        df = pd.read_csv(f, index_col=0)  # Read the CSV into a DataFrame
        graph = process_transactions_to_graph(df, label=0)
        graphs.append([graph, 0])  # 0 for normal graph
        y.append(0)  # Label for normal graph

    print(f"Processed {len(normal_first_graphs)} normal first-order graphs.")

    # Process phishing first-order graphs
    for f in phishing_first_graphs:
        file_name = os.path.basename(f)
        if file_name == "0x0000000000000000000000000000000000000000.csv":
            continue
        df = pd.read_csv(f, index_col=0)  # Read the CSV into a DataFrame
        graph = process_transactions_to_graph(df, label=1)
        graphs.append([graph, 1])  # 1 for phishing graph
        y.append(1)  # Label for phishing graph

    print(f"Processed {len(phishing_first_graphs)} phishing first-order graphs.")

    # Save the graphs to a pickle file
    pickle_file_path = os.path.join(output_dir, "graphs.pickle")
    with open(pickle_file_path, "wb") as f:
        pickle.dump(graphs, f)

    print(f"Graphs saved to {pickle_file_path}")

if __name__ == "__main__":
    main()
