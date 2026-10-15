import unittest
import pandas as pd

from rusty_baregain_mvp.comparables import comparable_summary
from rusty_baregain_mvp.data import load_modeling_data
from rusty_baregain_mvp.model import load_estimator, load_metadata


class MvpIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_modeling_data()

    def test_scope_is_ordinary_used_cars(self):
        self.assertTrue(self.data.RegistrationYear.between(1991, 2016).all())
        self.assertTrue(self.data.Price.gt(0).all())

    def test_model_predicts_a_valid_profile(self):
        profile = self.data.iloc[[0]][["AgeAtCrawl", "PowerForModel", "Mileage", "VehicleType", "Gearbox", "Model", "FuelType", "Brand", "NotRepaired"]]
        prediction = load_estimator().predict(profile)
        self.assertEqual(len(prediction), 1)
        self.assertGreater(prediction[0], 0)

    def test_comparables_return_a_known_contract(self):
        row = self.data.iloc[0]
        profile = {key: row[key] for key in ["Brand", "Model", "VehicleType", "Gearbox", "FuelType", "NotRepaired", "AgeAtCrawl", "PowerForModel", "Mileage"]}
        result = comparable_summary(self.data, profile)
        self.assertIn(result["level"], {"exacta", "bandas", "sin cobertura"})

    def test_metadata_contains_recalibrated_metrics(self):
        metrics = load_metadata()["metrics"]
        self.assertGreater(metrics["mae_eur"], 0)
        self.assertGreater(metrics["interval_half_width_eur"], 0)


if __name__ == "__main__":
    unittest.main()
