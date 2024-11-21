import pickle
import random
import os
import webbrowser
from pyvis.network import Network
import networkx as nx

# Load the graphs from the pickle file
with open("data/graphs/graphs.pickle", "rb") as f:
    graphs = pickle.load(f)
    print(f"Loaded {len(graphs)} graphs")

# Function to visualize a graph using PyVis
def visualize_graph_pyvis(graph_data, label):
    graph, _ = graph_data  # graph_data is [graph, label]
    net = Network(notebook=False, height="800px", width="100%", directed=True)
    
    # Add nodes and edges to the PyVis graph
    for node, attrs in graph.nodes(data=True):
        # Use the wallet address (if available) as the node label
        address = attrs.get('address', f"Node {node}")
        net.add_node(node, label=address, title=f"Wallet: {address}")
    
    for source, target, edge_data in graph.edges(data=True):
        # Extract the relevant information for the edge label
        txhash = edge_data.get('TxHash', 'N/A')  # Get the TxHash
        value = edge_data.get('Value', 'N/A')  # Get the Value
        timestamp = edge_data.get('TimeStamp', 'N/A')  # Get the Timestamp
        
        # Create an edge label with TxHash, Value, and Timestamp
        edge_title = f"TxHash: {txhash}\n Value: {value}\n Timestamp: {timestamp}"

        # Add edge to the graph
        net.add_edge(source, target, title=edge_title)

    # Create the 'viz' directory if it doesn't exist
    viz_dir = os.path.abspath("viz")
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)

    # Save the graph to an HTML file in the ../viz/ directory
    label_str = "Phishing" if label == 1 else "Normal"
    html_file = os.path.join(viz_dir, f"graph_{label_str}_{random.randint(1000, 9999)}.html")
    net.write_html(html_file)
    print(f"Visualization saved as {html_file}")

    # Open the saved HTML file in the default web browser
    webbrowser.open(f'file://{html_file}')

# Select a random graph for visualization
random_index = random.randint(0, len(graphs) - 1)
selected_graph, label = graphs[random_index]

# Visualize the selected graph
visualize_graph_pyvis((selected_graph, label), label)