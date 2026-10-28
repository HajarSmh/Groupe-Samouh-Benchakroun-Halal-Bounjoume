# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** …  ·  **Membres :** …  ·  **Date :** 28/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
(à coller : sortie réelle de votre terminal, du type « 3 failed, 4 passed in 0.xxs »)
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Les 4 tests qui passent sont ceux qui ne dépendent pas du contenu du schéma ni de `predict()` : le test de `/health` (la route est déjà codée), le test de la route inexistante (404, géré par FastAPI) et les deux tests qui attendent un code 422 (température hors bornes, champ inconnu). *(À vérifier avec votre sortie de `pytest`.)*

Les deux tests 422 passent pour une mauvaise raison : `SensorReading` ne déclare encore aucun champ (`pass`) et `extra="forbid"` refuse tout champ non déclaré. Donc **n'importe quel corps JSON contenant des champs est rejeté avec un 422**, y compris un relevé parfaitement valide. Le 422 obtenu ne vient pas de la validation des bornes ou du champ inconnu : il vient du fait que le schéma est vide. Le test est « vert » sans prouver que la validation fonctionne.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | `float` | -40 | 150 | -40 °C est la limite basse usuelle des capteurs et équipements industriels ; au-delà de 150 °C, on dépasse ce que supportent les isolants, roulements et capteurs courants : la valeur est forcément une erreur de mesure. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vitesse de vibration (valeur efficace) est une amplitude : jamais négative. Les zones de danger des machines tournantes se situent autour de 10 à 20 mm/s ; 100 mm/s correspond à une destruction mécanique ou à un capteur défaillant. |
| `load_pct` | `float` | 0 | 100 | C'est un pourcentage de la charge nominale : 0 % (à vide) à 100 % (pleine charge) par définition. |
| `runtime_hours` | `float` | 0 | 100000 | Un compteur d'heures ne peut pas être négatif ; 100 000 h représentent plus de 11 ans de fonctionnement continu, au-delà de la durée de vie réaliste d'une machine. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
(à coller : sortie réelle de votre terminal)
```

Les tests qui échouent encore (ceux qui appellent `/v1/predict` avec un relevé valide) remontent une `NotImplementedError`, levée par `predict()` qui n'est pas encore écrite. C'est un bon signe : la requête valide **passe maintenant la validation Pydantic** et arrive jusqu'à la fonction `predict()`. Le schéma fonctionne, et l'échec restant vient bien de la seule partie non écrite, ce qui confirme que les deux fichiers sont indépendants. Les tests 422 passent désormais pour la bonne raison (bornes et `extra="forbid"`).

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(status_code=503, detail="Modèle non chargé")
return predictor.predict(reading.model_dump())
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Le 500 (Internal Server Error) signale un bug imprévu du serveur. Ici, la situation est connue et prévue : le service est temporairement indisponible parce que le modèle n'a pas été entraîné ou chargé. Le 503 (Service Unavailable) le dit précisément : la requête du client est correcte, le problème vient de l'état du serveur, et il pourra se résoudre (après `python -m maintai.train`) sans que le client ne change rien. Il permet aussi à la supervision de distinguer une panne attendue d'un vrai bug.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Charger un modèle (lecture du fichier sur le disque, désérialisation) est une opération lente et coûteuse en mémoire. À chaque requête, cela ajouterait une latence importante et gaspillerait des ressources, surtout avec plusieurs requêtes simultanées. En le chargeant une fois dans `lifespan`, toutes les requêtes réutilisent le même objet déjà en mémoire, et l'erreur éventuelle (fichier absent) est détectée dès le démarrage et signalée par `/health`.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
(à coller : sortie réelle de votre terminal, attendue : « 7 passed in 0.xxs »)
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability": …, "alert": …, "threshold": …, "model_version": "…"}` *(à recopier depuis votre terminal : les valeurs dépendent de votre modèle entraîné)* |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", ...}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail": "Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

Dans la section **Schemas** en bas de la page, sous `SensorReading` : chaque champ affiche ses contraintes (`minimum`, `maximum`) et sa description. On les voit aussi dans le corps de requête (« Request body ») de la route `POST /v1/predict`, avec l'exemple fourni par `json_schema_extra`.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un **style d'architecture** (des conventions) : des ressources identifiées par des URL, manipulées avec les verbes HTTP (GET, POST…), sans état côté serveur, avec des codes de statut standard et en général du JSON. FastAPI est un **framework Python** qui permet de construire une API qui respecte ces conventions.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   (1) **Valider** les données d'entrée (types, bornes, champs interdits), avec un 422 automatique en cas d'erreur ; (2) **documenter** l'API, puisque FastAPI en déduit le schéma OpenAPI et la page `/docs` ; (3) **convertir** le JSON reçu en objet Python typé et exploitable (`reading.temperature_c`, `model_dump()`), et sérialiser la réponse.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` désigne la machine locale (son propre ordinateur, 127.0.0.1) ; `8000` est le **port** sur lequel le serveur uvicorn écoute ; `/v1/predict` est le **chemin** de la route (la ressource demandée) dans l'API, ici la version 1 de la prédiction.
4. Pourquoi `/v1` dans l'adresse ?
   Pour **versionner** l'API : on pourra publier une `/v2` avec un contrat différent (nouveaux champs, autre format) sans casser les clients qui utilisent encore la `/v1`.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` est le chemin du **module Python** (le fichier `maintai/api/main.py`) et `app` est le **nom de la variable** dans ce module qui contient l'objet `FastAPI(...)` que uvicorn doit servir.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp1` existe sur GitHub : oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 8. Ce qui reste flou

…