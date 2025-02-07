import pickle
import os
from api.tools.make_graph import process_transactions_to_graph  # Import your graph creation function
from api.tools.fetch_transactions import fetch_transactions  # Import your transaction fetching function
from api.tools.get_graph_embeddings import get_graph_embeddings
from api.tools.visualize_graph import visualize_graph_pyvis  # Import the visualization function
from karateclub import FeatherGraph, Graph2Vec, GL2Vec  # Import embedding models
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import Tuple, Union

# Suppress warnings for cleaner output
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def load_model(model_path: str):
    """Load a pre-trained model from the specified path."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    with open(model_path, "rb") as f:
        return pickle.load(f)
    
from datetime import datetime, timezone

def format_timestamp(timestamp):
    try:
        # Convert to integer if possible and create a timezone-aware datetime object
        if isinstance(timestamp, (int, float, str)) and str(timestamp).isdigit():
            return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        # If it's already a string, return as-is
        return str(timestamp)
    except Exception as e:
        print(f"Error in format_timestamp: {e}")
        return "N/A"  # Fallback for invalid timestamps


from typing import Union, Tuple, Dict
import os
import numpy as np
from sklearn.pipeline import Pipeline

def classify_wallet(wallet_address: str, model_name: str) -> Union[Tuple[float, Dict[str, list]], None]:
    """
    Classify a wallet as fraudulent or not and return the fraud probability and graph data.
    
    Args:
        wallet_address (str): The wallet address to classify.
        model_name (str): The name of the pre-trained model to use (e.g., "first_Feather-G_RF.joblib").
    
    Returns:
        Tuple[float, dict]: The predicted fraud probability (0 to 1) and graph data in JSON format.
        None: If an error occurs.
    """
    # Define paths
    models_dir = "api/models"
    model_path = os.path.join(models_dir, model_name)

    # Load the pre-trained model
    try:
        model = load_model(model_path)
    except FileNotFoundError as e:
        print(e)
        return None

    # Fetch transactions and create a graph
    try:
        transactions = fetch_transactions(wallet_address)
        graph = process_transactions_to_graph(transactions)
    except Exception as e:
        print(f"Error fetching transactions or creating graph: {e}")
        return None

    # Determine the embedding model from the model name
    embedding_model = model_name.split("_")[1]  # Extract embedding model (e.g., "Feather-G")

    # Generate graph embeddings
    try:
        embedding = get_graph_embeddings(embedding_model, [graph])[0]
        print(embedding.shape)
        print(embedding)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

    # Predict fraud probability
    try:
        # Ensure input shape matches model expectations
        if isinstance(model, Pipeline):
            embedding = np.array(embedding).reshape(1, -1)  # Reshape if using a pipeline
        probability = model.predict_proba(embedding)[0][1]  # Probability of the positive class (fraudulent)
        print("Probability:", probability)
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

    # Convert the graph to a JSON structure
    try:
        nodes = [{"id": str(node), "label": graph.nodes[node].get("address", f"Node {node}")}
                 for node in graph.nodes]
        edges = [{"source": str(source), 
                  "target": str(target), 
                  "value": edge_data.get("Value", 0), 
                  "timestamp": format_timestamp(edge_data.get("TimeStamp", "N/A"))}
                 for source, target, edge_data in graph.edges(data=True)]

        graph_data = {"nodes": nodes, "edges": edges}

    except Exception as e:
        print(f"Error converting graph to JSON: {e}")
        return None

    return probability, graph_data
