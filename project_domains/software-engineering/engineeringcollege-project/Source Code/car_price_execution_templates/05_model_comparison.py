"""
Step 5: Model Comparison
Purpose: Train and compare multiple regression algorithms.
"""
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
import numpy as np

# Assuming X_train, X_test, y_train, y_test are already prepared
# from train_test_scaling.py

# Step 1: Define multiple regression models
models = {
    'Linear Regression': LinearRegression(),
    'Lasso Regression': Lasso(alpha=1.0),
    'Ridge Regression': Ridge(alpha=1.0),
    'Random Forest Regression': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting Regression': GradientBoostingRegressor(
        n_estimators=100, 
        learning_rate=0.1, 
        random_state=42
    ),
}

# Step 2: Train and evaluate each model
results = []
print("Training models...\n")

for name, model in models.items():
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions on test set
    predictions = model.predict(X_test)
    
    # Calculate performance metrics
    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, predictions)
    
    results.append({
        'Model': name,
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'R2 Score': r2,
    })
    
    print(f"{name}:")
    print(f"  MAE: {mae:.4f}")
    print(f"  MSE: {mse:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R2 Score: {r2:.4f}\n")

# Step 3: Create results DataFrame
results_df = pd.DataFrame(results)
print("\n" + "="*60)
print("MODEL COMPARISON RESULTS")
print("="*60)
print(results_df.to_string(index=False))

# Find best model by R2 Score
best_model_idx = results_df['R2 Score'].idxmax()
best_model_name = results_df.loc[best_model_idx, 'Model']
best_r2 = results_df.loc[best_model_idx, 'R2 Score']
print(f"\nBest Model: {best_model_name} (R2 Score: {best_r2:.4f})")

# Optional: Save results to CSV
results_df.to_csv('model_comparison_results.csv', index=False)
print("\nResults saved to 'model_comparison_results.csv'")
