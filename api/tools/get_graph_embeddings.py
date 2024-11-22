from karateclub import Graph2Vec, FeatherGraph, GL2Vec

def get_graph_embeddings(embedding_model:str, graphs_list: list):
    """Generate graph embeddings using the specified model."""
    if embedding_model == "Feather-G":
        model = FeatherGraph()
    elif embedding_model == "GL2Vec":
        model = GL2Vec()
    elif embedding_model == "Graph2Vec":
        model = Graph2Vec()
    else:
        raise ValueError("Unsupported embedding model.")

    model.fit(graphs_list)
    return model.get_embedding()