from __future__ import annotations

from django.http import Http404
from django.shortcuts import redirect, render

from apriori_analysis import apriori_rules, make_transactions
from dataset_loader import available_datasets, normalize_dataset

from .forms import StudentRegistrationForm
from .models import ExecutionLog


PROJECT_TITLE = "Predicting Second Hand Cars Price using Machine Learning Algorithms"


GITHUB_EXECUTION_STEPS = [
    {
        "slug": "dataset-loading",
        "title": "Dataset Loading",
        "purpose": "Load the Kaggle Cardekho car_data.csv file and inspect the first records.",
        "code": """import pandas as pd

car_data = pd.read_csv('car_data.csv')
print(car_data.head())
print(car_data.info())
print(car_data.isnull().sum())
print(car_data.describe())""",
    },
    {
        "slug": "exploratory-data-analysis",
        "title": "Exploratory Data Analysis",
        "purpose": "Visualize price patterns by fuel type, seller type, transmission, and correlations.",
        "code": """import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
sns.barplot(x='Fuel_Type', y='Selling_Price', data=car_data, ax=axes[0])
sns.barplot(x='Seller_Type', y='Selling_Price', data=car_data, ax=axes[1])
sns.barplot(x='Transmission', y='Selling_Price', data=car_data, ax=axes[2])

numeric_columns = car_data.select_dtypes(include=['float64', 'int64']).columns
sns.heatmap(car_data[numeric_columns].corr(), annot=True)
plt.title('Correlation between the columns')
plt.show()""",
    },
    {
        "slug": "preprocessing",
        "title": "Preprocessing",
        "purpose": "Convert categorical vehicle fields into numeric features for machine learning.",
        "code": """car_data.replace({'Fuel_Type': {'Petrol': 0, 'Diesel': 1, 'CNG': 2}}, inplace=True)
car_data = pd.get_dummies(
    car_data,
    columns=['Seller_Type', 'Transmission'],
    drop_first=True,
)

X = car_data.drop(['Car_Name', 'Selling_Price'], axis=1)
y = car_data['Selling_Price']""",
    },
    {
        "slug": "train-test-scaling",
        "title": "Train Test Split and Scaling",
        "purpose": "Prepare train/test data and scale numeric features before model training.",
        "code": """from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)""",
    },
    {
        "slug": "model-comparison",
        "title": "Model Comparison",
        "purpose": "Train and compare the regression algorithms used in the GitHub reference project.",
        "code": """from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd

models = {
    'Linear Regression': LinearRegression(),
    'Lasso Regression': Lasso(alpha=1.0),
    'Ridge Regression': Ridge(alpha=1.0),
    'Random Forest Regression': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting Regression': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42),
}

results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    results.append({
        'Model': name,
        'MAE': mean_absolute_error(y_test, predictions),
        'MSE': mean_squared_error(y_test, predictions),
        'R2 Score': r2_score(y_test, predictions),
    })

results_df = pd.DataFrame(results)
print(results_df)""",
    },
    {
        "slug": "cross-validation",
        "title": "Cross Validation",
        "purpose": "Validate the model performance across multiple folds.",
        "code": """from sklearn.model_selection import cross_val_score
import numpy as np

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring='r2')
    print(name, 'Average R2:', np.mean(scores))""",
    },
    {
        "slug": "save-model",
        "title": "Save Model",
        "purpose": "Save the trained prediction model as model.pkl for later execution.",
        "code": """import pickle

final_model = LinearRegression()
final_model.fit(X_train, y_train)

with open('model.pkl', 'wb') as file:
    pickle.dump(final_model, file)""",
    },
    {
        "slug": "prediction-page",
        "title": "Prediction Page",
        "purpose": "Collect vehicle details and display the predicted second-hand car price.",
        "code": """import pickle
import pandas as pd
import streamlit as st

with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

st.title('Car Price Prediction')
present_price = st.number_input('Present Price in lakhs', min_value=0.0)
kms_driven = st.number_input('Kms Driven', min_value=0)
fuel_type = st.selectbox('Fuel Type', ['Petrol', 'Diesel', 'CNG'])
seller_type = st.selectbox('Seller Type', ['Dealer', 'Individual'])
transmission = st.selectbox('Transmission', ['Manual', 'Automatic'])
owner = st.selectbox('Owner', [0, 1, 2, 3])
year = st.number_input('Year', min_value=1900, max_value=2026, step=1)

if st.button('Predict'):
    input_data = pd.DataFrame({
        'Present_Price': [present_price],
        'Kms_Driven': [kms_driven],
        'Fuel_Type': [0 if fuel_type == 'Petrol' else 1 if fuel_type == 'Diesel' else 2],
        'Owner': [owner],
        'Year': [year],
        'Seller_Type_Individual': [1 if seller_type == 'Individual' else 0],
        'Transmission_Manual': [1 if transmission == 'Manual' else 0],
    })
    prediction = model.predict(input_data)[0]
    st.success(f'Predicted Selling Price: INR {prediction * 100000:.2f}')""",
    },
]


def registration(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            registration_record = form.save()
            request.session["student_registration_id"] = registration_record.id
            return redirect("execution-overview")
    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "car_price_app/registration.html",
        {
            "title": PROJECT_TITLE,
            "form": form,
        },
    )


def execution_overview(request):
    return render(
        request,
        "car_price_app/execution_overview.html",
        {
            "title": PROJECT_TITLE,
            "steps": GITHUB_EXECUTION_STEPS,
            "registered": bool(request.session.get("student_registration_id")),
        },
    )


def execution_step(request, step_slug):
    step = next(
        (item for item in GITHUB_EXECUTION_STEPS if item["slug"] == step_slug),
        None,
    )
    if not step:
        raise Http404("Execution step not found")
    return render(
        request,
        "car_price_app/execution_step.html",
        {
            "title": PROJECT_TITLE,
            "step": step,
            "steps": GITHUB_EXECUTION_STEPS,
        },
    )


def apriori_execution(request):
    dataset_key = request.GET.get("dataset", "cardekho-depreciation")
    if dataset_key not in available_datasets():
        dataset_key = "cardekho-depreciation"

    data = normalize_dataset(dataset_key)
    transactions = make_transactions(data)
    rules = apriori_rules(transactions, min_support=0.08, min_confidence=0.45)[:15]
    ExecutionLog.objects.create(
        algorithm="Apriori Association Rule Mining",
        dataset=dataset_key,
        rows_executed=len(data),
    )

    return render(
        request,
        "car_price_app/index.html",
        {
            "title": PROJECT_TITLE,
            "dataset_key": dataset_key,
            "datasets": available_datasets(),
            "row_count": len(data),
            "transaction_count": len(transactions),
            "rules": rules,
            "latest_runs": ExecutionLog.objects.order_by("-created_at")[:5],
        },
    )
