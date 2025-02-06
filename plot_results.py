import pandas as pd
from train import visualize_results

def main():
    # Read the CSV file
    df = pd.read_csv('api/results/evaluation_table.csv')
    
    # Apply the visualize_results function
    visualize_results(df)

if __name__ == "__main__":
    main()