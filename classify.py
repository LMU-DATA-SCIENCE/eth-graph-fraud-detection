import pickle
import os
from tools.make_graph import process_transactions_to_graph  # Import your graph creation function
from tools.fetch_transactions import fetch_transactions  # Import your transaction fetching function
from tools.get_graph_embeddings import get_graph_embeddings
from tools.visualize_graph import visualize_graph_pyvis  # Import the visualization function
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

def classify_wallet(wallet_address: str, model_name: str) -> Union[Tuple[float, str], None]:
    """
    Classify a wallet as fraudulent or not and return the fraud probability and graph visualization.
    
    Args:
        wallet_address (str): The wallet address to classify.
        model_name (str): The name of the pre-trained model to use (e.g., "first_Graph2Vec_RF.joblib").
    
    Returns:
        Tuple[float, str]: The predicted fraud probability (0 to 1) and HTML of the graph visualization.
        None: If an error occurs.
    """
    # Define paths
    models_dir = "models"
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
    embedding_model = model_name.split("_")[1]  # Extract embedding model (e.g., "Graph2Vec")

    # Generate graph embeddings
    try:
        embedding = get_graph_embeddings(embedding_model, [graph])[0]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

    # Predict fraud probability
    try:
        # Ensure input shape matches model expectations
        if isinstance(model, Pipeline):
            embedding = np.array(embedding).reshape(1, -1)  # Reshape if using a pipeline
        probability = model.predict_proba(embedding)[0][1]  # Probability of the positive class (fraudulent)
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None
    
    # Visualize the graph and generate the HTML
    try:
        graph_html = visualize_graph_pyvis((graph, round(probability)))
    except Exception as e:
        print(f"Error visualizing graph: {e}")
        return None

    return probability, graph_html
