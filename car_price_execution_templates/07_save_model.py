"""
Step 7: Save Model
Purpose: Save the trained prediction model for later use in production.
"""
import pickle
import joblib
from sklearn.linear_model import LinearRegression
import json
from datetime import datetime

# Assuming X_train, y_train are prepared from train_test_scaling.py
# and you've identified the best model from model_comparison.py

# Step 1: Train the final model (use best model from Step 5)
print("Training final model...")
final_model = LinearRegression()  # Replace with your best model
final_model.fit(X_train, y_train)
print("Model training complete!")

# Step 2: Save model using pickle
print("\nSaving model with pickle...")
with open('model.pkl', 'wb') as file:
    pickle.dump(final_model, file)
print("✓ Model saved as 'model.pkl'")

# Step 3: Alternative: Save using joblib (often better for large models)
print("\nSaving model with joblib...")
joblib.dump(final_model, 'model_joblib.pkl')
print("✓ Model saved as 'model_joblib.pkl'")

# Step 4: Save scaler (important for production)
print("\nSaving scaler...")
joblib.dump(scaler, 'scaler_joblib.pkl')
print("✓ Scaler saved as 'scaler_joblib.pkl'")

# Step 5: Save model metadata
metadata = {
    'model_type': str(type(final_model).__name__),
    'trained_at': datetime.now().isoformat(),
    'training_samples': X_train.shape[0],
    'feature_count': X_train.shape[1],
    'feature_names': list(X_train.columns),
    'input_scale_method': 'StandardScaler',
}

with open('model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print("✓ Metadata saved as 'model_metadata.json'")

# Step 6: Verify model can be loaded
print("\nVerifying model load...")
loaded_model = pickle.load(open('model.pkl', 'rb'))
test_prediction = loaded_model.predict(X_test[:1])
print(f"✓ Model loaded successfully")
print(f"✓ Test prediction (first sample): {test_prediction[0]:.4f}")

print("\n" + "="*60)
print("MODEL SAVED SUCCESSFULLY")
print("="*60)
print(f"Files created:")
print(f"  - model.pkl (pickle format)")
print(f"  - model_joblib.pkl (joblib format)")
print(f"  - scaler_joblib.pkl (feature scaler)")
print(f"  - model_metadata.json (model information)")
print("\nTo load in production:")
print("  import pickle")
print("  model = pickle.load(open('model.pkl', 'rb'))")
