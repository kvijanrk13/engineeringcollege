from __future__ import annotations

import tempfile
from pathlib import Path

from django.test import TestCase
from django.urls import reverse

from dataset_loader import available_datasets, normalize_dataset
from predict_price import predict
from train_model import build_pipeline, train


class CarPriceProjectTests(TestCase):
    def test_dataset_registry_contains_default_dataset(self):
        self.assertIn("cardekho-depreciation", available_datasets())

    def test_normalized_dataset_contains_required_columns(self):
        data = normalize_dataset("cardekho-depreciation")

        self.assertFalse(data.empty)
        for column in ["vehicle_age", "mileage", "fuel_type", "transmission", "target_price"]:
            self.assertIn(column, data.columns)

    def test_training_pipeline_can_be_constructed(self):
        pipeline = build_pipeline()

        self.assertIn("preprocessor", pipeline.named_steps)
        self.assertIn("model", pipeline.named_steps)

    def test_train_and_predict_with_temporary_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            metrics = train("cardekho-depreciation", output_dir)
            price = predict(
                output_dir / "car_price_model.joblib",
                {
                    "year": 2018,
                    "vehicle_age": 8,
                    "mileage": 45000,
                    "engine_size": 1.5,
                    "original_price": 8.5,
                    "make": "Honda",
                    "model": "City",
                    "fuel_type": "Petrol",
                    "transmission": "Manual",
                    "owner": "0",
                    "seller_type": "Dealer",
                    "condition": "Good",
                },
            )

        self.assertGreater(metrics["rows"], 0)
        self.assertIsInstance(price, float)

    def test_registration_page_loads(self):
        response = self.client.get(reverse("registration"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Used Car Price Prediction")

    def test_apriori_page_loads(self):
        response = self.client.get(reverse("apriori-execution"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apriori")
