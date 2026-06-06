"""
Step 3: Preprocessing
Purpose: Convert categorical vehicle fields into numeric features for machine learning.
"""
import pandas as pd
import numpy as np

# Assuming car_data is already loaded
# car_data = pd.read_csv('car_data.csv')

# Step 1: Replace categorical values with numeric codes
car_data.replace({'Fuel_Type': {'Petrol': 0, 'Diesel': 1, 'CNG': 2}}, inplace=True)

# Step 2: One-hot encode categorical features
car_data = pd.get_dummies(
    car_data,
    columns=['Seller_Type', 'Transmission'],
    drop_first=True,  # Drop first category to avoid multicollinearity
)

# Step 3: Separate features and target
# Drop non-numeric columns and the target variable
X = car_data.drop(['Car_Name', 'Selling_Price'], axis=1)
y = car_data['Selling_Price']

print("Preprocessing Complete!")
print(f"\nFeature Matrix (X) shape: {X.shape}")
print(f"Target Vector (y) shape: {y.shape}")
print(f"\nFeature columns: {list(X.columns)}")
print(f"\nFirst few rows of X:\n{X.head()}")
print(f"\nFirst few values of y:\n{y.head()}")

# Optional: Save preprocessed data
# X.to_csv('features.csv', index=False)
# y.to_csv('target.csv', index=False)
