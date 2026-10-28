"""Entraîne chaque modèle candidat, l'évalue sur le jeu de test et les compare.

Usage, depuis la racine du projet : python -m monprojet.train
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from monprojet import config
from monprojet.data import load_data, split
from monprojet.models import candidates

HIGHER_IS_BETTER = {"accuracy": True, "recall": True, "precision": True, "f1": True,
                    "mae": False, "rmse": False, "r2": True}


def build_preprocessing(X: pd.DataFrame) -> ColumnTransformer:
    """Prépare les colonnes : nombres mis à l'échelle, catégories encodées, texte vectorisé. (Fournie.)"""
    text = [config.TEXT_COLUMN] if config.TEXT_COLUMN else []
    numeric = [c for c in X.columns if c not in text and pd.api.types.is_numeric_dtype(X[c])]
    categorical = [c for c in X.columns if c not in text and c not in numeric]
    steps = []
    if numeric:
        steps.append(("nombres", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric))
    if categorical:
        steps.append(("categories", make_pipeline(SimpleImputer(strategy="most_frequent"),
                                                  OneHotEncoder(handle_unknown="ignore")), categorical))
    if text:
        steps.append(("texte", TfidfVectorizer(), config.TEXT_COLUMN))
    return ColumnTransformer(steps, sparse_threshold=0)


def evaluate(model, X_test, y_test) -> dict:
    """Prédit sur le jeu de test et renvoie un dictionnaire {nom de la métrique: valeur}."""
    y_pred = model.predict(X_test)

    if config.TASK == "classification":
        average = "binary" if y_test.nunique() == 2 else "macro"
        scores = {
            "accuracy": accuracy_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred, average=average, zero_division=0),
            "precision": precision_score(y_test, y_pred, average=average, zero_division=0),
            "f1": f1_score(y_test, y_pred, average=average, zero_division=0),
        }
    else:
        scores = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

    return {nom: round(float(valeur), 3) for nom, valeur in scores.items()}


def main() -> None:
    """Entraîne chaque candidat, l'évalue, compare, et sauvegarde."""
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)

    resultats = {}
    modeles = {}
    for nom, estimateur in candidates().items():
        model = Pipeline([
            ("preparation", build_preprocessing(X_train)),
            ("modele", estimateur),
        ])
        model.fit(X_train, y_train)
        resultats[nom] = evaluate(model, X_test, y_test)
        modeles[nom] = model

    # Tableau de comparaison, trié selon la métrique principale
    higher = HIGHER_IS_BETTER[config.MAIN_METRIC]
    tableau = pd.DataFrame(resultats).T.sort_values(config.MAIN_METRIC, ascending=not higher)
    print(tableau)

    # Le meilleur modèle est la première ligne du tableau trié
    meilleur = tableau.index[0]

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(modeles[meilleur], config.MODELS_DIR / "model.joblib")

    sortie = {
        "main_metric": config.MAIN_METRIC,
        "best": meilleur,
        "results": resultats,
    }
    with open(config.MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(sortie, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
