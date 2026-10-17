# Federated feature engineering demonstrator

This standalone research demonstrator turns selected themes from the cited review into a reproducible, executable experiment. It generates synthetic data locally; it does not contain the published article, reviewer materials, or private source data.

## What it demonstrates

- A fixed, named feature library of bounded raw, squared, and pairwise-interaction features.
- Horizontal partitioning of training samples across simulated clients.
- Federated full-batch gradient aggregation without pooling or sending client rows.
- Interpretable feature selection using a single record-level Laplace mechanism.
- Holdout accuracy, precision, recall, F1, and protected-group recall-gap reporting.

The privacy guarantee applies **only** to the feature-selection score release. The complete vector contains 13 bounded feature-label mean scores; under replace-one adjacency its L1 sensitivity is `2 * 13 / n_train`, and the Laplace scale is `2 * 13 / (n_train * epsilon)`. Model gradients and the final model are not differentially private. This is an in-process simulation, not secure aggregation or a production federated-learning deployment. Group metrics are diagnostic only and do not guarantee fairness.

## Run

Requires Python 3.10 or later.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m federated_feature_engineering.cli --output results/example_run.json
```

The command prints a JSON report and writes the same report to the requested output path. Re-run with the same seed to reproduce the result. Change `--epsilon`, `--clients`, `--samples`, or `--seed` to inspect the experiment settings.

On the Engineering College project page, select the **Execute** tab and choose one of three modes:

- **Generate synthetic dataset and evaluate**: tune generated records, clients, selected features, epsilon, and seed.
- **Upload my labeled CSV dataset**: provide UTF-8 CSV with columns `x0,x1,x2,x3,x4,x5,label`; `protected_group` is optional. Features must be finite values from -3 to 3; `label` and optional `protected_group` must be 0 or 1. The upload is limited to 1 MB and 5,000 rows. [Download a synthetic sample CSV](../Test%20Cases/sample_training.csv).
- **Enter one record and predict**: type six feature values. A model is trained on synthetic data, then predicts the entered record; the entered record is not used in training.

Choose **Run Experiment** to process the selected input. Results include holdout metrics (where applicable), feature coefficients, privacy limitations, and a full JSON report. Uploaded records are processed in memory for the request and are not intentionally saved by the app. Do not upload sensitive or identifying data unless authorized.

The app executes only its fixed project code. It does not execute uploaded files as code. Its horizontal clients are simulated in one process, and only the feature-selection score release has a stated differential-privacy guarantee; training, model outputs, and metrics are not covered.

Run the tests with:

```powershell
python -m unittest discover -s tests -v
```

## Project layout

- `federated_feature_engineering/experiment.py`: data validation, synthetic and labeled-data modes, record prediction, feature library, private ranking, simulated clients, federated optimization, and metrics.
- `federated_feature_engineering/cli.py`: command-line entry point, GUI request processing, sample-data generation, and JSON report.
- `Test Cases/sample_training.csv`: reproducible synthetic example of the expected CSV format.
- `tests/`: deterministic and boundary tests.
- `Documentation/PROJECT_DESIGN.md`: experiment assumptions, limitations, and interpretation notes.

## Citation

Vijay Kumar Kambhampati and K. B. V. Brahma Rao. “Scalable, interpretable, and privacy-preserving feature engineering for federated learning: a systematic literature review.” *Evolving Systems* 17, 92 (2026). https://doi.org/10.1007/s12530-026-09852-8

The citation is provided for context. This software is an independently written demonstrator and does not reproduce or redistribute the publisher's article.
