"""Carga y validación de los artefactos de la etapa 1."""
import json
import pandas as pd
from .config import DESCRIPTIVE_DATA, LINEAGE_REPORT, PROCESSED_DATA, FEATURES, MAX_REGISTRATION_YEAR, MIN_REGISTRATION_YEAR

def load_modeling_data():
    if not PROCESSED_DATA.exists():
        raise FileNotFoundError("Falta el artefacto de modelado. Ejecute primero el notebook de etapa 1.")
    frame = pd.read_csv(PROCESSED_DATA, parse_dates=["DateCrawled", "DateCreated", "LastSeen"])
    missing = set(FEATURES + ["Price", "DateCrawled"]).difference(frame.columns)
    if missing or not frame["Price"].gt(0).all():
        raise ValueError(f"Artefacto de modelado inválido; faltan={sorted(missing)} o Price no elegible.")
    if "RegistrationYear" not in frame.columns:
        raise ValueError("El artefacto no contiene RegistrationYear para aplicar el alcance del MVP.")
    scoped = frame.loc[frame["RegistrationYear"].between(MIN_REGISTRATION_YEAR, MAX_REGISTRATION_YEAR)].copy()
    if scoped.empty:
        raise ValueError("La regla de años del MVP dejó la población vacía.")
    return scoped

def load_descriptive_data():
    return pd.read_csv(DESCRIPTIVE_DATA, parse_dates=["DateCrawled", "DateCreated", "LastSeen"])

def load_lineage():
    return json.loads(LINEAGE_REPORT.read_text(encoding="utf-8"))
