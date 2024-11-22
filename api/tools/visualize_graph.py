import pickle
import random
import os
from pyvis.network import Network
import networkx as nx

def load_graphs(pickle_file_path="data/graphs/graphs.pickle"):
    """Load graphs from a pickle file."""
    if not os.path.exists(pickle_file_path):
        raise FileNotFoundError(f"Graphs file not found: {pickle_file_path}")
    with open(pickle_file_path, "rb") as f:
        graphs = pickle.load(f)
    print(f"Loaded {len(graphs)} graphs")
    return graphs

# Function to visualize a graph using PyVis
def visualize_graph_pyvis(graph_data):
    """
    Visualize a graph using PyVis and return the HTML as a string.

    Args:
        graph_data (tuple): A tuple containing the graph and its label (graph, label).

    Returns:
        str: The HTML representation of the graph visualization.
    """
    graph, label = graph_data  # graph_data is (graph, label)
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

    # Get the generated HTML
    graph_html = net.generate_html()

    # # Inject the necessary libraries in the <head> section of the HTML
    # head_content = """
    # <head>
    #     <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/9.1.2/vis-network.min.js"></script>
    #     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/vis/9.1.2/vis-network.min.css" />
    #     <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/tom-select/2.4.0/js/tom-select.complete.min.js"></script>
    #     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tom-select/2.4.0/css/tom-select.min.css" />
    # </head>
    # """

    # # Append the head content before the body content
    # graph_html = graph_html.replace("<head></head>", head_content)

    return graph_html

def main():
    """Main function to visualize a random graph when run from the command line."""
    try:
        graphs = load_graphs()
        # Select a random graph for visualization
        random_index = random.randint(0, len(graphs) - 1)
        selected_graph, label = graphs[random_index]

        # Visualize the selected graph
        graph_html = visualize_graph_pyvis((selected_graph, label))

        # Save the graph to a file for local viewing
        viz_dir = os.path.abspath("viz")
        os.makedirs(viz_dir, exist_ok=True)
        label_str = "Phishing" if label == 1 else "Normal"
        html_file = os.path.join(viz_dir, f"graph_{label_str}_{random.randint(1000, 9999)}.html")
        with open(html_file, "w") as f:
            f.write(graph_html)
        
        print(f"Visualization saved as {html_file}")

        # Open the saved HTML file in the default web browser
        import webbrowser
        webbrowser.open(f'file://{html_file}')
    except Exception as e:
        print(f"Error: {e}")

# Only run the main function when the script is executed directly
if __name__ == "__main__":
    main()
