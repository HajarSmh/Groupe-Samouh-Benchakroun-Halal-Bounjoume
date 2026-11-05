# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G6  ·  **Membres :** [Samouh Hajar - Benchakroun Imane - Halal Saad - Bounjoume Oussama]  ·  **Date :** 28/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
======================================== 3 failed, 10 passed, 1 warning in 2.66s ========================================
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Quatre tests passent déjà : `/health`, la route inexistante (404) et les deux tests qui attendent un 422 (température hors bornes, champ inconnu). Ils ne dépendent ni du schéma ni de `predict()` : `/health` est déjà codé et le 404 est géré par FastAPI.
Les trois qui échouent sont `test_predict_returns_probability`, `test_high_risk_reading_raises_alert` et `test_503_when_model_missing`. Un relevé valide reçoit un 422 au lieu d'un 200, et le test du 503 reçoit aussi un 422 (`assert 422 == 503`) : la validation bloque tout avant `predict()`.
Les deux tests 422 passent pour une mauvaise raison : `SensorReading` est vide (`pass`) et `extra="forbid"` refuse tous les champs non déclarés. Donc n'importe quel JSON avec des champs est rejeté, même un relevé valide. Le 422 ne vient pas des bornes ni du champ inconnu, mais du schéma vide. Les tests sont verts sans rien prouver.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | `float` | -40 | 150 | -40 °C est le bas de la plage des capteurs industriels courants ; au-dessus de 150 °C, on sort de ce que tolèrent la plupart des capteurs, isolants et roulements : une telle valeur est presque sûrement une erreur de mesure. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vitesse de vibration efficace est une amplitude, donc positive. Les zones d'alerte des machines tournantes se situent autour de 10 à 20 mm/s ; à 100 mm/s, la machine serait détruite ou le capteur défaillant. |
| `load_pct` | `float` | 0 | 100 | Pourcentage de la charge nominale : de 0 % (à vide) à 100 % (pleine charge) par définition. |
| `runtime_hours` | `float` | 0 | 100000 | Un compteur d'heures ne peut pas être négatif ; 100 000 h correspondent à plus de 11 ans de marche continue, au-delà de la durée de vie réaliste d'une machine. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
tests\test_api.py .FF..F.
...
reading = SensorReading(temperature_c=60.0, vibration_mm_s=2.0, load_pct=50.0, runtime_hours=5000.0)

    @router.post("/predict", response_model=PredictionOut)
    def predict(reading: SensorReading) -> PredictionOut:
>       raise NotImplementedError
E       NotImplementedError

maintai\api\main.py:46: NotImplementedError
...
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError
======================================== 3 failed, 10 passed, 1 warning in 4.91s ========================================
```

Les mêmes 3 tests échouent, mais l'erreur n'est plus un 422 : c'est une `NotImplementedError` dans `predict()` (ligne 46 de `main.py`). On voit aussi que `reading` est bien devenu un objet `SensorReading`.

C'est bon signe : le relevé valide passe la validation et arrive jusqu'à `predict()`. Ce qui échoue encore, c'est seulement la partie qu'on n'a pas écrite. Les tests 422 passent maintenant pour la bonne raison (les bornes et `extra="forbid"`).

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(status_code=503, detail="Modèle non chargé")
return predictor.predict(reading.model_dump())
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Un 500 signale un bug imprévu du serveur. Ici, on sait ce qui se passe : le modèle n'est pas chargé. Le 503 (service indisponible) le dit mieux : la requête du client est correcte, c'est le serveur qui n'est pas prêt, et ça se règle côté serveur (avec `python -m maintai.train`).

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Charger le modèle depuis le disque prend du temps. Le refaire à chaque requête ralentirait toutes les réponses. En le chargeant une fois dans `lifespan`, toutes les requêtes utilisent le même objet déjà en mémoire. Et si le fichier manque, on le voit tout de suite avec `/health`.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
============================================= 13 passed, 1 warning in 2.75s =============================================
```

Les 13 tests passent : 7 dans `test_api.py`, 3 dans `test_data.py` et 3 dans `test_train.py`. L'unique avertissement est une dépréciation liée à `httpx` dans le `TestClient` de Starlette, qui ne vient pas de notre code.

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-10-28T17:34:41Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail": "Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

Elles apparaissent dans la section **Schemas** en bas de la page, sous `SensorReading`, et dans le « Request body » de la route `POST /v1/predict`.

Le 422 est aussi utile : il indique le champ fautif (`temperature_c`) et la borne dépassée (150), alors que le 404 dit seulement que le chemin n'existe pas.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un style d'organisation d'une API (des URL pour les ressources, des verbes HTTP comme GET et POST, des codes de statut standard). FastAPI est un outil Python qui permet de construire une API qui suit ce style.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   À valider les données reçues (types, bornes, champs interdits, avec un 422 automatique), à documenter l'API dans `/docs`, et à transformer le JSON en objet Python utilisable (`reading.temperature_c`, `model_dump()`).
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` est mon propre ordinateur, `8000` est le port sur lequel uvicorn écoute, et `/v1/predict` est le chemin de la route de prédiction.
4. Pourquoi `/v1` dans l'adresse ?
   Pour pouvoir faire une `/v2` plus tard sans casser ceux qui utilisent encore la `/v1`.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` est le fichier `maintai/api/main.py`, et `app` est la variable de ce fichier qui contient l'application FastAPI.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp1` existe sur GitHub : oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?

## 8. Ce qui reste flou

- Le seuil d'alerte de l'API est de 0,3 (`MAINTAI_THRESHOLD`), alors qu'au TP0 nous avions travaillé avec le seuil par défaut de 0,5. Je ne sais pas comment ce 0,3 a été choisi : il favorise le rappel, mais augmente sûrement les fausses alertes, et sans coût chiffré des deux types d'erreur je ne peux pas dire s'il est bon.
- `model_version` est un simple horodatage. Il dit quand le modèle a été entraîné, mais pas avec quelles données ni quel code.
- Les tests vérifient que l'API se comporte correctement, pas qu'elle tient la charge : nous n'avons rien mesuré en nombre de requêtes par seconde ni en temps de réponse.
- Le 503 ne dit pas pourquoi le modèle manque (fichier absent, jamais entraîné, fichier illisible). Pour le savoir, il faudrait regarder les journaux du serveur.
