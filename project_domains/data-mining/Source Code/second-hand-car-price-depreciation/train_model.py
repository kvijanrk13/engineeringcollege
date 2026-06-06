from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from dataset_loader import available_datasets, normalize_dataset


NUMERIC_FEATURES = ["year", "vehicle_age", "mileage", "engine_size", "original_price"]
CATEGORICAL_FEATURES = ["make", "model", "fuel_type", "transmission", "owner", "seller_type", "condition"]


def build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=3)),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        min_samples_leaf=2,
        n_jobs=-1,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def train(dataset_key: str, output_dir: Path) -> dict:
    data = normalize_dataset(dataset_key)
    for column in NUMERIC_FEATURES:
        if data[column].isna().all():
            data[column] = 0
    for column in CATEGORICAL_FEATURES:
        if data[column].isna().all():
            data[column] = "Unknown"
    features = data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    target = data["target_price"]

    test_size = 0.2 if len(data) >= 50 else 0.1
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=42,
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    metrics = {
        "dataset_key": dataset_key,
        "rows": int(len(data)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(math.sqrt(mean_squared_error(y_test, predictions))),
        "r2": float(r2_score(y_test, predictions)),
    }
    if data["depreciation_percent"].notna().any():
        metrics["average_depreciation_percent"] = float(data["depreciation_percent"].mean())

    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "dataset_key": dataset_key,
            "numeric_features": NUMERIC_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
        },
        output_dir / "car_price_model.joblib",
    )
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    data.head(25).to_csv(output_dir / "normalized_sample.csv", index=False)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a second-hand car price prediction model.")
    parser.add_argument("--dataset", choices=available_datasets(), default="cardekho-depreciation")
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()

    metrics = train(args.dataset, Path(args.output_dir))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
