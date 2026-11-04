# Compte Rendu · TP1 & TP2 : API de Prédiction, Sécurisation et Client Web (MaintAI)

**Groupe :** G6  ·  **Auteur :** Bounjoume Oussama  ·  **Membres :** Bounjoume Oussama, Samouh Hajar, Benchakroune Imane, Halal Saad  
**Date :** 28 Octobre 2026  ·  **Rendu GitHub :** TP1 (`tag tp1`), TP2 (`tag tp2`)

---

## 1. TP1 — Bilan et Diagnostic des Tests

### 1.1. Lancement Initial (`python -m pytest`)

Avant d'écrire le schéma et la fonction `predict()`, le bilan des tests donnait **10 passed, 3 failed**.

### 1.2. Pourquoi les tests 422 passaient initialement « pour une mauvaise raison »

Le modèle `SensorReading` ne déclarait aucun champ (`pass`), mais contenait `model_config = ConfigDict(extra="forbid")`. Tout corps JSON contenant des propriétés était donc systématiquement rejeté avec une erreur HTTP `422`, indépendamment de la validité des valeurs. Le 422 n'était donc pas déclenché par les bornes physiques, mais par l'absence de champs déclarés.

### 1.3. Validation des bornes physiques (`maintai/api/schemas.py`)

| Champ | Type | Min (`ge`) | Max (`le`) | Justification physique |
| :-- | :--: | --: | --: | :-- |
| `temperature_c` | `float` | -40.0 | 150.0 | Limites opérationnelles standard des roulements et composants industriels. |
| `vibration_mm_s` | `float` | 0.0 | 100.0 | Amplitude vibratoire efficace (RMS). Non négative, 100 mm/s signale une casse imminente. |
| `load_pct` | `float` | 0.0 | 100.0 | Pourcentage de charge nominale (0% à 100%). |
| `runtime_hours` | `float` | 0.0 | 100 000.0 | Compteur d'heures cumulées (100k h ≈ 11.4 ans de service continu). |

---

## 2. Implémentation du Endpoint `/v1/predict` (`maintai/api/main.py`)

```python
@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return predictor.predict(reading.model_dump())
```

* **Pourquoi 503 et pas 500 ?** Un modèle non disponible est une indisponibilité temporaire du service et non une erreur imprévue du code serveur.
* **Chargement via `lifespan` :** Le modèle est désérialisé une seule fois au démarrage du serveur afin d'éviter la latence de lecture disque à chaque requête.

---

## 3. Activité 1 — Casser son API (`tests/test_casser.py`)

Un test paramétré `@pytest.mark.parametrize` valide les 5 requêtes de rejet :

```python
import pytest

HEADERS = {"X-API-Key": "test-key"}
VALID = {"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}

CAS_REFUSES = [
    ("champ manquant", "/v1/predict", {k: v for k, v in VALID.items() if k != "temperature_c"}, 422),
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": 600}, 422),
    ("texte au lieu d'un nombre", "/v1/predict", {**VALID, "temperature_c": "chaud"}, 422),
    ("champ en trop", "/v1/predict", {**VALID, "champ_en_trop": 123}, 422),
    ("mauvaise route", "/v1/doc", VALID, 404),
]

@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    assert client.post(url, json=corps, headers=HEADERS).status_code == attendu
```

**Bilan Pytest TP1 :** `18 passed` (13 originaux + 5 tests d'agressivité).

---

## 4. Questions de Synthèse Technique

1. **REST vs FastAPI :** REST est un style d'architecture fondé sur les ressources et les verbes HTTP. FastAPI est le framework Python permettant d'implémenter des API RESTful performantes.
2. **Fonctions de Pydantic :** (1) Validation automatique des entrées, (2) Génération de la documentation OpenAPI, (3) Conversion JSON <-> Objets Python.
3. **`http://localhost:8000/v1/predict` :** `localhost` (IP locale 127.0.0.1), `8000` (port d'écoute Uvicorn), `/v1/predict` (route d'inférence versionnée).
4. **Intérêt du préfixe `/v1` :** Permet de faire évoluer le contrat de l'API (`/v2`) sans casser les applications existantes.
5. **Commande Uvicorn `maintai.api.main:app` :** `maintai.api.main` est le module Python, `app` est l'instance de l'application FastAPI.

---

## 5. Rendu Git

* **Pull Request GitHub :** PR #1 (`tp1` -> `main`) & PR #2 (`tp2` -> `main`)
* **Tags GitHub :** `tp1` pushed ;)
