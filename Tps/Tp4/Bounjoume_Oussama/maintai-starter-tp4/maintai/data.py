"""Chargement et découpage des données."""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from maintai.config import FEATURES, SEED, TARGET


def load_data(path: Path) -> pd.DataFrame:
    """Charge le CSV et vérifie qu'il contient les colonnes attendues."""
    df = pd.read_csv(path)
    missing = set(FEATURES + [TARGET]) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {path} : {sorted(missing)}")
    return df


def split(df: pd.DataFrame, test_size: float = 0.2):
    """Sépare entraînement et test en gardant la même proportion de pannes (stratify)."""
    return train_test_split(
        df[FEATURES], df[TARGET], test_size=test_size, stratify=df[TARGET], random_state=SEED
    )
