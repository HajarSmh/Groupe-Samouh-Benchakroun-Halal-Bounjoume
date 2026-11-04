# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G6  ·  **Membres :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]  ·  **Date :** 04/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 |temperature manquante |422 | 422 Unprocessable Content|
| 2 | temperature = 600|422 |422 Unprocessable Content|
| 3 | temperature = chaud|422 |422 Unprocessable Content|
| 4 | champ en trop |422 |422 Unprocessable Content|
| 5 | mauvaise route /doc au lieu de /docs|404 |404 Not Found|

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Aucune de nos prévisions n'était fausse. Les cinq requêtes ont produit les codes HTTP attendus.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```====================================== 19 passed, 1 warning in 2.70s =======================================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

**@pytest.mark.parametrize** permet d'exécuter une même fonction de test plusieurs fois avec différents jeux de données et paramètres, sans avoir à écrire une fonction distincte pour chaque cas.

**Pytest** compte 5 tests pour notre fonction test_requete_refusee, car nous avons défini cinq cas dans la liste CAS_REFUSES. Grâce à @pytest.mark.parametrize, chaque cas est exécuté individuellement comme un test distinct.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
UP017 [*] Use `datetime.UTC` alias
  --> maintai\train.py:58:36
   |
56 |         "target": TARGET,
57 |         "threshold": settings.threshold,
58 |         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
   |                                    ^^^^^^^^^^^^
59 |         "sklearn_version": sklearn.__version__,
60 |     
   |
help: Convert to `datetime.UTC` alias
   |
5  | import json
   - from datetime import datetime, timezone
6  + from datetime import datetime, timezone, UTC
7  |
--------------------------------------------------------------------------------
57 |         "threshold": settings.threshold,
   -         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
58 +         "trained_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
59 |         "sklearn_version": sklearn.__version__,
   |

Found 1 error.
[*] 1 fixable with `--fix`.
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

**`ruff check .`** : analyse le code Python pour détecter les erreurs potentielles, les imports inutilisés et les problèmes de style, sans exécuter les tests.

- **`python -m pytest`** : exécute les tests automatisés pour vérifier que le programme fonctionne correctement et respecte les résultats attendus.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
================================== 2 failed, 16 passed, 1 warning in 6.18s ===================================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

**test_missing_key_is_rejected** : une requête sans clé API reçoit 200 OK au lieu de 401 Unauthorized.

**test_wrong_key_is_rejected** : une requête avec une clé API incorrecte reçoit également 200 OK au lieu de 401 Unauthorized.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
"""Refuse la requête si la clé est absente ou fausse."""

    # Récupérer la clé attendue côté serveur
    expected_key = get_settings().api_key

    # Vérifier que le serveur possède une clé configurée
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured"
        )

    # Vérifier la clé envoyée par le client
    if not x_api_key or not secrets.compare_digest(
        x_api_key, expected_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

Après avoir écrit `security.py` 2 test échouent, parce que la fonction require_api_key() existe dans security.py, mais elle n'est pas encore appelée par le router. Les routes /v1 restent donc accessibles sans vérification de la clé API et retournent 200 OK au lieu de 401 Unauthorized.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================================== 18 passed, 1 warning in 2.77s ========================================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé |200|{"status": "ok","model_loaded": false}|
| `POST /v1/predict`, relevé normal, sans clé |401|{"detail": "Invalid or missing API key"} |
| `POST /v1/predict`, relevé normal, fausse clé |401|{"detail": "Invalid or missing API key"} |
| `POST /v1/predict`, relevé normal, bonne clé |200|{"failure_probability": 0.0163,"alert": false,"threshold": 0.3,"model_version": "2026-11-04T18:00:01Z"} |
| `POST /v1/predict`, 500 °C, sans clé |401|{"detail": "Invalid or missing API key"} |
| `POST /v1/predict`, 500 °C, bonne clé |422|{"detail": [{"type": "less_than_equal","loc": ["body","temperature_c"],"msg": "Input should be less than or equal to 150","input": 500,"ctx": {"le": 150}}]} |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

Sans clé API, la dépendance require_api_key() refuse la requête avec le code 401 avant que la validation des données soit effectuée. Avec une clé valide, l'authentification réussit et FastAPI vérifie ensuite les données. La température de 500 °C dépasse la limite autorisée et provoque donc une erreur 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

500 Error: Internal Server Error, on obtient le code 500 au lieu de 401, car le fichier .env n'est plus chargé au démarrage du serveur. La clé API attendue (get_settings().api_key) vaut donc None. Le serveur ne possède aucune clé configurée et renvoie une erreur 500, même si le client transmet une clé valide.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
try {
    const url = document.getElementById("url").value.trim().replace(/\/+$/, "");
    const key = document.getElementById("key").value.trim();

    if (!url || !key) {
        show("err", "Veuillez renseigner l'URL de l'API et la clé API.");
        return;
    }

    const resp = await fetch(`${url}/v1/predict`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": key
        },
        body: JSON.stringify(reading)
    });

    const data = await resp.json();

    if (!resp.ok) {
        show("err", `Erreur HTTP ${resp.status} : ${JSON.stringify(data.detail)}`);
        return;
    }

    const probability = (data.failure_probability * 100).toFixed(2);

    if (data.alert) {
        show("alert", `ALERTE DE MAINTENANCE\nProbabilité de panne : ${probability} %\nUne intervention est recommandée.`);
    } else {
        show("ok", `Fonctionnement normal\nProbabilité de panne : ${probability} %\nAucune alerte détectée.`);
    }

} catch (error) {
    show("err", "Impossible de contacter l'API. Vérifiez le serveur et la configuration CORS.");
    console.error(error);
}
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé |Fonctionnement normal Probabilité de panne : 12.93 % Aucune alerte détectée.|
| 500 °C, bonne clé |Erreur HTTP 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}] |
| relevé normal, fausse clé |Erreur HTTP 401 : "Invalid or missing API key" |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

Impossible de contacter l'API. Vérifiez le serveur et la configuration CORS.
Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

{"failure_probability":0.9475,"alert":true,"threshold":0.3,"model_version":"2026-11-04T18:00:01Z"}

Avec curl.exe : la requête est envoyée directement à FastAPI. curl n'applique pas la politique CORS, donc le serveur retourne une réponse JSON.

Avec le navigateur (port 5501) : le navigateur applique la politique CORS. Comme les ports 5501 et 8000 sont différents, les origines sont différentes. Le navigateur bloque donc la requête si le serveur n'autorise pas cette origine.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

```
================================== 4 failed, 19 passed, 1 warning in 3.16s ==================================
```

Sans headers=HEADERS, 4 tests échouent avec le code 401 car la clé API est absente. Le cinquième test (mauvaise route) passe avec le code 404, car l'URL /v1/doc n'existe pas et la route est vérifiée avant l'authentification.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
======================================== 23 passed, 1 warning in 2.95s ========================================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   -401 : clé API absente ou invalide.
   -422 : données envoyées invalides ou incorrectes.
   -403 : accès refusé malgré une authentification valide.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   Pour protéger la clé secrète et éviter qu'elle soit exposée publiquement.
   - .env contient la vraie clé API et n'est pas commité.
   - .env.example contient un exemple de configuration sans vraie clé et est commité.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Pour éviter son exposition dans l'historique du navigateur, les logs et les URL partagées.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   Il compare deux chaînes de manière sécurisée en limitant les risques d'attaques par analyse du temps de  comparaison.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est définie par le protocole, le nom d'hôte et le port. Non, elles sont différentes car leurs ports (5500 et 8000) ne sont pas identiques.

## 8. Le rendu Git

- Lien de la pull request : https://github.com/HajarSmh/Groupe-Samouh-Benchakroun-Halal-Bounjoume/tree/dev/Tps/Tp2
- Le tag `tp2` existe sur GitHub : non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 9. Ce qui reste flou

Tout est clair
