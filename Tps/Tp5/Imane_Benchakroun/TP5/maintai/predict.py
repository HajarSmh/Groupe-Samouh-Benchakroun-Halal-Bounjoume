"""Chargement du modèle sauvegardé et prédiction pour un relevé."""
import json
from dataclasses import dataclass

import joblib
import pandas as pd

from maintai.config import Settings


@dataclass
class Predictor:
    model: object
    features: list[str]
    threshold: float
    version: str

    @classmethod
    def load(cls, settings: Settings) -> "Predictor":
        """Lève FileNotFoundError si le modèle n'a pas encore été entraîné."""
        model = joblib.load(settings.model_path)
        info = json.loads(settings.info_path.read_text(encoding="utf-8"))
        return cls(
            model=model,
            features=info["features"],
            threshold=info["threshold"],
            version=info["trained_at"],
        )

    def predict(self, reading: dict) -> dict:
        # Mêmes colonnes, dans le même ordre qu'à l'entraînement
        X = pd.DataFrame([reading])[self.features]
        proba = float(self.model.predict_proba(X)[0, 1])
        return {
            "failure_probability": round(proba, 4),
            "alert": proba >= self.threshold,
            "threshold": self.threshold,
            "model_version": self.version,
        }
