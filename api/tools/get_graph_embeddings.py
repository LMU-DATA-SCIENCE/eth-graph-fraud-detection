from karateclub import Graph2Vec, FeatherGraph, GL2Vec
import networkx as nx

def prepare_graphs(graphs_list):
    # Add default node labels
    for graph in graphs_list:
        for node in graph.nodes:
            graph.nodes[node]["label"] = str(graph.nodes[node].get("address", "unknown"))

        for edge in graph.edges:
            if "weight" not in graph.edges[edge]:
                graph.edges[edge]["weight"] = 1.0  # Default weight

        
def get_graph_embeddings(embedding_model: str, graphs_list: list):
    """
    Generate graph embeddings using the specified model.
    """
    if not all(isinstance(graph, nx.Graph) for graph in graphs_list):
        raise ValueError("All items in graphs_list must be NetworkX Graph objects.")

    prepare_graphs(graphs_list)

    if embedding_model == "Feather-G":
        model = FeatherGraph()
    elif embedding_model == "GL2Vec":
        model = GL2Vec()
    elif embedding_model == "Graph2Vec":
        model = Graph2Vec(dimensions=128, workers=4)
    # elif embedding_model == "DirectedFeatherGraph":
    #     model = DirectedFeatherGraph()
    else:
        raise ValueError("Unsupported embedding model.")

    print("Graph info:", nx.info(graphs_list[0]))
    print("Nodes:", list(graphs_list[0].nodes(data=True)))
    print("Edges:", list(graphs_list[0].edges(data=True)))

    try:
        model.fit(graphs_list)
    except Exception as e:
        print("Error during fitting:", e)
        raise

    return model.get_embedding()
