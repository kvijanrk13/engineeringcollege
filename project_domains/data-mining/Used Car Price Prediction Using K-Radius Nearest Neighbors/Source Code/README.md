# Used Car Price Prediction Using K-Radius Nearest Neighbors

This is a portable starter project for students to train machine learning models from the Kaggle car datasets stored in:

`../datasets/`

This `Source Code` folder is also a complete local Django project. After extracting the ZIP file, students can run Django migrations and execute the Apriori data mining page locally.

The default workflow trains a depreciation-focused model from the Cardekho `car data.csv` file because it contains both `Present_Price` and `Selling_Price`. Other datasets can be selected for ordinary used-car price prediction.

## Setup

```powershell
cd "project_domains\data-mining\Used Car Price Prediction Using K-Radius Nearest Neighbors\Source Code"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS/Linux:

```bash
cd "project_domains/data-mining/Used Car Price Prediction Using K-Radius Nearest Neighbors/Source Code"
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## Run the Django Execution Page

Windows:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

macOS/Linux:

```bash
./.venv/bin/python manage.py makemigrations
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py runserver
```

Open:

`http://127.0.0.1:8000/`

The first page is student registration. After registration, the app opens the GitHub-style execution pages:

- dataset loading
- exploratory data analysis
- preprocessing
- train/test split and scaling
- model comparison
- cross validation
- model saving
- prediction page
- Apriori Data Mining execution

The Apriori page is also available directly at:

`http://127.0.0.1:8000/apriori/`

## Train

```powershell
.\.venv\Scripts\python.exe train_model.py --dataset cardekho-depreciation
```

## Apriori Analysis

Apriori is used here as an association-rule mechanism, not as the final regression model. The car records are converted into transaction items such as `Age=Newer`, `Kilometers=Low KM`, `Fuel=Petrol`, `Transmission=Manual`, `Price=High`, and `Depreciation=Low`. Apriori then discovers frequent attribute combinations that imply price or depreciation bands.

```powershell
.\.venv\Scripts\python.exe apriori_analysis.py --dataset cardekho-depreciation
```

Other dataset keys:

- `used-cars-large`
- `used-car-cleaned`
- `cardekho-v3`
- `cardekho-v4`
- `car-price-2025`
- `ann-car-sales`

The model and metrics are written to `artifacts/`.

## Predict

```powershell
.\.venv\Scripts\python.exe predict_price.py --year 2018 --mileage 45000 --fuel Petrol --transmission Manual --make Honda --model City --engine-size 1.5
```

## Files

- `dataset_loader.py`: loads and normalizes the available Kaggle CSV files
- `train_model.py`: trains a regression model and stores artifacts
- `apriori_analysis.py`: runs association-rule mining for price/depreciation bands
- `predict_price.py`: loads the trained model and predicts a price from command-line inputs
- `manage.py`: runs the local Django execution page
- `car_price_project/`: local Django settings and URL configuration
- `car_price_app/`: local Django app that renders registration, GitHub execution pages, and Apriori execution output
- `requirements.txt`: minimal Python packages needed on a student laptop
