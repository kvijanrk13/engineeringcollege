from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import pandas as pd

from dataset_loader import available_datasets, normalize_dataset


def band_price(series: pd.Series, value: float) -> str:
    low = series.quantile(0.33)
    high = series.quantile(0.66)
    if value <= low:
        return "Low"
    if value <= high:
        return "Medium"
    return "High"


def band_kilometers(value: float) -> str:
    if pd.isna(value):
        return "Unknown"
    if value <= 30000:
        return "Low KM"
    if value <= 80000:
        return "Medium KM"
    return "High KM"


def make_transactions(data: pd.DataFrame) -> list[frozenset[str]]:
    price_series = data["target_price"].dropna()
    transactions = []
    for _, row in data.iterrows():
        depreciation = row.get("depreciation_percent")
        items = {
            f"Price={band_price(price_series, row['target_price'])}",
            f"Age={'Newer' if row['vehicle_age'] <= 5 else 'Mid Age' if row['vehicle_age'] <= 10 else 'Older'}",
            f"Kilometers={band_kilometers(row['mileage'])}",
            f"Fuel={row.get('fuel_type') or 'Unknown'}",
            f"Transmission={row.get('transmission') or 'Unknown'}",
            f"Seller={row.get('seller_type') or 'Unknown'}",
            f"Owner={row.get('owner') or 'Unknown'}",
        }
        if pd.notna(depreciation):
            items.add(
                "Depreciation="
                + ("Low" if depreciation <= 25 else "Medium" if depreciation <= 55 else "High")
            )
        transactions.append(frozenset(items))
    return transactions


def apriori_rules(
    transactions: list[frozenset[str]],
    min_support: float,
    min_confidence: float,
) -> list[dict]:
    total = len(transactions)
    item_counts: dict[str, int] = {}
    pair_counts: dict[frozenset[str], int] = {}

    for transaction in transactions:
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1
        for pair in itertools.combinations(sorted(transaction), 2):
            key = frozenset(pair)
            pair_counts[key] = pair_counts.get(key, 0) + 1

    rules = []
    for pair, count in pair_counts.items():
        support = count / total
        if support < min_support:
            continue
        first, second = tuple(pair)
        for antecedent, consequent in ((first, second), (second, first)):
            if not consequent.startswith(("Price=", "Depreciation=")):
                continue
            confidence = count / item_counts[antecedent]
            if confidence < min_confidence:
                continue
            consequent_support = item_counts[consequent] / total
            rules.append(
                {
                    "if": antecedent,
                    "then": consequent,
                    "support_percent": round(support * 100, 2),
                    "confidence_percent": round(confidence * 100, 2),
                    "lift": round(confidence / consequent_support, 2),
                }
            )
    return sorted(rules, key=lambda rule: (rule["lift"], rule["confidence_percent"]), reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Apriori association-rule analysis.")
    parser.add_argument("--dataset", choices=available_datasets(), default="cardekho-depreciation")
    parser.add_argument("--min-support", type=float, default=0.08)
    parser.add_argument("--min-confidence", type=float, default=0.45)
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()

    data = normalize_dataset(args.dataset)
    transactions = make_transactions(data)
    rules = apriori_rules(transactions, args.min_support, args.min_confidence)
    output = {
        "dataset": args.dataset,
        "rows": len(data),
        "min_support": args.min_support,
        "min_confidence": args.min_confidence,
        "rules": rules[:25],
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "apriori_rules.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
