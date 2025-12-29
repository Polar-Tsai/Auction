import pandas as pd
import sys
from pathlib import Path

# Define paths
data_dir = Path(__file__).parent / 'data'
products_csv = data_dir / 'products.csv'

try:
    # Read CSV
    df = pd.read_csv(products_csv)
    
    # Check if image_url column exists
    if 'image_url' in df.columns:
        print(f"Found 'image_url' column. Removing...")
        df = df.drop(columns=['image_url'])
        
        # Save back to CSV
        df.to_csv(products_csv, index=False)
        print(f"✓ Successfully removed 'image_url' column from {products_csv}")
    else:
        print("'image_url' column not found in CSV")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
