"""Suivi des entraînements avec MLflow : chaque entraînement devient un « run » qu'on peut comparer.

Les runs sont enregistrés dans mlflow.db (dossier courant) ; on les regarde avec : mlflow ui
"""
import hashlib
import os
from pathlib import Path

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")  # coupe un message d'information de MLflow

import mlflow
import mlflow.sklearn

EXPERIMENT = "maintai"
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]  # nécessaire pour --model forest


def file_md5(path: Path) -> str:
    """Empreinte du fichier de données : la même que celle que DVC écrit dans le fichier .dvc."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    # TODO TP5 sprint 1 : enregistrer le run dans MLflow
    #   1. choisir l'expérience : mlflow.set_experiment(EXPERIMENT)
    #   2. ouvrir un run :        with mlflow.start_run() as run:
    #   3. dans le with :
    #        - les paramètres :   mlflow.log_params(params)
    #        - la version des données : un paramètre "data_md5", calculé par file_md5(data_path)
    #        - les métriques :    mlflow.log_metrics(metrics)
    #        - le modèle :        mlflow.sklearn.log_model(model, name="model", input_example=X_example,
    #                                                      skops_trusted_types=TRUSTED_TYPES)
    #   4. renvoyer l'identifiant : run.info.run_id
    return ""
