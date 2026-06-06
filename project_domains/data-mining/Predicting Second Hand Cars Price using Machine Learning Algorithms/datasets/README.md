# Car Price Prediction Datasets

This folder stores Kaggle datasets collected for the Data Mining project:
`Predicting Prices of Second-Hand Cars and Depreciation`.

## Downloaded Sources

| Folder | Kaggle source | Main file(s) | Rows | Notes |
| --- | --- | --- | ---: | --- |
| `used-car-price-prediction-dataset-cleaned/` | https://www.kaggle.com/datasets/peacfl/used-car-price-prediction-dataset-cleaned | `used_car_cleaned.csv` | 3,918 | Cleaned used-car regression dataset with brand, model year, mileage, fuel, transmission, accident/title, engine fields, and price. License shown by Kaggle search as CC0 Public Domain. |
| `used-car-prediction-dataset/` | https://www.kaggle.com/datasets/harishkumardatalab/used-car-prediction-dataset | `used_cars.csv` | 99,187 | Large used-car dataset with model, year, price, transmission, mileage, fuel type, tax, mpg, engine size, and make. License shown by Kaggle search as CC0 Public Domain. |
| `vehicle-dataset-from-cardekho/` | https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho | `car data.csv`, `CAR DETAILS FROM CAR DEKHO.csv`, `Car details v3.csv`, `car details v4.csv` | 301 / 4,340 / 8,128 / 2,059 | Cardekho vehicle datasets with selling price, present price, kilometers driven, fuel, transmission, owner, engine, and power fields. |
| `ann-car-sales-price-prediction/` | https://www.kaggle.com/datasets/yashpaloswal/ann-car-sales-price-prediction | `car_purchasing.csv` | 500 | Car purchase amount dataset using customer demographics and financial features. Useful as a sales-price prediction baseline, not vehicle depreciation. |
| `car-price-prediction-2025/` | https://www.kaggle.com/datasets/aliiihussain/car-price-prediction | `car_price_prediction_.csv` | 2,500 | Newer car listing dataset with brand, year, engine size, fuel, transmission, mileage, condition, price, and model. |

The `.zip` archives are kept beside the extracted folders so the original Kaggle downloads remain available.

## Suggested Target Columns

- `price`, `Price`, `selling_price`, `Selling_Price`, or `car purchase amount`

## Suggested Depreciation Features

- Vehicle age from `Year` or `year`
- Usage from `Mileage`, `mileage`, `milage`, `Kms_Driven`, `km_driven`, or `Kilometer`
- Make/model from `Make`, `Brand`, `brand`, `model`, `Model`, or `Car_Name`
- Fuel and transmission fields
- Engine size, power, accident, title, owner, seller, and condition fields where available
