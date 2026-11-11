# MaintAI

Application de prédiction de panne à partir de relevés de capteurs, construite pas à pas pendant le cours « Développement et déploiement d'applications intelligentes ».

Les données fournies sont synthétiques : `python -m maintai.dataset` les génère. Elles se remplacent par des données réelles qui gardent les mêmes colonnes.

## Installation

```bash
python -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Linux / macOS :
source .venv/bin/activate

pip install -r requirements.txt
```

## Données et entraînement

```bash
python -m maintai.dataset      # écrit data/sensors.csv
python -m maintai.train        # écrit models/model.joblib, model_info.json, metrics.json
pytest                          # lance tous les tests
```

## Lancer l'API

```bash
uvicorn maintai.api.main:app --reload
```

Documentation interactive : http://localhost:8000/docs

## Clé API et client web

```bash
cp .env.example .env            # puis changez MAINTAI_API_KEY
uvicorn maintai.api.main:app --reload --env-file .env
python -m http.server 5500 -d web   # dans un second terminal
```

Ouvrez http://localhost:5500 et saisissez la clé définie dans `.env`.

## Interface Streamlit (TP3)

```bash
uvicorn maintai.api.main:app --reload --env-file .env   # terminal 1
python -m streamlit run ui/app.py                        # terminal 2
```

Ouvrez http://localhost:8501, saisissez l'URL de l'API et la clé dans la barre latérale.
Onglet « Données » : le jeu de données ; onglet « Prédiction » : un relevé envoyé à l'API.

## Installer MaintAI comme un package (TP4)

```bash
pip install -r requirements.txt   # versions figées, celles du modèle
pip install -e .                  # installe maintai en mode éditable
maintai-predict 72 6 85 15000     # la commande déclarée dans pyproject.toml
streamlit run ui/app.py           # fonctionne maintenant sans python -m
```

Construire la distribution : `python -m build` écrit `dist/maintai-0.2.0-py3-none-any.whl`.
Le wheel contient le code, pas le modèle : sur une autre machine, indiquez son dossier dans `MAINTAI_MODELS_DIR`.

## Structure

```
maintai/            code du projet
  config.py         chemins et paramètres
  dataset.py        génération des données synthétiques
  data.py           chargement et découpage
  train.py          entraînement, évaluation, sauvegarde
  predict.py        chargement du modèle et prédiction
  api/              API FastAPI (TP1, TP2)
  client.py         client HTTP de l'API (TP3)
  cli.py            commande maintai-predict (TP4)
web/                client web HTML/JS (TP2)
ui/                 interface Streamlit (TP3)
tests/              tests pytest
docs/adr/           décisions d'architecture
pyproject.toml      fiche d'identité du package (TP4)
```
