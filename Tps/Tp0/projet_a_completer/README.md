# Projet à compléter : entraîner et comparer des modèles

Vous écrivez vous-mêmes le chargement des données, le découpage entraînement / test, les modèles à comparer et leur évaluation. La structure du projet et les tests sont fournis : **les tests disent ce qui est attendu**, et vous avez fini quand ils passent tous.

## 1. Installer (une fois)

```
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows ; macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
python -m pytest                    # au départ : 7 failed, 1 passed (c'est normal)
```

## 2. Régler config.py

Votre fichier CSV dans `data/`, puis dans `monprojet/config.py` : `DATA_PATH`, `TARGET`, `TASK`, `MAIN_METRIC` (celle de votre section 5), `SPLIT` et `TIME_COLUMN` pour une série temporelle, `TEXT_COLUMN` pour du texte libre. Pas encore de données ? Gardez l'exemple `data/exemple_pannes.csv`.

## 3. Écrire le code, fonction par fonction

| Ordre | Fichier | Fonction | Tests qui passent ensuite |
|---|---|---|---|
| 1 | `monprojet/data.py` | `load_data()`, `split()` | 3 passed |
| 2 | `monprojet/models.py` | `candidates()` : la baseline d'abord, puis au moins trois modèles | 5 passed |
| 3 | `monprojet/train.py` | `evaluate()`, puis `main()` | 8 passed |

Chaque fonction contient un commentaire `TODO` qui dit ce qu'elle doit faire et quelles fonctions de pandas ou scikit-learn utiliser. `feature_columns()` et `build_preprocessing()` sont fournies.

Après chaque fonction : `python -m pytest`. Une fois tout écrit : `python -m monprojet.train` affiche le tableau de comparaison.

## 4. Choisir

Remplissez `docs/choix-modele.md` : les résultats sur le jeu de test, le modèle retenu, l'écart avec la baseline, le critère d'acceptation atteint ou non.

## Ce que produit l'entraînement

| Fichier | Contenu |
|---|---|
| `models/model.joblib` | Le meilleur modèle selon la métrique principale |
| `models/metrics.json` | `main_metric`, `best`, et les scores de tous les modèles |
