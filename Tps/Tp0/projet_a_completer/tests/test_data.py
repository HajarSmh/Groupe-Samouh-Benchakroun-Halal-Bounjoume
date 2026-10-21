"""Tests des données : chargement et découpage."""
import pandas as pd

from monprojet import config
from monprojet.data import load_data, split


def test_load_data_renvoie_un_tableau_avec_la_cible():
    df = load_data()
    assert isinstance(df, pd.DataFrame), "load_data() doit renvoyer un DataFrame pandas"
    assert len(df) > 0, "le fichier est vide"
    assert config.TARGET in df.columns, f"la colonne cible {config.TARGET} est absente"
    assert df[config.TARGET].notna().all(), "la cible ne doit pas contenir de valeurs manquantes"


def test_split_separe_entrainement_et_test():
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)
    assert len(X_train) == len(y_train) and len(X_test) == len(y_test)
    assert len(X_train) + len(X_test) == len(df), "toutes les lignes doivent être utilisées"
    assert abs(len(X_test) / len(df) - config.TEST_SIZE) < 0.02, "la taille du test doit suivre TEST_SIZE"
    assert set(X_train.index).isdisjoint(X_test.index), "une ligne ne peut pas être à la fois en entraînement et en test"
    assert config.TARGET not in X_train.columns, "la cible ne doit pas faire partie des variables d'entrée"


def test_split_chronologique_teste_sur_le_futur():
    if config.SPLIT != "chronologique":
        return                                   # rien à vérifier pour un découpage aléatoire
    df = load_data()
    X_train, X_test, _, _ = split(df)
    dates = pd.to_datetime(df[config.TIME_COLUMN])
    assert dates.loc[X_train.index].max() <= dates.loc[X_test.index].min(), \
        "en découpage chronologique, tout le test doit être postérieur à l'entraînement"
