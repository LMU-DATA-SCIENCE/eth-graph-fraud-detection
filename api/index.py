from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.tools.classify import classify_wallet

# Create FastAPI instance
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# Define data models
class Node(BaseModel):
    id: str
    label: str

class Edge(BaseModel):
    source: str
    target: str
    value: float
    timestamp: str  # Expected as ISO 8601 formatted string

class GraphData(BaseModel):
    nodes: list[Node]
    edges: list[Edge]

class ClassificationResponse(BaseModel):
    fraud_probability: float
    graph: GraphData

class ClassifyRequest(BaseModel):
    wallet_address: str
    model_name: str = "first_Graph2Vec_RF.joblib"  # Default value for model_name

# Define classify_wallet endpoint
@app.post("/api/py/classify", response_model=ClassificationResponse)
def classify_wallet_endpoint(request: ClassifyRequest):
    """
    Classify a wallet based on its transaction graph and return fraud probability and graph data.

    Args:
        request (ClassifyRequest): The request body containing wallet_address and model_name.

    Returns:
        dict: A response with the fraud probability and graph data.
    """
    try:
        # Call the classify_wallet function
        fraud_probability, graph_data = classify_wallet(request.wallet_address, request.model_name)

        if fraud_probability is None or graph_data is None:
            raise ValueError("Classification failed. Please check the wallet address or model.")

        # Structure and return the response
        return {
            "fraud_probability": fraud_probability,
            "graph": graph_data
        }
    except Exception as e:
        # Handle errors gracefully
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
