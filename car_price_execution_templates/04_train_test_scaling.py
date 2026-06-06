"""
Step 4: Train/Test Split and Scaling
Purpose: Prepare train/test data and scale numeric features before model training.
"""
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Assuming X and y are already prepared from Step 3
# X: feature matrix, y: target vector

# Step 1: Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,  # 30% for testing, 70% for training
    random_state=42,  # For reproducibility
)

print(f"Training set size: {X_train.shape[0]} samples")
print(f"Testing set size: {X_test.shape[0]} samples")

# Step 2: Scale the features to have mean=0 and std=1
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\nScaling Complete!")
print(f"X_train mean: {X_train_scaled.mean():.6f}, std: {X_train_scaled.std():.6f}")
print(f"X_test mean: {X_test_scaled.mean():.6f}, std: {X_test_scaled.std():.6f}")

# Convert back to DataFrames for easier handling (optional)
X_train = pd.DataFrame(X_train_scaled, columns=X.columns)
X_test = pd.DataFrame(X_test_scaled, columns=X.columns)

print(f"\nFinal shapes:")
print(f"X_train: {X_train.shape}")
print(f"X_test: {X_test.shape}")
print(f"y_train: {y_train.shape}")
print(f"y_test: {y_test.shape}")

# Optional: Save scaler for later use in predictions
import pickle
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("\nScaler saved as 'scaler.pkl'")
