# MaintAI · TP2 : Sécurisation, Tests et Client Web

Projet développé dans le cadre du cours *« Développement et déploiement d'applications intelligentes »* (École Marocaine des Sciences de l'Ingénieur - EMSI).  
**Auteur :** Bounjoume Oussama (Groupe G6)

Ce dépôt contient l'implémentation complète du **TP2**, couvrant l'authentification sécurisée par clé API, la gestion des politiques CORS pour le client web, ainsi que la suite de tests unitaires et d'intégration.

---

## Guide de Démarrage Rapide

### 1. Installation de l'Environnement

```bash
python -m venv .venv
# Sur Windows (PowerShell) :
..\TP1\.venv\Scripts\Activate.ps1
# Ou créez un venv local :
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configuration des Secrets (`.env`)

Copiez le modèle d'environnement et configurez votre clé secrète :

```bash
cp .env.example .env
```

Assurez-vous que votre fichier `.env` contient :

```env
MAINTAI_API_KEY=bounjoume-secret-key-2026
MAINTAI_CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### 3. Génération des Données et Entraînement du Modèle

```bash
python -m maintai.dataset
python -m maintai.train
```

### 4. Lancement de l'API avec Sécurisation

```bash
uvicorn maintai.api.main:app --reload --env-file .env
```

* Documentation interactive Swagger : [http://localhost:8000/docs](http://localhost:8000/docs) (requiert la saisie de l'en-tête `X-API-Key`).
* Route de santé publique : [http://localhost:8000/health](http://localhost:8000/health).

### 5. Exécution du Client Web (Second Terminal)

Dans un second terminal, servez l'interface web sur le port autorisé `5500` :

```bash
python -m http.server 5500 -d web
```

Ouvrez ensuite [http://localhost:5500](http://localhost:5500), saisissez votre clé API et testez les relevés de capteurs en temps réel.

---

## Validation par les Tests (`Pytest`)

Lancez la suite complète des tests unitaires, de robustesse (`test_casser.py`) et de sécurité (`test_security.py`) :

```bash
python -m pytest -v
```

---

## Structure du Projet (TP2)

```text
.
├── .env                  # Configuration locale des secrets (ignorée par Git)
├── .env.example          # Modèle de configuration des variables d'environnement
├── README.md             # Documentation principale du projet
├── COMPTE_RENDU.md       # Compte rendu détaillé du TP2 (Bounjoume Oussama)
├── body.json             # Exemples de charges utiles JSON pour requêtes
├── data/                 # Données synthétiques ou réelles (sensors.csv)
├── docs/
│   └── adr/              # Décisions d'architecture (ADR 003 : Sécurité & CORS)
├── maintai/              # Code source de l'application
│   ├── config.py         # Chargement de la configuration (.env, CORS, clés)
│   ├── dataset.py        # Génération des relevés de capteurs synthétiques
│   ├── data.py           # Chargement et découpage stratifié
│   ├── train.py          # Entraînement et sérialisation du modèle (Pipeline scikit-learn)
│   ├── predict.py        # Inférence et calcul de probabilité de panne
│   └── api/
│       ├── main.py       # Application FastAPI, middleware CORS et routeur /v1
│       ├── schemas.py    # Schémas de validation Pydantic et contraintes physiques
│       └── security.py   # Authentification par clé API (en-tête X-API-Key)
├── tests/                # Suite de tests automatisés (pytest)
│   ├── conftest.py       # Fixtures de test isolées
│   ├── test_api.py       # Tests fonctionnels de l'API
│   ├── test_casser.py    # Tests d'robustesse et d'exceptions (paramétrés)
│   ├── test_security.py  # Tests d'authentification (401, 200, headers)
│   └── test_train.py     # Vérification des artefacts d'entraînement
└── web/                  # Interface utilisateur Web (HTML / JS fetch)
    └── index.html        # Page de test interactive avec gestion des erreurs et CORS
```

---

## Références et Rendu

* **Auteur :** Bounjoume Oussama — Groupe G6
* **Rapport détaillé :** Voir [tp2_compte_rendu_bounjoume_oussama.md](./tp2_compte_rendu_bounjoume_oussama.md) pour l'analyse complète, les captures de tests, et les décisions techniques du TP2.
