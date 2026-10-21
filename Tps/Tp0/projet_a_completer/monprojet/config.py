"""Configuration du projet : c'est le seul fichier à adapter à votre sujet."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- Vos données -------------------------------------------------------------
DATA_PATH = ROOT / "data" / "exemple_pannes.csv"   # remplacez par votre fichier CSV
TARGET = "failure"                                  # la colonne à prédire
FEATURES = None              # None = toutes les colonnes sauf la cible ; sinon une liste de noms
TEXT_COLUMN = None           # le nom d'une colonne de texte libre (réclamations…), sinon None

# --- Type de problème --------------------------------------------------------
TASK = "classification"      # "classification" ou "regression"
MAIN_METRIC = "recall"       # classification : "accuracy", "recall", "precision", "f1"
                             # regression : "mae", "rmse", "r2"

# --- Découpage entraînement / test -------------------------------------------
SPLIT = "random"             # "random" ; ou "chronologique" pour une série temporelle
TIME_COLUMN = None           # colonne de date, obligatoire si SPLIT = "chronologique"
TEST_SIZE = 0.2              # part des données gardée pour le test
SEED = 42                    # graine : mêmes résultats à chaque lancement

MODELS_DIR = ROOT / "models"
