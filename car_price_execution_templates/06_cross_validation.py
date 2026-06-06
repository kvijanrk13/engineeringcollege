"""
Step 6: Cross Validation
Purpose: Validate model performance across multiple folds for better generalization assessment.
"""
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import numpy as np
import pandas as pd

# Assuming X, y are already prepared (full dataset, not train/test split)
# For cross-validation, we use the entire dataset

# Define models to cross-validate
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=1.0),
    'Random Forest Regression': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting Regression': GradientBoostingRegressor(
        n_estimators=100, 
        learning_rate=0.1, 
        random_state=42
    ),
}

# Perform cross-validation with 5 folds
cv = KFold(n_splits=5, shuffle=True, random_state=42)
cv_results = []

print("Performing 5-Fold Cross Validation...\n")

for name, model in models.items():
    # Calculate cross-validation scores
    scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
    
    cv_results.append({
        'Model': name,
        'Mean R2': np.mean(scores),
        'Std R2': np.std(scores),
        'Min R2': np.min(scores),
        'Max R2': np.max(scores),
    })
    
    print(f"{name}:")
    print(f"  Mean R2 Score: {np.mean(scores):.4f}")
    print(f"  Std Dev: {np.std(scores):.4f}")
    print(f"  Range: {np.min(scores):.4f} - {np.max(scores):.4f}")
    print(f"  Individual fold scores: {[f'{s:.4f}' for s in scores]}\n")

# Create results DataFrame
cv_results_df = pd.DataFrame(cv_results)
print("\n" + "="*70)
print("CROSS VALIDATION RESULTS (5-Fold)")
print("="*70)
print(cv_results_df.to_string(index=False))

# Find best model
best_idx = cv_results_df['Mean R2'].idxmax()
best_model = cv_results_df.loc[best_idx, 'Model']
best_score = cv_results_df.loc[best_idx, 'Mean R2']
print(f"\nBest Model: {best_model} (Mean R2: {best_score:.4f})")

# Optional: Save results
cv_results_df.to_csv('cross_validation_results.csv', index=False)
print("\nResults saved to 'cross_validation_results.csv'")

# Optional: Try different scoring metrics
print("\n" + "="*70)
print("Testing other scoring metrics (for best model)...")
print("="*70)
best_model_obj = models[best_model]

for scoring_metric in ['neg_mean_absolute_error', 'neg_mean_squared_error', 'r2']:
    scores = cross_val_score(best_model_obj, X, y, cv=cv, scoring=scoring_metric)
    print(f"{scoring_metric}: Mean={np.mean(scores):.4f}, Std={np.std(scores):.4f}")
