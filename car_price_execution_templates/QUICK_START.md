# Quick Start Guide - Car Price Prediction Templates

## 🎯 First Time Users

Start here if you're new to these templates!

### Prerequisites
```bash
# Install required packages (do this first!)
pip install pandas numpy scikit-learn matplotlib seaborn streamlit joblib
```

### Choice 1: View Templates First (Recommended for Learning)

1. **Open in Browser**
   - Navigate to `car_price_execution_templates/`
   - Double-click any `.html` file
   - Read the purpose and modification guide
   - Copy interesting code to try

2. **Start with Step 1**
   - Open `01_dataset_loading.html` in your browser
   - Understand what happens
   - Look at the Python code

### Choice 2: Run Templates Immediately

**Prerequisites:**
- Have `car_data.csv` in the same directory as scripts
- Have all packages installed

**Run in sequence:**

```bash
# Step 1: Load data
python 01_dataset_loading.py
# Output: Dataset info, null counts, statistics

# Step 2: Visualize patterns
python 02_exploratory_data_analysis.py
# Output: Charts showing price patterns

# Step 3: Prepare features
python 03_preprocessing.py
# Output: X and y ready for training

# Step 4: Split and scale
python 04_train_test_scaling.py
# Output: Training/test sets saved

# Step 5: Train models
python 05_model_comparison.py
# Output: CSV file with model metrics

# Step 6: Validate performance
python 06_cross_validation.py
# Output: Cross-validation results

# Step 7: Save trained model
python 07_save_model.py
# Output: model.pkl, scaler.pkl created

# Step 8: Launch web interface
streamlit run 08_prediction_page.py
# Output: Open http://localhost:8501 in browser
```

---

## 🎓 Learning Paths

### Path A: Understand Theory First
1. Read HTML file for each step
2. Study the purpose and modifications
3. Then run the Python code
4. Compare output with expectations

### Path B: Learn by Doing
1. Run Python scripts in order
2. Observe outputs
3. Read HTML to understand what happened
4. Modify code based on suggestions

### Path C: Jump to Specific Interest
- **Visualizations?** → Start with Step 2
- **Data Processing?** → Start with Step 3
- **Model Training?** → Start with Step 5
- **Web App?** → Start with Step 8

---

## ⚡ Common Tasks

### "I want to use my own dataset"

1. Replace `car_data.csv` with your file
2. Update column names in each script:
   ```python
   # Change this:
   car_data['Selling_Price']
   # To your column name:
   car_data['YourColumnName']
   ```
3. Run steps again

### "I want to add a new model"

1. Open `05_model_comparison.py`
2. Add to the models dictionary:
   ```python
   from sklearn.svm import SVR
   models['Support Vector Machine'] = SVR(kernel='rbf')
   ```
3. Run the script

### "I want to see how predictions work"

1. Make sure you've run steps 1-7
2. Run `streamlit run 08_prediction_page.py`
3. Enter values and click "Predict"

### "I want to modify the prediction page"

1. Edit `08_prediction_page.py`
2. Change inputs, add visualizations, etc.
3. Save and refresh Streamlit (Cmd+R)

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| "No module named 'pandas'" | Run: `pip install pandas` |
| "file not found: car_data.csv" | Place dataset in same folder as scripts |
| "No pickle file found" | Run steps 1-7 first |
| "Streamlit not starting" | Try: `pip install --upgrade streamlit` |
| "Can't find X_train" | Run step 4 before step 5 |

---

## 📝 File Naming Convention

Each file is numbered 01-08 to show execution order:

| Number | Meaning |
|--------|---------|
| **01-03** | Data Preparation Phase |
| **04-06** | Model Development Phase |
| **07-08** | Deployment Phase |

**Always run in order!** Step 5 depends on Step 4, etc.

---

## 🎯 Minimum Viable Example

If you just want to see it work, copy this script:

```python
# quick_test.py
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load
car_data = pd.read_csv('car_data.csv')
print("Dataset loaded:", car_data.shape)

# Preprocess
X = car_data.drop(['Selling_Price'], axis=1)
y = car_data['Selling_Price']

# Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train
model = LinearRegression()
model.fit(X_train, y_train)

# Test
score = model.score(X_test, y_test)
print(f"Model Score: {score:.4f}")

# Save
import pickle
pickle.dump(model, open('model.pkl', 'wb'))
print("✓ Model saved!")
```

Run with: `python quick_test.py`

---

## 🚀 What's Next?

After running all templates:

1. **Modify templates** - Adjust code for your needs
2. **Combine steps** - Create one big pipeline script
3. **Deploy app** - Put Streamlit on cloud
4. **Add features** - Implement model explanations, batch predictions, etc.
5. **Use for production** - Replace model.pkl with retrained version

---

## 💡 Pro Tips

✅ **Always start with Step 1** - It shows you your data

✅ **Keep original files** - Save modified versions as `01_dataset_loading_v2.py`

✅ **Document changes** - Add comments explaining your modifications

✅ **Test after changes** - Run next step to ensure compatibility

✅ **Save outputs** - Add code to save CSVs/plots for reference

---

## 📚 Complete Example Flow

```
1. Open 01_dataset_loading.html in browser
   ↓
2. Read and understand the purpose
   ↓
3. Run: python 01_dataset_loading.py
   ↓
4. Review output (data shape, stats, nulls)
   ↓
5. Move to 02_exploratory_data_analysis.html
   ↓
6. Repeat steps 2-4 for all files
   ↓
7. After step 7, run streamlit for web interface
   ↓
8. Modify and experiment!
```

---

## ❓ Still Have Questions?

1. **Check README.md** - Full documentation
2. **Read the HTML file** - Each step explains modifications
3. **Check Python comments** - Code is well-documented
4. **Run with --verbose** - Add debugging output

---

## ✨ You're Ready!

Start with Step 1 and follow the sequence. Good luck! 🎓

**Next: Open `01_dataset_loading.html` in your browser →**
