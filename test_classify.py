import argparse
from api.tools.classify import classify_wallet

def main():
    parser = argparse.ArgumentParser(description="Classify a wallet address using a specified model.")
    parser.add_argument("--wallet_address", type=str, required=True, help="The wallet address to classify.")
    parser.add_argument("--embedding", type=str, required=True, help="The embedding method to use (e.g., Feather-G).")
    parser.add_argument("--model", type=str, required=True, help="The model name to use (e.g., GB).")
    
    args = parser.parse_args()
    model_name = f"first_{args.embedding}_{args.model}.joblib"
    
    result = classify_wallet(args.wallet_address, model_name)

    if result:
        probability, graph_dict = result
        print(f"Fraud Probability: {probability}")
    else:
        print("Classification failed.")

if __name__ == "__main__":
    main()
