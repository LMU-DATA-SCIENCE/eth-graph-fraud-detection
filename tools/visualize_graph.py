import pickle
import random
import networkx as nx
import matplotlib.pyplot as plt

# Load the graphs from the pickle file
with open("data/graphs/graphs.pickle", "rb") as f:
    graphs = pickle.load(f)
    print(f"Loaded {len(graphs)} graphs")

# Function to visualize a graph
def visualize_graph(graph_data, label, node_color='blue'):
    print(graph_data)
    graph, _ = graph_data  # graph_data is [graph, label]
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph, seed=42)  # Compute layout for visualization
    nx.draw_networkx_nodes(graph, pos, node_size=50, node_color=node_color, alpha=0.8)
    nx.draw_networkx_edges(graph, pos, alpha=0.5)
    plt.title(f"Graph Visualization (Label: {label})")
    plt.axis("off")
    plt.show()

# Select a random graph for visualization
random_index = random.randint(0, len(graphs) - 1)
selected_graph, label = graphs[random_index]

# Visualize the selected graph
visualize_graph((selected_graph, label), label, node_color='red' if label == 1 else 'blue')