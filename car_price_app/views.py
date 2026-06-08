from __future__ import annotations

from pathlib import Path
from urllib.parse import quote as urlquote

from django.http import Http404
from django.shortcuts import redirect, render, reverse

from apriori_analysis import apriori_rules, make_transactions
from dataset_loader import DATASET_FILES, available_datasets, normalize_dataset, read_csv
import pandas as pd

from .forms import CarEstimateForm, StudentRegistrationForm
from .maruti_data import YEARS, maruti_project_dataset
from .models import ExecutionLog


PROJECT_TITLE = "Predicting Second Hand Cars Price using Machine Learning Algorithms"
EXECUTION_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "car_price_execution_templates"


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


def _require_gmail_or_registered(request, next_url=None):
    is_gmail_logged_in = (
        request.session.get("google_oauth_email", "").endswith("@gmail.com")
        or request.user.is_authenticated
        and getattr(request.user, "email", "").lower().endswith("@gmail.com")
    )
    has_registration = request.session.get("student_registration_id") is not None
    if not (is_gmail_logged_in or has_registration):
        if next_url is None:
            next_url = request.build_absolute_uri()
        return redirect(f"{reverse('dashboard:google_login')}?role=student&continue=1&next={urlquote(next_url)}")
    return None


def _maruti_execution_context(title: str) -> dict:
    maruti_data = maruti_project_dataset()
    return {
        "title": title,
        "years": YEARS,
        "maruti_data": maruti_data,
        "maruti_lookup": {model["name"]: model for model in maruti_data},
    }


def execution_overview(request):
    redirect_response = _require_gmail_or_registered(request)
    if redirect_response is not None:
        return redirect_response
    return render(
        request,
        "car_price_app/execution_overview.html",
        _maruti_execution_context("Maruti Suzuki Khammam Car Price Selection"),
    )


def execution_step(request, step_slug):
    redirect_response = _require_gmail_or_registered(request)
    if redirect_response is not None:
        return redirect_response
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


def _normalize_owner(owner_value: str) -> str:
    owner_text = str(owner_value or "").strip().lower()
    if owner_text.startswith("first"):
        return "First Owner"
    if owner_text.startswith("second"):
        return "Second Owner"
    if owner_text.startswith("third"):
        return "Third Owner"
    if owner_text.isdigit():
        return {
            "1": "First Owner",
            "2": "Second Owner",
            "3": "Third Owner",
        }.get(owner_text, "More than Third Owner")
    return owner_text.title() if owner_text else "Unknown"


def _bucket_kilometers(value: float) -> str:
    if pd.isna(value):
        return "Unknown"
    if value <= 30000:
        return "Low KM"
    if value <= 80000:
        return "Medium KM"
    return "High KM"


def _build_input_items(cleaned_data: dict) -> set[str]:
    year = cleaned_data.get("model_year")
    age_item = "Unknown Age"
    if isinstance(year, int):
        if year >= pd.Timestamp.today().year - 5:
            age_item = "Age=Newer"
        elif year >= pd.Timestamp.today().year - 10:
            age_item = "Age=Mid Age"
        else:
            age_item = "Age=Older"

    km_item = _bucket_kilometers(cleaned_data.get("kilometers", 0))
    owner_item = f"Owner={_normalize_owner(cleaned_data.get('owners'))}"

    items = {age_item, f"Kilometers={km_item}" if km_item else "Kilometers=Unknown", owner_item}
    return items


def _match_apriori_rules(rules: list[dict], input_items: set[str]) -> list[dict]:
    matched = [rule for rule in rules if rule["if"] in input_items]
    return sorted(matched, key=lambda rule: (rule["lift"], rule["confidence_percent"]), reverse=True)[:6]


def _estimate_price(data: pd.DataFrame, dataset_key: str, cleaned_data: dict) -> dict:
    raw = read_csv(DATASET_FILES[dataset_key])
    original_price_unit = "INR"
    price_multiplier = 1.0
    if dataset_key == "cardekho-depreciation":
        price_multiplier = 100000.0
        original_price_unit = "INR"
    elif dataset_key in {"cardekho-v3", "cardekho-v4"}:
        original_price_unit = "INR"
    else:
        original_price_unit = "dataset units"

    candidates = data.copy()
    brand = str(cleaned_data.get("brand") or "").strip().lower()
    model = str(cleaned_data.get("model") or "").strip().lower()
    year = cleaned_data.get("model_year")
    engine_capacity = cleaned_data.get("engine_capacity")
    owner = _normalize_owner(cleaned_data.get("owners"))
    kilometer_bucket = _bucket_kilometers(cleaned_data.get("kilometers", 0))

    if brand:
        candidates = candidates[candidates["make"].fillna("").str.lower().str.contains(brand, regex=False)]
    if model:
        candidates = candidates[candidates["model"].fillna("").str.lower().str.contains(model, regex=False)]
    if year is not None:
        candidates = candidates[candidates["year"].between(year - 1, year + 1)]
    if not candidates.empty and pd.notna(engine_capacity):
        candidates = candidates[(candidates["engine_size"].between(engine_capacity - 300, engine_capacity + 300)) | candidates["engine_size"].isna()]
    if not candidates.empty:
        candidates = candidates[candidates["owner"].fillna("").str.contains(owner, case=False, regex=False)]
    if not candidates.empty:
        candidates = candidates[candidates["mileage"].apply(lambda value: _bucket_kilometers(value) == kilometer_bucket if pd.notna(value) else False)]

    if len(candidates) < 10:
        candidates = data.copy()
        if brand:
            candidates = candidates[candidates["make"].fillna("").str.lower().str.contains(brand, regex=False)]
        if year is not None:
            candidates = candidates[candidates["year"].between(year - 2, year + 2)]
        if not candidates.empty and pd.notna(engine_capacity):
            candidates = candidates[(candidates["engine_size"].between(engine_capacity - 500, engine_capacity + 500)) | candidates["engine_size"].isna()]
        if not candidates.empty:
            candidates = candidates[candidates["mileage"].apply(lambda value: _bucket_kilometers(value) == kilometer_bucket if pd.notna(value) else False)]

    if candidates.empty:
        average_price = data["target_price"].mean()
        note = "Used the full dataset because no close matches were found."
    else:
        average_price = candidates["target_price"].mean()
        note = f"Based on {len(candidates)} similar listings from the selected dataset."

    adjustment = 1.0
    if cleaned_data.get("accident") == "yes":
        adjustment -= 0.10
    if cleaned_data.get("repairs") == "yes":
        adjustment -= 0.08
    if cleaned_data.get("tyres_modified") == "yes":
        adjustment -= 0.05
    if cleaned_data.get("owners") == "Third":
        adjustment -= 0.05
    if cleaned_data.get("owners") == "More":
        adjustment -= 0.10

    estimated_price = max(average_price * adjustment, 0)
    return {
        "dataset_key": dataset_key,
        "average_price": average_price,
        "estimated_price": estimated_price,
        "currency": original_price_unit,
        "display_price": estimated_price * price_multiplier,
        "note": note,
        "depreciation_adjustment": round((1 - adjustment) * 100, 1),
    }


def _load_execution_files() -> list[dict[str, str]]:
    execution_files = []
    for path in sorted(EXECUTION_TEMPLATES_DIR.glob("*")):
        if path.suffix.lower() not in {".py", ".html"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="ISO-8859-1")
        execution_files.append(
            {
                "name": path.name,
                "type": "Python" if path.suffix.lower() == ".py" else "HTML",
                "content": content,
            }
        )
    return execution_files


def apriori_execution(request):
    maruti_data = maruti_project_dataset()

    return render(
        request,
        "car_price_app/maruti_apriori.html",
        {
            "title": "Maruti Suzuki Khammam Car Price Prediction Execution",
            "years": YEARS,
            "maruti_data": maruti_data,
            "execution_files": _load_execution_files(),
            "model_count": len(maruti_data),
        },
    )


def maruti_prices(request):
    return render(
        request,
        "car_price_app/execution_overview.html",
        _maruti_execution_context("Maruti Suzuki Cars - Khammam Price, Questionnaire, and K-RADIUS Prediction"),
    )
