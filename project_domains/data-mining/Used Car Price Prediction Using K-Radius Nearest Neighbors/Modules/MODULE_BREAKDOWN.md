# Module Breakdown

## Dataset Module

Files:

- `Source Code/dataset_loader.py`
- `datasets/README.md`

Responsibilities:

- Load available CSV datasets
- Normalize column names
- Select target fields for price and depreciation

## Training Module

Files:

- `Source Code/train_model.py`

Responsibilities:

- Split training and testing data
- Encode categorical values
- Train regression models
- Store model artifacts

## Prediction Module

Files:

- `Source Code/predict_price.py`
- `Source Code/car_price_app/`

Responsibilities:

- Accept vehicle attributes
- Load trained model
- Return predicted price

## Apriori Data Mining Module

Files:

- `Source Code/apriori_analysis.py`

Responsibilities:

- Convert car rows into transaction items
- Generate frequent itemsets
- Produce price and depreciation association rules

## Django Execution Module

Files:

- `Source Code/manage.py`
- `Source Code/car_price_project/`
- `Source Code/car_price_app/`

Responsibilities:

- Run migrations
- Start local server
- Render registration, execution, Apriori, and result pages
