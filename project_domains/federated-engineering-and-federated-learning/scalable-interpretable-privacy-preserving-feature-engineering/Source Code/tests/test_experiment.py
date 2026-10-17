import unittest

import numpy as np

from federated_feature_engineering.experiment import (
    BASE_FEATURE_NAMES,
    FEATURE_NAMES,
    ExperimentConfig,
    _engineer_features,
    _partition_clients,
    run_experiment,
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
        sensitivity = 2.0 / first["data"]["train_samples"]
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


if __name__ == "__main__":
    unittest.main()
