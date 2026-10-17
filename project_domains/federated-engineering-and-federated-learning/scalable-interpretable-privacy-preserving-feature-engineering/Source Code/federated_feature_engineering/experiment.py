"""Synthetic horizontal-federated feature engineering and evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

BASE_FEATURE_NAMES = tuple(f"x{i}" for i in range(6))
SQUARED_FEATURE_INDICES = (0, 1, 3)
INTERACTION_FEATURE_PAIRS = ((0, 1), (1, 2), (2, 4), (4, 5))
FEATURE_NAMES = (
    *BASE_FEATURE_NAMES,
    *(f"x{i}^2" for i in SQUARED_FEATURE_INDICES),
    *(f"x{i}*x{j}" for i, j in INTERACTION_FEATURE_PAIRS),
)


@dataclass(frozen=True)
class ExperimentConfig:
    """Reproducibility and resource settings for one experiment."""

    samples: int = 1200
    clients: int = 4
    selected_features: int = 8
    rounds: int = 200
    learning_rate: float = 0.5
    epsilon: float = 1.0
    seed: int = 17
    test_fraction: float = 0.25

    def validate(self) -> None:
        if self.samples < 80:
            raise ValueError("samples must be at least 80.")
        if self.clients < 2 or self.clients > self.samples:
            raise ValueError("clients must be between 2 and samples.")
        if not 1 <= self.selected_features <= len(FEATURE_NAMES):
            raise ValueError(
                f"selected_features must be between 1 and {len(FEATURE_NAMES)}."
            )
        if self.rounds < 1:
            raise ValueError("rounds must be positive.")
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive.")
        if self.epsilon <= 0:
            raise ValueError("epsilon must be positive.")
        if not 0.1 <= self.test_fraction <= 0.5:
            raise ValueError("test_fraction must be between 0.1 and 0.5.")


def _make_synthetic_data(
    samples: int,
    seed: int,
) -> tuple[FloatArray, IntArray, IntArray]:
    rng = np.random.default_rng(seed)
    inputs = np.clip(rng.normal(size=(samples, len(BASE_FEATURE_NAMES))), -3.0, 3.0)
    protected_group = rng.integers(0, 2, size=samples, dtype=np.int64)
    logits = (
        1.25 * inputs[:, 0]
        + 1.0 * inputs[:, 1] * inputs[:, 2]
        - 0.9 * np.square(inputs[:, 3])
        + 0.45 * inputs[:, 4]
        - 0.35
    )
    probabilities = 1.0 / (1.0 + np.exp(-np.clip(logits, -30.0, 30.0)))
    labels = rng.binomial(1, probabilities).astype(np.int64)
    return inputs, labels, protected_group


def _engineer_features(inputs: FloatArray) -> FloatArray:
    """Build named, bounded candidates; protected attributes are not inputs."""
    columns: list[FloatArray] = [
        np.clip(inputs[:, index] / 3.0, -1.0, 1.0)
        for index in range(len(BASE_FEATURE_NAMES))
    ]
    columns.extend(
        np.square(inputs[:, index]) / 9.0
        for index in SQUARED_FEATURE_INDICES
    )
    columns.extend(
        inputs[:, left] * inputs[:, right] / 9.0
        for left, right in INTERACTION_FEATURE_PAIRS
    )
    return np.column_stack(columns).astype(np.float64, copy=False)


def _stratified_split(
    labels: IntArray,
    test_fraction: float,
    seed: int,
) -> tuple[IntArray, IntArray]:
    rng = np.random.default_rng(seed)
    train_parts: list[IntArray] = []
    test_parts: list[IntArray] = []
    for label in (0, 1):
        indices = np.flatnonzero(labels == label)
        if len(indices) < 2:
            raise ValueError("Synthetic data must contain both label classes.")
        rng.shuffle(indices)
        test_count = max(1, int(round(len(indices) * test_fraction)))
        test_parts.append(indices[:test_count])
        train_parts.append(indices[test_count:])
    train_indices = np.concatenate(train_parts)
    test_indices = np.concatenate(test_parts)
    rng.shuffle(train_indices)
    rng.shuffle(test_indices)
    return train_indices, test_indices


def _partition_clients(
    sample_count: int,
    clients: int,
    seed: int,
) -> list[IntArray]:
    if clients < 2 or clients > sample_count:
        raise ValueError("clients must be between 2 and the sample count.")
    indices = np.random.default_rng(seed).permutation(sample_count)
    partitions = [
        part.astype(np.int64, copy=False)
        for part in np.array_split(indices, clients)
    ]
    if any(len(part) == 0 for part in partitions):
        raise ValueError("Every simulated client must receive training samples.")
    return partitions


def _private_feature_ranking(
    features: FloatArray,
    labels: IntArray,
    epsilon: float,
    seed: int,
) -> tuple[FloatArray, float]:
    """Release bounded mean feature-label scores using one Laplace query."""
    centered_labels = (2 * labels - 1).astype(np.float64)
    raw_mean_scores = features.T @ centered_labels / len(labels)
    sensitivity = 2.0 / len(labels)
    noise = np.random.default_rng(seed).laplace(
        loc=0.0,
        scale=sensitivity / epsilon,
        size=features.shape[1],
    )
    return raw_mean_scores + noise, sensitivity / epsilon


def _client_gradient(features: FloatArray, labels: IntArray, weights: FloatArray) -> FloatArray:
    logits = np.clip(features @ weights[:-1] + weights[-1], -30.0, 30.0)
    probabilities = 1.0 / (1.0 + np.exp(-logits))
    errors = probabilities - labels
    weight_gradient = features.T @ errors / len(labels) + 1e-3 * weights[:-1]
    bias_gradient = np.array([errors.mean()], dtype=np.float64)
    return np.concatenate((weight_gradient, bias_gradient))


def _federated_fit(
    features: FloatArray,
    labels: IntArray,
    client_partitions: list[IntArray],
    rounds: int,
    learning_rate: float,
) -> FloatArray:
    """Apply weighted client gradients without transferring client records."""
    weights = np.zeros(features.shape[1] + 1, dtype=np.float64)
    train_count = len(labels)
    for _ in range(rounds):
        aggregate_gradient = np.zeros_like(weights)
        for indices in client_partitions:
            local_gradient = _client_gradient(
                features[indices],
                labels[indices],
                weights,
            )
            aggregate_gradient += len(indices) / train_count * local_gradient
        weights -= learning_rate * aggregate_gradient
    return weights


def _group_recall_gap(
    labels: IntArray,
    predictions: IntArray,
    groups: IntArray,
) -> float | None:
    recalls: list[float] = []
    for group in (0, 1):
        positive = (groups == group) & (labels == 1)
        if not np.any(positive):
            return None
        recalls.append(float(np.mean(predictions[positive] == 1)))
    return abs(recalls[0] - recalls[1])


def run_experiment(config: ExperimentConfig | None = None) -> dict[str, Any]:
    """Run a deterministic synthetic feature-selection and federated-fit study."""
    settings = config or ExperimentConfig()
    settings.validate()
    inputs, labels, groups = _make_synthetic_data(settings.samples, settings.seed)
    train_indices, test_indices = _stratified_split(
        labels,
        settings.test_fraction,
        settings.seed + 1,
    )
    all_features = _engineer_features(inputs)
    train_features = all_features[train_indices]
    train_labels = labels[train_indices]
    client_partitions = _partition_clients(
        len(train_indices),
        settings.clients,
        settings.seed + 2,
    )
    noisy_scores, laplace_scale = _private_feature_ranking(
        train_features,
        train_labels,
        settings.epsilon,
        settings.seed + 3,
    )
    selected_indices = np.argsort(-np.abs(noisy_scores), kind="stable")[
        :settings.selected_features
    ]
    selected_train = train_features[:, selected_indices]
    weights = _federated_fit(
        selected_train,
        train_labels,
        client_partitions,
        settings.rounds,
        settings.learning_rate,
    )

    test_features = all_features[test_indices][:, selected_indices]
    logits = np.clip(test_features @ weights[:-1] + weights[-1], -30.0, 30.0)
    probabilities = 1.0 / (1.0 + np.exp(-logits))
    predictions = (probabilities >= 0.5).astype(np.int64)
    test_labels = labels[test_indices]
    test_groups = groups[test_indices]

    return {
        "experiment": "synthetic-horizontal-federated-feature-engineering",
        "config": asdict(settings),
        "data": {
            "kind": "synthetic",
            "train_samples": int(len(train_indices)),
            "test_samples": int(len(test_indices)),
            "client_samples": [int(len(indices)) for indices in client_partitions],
            "raw_feature_count": len(BASE_FEATURE_NAMES),
            "candidate_feature_count": len(FEATURE_NAMES),
        },
        "privacy": {
            "feature_selection_mechanism": "Laplace mechanism on bounded feature-label mean scores",
            "adjacency": "replace-one training record",
            "epsilon": settings.epsilon,
            "delta": 0.0,
            "sensitivity": 2.0 / len(train_indices),
            "laplace_scale": laplace_scale,
            "scope": (
                "The guarantee applies only to the feature-selection score release. "
                "Model gradients and final model are not differentially private."
            ),
        },
        "federation": {
            "layout": "horizontal",
            "clients": settings.clients,
            "training": "weighted full-batch gradient aggregation in one process",
            "raw_records_shared": False,
            "secure_aggregation": False,
        },
        "selected_features": [
            {
                "name": FEATURE_NAMES[index],
                "private_score": float(noisy_scores[index]),
                "coefficient": float(weights[position]),
            }
            for position, index in enumerate(selected_indices)
        ],
        "metrics": {
            "accuracy": float(accuracy_score(test_labels, predictions)),
            "precision": float(
                precision_score(test_labels, predictions, zero_division=0)
            ),
            "recall": float(recall_score(test_labels, predictions, zero_division=0)),
            "f1": float(f1_score(test_labels, predictions, zero_division=0)),
            "group_recall_gap": _group_recall_gap(
                test_labels,
                predictions,
                test_groups,
            ),
        },
        "limitations": [
            "Synthetic data is for method demonstration and does not establish real-world performance.",
            "The in-process clients do not provide network isolation or secure aggregation.",
            "Only the feature-selection score release has a stated differential-privacy guarantee.",
            "The group recall gap is descriptive and is not a fairness guarantee.",
        ],
    }
