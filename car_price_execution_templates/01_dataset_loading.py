"""
Step 1: Dataset Loading
Purpose: Load the Kaggle Cardekho car_data.csv file and inspect the first records.
"""
import pandas as pd

# Load the dataset
car_data = pd.read_csv('car_data.csv')

# Display first 5 rows
print("First 5 rows:")
print(car_data.head())

# Display data types and null counts
print("\nData Info:")
print(car_data.info())

# Display null value counts
print("\nNull Values:")
print(car_data.isnull().sum())

# Display statistical summary
print("\nStatistical Summary:")
print(car_data.describe())

# Optional: Check data shape and columns
print(f"\nDataset shape: {car_data.shape}")
print(f"Columns: {list(car_data.columns)}")
