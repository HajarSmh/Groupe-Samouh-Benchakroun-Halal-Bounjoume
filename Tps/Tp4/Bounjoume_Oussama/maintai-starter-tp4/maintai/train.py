"""Entraîne le modèle, le compare à la baseline et sauvegarde les artefacts.

Usage : python -m maintai.train
"""
import json
from datetime import datetime, timezone

import joblib
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from maintai.config import FEATURES, TARGET, Settings, get_settings
from maintai.data import load_data, split


def build_model() -> Pipeline:
    """Le prétraitement fait partie du modèle : scaler et classifieur sont sauvegardés ensemble."""
    return Pipeline([
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000)),
    ])


def evaluate(model, X_test, y_test, threshold: float) -> dict:
    """Mesure le modèle au seuil de décision choisi, et non au seuil 0,5 par défaut."""
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y_test, pred)), 3),
        "recall": round(float(recall_score(y_test, pred)), 3),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 3),
        "threshold": threshold,
    }


def evaluate_baseline(X_train, y_train, X_test, y_test) -> dict:
    """La méthode la plus simple : toujours prédire la classe majoritaire (« pas de panne »)."""
    baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    pred = baseline.predict(X_test)
    return {
        "accuracy": round(float(accuracy_score(y_test, pred)), 3),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 3),
    }


def save(model, metrics: dict, settings: Settings) -> None:
    """Écrit le modèle, son contrat d'entrée (model_info.json) et ses métriques."""
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, settings.model_path)
    info = {
        "features": FEATURES,
        "target": TARGET,
        "threshold": settings.threshold,
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sklearn_version": sklearn.__version__,
    }
    settings.info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    settings.metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def main() -> dict:
    settings = get_settings()
    df = load_data(settings.data_path)
    X_train, X_test, y_train, y_test = split(df)
    model = build_model().fit(X_train, y_train)
    metrics = {
        "model": evaluate(model, X_test, y_test, settings.threshold),
        "baseline": evaluate_baseline(X_train, y_train, X_test, y_test),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    save(model, metrics, settings)
    print(json.dumps(metrics, indent=2))
    print(f"Modèle sauvegardé dans {settings.model_path}")
    return metrics


if __name__ == "__main__":
    main()
