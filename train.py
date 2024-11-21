import pickle
import networkx as nx
from karateclub import Graph2Vec, FeatherGraph, GL2Vec
from sklearn.metrics import f1_score, recall_score, precision_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
import pandas as pd
from joblib import Parallel, delayed
import os
from tqdm import tqdm
import warnings

# Suppress urllib3 warnings
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="urllib3 v2 only supports OpenSSL 1.1.1+.*",
)

from urllib3.exceptions import NotOpenSSLWarning
# Suppress the specific urllib3 warning
warnings.simplefilter("ignore", NotOpenSSLWarning)


def load_graphs(order):
    """Load graphs based on their order (first-order or second-order)."""
    file_map = {
        "first": "data/graphs/graphs.pickle",
        "second": "data/graphs/second_graphs.pickle",
    }
    file_path = file_map.get(order)
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    graphs = [x[0] for x in data]
    labels = [x[1] for x in data]

    return graphs, labels


def get_embeddings(embedding_model, graphs):
    """Generate graph embeddings using the specified model."""
    if embedding_model == "Feather-G":
        model = FeatherGraph()
    elif embedding_model == "GL2Vec":
        model = GL2Vec()
    elif embedding_model == "Graph2Vec":
        model = Graph2Vec()
    else:
        raise ValueError("Unsupported embedding model.")

    model.fit(graphs)
    return model.get_embedding()


def train_and_evaluate(order, embedding_model, classifier_name):
    """Train and evaluate a model with the specified parameters."""
    graphs, labels = load_graphs(order)
    embeddings = get_embeddings(embedding_model, graphs)

    # Split dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split(embeddings, labels, test_size=0.3, random_state=42)

    # Choose classifier
    if classifier_name == "SVM":
        clf = make_pipeline(StandardScaler(), SGDClassifier())
    elif classifier_name == "RF":
        clf = make_pipeline(StandardScaler(), RandomForestClassifier())
    elif classifier_name == "MLP":
        clf = MLPClassifier()
    else:
        raise ValueError("Unsupported classifier.")

    # Train and predict
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    # Evaluate model
    metrics = {
        "Order": order,
        "Embedding": embedding_model,
        "Classifier": classifier_name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "AUC": roc_auc_score(y_test, y_pred),
        "F1": f1_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
    }

    # Save the trained model
    model_filename = f"models/{order}_{embedding_model}_{classifier_name}.joblib"
    os.makedirs("models", exist_ok=True)
    pickle.dump(clf, open(model_filename, "wb"))

    print(f"run completed for {order}_{embedding_model}_{classifier_name}")

    return metrics, model_filename


def main():
    # Define hyperparameter grid
    orders = ["first"]
    embeddings = ["Feather-G", "Graph2Vec"]
    classifiers = ["SVM", "RF"]

    # Create output directory
    os.makedirs("results", exist_ok=True)

    # Prepare hyperparameter combinations
    combinations = [(order, embedding, classifier) for order in orders for embedding in embeddings for classifier in classifiers]

    # Parallelize training and evaluation with tqdm progress bar
    results = Parallel(n_jobs=-1)(
        delayed(train_and_evaluate)(order, embedding, classifier)
        for order, embedding, classifier in tqdm(combinations, desc="Training Models")
    )

    # Collect evaluation metrics
    metrics_list, model_files = zip(*results)

    # Save evaluation table
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv("results/evaluation_table.csv", index=False)

    print("All models trained and evaluated. Results saved to 'results/evaluation_table.csv'.")


if __name__ == "__main__":
    main()
