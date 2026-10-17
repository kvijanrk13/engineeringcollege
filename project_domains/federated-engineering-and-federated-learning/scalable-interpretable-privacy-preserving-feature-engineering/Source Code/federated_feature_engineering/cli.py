"""Command-line entry point for the synthetic federated experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .experiment import ExperimentConfig, run_experiment


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
    report = run_experiment(config)
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
