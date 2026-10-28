"""Chargement et découpage des données.

À vous d'écrire load_data() et split(). Les tests de tests/test_data.py disent ce qui est attendu.
"""
import pandas as pd
from sklearn.model_selection import train_test_split

from monprojet import config


def load_data(path=None) -> pd.DataFrame:
    """Lit le fichier CSV et renvoie un DataFrame.

    - lit config.DATA_PATH (ou `path` s'il est donné) ;
    - lève une ValueError si la colonne config.TARGET n'existe pas ;
    - retire les lignes où la cible est manquante.
    """
    df = pd.read_csv(path if path is not None else config.DATA_PATH)

    if config.TARGET not in df.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET}' est introuvable dans le fichier. "
            f"Colonnes disponibles : {list(df.columns)}"
        )

    return df.dropna(subset=[config.TARGET]).reset_index(drop=True)


def feature_columns(df: pd.DataFrame) -> list:
    """Les colonnes d'entrée : celles de config.FEATURES, ou toutes sauf la cible et la date. (Fournie.)"""
    if config.FEATURES is not None:
        return list(config.FEATURES)
    excluded = {config.TARGET, config.TIME_COLUMN}
    return [c for c in df.columns if c not in excluded]


def split(df: pd.DataFrame):
    """Renvoie X_train, X_test, y_train, y_test."""
    X = df[feature_columns(df)]
    y = df[config.TARGET]

    if config.SPLIT == "random":
        stratify = y if config.TASK == "classification" else None
        return train_test_split(
            X,
            y,
            test_size=config.TEST_SIZE,
            random_state=config.SEED,
            stratify=stratify,
        )

    if config.SPLIT == "chronologique":
        if config.TIME_COLUMN is None:
            raise ValueError(
                "config.TIME_COLUMN est obligatoire quand SPLIT = 'chronologique'."
            )
        # Tri du plus ancien au plus récent
        order = pd.to_datetime(df[config.TIME_COLUMN]).argsort().to_numpy()
        X = X.iloc[order]
        y = y.iloc[order]

        # Les lignes les plus récentes vont dans le jeu de test
        n_test = max(1, int(round(len(df) * config.TEST_SIZE)))
        n_train = len(df) - n_test
        return X.iloc[:n_train], X.iloc[n_train:], y.iloc[:n_train], y.iloc[n_train:]

    raise ValueError(
        f"SPLIT inconnu : '{config.SPLIT}'. Utilisez 'random' ou 'chronologique'."
    )