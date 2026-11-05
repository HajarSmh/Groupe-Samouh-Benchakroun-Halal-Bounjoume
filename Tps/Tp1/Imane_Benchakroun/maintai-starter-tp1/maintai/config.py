"""Configuration du projet : chemins et paramètres, lus depuis l'environnement."""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Contrat d'entrée du modèle : noms et ordre des variables
FEATURES = ["temperature_c", "vibration_mm_s", "load_pct", "runtime_hours"]
TARGET = "failure"
SEED = 42


@dataclass(frozen=True)
class Settings:
    data_path: Path
    models_dir: Path
    threshold: float

    @property
    def model_path(self) -> Path:
        return self.models_dir / "model.joblib"

    @property
    def info_path(self) -> Path:
        return self.models_dir / "model_info.json"

    @property
    def metrics_path(self) -> Path:
        return self.models_dir / "metrics.json"


def get_settings() -> Settings:
    """Lit la configuration à chaque appel, pour que les tests puissent la modifier."""
    return Settings(
        data_path=Path(os.getenv("MAINTAI_DATA_PATH", str(ROOT / "data" / "sensors.csv"))),
        models_dir=Path(os.getenv("MAINTAI_MODELS_DIR", str(ROOT / "models"))),
        threshold=float(os.getenv("MAINTAI_THRESHOLD", "0.3")),
    )
