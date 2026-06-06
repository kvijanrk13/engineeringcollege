from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DATASETS_DIR = PROJECT_DIR.parents[1] / "datasets"


DATASET_FILES = {
    "cardekho-depreciation": DATASETS_DIR / "vehicle-dataset-from-cardekho" / "car data.csv",
    "cardekho-v3": DATASETS_DIR / "vehicle-dataset-from-cardekho" / "Car details v3.csv",
    "cardekho-v4": DATASETS_DIR / "vehicle-dataset-from-cardekho" / "car details v4.csv",
    "used-cars-large": DATASETS_DIR / "used-car-prediction-dataset" / "used_cars.csv",
    "used-car-cleaned": DATASETS_DIR / "used-car-price-prediction-dataset-cleaned" / "used_car_cleaned.csv",
    "car-price-2025": DATASETS_DIR / "car-price-prediction-2025" / "car_price_prediction_.csv",
    "ann-car-sales": DATASETS_DIR / "ann-car-sales-price-prediction" / "car_purchasing.csv",
}


def available_datasets() -> list[str]:
    return sorted(DATASET_FILES)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="ISO-8859-1")


def numeric_series(values: pd.Series) -> pd.Series:
    cleaned = (
        values.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)", expand=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def first_existing(df: pd.DataFrame, names: list[str]) -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([np.nan] * len(df), index=df.index)


def normalize_dataset(dataset_key: str) -> pd.DataFrame:
    raw = read_csv(DATASET_FILES[dataset_key])
    df = raw.copy()

    year = numeric_series(first_existing(df, ["Year", "year", "model_year"]))
    current_year = pd.Timestamp.today().year
    vehicle_age = (current_year - year).clip(lower=0)

    mileage = numeric_series(
        first_existing(df, ["Mileage", "mileage", "milage", "Kms_Driven", "km_driven", "Kilometer"])
    )
    if dataset_key == "used-car-cleaned":
        mileage = mileage * 1.60934

    target_price = numeric_series(
        first_existing(df, ["Selling_Price", "selling_price", "Price", "price", "car purchase amount"])
    )
    original_price = numeric_series(first_existing(df, ["Present_Price"]))

    make = first_existing(df, ["Make", "Brand", "brand"])
    model = first_existing(df, ["Model", "model", "name", "Car_Name"])
    if make.isna().all() and "Car_Name" in df.columns:
        make = df["Car_Name"].astype(str).str.split().str[0]

    normalized = pd.DataFrame(
        {
            "dataset_key": dataset_key,
            "make": make.astype(str).replace("nan", np.nan),
            "model": model.astype(str).replace("nan", np.nan),
            "year": year,
            "vehicle_age": vehicle_age,
            "mileage": mileage,
            "fuel_type": first_existing(df, ["Fuel_Type", "fuel", "fuelType", "Fuel Type", "fuel_type"]).astype(str),
            "transmission": first_existing(df, ["Transmission", "transmission"]).astype(str),
            "owner": first_existing(df, ["Owner", "owner"]).astype(str),
            "seller_type": first_existing(df, ["Seller_Type", "seller_type", "Seller Type"]).astype(str),
            "condition": first_existing(df, ["Condition", "condition"]).astype(str),
            "engine_size": numeric_series(first_existing(df, ["Engine Size", "engineSize", "engine_capacity", "engine", "Engine"])),
            "original_price": original_price,
            "target_price": target_price,
        }
    )

    normalized["depreciation_amount"] = normalized["original_price"] - normalized["target_price"]
    normalized["depreciation_percent"] = (
        normalized["depreciation_amount"] / normalized["original_price"].replace(0, np.nan)
    ) * 100
    text_columns = normalized.select_dtypes(include=["object"]).columns
    normalized[text_columns] = normalized[text_columns].mask(normalized[text_columns].isin(["nan", "NaN"]), np.nan)
    return normalized.dropna(subset=["target_price"])


def clean_feature_text(value: str) -> str:
    value = str(value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value if value and value.lower() != "nan" else "Unknown"
