# Used Car Price Prediction Using K-Radius Nearest Neighbors

## Abstract

This project predicts second-hand car prices using data mining and machine learning. The system loads used-car datasets, cleans mixed-format attributes, derives useful features such as vehicle age and depreciation, trains regression models, mines Apriori association rules, and presents execution pages through a standalone Django application.

## Scope

The project focuses on car-price analytics only. It does not include payment-gateway workflows, cloud-media storage, certificate uploads, or Engineering College administration features.

## Objectives

- Normalize multiple car datasets into a common schema.
- Predict selling price from vehicle age, mileage, fuel type, transmission, ownership, seller type, engine size, make, and model.
- Compare price trends and depreciation patterns.
- Mine frequent rules that connect car attributes to price and depreciation bands.
- Provide a runnable Django interface for registration, execution steps, Apriori results, and local demonstration.

## System Modules

1. Dataset Loader: reads CSV datasets and standardizes column names.
2. Preprocessing: extracts numeric values, cleans text fields, derives vehicle age, and handles missing values.
3. Model Training: trains a Random Forest regression pipeline with numeric imputation and categorical one-hot encoding.
4. Prediction: loads saved `joblib` artifacts and predicts prices for new vehicle inputs.
5. Apriori Mining: converts vehicle records into transaction items and discovers frequent association rules.
6. Django Web UI: renders registration, execution steps, Maruti price questionnaire, research-paper page, and Apriori results.
7. Database Logging: stores student registrations and execution-log entries in SQLite.

## Input Data

The local `datasets/` folder contains Cardekho, cleaned used-car, ANN car sales, 2025 car-price, and Maruti Suzuki Khammam data files. The default training key is `cardekho-depreciation` because it includes both present price and selling price.

## Output

- Trained model: `Source Code/artifacts/car_price_model.joblib`
- Metrics: `Source Code/artifacts/metrics.json`
- Normalized sample: `Source Code/artifacts/normalized_sample.csv`
- Apriori rules rendered on the Django page
- Student registration and execution logs stored in `db.sqlite3`

## Algorithm Notes

The implementation uses Random Forest regression for robust nonlinear prediction. The project title references K-Radius Nearest Neighbors as a conceptual local-neighborhood comparison idea; the runnable implementation supports vehicle-neighborhood reasoning through feature similarity, dataset segmentation, and Apriori attribute grouping.

## Security and Privacy

The project is designed for local student execution. It does not collect payments, upload files to external media services, or store cloud credentials.
