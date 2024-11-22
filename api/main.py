
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
import argparse

def parameter_parser():
    parser = argparse.ArgumentParser(description="Run Identity Inference a.")

    parser.add_argument("--graph",
                    default="first",
                    nargs='?',
                    choices=['first', 'second'],
                    help="Order of transaction graphs(first, second). Default is 'first'.")

    parser.add_argument("--embedding",
                    default="Feather-G",
                    nargs='?',
                    choices=['Feather-G', 'Graph2Vec', 'GL2Vec'],
                    help="Embedding algorithms(Feather-G, Graph2Vec, GL2Vec). Default is 'Feather-G'.")

    parser.add_argument("--classifier",
                    default="RF",
                    nargs='?',
                    choices=['SVM', 'MLP', 'RF'],
                    help="Classifier(SVM, MLP, RF).	Default is 'RF'.")

    return parser.parse_args()


def order_graph(order):
    data = []

    if order == "first": # Loading First-order Transacation Graphs
        with open("data/graphs/graphs.pickle", "rb") as f:
            data = pickle.load(f)
            y = []
            graphs = []

            for x in data:
                graphs.append(x[0])
                y.append(x[1])

            return graphs, y

    elif order =="second": # Loading Second-order Transacation Graphs
        with open("data/graphs/second_graphs.pickle", "rb") as f:
            data = pickle.load(f)
            y = []
            graphs = []

            for x in data:
                graphs.append(x[0])
                y.append(x[1])

            return graphs, y

def select_embedding(emb, graphs):
    if emb == "Feather-G": #Feather-G for Graph Embedding
        model = FeatherGraph()
    elif emb == "GL2Vec":
        model = GL2Vec() #GL2Vec for Graph Embedding
    elif emb == "Graph2Vec":
        model = Graph2Vec() #Graph2Vec for Graph Embedding

    model.fit(graphs)

    # Get graph embedding vectors
    X = model.get_embedding()

    return X

def classify(classifier, X, y, emb):
    # Split dataset into train and test

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    if classifier == "SVM":
        clf = make_pipeline(StandardScaler(), SGDClassifier())
        clf.fit(X_train, y_train)
        y_hat = clf.predict(X_test)

    elif classifier == "RF":
        clf = make_pipeline(StandardScaler(), RandomForestClassifier())
        clf.fit(X_train, y_train)
        y_hat = clf.predict(X_test)

    elif classifier == "MLP":
        clf = MLPClassifier()
        clf.fit(X_train, y_train)
        y_hat = clf.predict(X_test)

    print(emb, "with", classifier)

    acc = accuracy_score(y_test, y_hat)
    print('Acc: {:.4f}'.format(acc))

    auc = roc_auc_score(y_test, y_hat)
    print('AUC: {:.4f}'.format(auc))

    f1 = f1_score(y_test, y_hat)
    precision = precision_score(y_test, y_hat)
    recall = recall_score(y_test, y_hat)
    print('F1: {:.4f}, Precision: {:.4f}, Recall: {:.4f}'.format(f1, precision, recall))

def main(args):
    print(args)
    graphs = order_graph(args.graph)
    print("get embedding")
    embeddings = select_embedding(args.embedding, graphs[0])
    print("classify")
    classify(args.classifier, embeddings, graphs[1], args.embedding)

if __name__ == "__main__":
    args = parameter_parser()
    main(args)