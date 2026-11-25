"""Commande maintai-predict : une prédiction depuis le terminal, sans API.

Usage : maintai-predict 72 6 85 15000
"""
import argparse
import sys

from maintai import __version__
from maintai.config import FEATURES, get_settings
from maintai.predict import Predictor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="maintai-predict", description="Probabilité de panne pour un relevé de capteurs."
    )
    for f in FEATURES:
        parser.add_argument(f, type=float)
    parser.add_argument("--version", action="version", version=f"maintai {__version__}")
    reading = vars(parser.parse_args(argv))

    settings = get_settings()
    try:
        predictor = Predictor.load(settings)
    except FileNotFoundError:
        # Le package contient le code, pas le modèle : il faut lui dire où le trouver
        print(f"Modèle introuvable : {settings.model_path}", file=sys.stderr)
        print("Entraînez-le (python -m maintai.train) ou indiquez son dossier "
              "dans MAINTAI_MODELS_DIR.", file=sys.stderr)
        return 1

    res = predictor.predict(reading)
    etat = "ALERTE" if res["alert"] else "normal"
    print(f"Probabilité de panne : {round(res['failure_probability'] * 100)} % ({etat})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
