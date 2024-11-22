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


@app.post("/api/py/classify", response_model=ClassificationResponse)
def classify_wallet_endpoint(wallet_address: str, model_name: str = "first_Graph2Vec_RF.joblib"):
    """
    Classify a wallet based on its transaction graph and return fraud probability and visualization HTML.

    Args:
        wallet_address (str): The wallet address to classify.
        model_name (str): Name of the pre-trained model to use for classification.

    Returns:
        dict: A response with the fraud probability and graph visualization HTML.
    """
    try:
        # Classify the wallet
        fraud_probability = classify_wallet(wallet_address, model_name)
        if fraud_probability is None:
            raise ValueError("Classification failed. Please check the wallet address or model.")

        # Fetch transactions and create graph for visualization
        transactions = fetch_transactions(wallet_address)
        graph = process_transactions_to_graph(transactions)
        visualization_html = visualize_graph_pyvis((graph, None))  # No label for new graphs

        return {
            "fraud_probability": fraud_probability,
            "visualization_html": visualization_html
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
