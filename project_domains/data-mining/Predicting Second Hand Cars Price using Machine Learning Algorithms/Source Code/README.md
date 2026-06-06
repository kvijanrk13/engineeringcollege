# Second-Hand Car Price and Depreciation Prediction

This is a portable starter project for students to train machine learning models from the Kaggle car datasets stored in:

`../datasets/`

The default workflow trains a depreciation-focused model from the Cardekho `car data.csv` file because it contains both `Present_Price` and `Selling_Price`. Other datasets can be selected for ordinary used-car price prediction.

## Setup

```powershell
cd "project_domains\data-mining\Predicting Second Hand Cars Price using Machine Learning Algorithms\Source Code"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS/Linux:

```bash
cd "project_domains/data-mining/Predicting Second Hand Cars Price using Machine Learning Algorithms/Source Code"
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## Train

```powershell
.\.venv\Scripts\python.exe train_model.py --dataset cardekho-depreciation
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
- `predict_price.py`: loads the trained model and predicts a price from command-line inputs
- `requirements.txt`: minimal Python packages needed on a student laptop
