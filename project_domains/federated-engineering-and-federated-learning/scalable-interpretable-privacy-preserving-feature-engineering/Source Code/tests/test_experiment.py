import unittest

import numpy as np

from federated_feature_engineering.experiment import (
    BASE_FEATURE_NAMES,
    FEATURE_NAMES,
    ExperimentConfig,
    _engineer_features,
    _make_synthetic_data,
    _partition_clients,
    predict_record,
    run_experiment,
    run_dataset_experiment,
)


class FeatureEngineeringTests(unittest.TestCase):
    def test_feature_library_is_named_bounded_and_excludes_group(self):
        inputs = np.array(
            [
                [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0],
                [3.0, 2.0, 1.0, -1.0, -2.0, -3.0],
            ]
        )

        transformed = _engineer_features(inputs)

        self.assertEqual(transformed.shape, (2, len(FEATURE_NAMES)))
        self.assertEqual(len(BASE_FEATURE_NAMES), 6)
        self.assertTrue(np.all(np.isfinite(transformed)))
        self.assertTrue(np.all(np.abs(transformed) <= 1.0))
        self.assertFalse(any("group" in name for name in FEATURE_NAMES))

    def test_client_partition_covers_each_training_record_once(self):
        partitions = _partition_clients(sample_count=103, clients=4, seed=9)
        combined = np.concatenate(partitions)

        self.assertEqual(sorted(combined.tolist()), list(range(103)))
        self.assertEqual([len(part) for part in partitions], [26, 26, 26, 25])

    def test_experiment_is_reproducible_and_reports_scope(self):
        config = ExperimentConfig(samples=400, rounds=80, seed=21)

        first = run_experiment(config)
        second = run_experiment(config)

        self.assertEqual(first, second)
        self.assertEqual(first["data"]["kind"], "synthetic")
        self.assertFalse(first["federation"]["raw_records_shared"])
        self.assertFalse(first["federation"]["secure_aggregation"])
        self.assertIn("only", first["privacy"]["scope"])
        sensitivity = (
            2.0 * len(FEATURE_NAMES) / first["data"]["train_samples"]
        )
        self.assertAlmostEqual(first["privacy"]["sensitivity"], sensitivity)
        self.assertAlmostEqual(
            first["privacy"]["laplace_scale"],
            sensitivity / config.epsilon,
        )
        self.assertEqual(len(first["selected_features"]), config.selected_features)
        self.assertTrue(0.0 <= first["metrics"]["accuracy"] <= 1.0)
        self.assertTrue(
            0.0 <= first["metrics"]["group_recall_gap"] <= 1.0
        )

    def test_invalid_experiment_settings_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "epsilon must be positive"):
            run_experiment(ExperimentConfig(epsilon=0))

        with self.assertRaisesRegex(ValueError, "clients must be"):
            run_experiment(ExperimentConfig(clients=1))

    def test_labeled_csv_data_runs_through_federated_pipeline(self):
        inputs, labels, groups = _make_synthetic_data(400, 31)
        config = ExperimentConfig(samples=400, clients=3, seed=12)

        report = run_dataset_experiment(inputs, labels, groups, config)

        self.assertEqual(report["data"]["kind"], "uploaded_csv")
        self.assertEqual(report["data"]["total_samples"], 400)
        self.assertEqual(report["federation"]["clients"], 3)
        self.assertIsNotNone(report["metrics"]["group_recall_gap"])
        self.assertEqual(len(report["selected_features"]), config.selected_features)

    def test_labeled_csv_can_omit_protected_group(self):
        inputs, labels, _groups = _make_synthetic_data(200, 35)

        report = run_dataset_experiment(
            inputs,
            labels,
            config=ExperimentConfig(samples=200),
        )

        self.assertIsNone(report["metrics"]["group_recall_gap"])
        self.assertEqual(report["data"]["kind"], "uploaded_csv")

    def test_dataset_requires_valid_features_labels_and_groups(self):
        inputs, labels, groups = _make_synthetic_data(200, 32)
        config = ExperimentConfig(samples=200)

        with self.assertRaisesRegex(ValueError, "six feature columns"):
            run_dataset_experiment(inputs[:, :5], labels, config=config)
        invalid_labels = labels.astype(float)
        invalid_labels[0] = 0.5
        with self.assertRaisesRegex(ValueError, "Labels must be binary"):
            run_dataset_experiment(inputs, invalid_labels, config=config)
        invalid_groups = groups.copy()
        invalid_groups[0] = 2
        with self.assertRaisesRegex(ValueError, "Protected groups"):
            run_dataset_experiment(inputs, labels, invalid_groups, config)

    def test_single_record_prediction_returns_probability_and_feature_values(self):
        config = ExperimentConfig(samples=400, seed=27)

        report = predict_record(np.array([0.2, -0.4, 0.5, 1.0, -1.2, 0.0]), config)

        self.assertEqual(
            report["experiment"],
            "single-record-prediction-with-synthetic-training",
        )
        self.assertIn(report["prediction"]["label"], (0, 1))
        self.assertTrue(0.0 <= report["prediction"]["positive_probability"] <= 1.0)
        self.assertEqual(report["prediction"]["input_features"]["x3"], 1.0)
        self.assertEqual(report["prediction"]["training_data"], "synthetic")


if __name__ == "__main__":
    unittest.main()
