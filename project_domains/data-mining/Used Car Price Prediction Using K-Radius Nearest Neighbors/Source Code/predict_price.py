from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd


def predict(model_path: Path, values: dict) -> float:
    artifact = joblib.load(Path(model_path))
    current_year = pd.Timestamp.today().year
    year = float(values.get("year", current_year))
    row = pd.DataFrame(
        [
            {
                "make": values.get("make", "Unknown"),
                "model": values.get("model", "Unknown"),
                "year": year,
                "vehicle_age": values.get("vehicle_age", max(current_year - year, 0)),
                "mileage": values.get("mileage", 0),
                "fuel_type": values.get("fuel_type", values.get("fuel", "Petrol")),
                "transmission": values.get("transmission", "Manual"),
                "owner": values.get("owner", "Unknown"),
                "seller_type": values.get("seller_type", "Unknown"),
                "condition": values.get("condition", "Unknown"),
                "engine_size": values.get("engine_size", 1.2),
                "original_price": values.get("original_price", 0),
            }
        ]
    )
    return float(artifact["pipeline"].predict(row)[0])


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict the price of a second-hand car.")
    parser.add_argument("--model-path", default="artifacts/car_price_model.joblib")
    parser.add_argument("--year", type=float, required=True)
    parser.add_argument("--mileage", type=float, required=True)
    parser.add_argument("--fuel", default="Petrol")
    parser.add_argument("--transmission", default="Manual")
    parser.add_argument("--make", default="Unknown")
    parser.add_argument("--model", default="Unknown")
    parser.add_argument("--engine-size", type=float, default=1.2)
    parser.add_argument("--original-price", type=float, default=0)
    parser.add_argument("--owner", default="Unknown")
    parser.add_argument("--seller-type", default="Unknown")
    parser.add_argument("--condition", default="Unknown")
    args = parser.parse_args()

    predicted_price = predict(
        Path(args.model_path),
        {
            "make": args.make,
            "model": args.model,
            "year": args.year,
            "mileage": args.mileage,
            "fuel_type": args.fuel,
            "transmission": args.transmission,
            "owner": args.owner,
            "seller_type": args.seller_type,
            "condition": args.condition,
            "engine_size": args.engine_size,
            "original_price": args.original_price,
        },
    )
    print(f"Predicted price: {predicted_price:.2f}")
    if args.original_price > 0:
        depreciation = args.original_price - predicted_price
        depreciation_percent = depreciation / args.original_price * 100
        print(f"Estimated depreciation: {depreciation:.2f} ({depreciation_percent:.2f}%)")


if __name__ == "__main__":
    main()
