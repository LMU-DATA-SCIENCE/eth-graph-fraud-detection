from api.tools.classify import classify_wallet

if __name__ == "__main__":
    wallet_address = "0x2d69692d54f9df37d9a2a509b148ed10fcf6d766"
    model_name = "first_Graph2Vec_RF.joblib"

    result = classify_wallet(wallet_address, model_name)
    if result:
        probability, graph_html = result
        print(f"Fraud Probability: {probability}")
        # Save the HTML for visualization
        with open("graph_visualization.html", "w") as f:
            f.write(graph_html)
    else:
        print("Classification failed.")
