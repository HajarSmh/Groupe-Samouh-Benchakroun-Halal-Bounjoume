"""Configuration du projet : c'est le seul fichier à adapter à votre sujet."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- Vos données -------------------------------------------------------------
DATA_PATH = ROOT / "data" / "cantine_repas.csv"
TARGET = "repas_servis"
FEATURES = None              # None = toutes les colonnes sauf la cible ; sinon une liste de noms
TEXT_COLUMN = None           # le nom d'une colonne de texte libre (réclamations…), sinon None

# --- Type de problème --------------------------------------------------------
TASK = "regression"      # "classification" ou "regression"
MAIN_METRIC = "mae"       # classification : "accuracy", "recall", "precision", "f1"
                             # regression : "mae", "rmse", "r2"

# --- Découpage entraînement / test -------------------------------------------
SPLIT = "chronologique"             # "random" ; ou "chronologique" pour une série temporelle
TIME_COLUMN = "date"           # colonne de date, obligatoire si SPLIT = "chronologique"
TEST_SIZE = 0.2              # part des données gardée pour le test
SEED = 42                    # graine : mêmes résultats à chaque lancement

MODELS_DIR = ROOT / "models"
