"""Tests de l'évaluation et de la comparaison."""
import json

from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.pipeline import Pipeline

from monprojet import config
from monprojet.data import load_data, split
from monprojet.train import HIGHER_IS_BETTER, build_preprocessing, evaluate, main


def test_evaluate_renvoie_la_metrique_principale():
    X_train, X_test, y_train, y_test = split(load_data())
    dummy = DummyClassifier() if config.TASK == "classification" else DummyRegressor()
    model = Pipeline([("preparation", build_preprocessing(X_train)), ("modele", dummy)]).fit(X_train, y_train)
    scores = evaluate(model, X_test, y_test)
    assert isinstance(scores, dict), "evaluate() doit renvoyer un dictionnaire"
    assert config.MAIN_METRIC in scores, f"evaluate() doit contenir la métrique principale « {config.MAIN_METRIC} »"
    assert isinstance(scores[config.MAIN_METRIC], float)


def test_main_ecrit_les_resultats():
    main()
    metrics = json.loads((config.MODELS_DIR / "metrics.json").read_text(encoding="utf-8"))
    assert {"main_metric", "best", "results"} <= set(metrics), "metrics.json doit contenir main_metric, best et results"
    assert (config.MODELS_DIR / "model.joblib").exists(), "le meilleur modèle doit être sauvegardé dans model.joblib"


def test_le_meilleur_modele_bat_la_baseline():
    main()
    metrics = json.loads((config.MODELS_DIR / "metrics.json").read_text(encoding="utf-8"))
    results, metric = metrics["results"], metrics["main_metric"]
    baseline = results[next(iter(results))][metric]
    best = results[metrics["best"]][metric]
    assert best > baseline if HIGHER_IS_BETTER[metric] else best < baseline
