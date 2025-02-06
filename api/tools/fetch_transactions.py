import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Etherscan API configuration
API_URL = "https://api.etherscan.io/api"
API_KEY = os.getenv("ETHERSCAN_API_KEY")  # Load API key from environment variable

# Function to fetch transactions for a wallet address
def fetch_transactions(wallet_address, start_block=0, end_block=99999999):
    """
    Fetch all transactions for a given wallet address and save as CSV, filtering out transactions with value 0.

    :param wallet_address: The Ethereum wallet address to fetch transactions for.
    :param output_csv: Path to save the resulting CSV file.
    :param start_block: The starting block number (default is 0).
    :param end_block: The ending block number (default is 99999999).
    """

    # Specify the directory to save the output CSV file
    output_directory = "api/data/eth_transactions/etherscan/"
    os.makedirs(output_directory, exist_ok=True)

    # Set output CSV path
    output_csv = os.path.join(output_directory, f"{wallet_address}.csv")

    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": start_block,
        "endblock": end_block,
        "sort": "asc",
        "apikey": API_KEY,
    }

    # Make the API request
    print(f"Fetching transactions for wallet: {wallet_address}...")
    response = requests.get(API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "1":
            print(f"Found {len(data['result'])} transactions.")
            
            # Convert the result to a DataFrame
            df = pd.DataFrame(data["result"])
              
            # Convert 'value' from wei to Ether safely
            df["value"] = df["value"].astype(float) / 1e18  # Convert to numeric after dividing

            # Create a new dataframe with the required columns
            df_transformed = df[['hash', 'blockNumber', 'timeStamp', 'from', 'to', 'value', 'contractAddress', 'input', 'isError']].copy()

            # Rename columns to match the second format
            df_transformed.columns = ['TxHash', 'BlockHeight', 'TimeStamp', 'From', 'To', 'Value', 'ContractAddress', 'Input', 'isError']
        
            # Filter out transactions with value 0   
            df_filtered = df_transformed[df_transformed["Value"] > 0]
            
            print(f"{len(df_filtered)} transactions remaining after filtering value 0.")
            
            # Save to CSV
            df_filtered.to_csv(output_csv, index=True)
            print(f"Filtered transactions saved to {output_csv}")

            return df_filtered
        else:
            print(f"No transactions found or an error occurred: {data['message']}")
    else:
        print(f"Error: Unable to fetch data (HTTP {response.status_code})")
    return None

# Example usage
if __name__ == "__main__":
    # Replace with your Ethereum wallet address
    wallet_address = "0x00a2df284ba5f6428a39dff082ba7ff281852e06"
    
    fetch_transactions(wallet_address)
