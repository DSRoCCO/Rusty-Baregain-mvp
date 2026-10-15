from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA = ROOT / "data" / "processed" / "rusty_baregain_modeling_base.csv"
DESCRIPTIVE_DATA = ROOT / "data" / "processed" / "rusty_baregain_descriptive.csv"
LINEAGE_REPORT = ROOT / "reports" / "rusty_baregain_data_lineage.json"
MODEL_PATH = ROOT / "models" / "price_estimator.joblib"
MODEL_METADATA = ROOT / "models" / "price_estimator_metadata.json"
NUMERIC_FEATURES = ["AgeAtCrawl", "PowerForModel", "Mileage"]
CATEGORICAL_FEATURES = ["VehicleType", "Gearbox", "Model", "FuelType", "Brand", "NotRepaired"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
# Referencia de respaldo; la interfaz lee el valor recalibrado del metadato.
INTERVAL_HALF_WIDTH_EUR = 2277.25392234241
REFERENCE_YEAR = 2016
MIN_REGISTRATION_YEAR = 1991
MAX_REGISTRATION_YEAR = 2016
