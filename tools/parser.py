import argparse

def parameter_parser():
    parser = argparse.ArgumentParser(description="Run Identity Inference a.")

    parser.add_argument("--graph",
                    default="first",
                    nargs='?',
                    choices=['first, second'],
                    help="Order of transaction graphs(first, second). Default is 'first'.")

    parser.add_argument("--embedding",
                    default="Feather-G",
                    nargs='?',
                    choices=['Feather-G, Graph2Vec, GL2Vec'],
                    help="Embedding algorithms(Feather-G, Graph2Vec, GL2Vec). Default is 'Feather-G'.")

    parser.add_argument("--classifier",
                    default="RF",
                    nargs='?',
                    choices=['SVM, MLP, RF'],
                    help="Classifier(SVM, MLP, RF).	Default is 'RF'.")

    return parser.parse_args()
