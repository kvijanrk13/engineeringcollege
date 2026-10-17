# Federated feature engineering demonstrator

This standalone research demonstrator turns selected themes from the cited review into a reproducible, executable experiment. It generates synthetic data locally; it does not contain the published article, reviewer materials, or private source data.

## What it demonstrates

- A fixed, named feature library of bounded raw, squared, and pairwise-interaction features.
- Horizontal partitioning of training samples across simulated clients.
- Federated full-batch gradient aggregation without pooling or sending client rows.
- Interpretable feature selection using a single record-level Laplace mechanism.
- Holdout accuracy, precision, recall, F1, and protected-group recall-gap reporting.

The privacy guarantee applies **only** to the feature-selection score release: for replace-one adjacency and the bounded per-record score in this implementation, its sensitivity is `2 / n_train` and its Laplace scale is `2 / (n_train * epsilon)`. Model gradients and the final model are not differentially private. This is an in-process simulation, not secure aggregation or a production federated-learning deployment. Group metrics are diagnostic only and do not guarantee fairness.

## Run

Requires Python 3.10 or later.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m federated_feature_engineering.cli --output results/example_run.json
```

The command prints a JSON report and writes the same report to the requested output path. Re-run with the same seed to reproduce the result. Change `--epsilon`, `--clients`, `--samples`, or `--seed` to inspect the experiment settings.

On the Engineering College project page, select the **Execute** tab, configure the generated sample count, client count, selected feature count, privacy epsilon, and random seed, then choose **Run Experiment**. The page displays model-quality cards, selected-feature coefficients, experiment settings, and privacy limitations, with the complete JSON available as a detail. Inputs are bounded by the server and no uploaded data or user-provided code is executed.

Run the tests with:

```powershell
python -m unittest discover -s tests -v
```

## Project layout

- `federated_feature_engineering/experiment.py`: synthetic data, feature library, private ranking, simulated clients, federated optimization, and metrics.
- `federated_feature_engineering/cli.py`: command-line entry point and JSON report.
- `tests/`: deterministic and boundary tests.
- `Documentation/PROJECT_DESIGN.md`: experiment assumptions, limitations, and interpretation notes.

## Citation

Vijay Kumar Kambhampati and K. B. V. Brahma Rao. “Scalable, interpretable, and privacy-preserving feature engineering for federated learning: a systematic literature review.” *Evolving Systems* 17, 92 (2026). https://doi.org/10.1007/s12530-026-09852-8

The citation is provided for context. This software is an independently written demonstrator and does not reproduce or redistribute the publisher's article.
