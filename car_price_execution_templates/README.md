# Car Price Prediction - Execution Templates
## Complete Guide to Standalone Python & HTML Files for Modification

This directory contains **standalone, modifiable templates** for the Car Price Prediction Machine Learning project. Each template is available in both **HTML** (for viewing) and **Python** (for execution) formats.

---

## 📁 Directory Structure

```
car_price_execution_templates/
├── README.md (this file)
├── MODIFICATION_GUIDE.md (detailed modification instructions)
├── QUICK_START.md (quick start guide)
│
├── HTML Templates (for viewing in browser)
│   ├── 01_dataset_loading.html
│   ├── 02_exploratory_data_analysis.html
│   ├── 03_preprocessing.html
│   ├── 04_train_test_scaling.html
│   ├── 05_model_comparison.html
│   ├── 06_cross_validation.html
│   ├── 07_save_model.html
│   └── 08_prediction_page.html
│
└── Python Scripts (executable files)
    ├── 01_dataset_loading.py
    ├── 02_exploratory_data_analysis.py
    ├── 03_preprocessing.py
    ├── 04_train_test_scaling.py
    ├── 05_model_comparison.py
    ├── 06_cross_validation.py
    ├── 07_save_model.py
    └── 08_prediction_page.py
```

---

## 🎯 Project Overview

**Objective:** Predict second-hand car prices using machine learning algorithms

**Dataset:** Kaggle CarDekho dataset (car_data.csv)

**Target Variable:** Selling Price (in lakhs)

**Features:**
- Present Price
- Kilometers Driven
- Fuel Type (Petrol, Diesel, CNG)
- Seller Type (Dealer, Individual)
- Transmission (Manual, Automatic)
- Number of Owners (0-3)
- Year of Manufacture

---

## 🔄 Execution Pipeline

The templates follow a linear pipeline that you can execute in sequence:

### Phase 1: Data Preparation
1. **Dataset Loading** → Load and inspect the CSV file
2. **Exploratory Data Analysis (EDA)** → Visualize patterns and correlations
3. **Preprocessing** → Convert categorical variables to numeric features

### Phase 2: Model Development
4. **Train/Test Split & Scaling** → Prepare data for training
5. **Model Comparison** → Train and compare 5 regression algorithms
6. **Cross Validation** → Validate model performance across folds

### Phase 3: Deployment
7. **Save Model** → Serialize trained model for production
8. **Prediction Page** → Create Streamlit web interface for predictions

---

## 🚀 Quick Start

### Option A: Run All Steps Sequentially

```bash
# Step 1: Load dataset
python 01_dataset_loading.py

# Step 2: Exploratory analysis
python 02_exploratory_data_analysis.py

# Step 3: Preprocessing
python 03_preprocessing.py

# Step 4: Train/Test split
python 04_train_test_scaling.py

# Step 5: Compare models
python 05_model_comparison.py

# Step 6: Cross validation
python 06_cross_validation.py

# Step 7: Save model
python 07_save_model.py

# Step 8: Launch prediction app
streamlit run 08_prediction_page.py
```

### Option B: View HTML Templates

Simply open any `.html` file in your web browser:
- Double-click the file, or
- Drag and drop into browser, or
- Right-click → Open with → Your browser

Each HTML file includes:
- Step purpose and description
- Complete code snippets
- Expected output
- **Modification Guide** with improvement suggestions

---

## 📝 Modification Guide (Quick Reference)

### Step 1: Dataset Loading
**Possible modifications:**
```python
# Change dataset source
car_data = pd.read_csv('alternate_dataset.csv')

# Filter data
car_data = car_data[car_data['Selling_Price'] > 5]

# Add column preprocessing
car_data['Age'] = 2024 - car_data['Year']

# Export summary
car_data.describe().to_csv('data_summary.csv')
```

### Step 2: Exploratory Data Analysis
**Possible modifications:**
```python
# Different plot types
sns.histplot(data=car_data, x='Selling_Price', kde=True)
sns.violinplot(x='Fuel_Type', y='Selling_Price', data=car_data)
sns.boxplot(x='Transmission', y='Selling_Price', data=car_data)

# Save figures
plt.savefig('price_by_fuel_type.png', dpi=300, bbox_inches='tight')

# Different color palettes
sns.set_palette('husl')
```

### Step 3: Preprocessing
**Possible modifications:**
```python
# Handle missing values
car_data.fillna(car_data.mean(), inplace=True)

# Different encoding method
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
car_data['Fuel_Type'] = le.fit_transform(car_data['Fuel_Type'])

# Feature engineering
car_data['Price_per_KM'] = car_data['Selling_Price'] / car_data['Kms_Driven']
car_data['Age'] = 2024 - car_data['Year']

# Drop different columns
X = car_data.drop(['Selling_Price', 'Car_Name', 'Outlier_Column'], axis=1)
```

### Step 4: Train/Test Split & Scaling
**Possible modifications:**
```python
# Different train/test ratio
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Different scaler
from sklearn.preprocessing import MinMaxScaler, RobustScaler
scaler = MinMaxScaler()  # or RobustScaler()

# Cross-validation
from sklearn.model_selection import KFold
cv = KFold(n_splits=10, shuffle=True)

# Save train/test data
X_train.to_csv('X_train.csv')
X_test.to_csv('X_test.csv')
```

### Step 5: Model Comparison
**Possible modifications:**
```python
# Add more models
from sklearn.svm import SVR
from xgboost import XGBRegressor

models['Support Vector Regressor'] = SVR(kernel='rbf', C=100)
models['XGBoost'] = XGBRegressor(n_estimators=100)

# Tune hyperparameters
models['Random Forest'] = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    random_state=42
)

# Add more metrics
from sklearn.metrics import mean_absolute_percentage_error
results.append({
    'Model': name,
    'MAE': mae,
    'MAPE': mean_absolute_percentage_error(y_test, predictions),
})

# Visualize comparison
results_df.plot(x='Model', y=['MAE', 'R2 Score'], kind='bar')
plt.xticks(rotation=45)
plt.show()
```

### Step 6: Cross Validation
**Possible modifications:**
```python
# Different number of folds
cv = KFold(n_splits=10, shuffle=True, random_state=42)

# Stratified cross-validation (for imbalanced data)
from sklearn.model_selection import StratifiedKFold
cv = StratifiedKFold(n_splits=5)

# Time series cross-validation
from sklearn.model_selection import TimeSeriesSplit
cv = TimeSeriesSplit(n_splits=5)

# Nested cross-validation for hyperparameter tuning
from sklearn.model_selection import GridSearchCV
param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [10, 20, 30]}
grid_search = GridSearchCV(RandomForestRegressor(), param_grid, cv=5)
grid_search.fit(X, y)
```

### Step 7: Save Model
**Possible modifications:**
```python
# Save best model from Step 5 (don't just use LinearRegression)
best_model_name = 'Random Forest Regression'  # or whatever performed best
final_model = models[best_model_name]

# Add model performance to metadata
metadata['r2_score'] = 0.92
metadata['mae'] = 0.45
metadata['model_performance_date'] = datetime.now().isoformat()

# Compress model for deployment
import gzip
with open('model.pkl', 'rb') as f_in:
    with gzip.open('model.pkl.gz', 'wb') as f_out:
        f_out.writelines(f_in)

# Version model
import hashlib
model_hash = hashlib.md5(pickle.dumps(final_model)).hexdigest()
```

### Step 8: Prediction Page
**Possible modifications:**
```python
# Add confidence intervals
import numpy as np
predictions = model.predict(input_data)
confidence = np.random.uniform(0.85, 0.95)  # Replace with actual CI calculation

# Show similar cars
similar_cars = car_data[
    (car_data['Fuel_Type'] == input_fuel_type) &
    (car_data['Selling_Price'].between(prediction * 0.9, prediction * 1.1))
]
st.dataframe(similar_cars.head(5))

# Add SHAP explanations
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(input_data)

# Batch predictions
st.file_uploader("Upload CSV for batch predictions", type='csv')

# Store prediction history
if 'predictions' not in st.session_state:
    st.session_state.predictions = []
st.session_state.predictions.append({
    'inputs': input_data,
    'prediction': prediction,
    'timestamp': datetime.now()
})
```

---

## 🔧 Dependency Requirements

```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.2.0
matplotlib>=3.5.0
seaborn>=0.12.0
streamlit>=1.20.0
joblib>=1.2.0
xgboost>=1.7.0  # Optional, for advanced models
shap>=0.42.0    # Optional, for model explanations
```

**Install all at once:**
```bash
pip install pandas numpy scikit-learn matplotlib seaborn streamlit joblib
```

---

## 📊 Expected Outputs at Each Step

| Step | Output Files | Key Metrics |
|------|--------------|-------------|
| 1 | Dataset loaded in memory | Shape, data types, null counts |
| 2 | Visualizations (plots) | Distribution patterns, correlations |
| 3 | X (features), y (target) | Shape of X, list of features |
| 4 | X_train, X_test, y_train, y_test | Shapes, scaler stats |
| 5 | model_comparison_results.csv | MAE, MSE, RMSE, R² for each model |
| 6 | cross_validation_results.csv | Mean/Std R² for each fold |
| 7 | model.pkl, scaler.pkl, metadata.json | Model file size, feature count |
| 8 | Streamlit web interface | Live predictions with confidence |

---

## 🎨 HTML Templates Features

Each HTML template includes:

1. **Purpose Section** - What the step does
2. **Code Block** - Copy-paste ready Python code
3. **Modification Guide** - Suggested improvements
4. **Expected Output** - What to expect when running
5. **Navigation** - Links to other steps

**How to use:**
- Open in browser for reading
- Copy code to your Python editor
- Modify as needed
- Run the Python script

---

## 🐛 Troubleshooting

### Issue: "No module named 'pandas'"
**Solution:** Install missing dependency
```bash
pip install pandas
```

### Issue: "car_data.csv not found"
**Solution:** Ensure dataset is in the same directory as script
```bash
# Copy dataset to working directory
cp /path/to/car_data.csv ./
```

### Issue: "scaler.pkl not found" in Step 7
**Solution:** Run Step 4 first to generate the scaler
```bash
python 04_train_test_scaling.py
```

### Issue: Streamlit app won't start
**Solution:** Install Streamlit properly
```bash
pip install --upgrade streamlit
```

---

## 📚 Learning Resources

### Concepts Covered:
- **Data Loading & Exploration** - Pandas, NumPy operations
- **Data Visualization** - Matplotlib, Seaborn for EDA
- **Feature Engineering** - One-hot encoding, scaling, preprocessing
- **Machine Learning Models** - Linear regression, ensemble methods
- **Model Evaluation** - Metrics, cross-validation, hyperparameter tuning
- **Model Deployment** - Serialization, web interface with Streamlit

### Recommended Study Order:
1. Read HTML file for conceptual understanding
2. Study Python script for implementation details
3. Modify and customize based on your requirements
4. Run and observe results
5. Experiment with suggested modifications

---

## 🎯 Next Steps After Mastering Templates

1. **Apply to Your Own Dataset**
   - Replace car_data.csv with your dataset
   - Adapt preprocessing for your features
   - Retrain models with your data

2. **Enhance the Pipeline**
   - Add more visualization types
   - Implement hyperparameter tuning
   - Add cross-validation strategies
   - Create ensemble models

3. **Deploy to Production**
   - Containerize with Docker
   - Deploy Streamlit app to cloud (Heroku, AWS, Google Cloud)
   - Create REST API endpoints
   - Set up monitoring and logging

4. **Advanced Topics**
   - Deep learning with neural networks
   - Time series forecasting
   - Anomaly detection
   - Real-time predictions

---

## 📞 Support & Questions

For questions about specific steps:
1. Check the **Modification Guide** section of corresponding HTML file
2. Review the inline comments in Python scripts
3. Refer to official documentation:
   - [Scikit-learn](https://scikit-learn.org/)
   - [Pandas](https://pandas.pydata.org/)
   - [Streamlit](https://docs.streamlit.io/)

---

## 📄 License & Attribution

These templates are created for the **Engineering College Django Project** - Machine Learning Demonstrations.

**Original GitHub Reference:**
- Project: Predicting Second Hand Cars Price using Machine Learning Algorithms
- Dataset: Kaggle CarDekho dataset

---

## ✅ Checklist Before Running

- [ ] Dataset (car_data.csv) is in the working directory
- [ ] All required Python packages are installed
- [ ] Running Python 3.8 or higher
- [ ] Have 2-4 GB free RAM for model training
- [ ] Read Step 1 before running other steps
- [ ] Check modification guide for your use case

---

## 🎓 Educational Value

These templates serve as:
- **Learning Resource** - Understand ML pipeline from start to finish
- **Reference Implementation** - Best practices in ML development
- **Customization Template** - Easily modify for your specific needs
- **Production Starter** - Ready-to-adapt for real-world use

**Happy Learning! 🚀**
