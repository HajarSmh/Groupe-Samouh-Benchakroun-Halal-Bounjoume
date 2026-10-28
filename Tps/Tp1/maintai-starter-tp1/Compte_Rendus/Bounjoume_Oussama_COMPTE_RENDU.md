# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G6  ·  **Membres :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]  ·  **Date :** 28/10/2026

---

## Informations générales

| Élément | Détail |
|:--|:--|
| **TP** | TP1 — API de prédiction |
| **Projet** | MaintAI |
| **Groupe** | G6 |
| **Membres** | Samouh Hajar · Benchakroune Imane · Halal Saad · Bounjoume Oussama |
| **Date** | 28 octobre 2026 |
| **Technologies** | Python · FastAPI · Pydantic · Pytest · Uvicorn |

> **Objectif du TP :** concevoir une API capable de recevoir des mesures industrielles, de valider les données transmises, de prédire une probabilité de défaillance et de déclencher une alerte lorsque le risque dépasse un seuil défini.

---

# 1. Mise en place et analyse des tests initiaux

## 1.1. Résultat initial

Après la mise en place du projet, mais avant l'implémentation des fonctionnalités manquantes, la commande suivante est exécutée :

```bash
python -m pytest
```

Résultat obtenu :

```text
========================================
3 failed, 10 passed, 1 warning in 2.66s
========================================
```

Au total, **10 tests passent et 3 échouent**. Parmi les 7 tests de `tests/test_api.py`, 4 passent déjà, alors que certaines parties de l'API ne sont pas encore implémentées.

## 1.2. Quels sont les quatre tests qui passent ?

| Test | Explication |
|:--|:--|
| `test_health` | La route `/health` est déjà implémentée dans `main.py` et renvoie un état du service ainsi que l'information indiquant si le modèle est chargé. |
| `test_openapi_documents_predict` | FastAPI génère automatiquement la documentation OpenAPI. La route `/v1/predict` y apparaît dès lors qu'elle est déclarée. |
| `test_out_of_range_value_is_rejected` | Une température de `500 °C` est rejetée avec un code HTTP `422`. |
| `test_missing_field_is_rejected` | Une requête ne contenant pas le champ `load_pct` est rejetée avec un code HTTP `422`. |

### Pourquoi les deux tests `422` passent-ils pour une mauvaise raison ?

Dans `schemas.py`, le modèle `SensorReading` ne contient initialement aucun champ : son corps est simplement défini par `pass`.

Cependant, sa configuration comprend déjà :

```python
model_config = ConfigDict(extra="forbid")
```

Cette option interdit les champs qui ne sont pas déclarés dans le schéma.

Puisque **le schéma ne déclare aucun champ**, toutes les propriétés présentes dans le JSON sont considérées comme supplémentaires et sont rejetées.

Ainsi, même une requête parfaitement valide est refusée avec un code `422`.

Le test concernant la température hors limites et celui concernant le champ manquant passent donc, mais **ils ne prouvent pas encore que la validation métier fonctionne correctement**.

Le code `422` est bien renvoyé, mais pour une mauvaise raison : le schéma est vide.

## 1.3. Les trois tests qui échouent

| Test | Résultat observé | Interprétation |
|:--|:--|:--|
| `test_predict_returns_probability` | `assert 422 == 200` | Une requête valide est rejetée au lieu de produire une prédiction. |
| `test_high_risk_reading_raises_alert` | `KeyError: 'alert'` | La réponse ne contient pas le champ `alert` attendu. |
| `test_503_when_model_missing` | `assert 422 == 503` | La validation échoue avant que la fonction de prédiction puisse vérifier la disponibilité du modèle. |

Ces échecs confirment que le schéma d'entrée doit être correctement défini avant de pouvoir tester le fonctionnement de la prédiction.

---

# 2. Définition du schéma d'entrée

**Fichier concerné :** `maintai/api/schemas.py`

Le schéma `SensorReading` représente les mesures industrielles transmises à l'API. Il permet de vérifier que chaque valeur respecte un type et des contraintes cohérents avec sa signification physique.

## 2.1. Définition des variables et de leurs bornes

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|:--|:--:|--:|--:|:--|
| `temperature_c` | `float` | -40 | 150 | Une plage de -40 à 150 °C constitue une plage de validation plausible pour certains capteurs et équipements industriels. Au-delà, une vérification de la mesure ou du matériel est nécessaire. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vitesse vibratoire ne peut pas être négative lorsqu'elle représente une amplitude ou une valeur efficace. Des valeurs très élevées peuvent signaler une vibration extrême ou un défaut de mesure. |
| `load_pct` | `float` | 0 | 100 | Le pourcentage de charge est défini entre 0 % et 100 % de la charge nominale. |
| `runtime_hours` | `float` | 0 | 100 000 | Un compteur d'heures de fonctionnement ne peut pas être négatif. Une valeur de 100 000 heures représente plus de 11 ans de fonctionnement continu. |

> **Remarque :** ces bornes sont choisies à partir de considérations physiques et opérationnelles, et non simplement à partir des valeurs minimales et maximales observées dans `sensors.csv`. Elles constituent néanmoins des limites de validation à adapter aux spécifications réelles des capteurs et des machines.

## 2.2. Pourquoi ces contraintes sont-elles importantes ?

La validation permet notamment de rejeter :

- Une température de `500 °C`, qui dépasse la plage autorisée.
- Une vibration négative, incompatible avec la représentation retenue.
- Une charge de `120 %`, supérieure à la charge nominale définie.
- Un temps de fonctionnement négatif, qui n'a pas de sens pour un compteur cumulatif.

Cela évite de transmettre au modèle des valeurs manifestement invalides.

## 2.3. Résultat des tests après l'implémentation du schéma

Après avoir complété uniquement `schemas.py`, la commande suivante est exécutée :

```bash
python -m pytest
```

Résultat obtenu :

```text
tests/test_api.py .FF..F.
...
reading = SensorReading(
    temperature_c=60.0,
    vibration_mm_s=2.0,
    load_pct=50.0,
    runtime_hours=5000.0
)

@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:

    raise NotImplementedError

E   NotImplementedError

maintai/api/main.py:46

...
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError

========================================
3 failed, 10 passed, 1 warning in 4.91s
========================================
```

### Pourquoi ce résultat est-il encourageant ?

Les trois mêmes tests échouent encore, mais la nature de l'erreur a changé.

Auparavant, les requêtes valides étaient rejetées avec un code `422`. Désormais, l'objet `SensorReading` est correctement construit à partir des valeurs reçues.

L'erreur est maintenant une `NotImplementedError`, levée dans la fonction `predict()` de `main.py`.

Cela signifie que :

1. Les données valides passent la validation Pydantic.
2. La requête atteint la fonction de prédiction.
3. Les échecs restants proviennent de la partie de la fonction qui n'est pas encore implémentée.

**Conclusion :** le schéma fonctionne correctement. Il reste à implémenter la logique de prédiction.

---

# 3. Implémentation de la fonction `predict()`

**Fichier concerné :** `maintai/api/main.py`

La fonction `predict()` reçoit un objet `SensorReading`, vérifie que le modèle est disponible, puis transmet les mesures au prédicteur.

## 3.1. Code implémenté

```python
predictor = state.get("predictor")

if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle non chargé"
    )

return predictor.predict(reading.model_dump())
```

### Fonctionnement

1. **Récupération du modèle :** l'API recherche le prédicteur dans l'état de l'application.
2. **Vérification de disponibilité :** si le modèle est absent, une erreur HTTP `503` est renvoyée.
3. **Conversion des données :** `reading.model_dump()` transforme l'objet Pydantic en dictionnaire Python.
4. **Prédiction :** le dictionnaire est transmis à `predictor.predict()`, qui retourne le résultat attendu.

## 3.2. Pourquoi renvoyer un code `503` plutôt que `500` ?

Le code HTTP `500 Internal Server Error` désigne une erreur interne inattendue du serveur.

Dans notre cas, l'absence du modèle est une situation identifiée : le service ne peut pas effectuer de prédiction tant que le modèle n'est pas disponible.

Le code `503 Service Unavailable` est donc plus adapté, car il indique que le service est temporairement indisponible.

Il permet également de distinguer :

- **503 :** le service ne peut pas fonctionner normalement parce que le modèle est indisponible.
- **500 :** une erreur interne inattendue empêche le traitement de la requête.

Cette distinction facilite la supervision et le diagnostic des problèmes.

## 3.3. Pourquoi charger le modèle une seule fois au démarrage ?

Le chargement d'un modèle implique généralement la lecture d'un fichier sur le disque et sa désérialisation en mémoire.

Répéter cette opération à chaque requête aurait plusieurs inconvénients :

- Une augmentation de la latence.
- Des opérations d'entrée-sortie inutiles.
- Une consommation supplémentaire de ressources.
- Une moins bonne capacité à traiter plusieurs requêtes.

Le modèle est donc chargé au démarrage de l'application, dans le mécanisme `lifespan` de FastAPI.

Toutes les requêtes peuvent ensuite réutiliser le même objet en mémoire.

Cette approche permet de **réduire le coût de chaque requête et de détecter plus tôt certains problèmes de disponibilité du modèle**.

La route `/health` peut également exposer l'état de chargement du modèle.

---

# 4. Validation finale avec Pytest

Une fois le schéma et la fonction de prédiction implémentés, la suite de tests est exécutée à nouveau :

```bash
python -m pytest
```

Résultat final :

```text
=============================================
13 passed, 1 warning in 2.75s
=============================================
```

### Bilan des tests

Les **13 tests passent**. Ils couvrent les trois principaux ensembles de tests du projet.

| Fichier | Nombre de tests | Résultat |
|:--|--:|:--:|
| `tests/test_api.py` | 7 | ✅ 7 réussis |
| `tests/test_data.py` | 3 | ✅ 3 réussis |
| `tests/test_train.py` | 3 | ✅ 3 réussis |
| **Total** | **13** | **✅ 13 réussis** |

## 4.1. Détail des tests de l'API

| Test | Fonctionnalité vérifiée | Résultat |
|:--|:--|:--:|
| `test_health` | `GET /health` renvoie `200` et indique que le modèle est chargé. | ✅ |
| `test_predict_returns_probability` | Une requête valide produit une probabilité comprise entre 0 et 1 et un champ `alert` booléen. | ✅ |
| `test_high_risk_reading_raises_alert` | Une mesure présentant un risque élevé déclenche une alerte. | ✅ |
| `test_out_of_range_value_is_rejected` | Une température de `500 °C` est rejetée avec `422`. | ✅ |
| `test_missing_field_is_rejected` | L'absence du champ obligatoire `load_pct` entraîne une erreur `422`. | ✅ |
| `test_503_when_model_missing` | L'absence du modèle entraîne une erreur `503`. | ✅ |
| `test_openapi_documents_predict` | La route `/v1/predict` figure dans la documentation OpenAPI. | ✅ |

L'avertissement restant concerne une dépréciation liée à `httpx` et au `TestClient` de Starlette. Il ne correspond pas à un échec de test.

**Bilan :** les tests confirment le fonctionnement attendu des principales fonctionnalités de l'API, notamment la validation des entrées, la prédiction et la gestion de l'indisponibilité du modèle.

---

# 5. Exécution et utilisation de l'API

## 5.1. Lancement de l'application

Avant de lancer le serveur, il faut générer le jeu de données puis entraîner le modèle.

```bash
python -m maintai.dataset
python -m maintai.train
```

Une fois ces étapes terminées, démarrer le serveur avec :

```bash
uvicorn maintai.api.main:app --reload
```

L'API devient alors accessible à l'adresse locale suivante :

```text
http://localhost:8000
```

La documentation interactive est disponible sur :

```text
http://localhost:8000/docs
```

Elle permet de consulter les routes, les schémas et les contraintes de validation, puis d'envoyer des requêtes directement depuis le navigateur.

## 5.2. Vérification de l'état du service

**Requête :**

```http
GET /health
```

**Code HTTP :** `200 OK`

**Réponse JSON :**

```json
{
  "status": "ok",
  "model_loaded": true
}
```

Cette réponse indique que le service fonctionne et que le modèle est chargé.

## 5.3. Prédiction sur une mesure industrielle

**Requête :**

```http
POST /v1/predict
Content-Type: application/json
```

**Corps JSON :**

```json
{
  "temperature_c": 72.5,
  "vibration_mm_s": 6.1,
  "load_pct": 85,
  "runtime_hours": 15000
}
```

**Code HTTP :** `200 OK`

**Réponse obtenue :**

```json
{
  "failure_probability": 0.9553,
  "alert": true,
  "threshold": 0.3,
  "model_version": "2026-10-28T17:34:41Z"
}
```

### Interprétation

| Champ | Signification |
|:--|:--|
| `failure_probability` | Probabilité de défaillance estimée par le modèle, comprise entre 0 et 1. |
| `alert` | Indique si le seuil de décision est atteint ou dépassé. |
| `threshold` | Seuil utilisé pour déclencher l'alerte, ici `0.3`. |
| `model_version` | Identifiant temporel utilisé pour identifier la version du modèle. |

Dans cet exemple, la probabilité estimée est de `0.9553`, soit environ **95,53 %**. Elle dépasse le seuil de `0.3`, ce qui explique pourquoi `alert` vaut `true`.

> **Attention :** cette probabilité est une estimation produite par le modèle, et non une garantie qu'une défaillance surviendra. Son interprétation dépend notamment de la calibration du modèle et de la représentativité des données d'entraînement.

## 5.4. Vérification de la validation des entrées

Une température de `500 °C` dépasse la borne maximale de `150 °C`.

**Requête :**

```json
{
  "temperature_c": 500,
  "vibration_mm_s": 6.1,
  "load_pct": 85,
  "runtime_hours": 15000
}
```

**Code HTTP attendu :** `422 Unprocessable Entity`

**Réponse obtenue :**

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": [
        "body",
        "temperature_c"
      ],
      "msg": "Input should be less than or equal to 150",
      "input": 500,
      "ctx": {
        "le": 150.0
      }
    }
  ]
}
```

La réponse indique que le champ `temperature_c` ne respecte pas la borne maximale définie dans le schéma Pydantic.

La requête est donc rejetée **avant l'exécution de la fonction de prédiction**.

## 5.5. Vérification d'une route inexistante

Une faute de frappe dans l'adresse entraîne une erreur `404 Not Found`.

**Requête :**

```http
POST /v1/predicte
```

**Réponse :**

```json
{
  "detail": "Not Found"
}
```

Cette réponse signifie que la route demandée n'existe pas. Il s'agit d'une erreur de chemin, différente d'une erreur de validation `422`.

## 5.6. Où consulter les bornes dans `/docs` ?

Dans la documentation interactive, les contraintes sont visibles à deux endroits :

1. **Section `Schemas` → `SensorReading` :** chaque champ présente son type et ses contraintes, notamment les valeurs minimales et maximales.
2. **Route `POST /v1/predict` → `Request body` :** le schéma de la requête expose les propriétés attendues et leurs contraintes.

Les descriptions et les exemples configurés dans Pydantic peuvent également apparaître dans la documentation générée par FastAPI.

---

# 6. Questions de compréhension

## 6.1. Quelle est la différence entre REST et FastAPI ?

**REST** est un style d'architecture destiné à concevoir des services web. Il repose notamment sur des ressources identifiées par des URL, l'utilisation des méthodes HTTP, des codes de statut standardisés et des échanges sans état applicatif conservé entre les requêtes.

**FastAPI** est un framework Python permettant de développer des API web. Il facilite la création des routes, la validation des données, la gestion des réponses et la génération automatique de la documentation OpenAPI.

En résumé :

- REST définit des principes de conception.
- FastAPI fournit les outils pour implémenter une API qui peut respecter ces principes.

## 6.2. Quelles sont les trois fonctions principales du schéma Pydantic ?

Le schéma Pydantic remplit trois fonctions essentielles.

**1. Valider les données**

Il vérifie les types, les champs obligatoires et les contraintes définies. Une entrée invalide entraîne automatiquement une réponse `422` lorsque la validation de la requête échoue.

**2. Documenter l'API**

FastAPI utilise les modèles Pydantic pour générer la documentation OpenAPI et l'interface interactive accessible sur `/docs`.

**3. Transformer les données**

Le JSON reçu est converti en objet Python typé. Les champs deviennent accessibles directement, par exemple avec `reading.temperature_c`, tandis que `reading.model_dump()` permet de récupérer les données sous forme de dictionnaire.

Les modèles de réponse contribuent également à structurer et à sérialiser les résultats renvoyés par l'API.

## 6.3. Que signifient `localhost`, `8000` et `/v1/predict` ?

Dans l'adresse :

```text
http://localhost:8000/v1/predict
```

| Élément | Signification |
|:--|:--|
| `localhost` | Désigne la machine locale, généralement accessible via l'adresse IP `127.0.0.1`. |
| `8000` | Correspond au port sur lequel le serveur Uvicorn écoute. |
| `/v1/predict` | Correspond au chemin de la route de prédiction de l'API. |

Le client envoie donc une requête au serveur qui écoute sur le port `8000` de la machine locale, en ciblant la route `/v1/predict`.

## 6.4. Pourquoi utiliser `/v1` dans l'adresse ?

Le préfixe `/v1` permet de versionner l'API.

Si une évolution importante modifie le format des requêtes ou des réponses, une version `/v2` pourra être publiée sans nécessairement casser les clients qui utilisent encore `/v1`.

Le versionnement facilite donc l'évolution du service et la compatibilité entre différentes versions du contrat d'API.

## 6.5. Que désignent `maintai.api.main` et `app` dans la commande Uvicorn ?

La commande utilisée est :

```bash
uvicorn maintai.api.main:app --reload
```

- `maintai.api.main` désigne le module Python correspondant au fichier `maintai/api/main.py`.
- `app` désigne la variable de ce module qui contient l'instance de l'application FastAPI.
- `--reload` active le rechargement automatique du serveur lorsque des fichiers surveillés sont modifiés, ce qui est pratique pendant le développement.

Uvicorn importe donc l'objet `app` et l'utilise pour servir les requêtes HTTP.

---

# 7. Rendu Git et pull request

Cette partie doit être complétée avec les informations réelles du dépôt GitHub.

| Élément | Réponse |
|:--|:--|
| **Lien de la pull request** | À compléter |
| **Tag `tp1` présent sur GitHub** | Oui / Non |
| **Personne ayant relu la pull request** | À compléter |
| **Commentaire laissé lors de la relecture** | À compléter |

### Vérifications avant le rendu

- [ ] Le code de l'API est implémenté et les tests passent.
- [ ] Les modifications sont poussées sur la branche prévue.
- [ ] La pull request est créée et son lien est renseigné.
- [ ] Le tag `tp1` est présent sur GitHub si cela est demandé.
- [ ] La pull request a été relue.
- [ ] Le commentaire du relecteur est renseigné dans ce compte rendu.

---

# 8. Points restant à clarifier

Même si tous les tests passent, plusieurs questions de conception méritent d'être approfondies.

## 8.1. Justification du seuil de décision

Le seuil de décision utilisé est `0.3`, défini par `MAINTAI_THRESHOLD` dans `config.py`.

Ce seuil signifie qu'une alerte peut être déclenchée lorsque la probabilité estimée de défaillance atteint ou dépasse 30 %.

Un seuil inférieur à `0.5` peut être pertinent lorsque manquer une défaillance est plus coûteux que déclencher une fausse alerte. Il favorise potentiellement le rappel, mais peut également augmenter le nombre de faux positifs.

Le choix devrait donc être justifié à partir des coûts opérationnels :

- **Faux négatif (FN) :** une défaillance réelle n'est pas détectée.
- **Faux positif (FP) :** une alerte est déclenchée alors qu'aucune défaillance ne survient.

Une analyse de ces coûts permettrait de mieux justifier le seuil retenu.

## 8.2. Choix du modèle

Le modèle utilisé est une régression logistique, d'après `maintai/train.py`.

Cependant, le TP1 ne demande pas de reproduire la comparaison des modèles éventuellement effectuée au TP0.

Il reste donc à vérifier si la régression logistique demeure le meilleur choix pour le problème considéré, notamment lorsque le seuil de décision est fixé à `0.3`.

Une comparaison sur des données de validation pourrait prendre en compte le rappel, la précision, le score F1 et les coûts des erreurs.

## 8.3. Signification de `model_version`

Le champ `model_version` contient un horodatage au format ISO.

Cette approche facilite la traçabilité temporelle, mais elle ne précise pas à elle seule ce qui est versionné :

- Le fichier `model.joblib`.
- Les hyperparamètres du modèle.
- Les données d'entraînement.
- Le code ayant servi à entraîner le modèle.

Une stratégie de versionnement plus complète pourrait associer le modèle à un identifiant unique, à la version du code et à une empreinte des données utilisées.

## 8.4. Absence de test de charge

Les tests actuels vérifient le comportement fonctionnel de l'API, mais ne mesurent pas ses performances sous une charge importante.

Il reste à déterminer :

- Le nombre de requêtes par seconde que l'API peut traiter.
- La latence moyenne et les latences élevées.
- Le comportement lorsque plusieurs requêtes arrivent simultanément.
- La consommation de mémoire lorsque le modèle est chargé.
- La stabilité du service sur une période prolongée.

Un test de charge permettrait d'évaluer plus précisément l'aptitude de l'API à être utilisée en production.

## 8.5. Diagnostic d'un modèle indisponible

Lorsque le modèle n'est pas disponible, l'API renvoie une réponse `503`.

Cette réponse indique correctement que le service ne peut pas effectuer la prédiction, mais ne distingue pas les différentes causes possibles :

- Le fichier du modèle est absent.
- Le modèle n'a jamais été entraîné.
- Le fichier ne peut pas être désérialisé.
- Le chargement a échoué pour une autre raison.

Les journaux du serveur doivent permettre de diagnostiquer ces situations. Une amélioration possible consisterait à renforcer la journalisation et la supervision tout en conservant une réponse HTTP qui n'expose pas inutilement des détails internes.

---

# 9. Conclusion générale

Ce TP a permis de mettre en place les éléments essentiels d'une API de prédiction pour MaintAI.

Le travail réalisé couvre :

- La définition d'un schéma d'entrée avec Pydantic.
- La validation des mesures industrielles et le rejet des valeurs invalides.
- L'intégration du modèle de prédiction dans FastAPI.
- La gestion de l'indisponibilité du modèle avec un code HTTP `503`.
- L'exposition de routes HTTP et la génération automatique de la documentation OpenAPI.
- La vérification du comportement de l'application avec Pytest.

Le résultat final est satisfaisant sur le plan fonctionnel : **les 13 tests passent**, et les principales situations attendues — prédiction réussie, entrée invalide et modèle indisponible — sont couvertes.

Les prochaines améliorations pourraient porter sur la justification du seuil de décision, l'évaluation du modèle, la traçabilité des versions et les performances de l'API sous charge.

> **Résultat final :** une API fonctionnelle, testée et documentée, constituant une première étape vers l'intégration d'un système de maintenance prédictive.

---

*Compte rendu du TP1 — MaintAI · Groupe G6 · 28 octobre 2026*