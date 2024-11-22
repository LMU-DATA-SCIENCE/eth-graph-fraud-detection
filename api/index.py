from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.tools.classify import classify_wallet
from api.tools.visualize_graph import visualize_graph_pyvis
from api.tools.make_graph import process_transactions_to_graph
from api.tools.fetch_transactions import fetch_transactions

# Create FastAPI instance
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

class ClassificationResponse(BaseModel):
    fraud_probability: float
    visualization_html: str

class ClassifyRequest(BaseModel):
    wallet_address: str
    model_name: str = "first_Graph2Vec_RF.joblib"  # Default value for model_name


@app.post("/api/py/classify", response_model=ClassificationResponse)
def classify_wallet_endpoint(request: ClassifyRequest):
    """
    Classify a wallet based on its transaction graph and return fraud probability and visualization HTML.

    Args:
        request (ClassifyRequest): The request body containing wallet_address and model_name.

    Returns:
        dict: A response with the fraud probability and graph visualization HTML.
    """
    try:
        wallet_address = request.wallet_address
        model_name = request.model_name

        # Classify the wallet
        fraud_probability, graph_html = classify_wallet(wallet_address, model_name)
        if fraud_probability is None:
            raise ValueError("Classification failed. Please check the wallet address or model.")

        return {
            "fraud_probability": fraud_probability,
            "visualization_html": graph_html
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")