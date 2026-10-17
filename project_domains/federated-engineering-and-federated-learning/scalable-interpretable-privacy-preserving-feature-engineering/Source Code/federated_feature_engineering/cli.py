"""Command-line entry point for the synthetic federated experiment."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Sequence

import numpy as np

from .experiment import (
    ExperimentConfig,
    _make_synthetic_data,
    predict_record,
    run_dataset_experiment,
    run_experiment,
)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the synthetic federated feature-engineering demonstrator."
    )
    parser.add_argument("--samples", type=int, default=1200)
    parser.add_argument("--clients", type=int, default=4)
    parser.add_argument("--selected-features", type=int, default=8)
    parser.add_argument("--rounds", type=int, default=200)
    parser.add_argument("--learning-rate", type=float, default=0.5)
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--request-json-stdin",
        action="store_true",
        help="Read one validated GUI request as JSON from standard input.",
    )
    parser.add_argument(
        "--export-synthetic-csv",
        type=Path,
        help="Write a generated labeled sample dataset to this path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for writing the JSON experiment report.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    config = ExperimentConfig(
        samples=args.samples,
        clients=args.clients,
        selected_features=args.selected_features,
        rounds=args.rounds,
        learning_rate=args.learning_rate,
        epsilon=args.epsilon,
        seed=args.seed,
    )
    if args.export_synthetic_csv is not None:
        inputs, labels, groups = _make_synthetic_data(config.samples, config.seed)
        args.export_synthetic_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.export_synthetic_csv.open('w', newline='', encoding='utf-8') as output:
            writer = csv.writer(output)
            writer.writerow([*(f"x{index}" for index in range(6)), "label", "protected_group"])
            for features, label, group in zip(inputs, labels, groups):
                writer.writerow([*(f"{value:.6f}" for value in features), int(label), int(group)])
        return 0

    if args.request_json_stdin:
        request_data = json.load(sys.stdin)
        request_settings = request_data.get("settings", {})
        if request_settings:
            config = ExperimentConfig(
                samples=request_settings["samples"],
                clients=request_settings["clients"],
                selected_features=request_settings["selected_features"],
                epsilon=request_settings["epsilon"],
                seed=request_settings["seed"],
            )
        mode = request_data.get("mode")
        if mode == "record":
            report = predict_record(
                np.asarray(request_data["features"], dtype=np.float64),
                config,
            )
        elif mode == "uploaded_csv":
            report = run_dataset_experiment(
                np.asarray(request_data["features"], dtype=np.float64),
                np.asarray(request_data["labels"], dtype=np.int64),
                (
                    np.asarray(request_data["groups"], dtype=np.int64)
                    if request_data.get("groups") is not None
                    else None
                ),
                config,
            )
        else:
            raise ValueError("Unsupported GUI execution mode.")
    else:
        report = run_experiment(config)
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
