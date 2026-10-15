"""Entrenamiento e inferencia del estimador histórico."""
from dataclasses import dataclass
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder
from .config import CATEGORICAL_FEATURES, FEATURES, INTERVAL_HALF_WIDTH_EUR, MODEL_METADATA, MODEL_PATH, NUMERIC_FEATURES

@dataclass
class PriceEstimator:
    numeric_imputer: SimpleImputer
    categorical_imputer: SimpleImputer
    encoder: OrdinalEncoder
    model: HistGradientBoostingRegressor
    def matrix(self, frame):
        return np.hstack([self.numeric_imputer.transform(frame[NUMERIC_FEATURES]), self.encoder.transform(self.categorical_imputer.transform(frame[CATEGORICAL_FEATURES]))])
    def predict(self, frame):
        missing = set(FEATURES).difference(frame.columns)
        if missing: raise ValueError(f"Faltan entradas: {sorted(missing)}")
        return self.model.predict(self.matrix(frame))

def train_estimator(frame, random_state=42):
    ni, ci = SimpleImputer(strategy="median"), SimpleImputer(strategy="most_frequent")
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    matrix = np.hstack([ni.fit_transform(frame[NUMERIC_FEATURES]), enc.fit_transform(ci.fit_transform(frame[CATEGORICAL_FEATURES]))])
    model = HistGradientBoostingRegressor(learning_rate=.08, max_iter=120, max_leaf_nodes=31, l2_regularization=1., early_stopping=True, validation_fraction=.1, categorical_features=[False]*3+[True]*6, random_state=random_state).fit(matrix, frame["Price"])
    return PriceEstimator(ni, ci, enc, model)

def evaluate_temporal(frame):
    days=np.sort(frame["DateCrawled"].dt.normalize().unique())
    cutoff=days[int(len(days)*.8)]
    train=frame.loc[frame.DateCrawled.dt.normalize()<cutoff].copy()
    test=frame.loc[frame.DateCrawled.dt.normalize()>=cutoff].copy()
    estimator=train_estimator(train)
    prediction=estimator.predict(test)
    # La cola temporal interna calibra incertidumbre sin usar el test para ajustarla.
    cal_cutoff=np.sort(train.DateCrawled.dt.normalize().unique())[-3]
    dev=train.loc[train.DateCrawled.dt.normalize()<cal_cutoff]
    calibration=train.loc[train.DateCrawled.dt.normalize()>=cal_cutoff]
    cal_model=train_estimator(dev)
    half_width=float(np.quantile(np.abs(cal_model.predict(calibration)-calibration.Price.to_numpy()), .90))
    coverage=float(((test.Price >= prediction-half_width) & (test.Price <= prediction+half_width)).mean())
    bands=pd.cut(test.Price,[0,1000,5000,10000,np.inf],include_lowest=True)
    segment=(pd.DataFrame({"rango":bands,"error":np.abs(test.Price.to_numpy()-prediction)}).groupby("rango",observed=True).error.agg(["size","mean"]).reset_index())
    error_by_price=[{"rango":str(row.rango),"n":int(row.size),"mae_eur":float(row.mean)} for row in segment.itertuples(index=False)]
    return {"mae_eur":float(mean_absolute_error(test.Price,prediction)),"rmse_eur":float(root_mean_squared_error(test.Price,prediction)),"interval_half_width_eur":half_width,"interval_coverage":coverage,"test_rows":len(test),"calibration_rows":len(calibration),"error_by_price":error_by_price}

def save_estimator(estimator, source_rows, metrics):
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(estimator, MODEL_PATH)
    MODEL_METADATA.write_text(json.dumps({"schema_version":"1.0","source_rows":source_rows,"features":FEATURES,"metrics":metrics,"model_note":"HGB; la UI exige entradas completas."}, ensure_ascii=False, indent=2), encoding="utf-8")

def load_estimator():
    if not MODEL_PATH.exists(): raise FileNotFoundError("No existe el modelo. Ejecute `python -m rusty_baregain_mvp.train`.")
    return joblib.load(MODEL_PATH)

def load_metadata():
    return json.loads(MODEL_METADATA.read_text(encoding="utf-8"))
