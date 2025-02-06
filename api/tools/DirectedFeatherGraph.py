import math
import numpy as np
import networkx as nx
import scipy.sparse as sparse
from functools import partial
from karateclub.estimator import Estimator

class DirectedFeatherGraph(Estimator):
    r"""A modified version of Feather‑G for directed, weighted graphs.
    
    This implementation is designed for transaction graphs where each graph
    is a star‐like structure (a central wallet connected to its direct neighbors)
    with directed edges carrying ETH value as weight.
    
    For each node, four features are computed:
      - log(in-degree + 1) (using weighted in‑degree)
      - log(out-degree + 1) (using weighted out‑degree)
      - log(total incoming ETH + 1)
      - log(total outgoing ETH + 1)
    
    These node features are then “scattered” via cosine and sine transforms
    over a set of evaluation points and propagated over several adjacency powers,
    then pooled into a single graph embedding.
    
    Args:
        order (int): Number of propagation steps (default: 5)
        eval_points (int): Number of evaluation points (default: 25)
        theta_max (float): Maximum evaluation point (default: 2.5)
        seed (int): Random seed (default: 42)
        pooling (str): Pooling function to use ('mean', 'max', or 'min'; default: "mean")
    """
    def __init__(self, order: int = 5, eval_points: int = 25, theta_max: float = 2.5,
                 seed: int = 42, pooling: str = "mean"):
        super(DirectedFeatherGraph, self).__init__()
        self.order = order
        self.eval_points = eval_points
        self.theta_max = theta_max
        self.seed = seed
        try:
            pool_fn = getattr(np, pooling)
        except AttributeError:
            raise ValueError(f"{pooling} is not a valid pooling function")
        self.pool_fn = partial(pool_fn, axis=0)

    def _create_d_inverse(self, n: int, degrees: np.ndarray) -> sparse.coo_matrix:
        """Create a diagonal inverse degree matrix for normalization."""
        index = np.arange(n)
        values = np.array([1.0 / d if d != 0 else 0.0 for d in degrees])
        shape = (n, n)
        return sparse.coo_matrix((values, (index, index)), shape=shape)

    def _get_normalized_adjacency(self, graph: nx.DiGraph) -> sparse.coo_matrix:
        """
        Compute the normalized adjacency matrix using out-degrees for normalization.
        This respects the direction: each node's outgoing edges are scaled.
        """
        n = graph.number_of_nodes()
        A = nx.adjacency_matrix(graph, nodelist=range(n))
        # Get weighted out-degrees
        out_degrees = np.array([graph.out_degree(node, weight="weight") for node in range(n)])
        D_inv = self._create_d_inverse(n, out_degrees)
        A_hat = D_inv.dot(A)
        return A_hat

    def _create_node_feature_matrix(self, graph: nx.DiGraph) -> np.ndarray:
        """
        Create node features including both degree and transaction value features.
        For each node, we compute:
            - log(weighted in-degree + 1)
            - log(weighted out-degree + 1)
            - log(total incoming ETH + 1)
            - log(total outgoing ETH + 1)
        """
        n = graph.number_of_nodes()
        # Compute weighted degrees:
        in_deg = np.array([graph.in_degree(node, weight="weight") for node in range(n)])
        out_deg = np.array([graph.out_degree(node, weight="weight") for node in range(n)])
        # Compute total ETH transferred (summing the 'weight' on edges)
        in_value = np.array([
            sum(data.get("weight", 1.0) for _, data in graph.in_edges(node, data=True))
            for node in range(n)
        ])
        out_value = np.array([
            sum(data.get("weight", 1.0) for _, data in graph.out_edges(node, data=True))
            for node in range(n)
        ])
        # Use logarithmic transformation to compress the scale
        features = np.column_stack([
            np.log(in_deg + 1),
            np.log(out_deg + 1),
            np.log(in_value + 1),
            np.log(out_value + 1)
        ])
        return features

    def _calculate_embedding(self, graph: nx.DiGraph) -> np.ndarray:
        """
        Compute the graph-level embedding.
        The process:
          1. Compute the normalized adjacency matrix.
          2. Compute the node feature matrix.
          3. For each feature, compute an outer product with evaluation points,
             then apply cosine and sine transforms.
          4. Propagate the transformed features using powers of the normalized adjacency.
          5. Pool the propagated features across nodes.
        """
        n = graph.number_of_nodes()
        A_hat = self._get_normalized_adjacency(graph)
        X = self._create_node_feature_matrix(graph)  # shape: (n, 4)
        theta = np.linspace(0.01, self.theta_max, self.eval_points)
        
        # For each node feature, evaluate it at the given theta values:
        X_expanded = np.zeros((n, X.shape[1] * self.eval_points))
        for i in range(X.shape[1]):
            col = X[:, i]  # shape (n,)
            # For each node, compute outer product with theta:
            outer = np.outer(col, theta)  # shape: (n, eval_points)
            X_expanded[:, i*self.eval_points:(i+1)*self.eval_points] = outer
        
        # Apply the cosine and sine transformations
        X_cos = np.cos(X_expanded)
        X_sin = np.sin(X_expanded)
        X_transformed = np.concatenate([X_cos, X_sin], axis=1)
        
        # Propagate the features using the normalized adjacency matrix:
        feature_blocks = []
        for _ in range(self.order):
            X_transformed = A_hat.dot(X_transformed)
            feature_blocks.append(X_transformed)
        
        # Pool (e.g., take the mean) over all nodes to get the graph embedding:
        embedding = self.pool_fn(np.concatenate(feature_blocks, axis=1))
        return embedding

    def fit(self, graphs: list) -> None:
        """
        Fit the model to a list of graphs (each a NetworkX DiGraph).
        Note: The model is not pretrained; embeddings are computed directly from the input graphs.
        """
        self._set_seed()
        # It is recommended that you pass a collection of graphs for downstream tasks.
        self._embedding = [self._calculate_embedding(graph) for graph in graphs]

    def get_embedding(self) -> np.array:
        """Return the graph embeddings as a NumPy array."""
        return np.array(self._embedding)

    def infer(self, graphs: list) -> np.array:
        """Infer graph embeddings for new graphs."""
        self._set_seed()
        embedding = np.array([self._calculate_embedding(graph) for graph in graphs])
        return embedding
