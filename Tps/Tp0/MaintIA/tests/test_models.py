"""Tests des modèles candidats."""
from monprojet.models import candidates


def test_la_baseline_est_le_premier_modele():
    first = next(iter(candidates().values()))
    assert type(first).__name__ in ("DummyClassifier", "DummyRegressor"), \
        "le premier modèle doit être une baseline (DummyClassifier ou DummyRegressor)"


def test_au_moins_trois_modeles_en_plus_de_la_baseline():
    assert len(candidates()) >= 4
