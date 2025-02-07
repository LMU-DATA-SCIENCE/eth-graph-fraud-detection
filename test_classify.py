from api.tools.classify import classify_wallet

if __name__ == "__main__":
    wallet_address = "0xa83c4a6d0418074655bdbe74fed8435c46c19f66"
    model_name = "first_Feather-G_RF.joblib"

    result = classify_wallet(wallet_address, model_name)
    if result:
        probability, graph_dict = result
        print(f"Fraud Probability: {probability}")
        # Save the HTML for visualization
        # with open("graph_visualization.html", "w") as f:
        #     f.write(graph_html)
    else:
        print("Classification failed.")
