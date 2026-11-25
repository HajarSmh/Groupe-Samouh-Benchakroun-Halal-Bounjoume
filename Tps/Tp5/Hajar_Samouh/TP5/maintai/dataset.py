"""Génère un jeu de données synthétique de capteurs.

Les données sont inventées pour que le projet fonctionne sans téléchargement.
Remplacez-les par des données réelles en gardant les mêmes colonnes.

Usage : python -m maintai.dataset
        python -m maintai.dataset --n 8000 --seed 7     (une autre version des données)
"""
import argparse
import sys

import numpy as np
import pandas as pd

from maintai.config import SEED, get_settings


def make_dataset(n: int = 5000, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "temperature_c": rng.normal(60, 10, n).round(1),
        "vibration_mm_s": rng.gamma(2.0, 1.5, n).round(2),
        "load_pct": rng.uniform(20, 100, n).round(1),
        "runtime_hours": rng.uniform(0, 20000, n).round(0),
    })
    # Une panne est plus probable quand la machine chauffe, vibre, est chargée et ancienne
    risk = (
        0.08 * (df.temperature_c - 60)
        + 0.6 * (df.vibration_mm_s - 3)
        + 0.03 * (df.load_pct - 60)
        + 0.00008 * (df.runtime_hours - 10000)
    )
    df["failure"] = (risk + rng.normal(0, 1, n) > 2.2).astype(int)
    return df


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="python -m maintai.dataset")
    p.add_argument("--n", type=int, default=5000, help="nombre de relevés")
    p.add_argument("--seed", type=int, default=SEED, help="graine du générateur")
    args = p.parse_args(argv or [])
    path = get_settings().data_path
    path.parent.mkdir(parents=True, exist_ok=True)
    df = make_dataset(args.n, args.seed)
    df.to_csv(path, index=False)
    print(f"{len(df)} relevés écrits dans {path} (taux de panne : {df.failure.mean():.1%})")


if __name__ == "__main__":
    main(sys.argv[1:])
