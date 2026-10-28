"""Les modèles à comparer.

À vous d'écrire candidates(). Les tests de tests/test_models.py disent ce qui est attendu.
"""
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import (GradientBoostingRegressor, RandomForestClassifier,
                              RandomForestRegressor)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from monprojet import config


def candidates() -> dict:
    """Renvoie un dictionnaire {nom: modèle scikit-learn non entraîné}.

    - le PREMIER modèle est la baseline (le plus simple possible) ;
    - ensuite, trois vrais modèles adaptés à config.TASK ;
    - random_state=config.SEED pour les modèles qui ont du hasard.
    """
    if config.TASK == "classification":
        return {
            "baseline": DummyClassifier(strategy="most_frequent"),
            "regression_logistique": LogisticRegression(
                max_iter=1000, class_weight="balanced", random_state=config.SEED
            ),
            "arbre": DecisionTreeClassifier(
                max_depth=5, class_weight="balanced", random_state=config.SEED
            ),
            "foret_aleatoire": RandomForestClassifier(
                n_estimators=200, class_weight="balanced", random_state=config.SEED
            ),
        }

    if config.TASK == "regression":
        return {
            "baseline": DummyRegressor(strategy="mean"),
            "regression_lineaire": LinearRegression(),
            "foret_aleatoire": RandomForestRegressor(
                n_estimators=200, random_state=config.SEED
            ),
            "gradient_boosting": GradientBoostingRegressor(random_state=config.SEED),
        }

    raise ValueError(
        f"TASK inconnue : '{config.TASK}'. Utilisez 'classification' ou 'regression'."
    )