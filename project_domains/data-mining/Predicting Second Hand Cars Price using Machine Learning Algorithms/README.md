# Predicting Prices of Second-Hand Cars and Depreciation

## Identified GitHub Reference Project

- Repository: https://github.com/vasugi2003/second-hand-car-price-prediction-using-machine-learning
- Title: `SECOND-HAND-CAR-PRICE-PREDICTION-USING-MACHINE-LEARNING`
- Repository description: Predicting price of second hand automotives.
- Main artifacts visible on GitHub: `carprice_prediction.ipynb`, `model.py`, `app.py`, `model.pkl`, `car_data.csv`, and Streamlit templates.
- Topics visible on GitHub include machine learning algorithms, prediction, pandas, Kaggle, regression models, scikit-learn, and Streamlit.

This local folder is a project workspace for adapting the idea with the collected Kaggle datasets in `../datasets/`.

## Folder Structure

This project folder is organized for student submission and download:

- `Source Code/` - executable standalone Django project and ML scripts
- `Modules/` - module breakdown and implementation notes
- `Documentation/` - project report, setup guide, and viva notes
- `PPT/` - presentation outline or slide deck
- `Video/` - demo script or video link notes
- `Test Cases/` - manual and command-line test cases
- `UML Diagrams/` - use case, activity, class, and component diagrams
- `Databases/` - database notes, schema references, migration notes, and SQLite guidance
- `datasets/` - Kaggle datasets and generated Khammam Maruti Suzuki sample data

The runnable starter source code is stored in:

`Source Code/`

## Project Objective

Build machine learning and data mining models that estimate second-hand car price and depreciation using vehicle age, mileage, make, model, fuel type, transmission, engine capacity, ownership history, seller type, condition, and related listing fields.

## Candidate Algorithms

- Linear Regression, Ridge, Lasso, and ElasticNet for interpretable baseline models
- Decision Tree and Random Forest Regressor for nonlinear price patterns
- Gradient boosting models such as XGBoost, LightGBM, or scikit-learn HistGradientBoosting
- K-Means clustering or segment-based modeling for depreciation bands by car age, mileage, make, and price range

## Local Dataset Folder

Use:

`project_domains/data-mining/Predicting Second Hand Cars Price using Machine Learning Algorithms/datasets/`

The dataset manifest in that folder lists source URLs, extracted CSV files, row counts, and suggested target/depreciation fields.

## Run the Standalone Student Project

From this project folder:

```powershell
cd "Source Code"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Run Inside the Main EngineeringCollege Project

From the main `engineeringcollege` repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open:

- `http://127.0.0.1:8000/car-price/`
- `http://127.0.0.1:8000/car-price/maruti-prices/`
- `http://127.0.0.1:8000/car-price/research-paper/`
