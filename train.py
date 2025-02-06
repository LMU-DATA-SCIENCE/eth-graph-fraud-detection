import pickle
import networkx as nx
from karateclub import Graph2Vec, FeatherGraph, GL2Vec
from sklearn.metrics import f1_score, recall_score, precision_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
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
import matplotlib.pyplot as plt
import seaborn as sns
from api.tools.get_graph_embeddings import get_graph_embeddings
from sklearn.model_selection import GridSearchCV

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
        "first": "api/data/graphs/graphs.pickle",
        "second": "api/data/graphs/second_graphs.pickle",
    }
    file_path = file_map.get(order)
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    graphs = [x[0] for x in data]
    labels = [x[1] for x in data]

    return graphs, labels


def train_and_evaluate(order, embedding_model, classifier_name):
    """Train and evaluate a model with hyperparameter tuning."""
    graphs, labels = load_graphs(order)
    embeddings = get_graph_embeddings(embedding_model, graphs)

    # Split dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split(embeddings, labels, test_size=0.3, random_state=42)

    # Define classifier and hyperparameter grid
    if classifier_name == "SVM":
        pipeline = make_pipeline(StandardScaler(), SGDClassifier(random_state=42))
        param_grid = {
            "sgdclassifier__alpha": [1e-4, 1e-3, 1e-2],
            "sgdclassifier__penalty": ["l2", "elasticnet"],
            "sgdclassifier__max_iter": [1000, 2000],
        }
    elif classifier_name == "RF":
        pipeline = make_pipeline(StandardScaler(), RandomForestClassifier(random_state=42))
        param_grid = {
            "randomforestclassifier__n_estimators": [100, 200, 300],
            "randomforestclassifier__max_depth": [None, 10, 20],
            "randomforestclassifier__min_samples_split": [2, 5],
        }
    elif classifier_name == "MLP":
        pipeline = make_pipeline(StandardScaler(), MLPClassifier(random_state=42))
        param_grid = {
            "mlpclassifier__hidden_layer_sizes": [(100,), (50, 50), (100, 50)],
            "mlpclassifier__activation": ["relu", "tanh"],
            "mlpclassifier__alpha": [1e-4, 1e-3],
        }
    elif classifier_name == "GB":
        pipeline = make_pipeline(StandardScaler(), GradientBoostingClassifier(random_state=42))
        param_grid = {
            "gradientboostingclassifier__n_estimators": [100],
            "gradientboostingclassifier__learning_rate": [0.001, 0.01, 0.1],
            "gradientboostingclassifier__max_depth": [3,5,10],
            "gradientboostingclassifier__subsample": [0.5, 0.8, 1.0],
        }
    else:
        raise ValueError("Unsupported classifier.")

    # Perform grid search
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="f1",  # Use F1 score for model selection
        cv=5,  # 5-fold cross-validation
        n_jobs=-1,  # Use all available cores
        verbose=1,
    )
    grid_search.fit(X_train, y_train)

    # Best model
    best_model = grid_search.best_estimator_

    # Predict on test data
    y_pred = best_model.predict(X_test)

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
        "Best Params": grid_search.best_params_,
    }

    print(f"Evaluation completed for {order}_{embedding_model}_{classifier_name}")

    # Retrain the model on the full dataset (entire graph data)
    best_model.fit(embeddings, labels)

    # Save the retrained model under the 'models/' directory
    retrained_model_filename = f"api/models/{order}_{embedding_model}_{classifier_name}.joblib"
    os.makedirs("api/models", exist_ok=True)
    pickle.dump(best_model, open(retrained_model_filename, "wb"))

    print(f"Retrained model saved to {retrained_model_filename}")

    return metrics, retrained_model_filename


def visualize_results(metrics_df):
    """Visualize the results as subplots for each metric in two columns."""
    metrics = ["Accuracy", "AUC", "F1", "Precision", "Recall"]
    
    # Melt the DataFrame for easier plotting
    metrics_df_melted = metrics_df.melt(id_vars=["Order", "Embedding", "Classifier"], value_vars=metrics, 
                                        var_name="Metric", value_name="Value")

    # Set up the figure with subplots in 2 columns
    n_metrics = len(metrics)
    n_cols = 1
    n_rows = n_metrics  # Calculate rows needed for 2 columns

    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8, 2 * n_rows))
    
    # Flatten axes for easy iteration, in case it's a 2D array
    axes = axes.flatten()

    # Plot each metric in a separate subplot
    for i, metric in enumerate(metrics):
        ax = axes[i]
        
        # Filter data for the current metric
        metric_data = metrics_df_melted[metrics_df_melted["Metric"] == metric]
        
        # Create a barplot
        sns.barplot(data=metric_data, x="Classifier", y="Value", hue="Embedding", ax=ax, errorbar=None)

        # Set title and labels
        ax.set_title(metric)
        ax.set_xlabel("Classifier")
        ax.set_ylabel(metric)
        
        # Make the legend smaller
        ax.legend(loc='lower right', fontsize='small')

    # Adjust layout for better spacing
    plt.tight_layout()

    # Save and show the plot
    os.makedirs("viz", exist_ok=True)
    plot_filename = "api/viz/evaluation_results_subplots_2cols.png"
    plt.savefig(plot_filename)
    plt.show()
    print(f"Plot saved to {plot_filename}")

def main():
    # Define hyperparameter grid
    orders = ["first"]
    embeddings = ["Feather-G", "Graph2Vec"]
    classifiers = ["GB","SVM", "RF","MLP"]#, 

    # Create output directory
    os.makedirs("api/results", exist_ok=True)

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
    metrics_df.to_csv("api/results/evaluation_table.csv", index=False)

    # Visualize the results
    visualize_results(metrics_df)

    print("All models trained and evaluated. Results saved to 'api/results/evaluation_table.csv'.")


if __name__ == "__main__":
    main()