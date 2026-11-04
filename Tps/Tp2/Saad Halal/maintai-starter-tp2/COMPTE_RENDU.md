# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G6 ·  **Membres :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama] ·  **Date :** 04/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | vibration manquante |422|422 Unprocessable Content |
| 2 | vibration = 800 |422|422 Unprocessable Content |
| 3 | vibration = eleve |422|422 Unprocessable Content |
| 4 | champ en trop |422|422 Unprocessable Content |
| 5 | mauvaise route /doc |404|404 Not Found |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

- Non, toutes les prévisions étaient correctes. Les cinq scénarios de requêtes refusées ont retourné les codes HTTP attendus : 422 pour les données invalides et 404 pour une route inexistante.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
============================================================== 19 passed, 1 warning in 15.58s ===============================================================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

- Il permet de tester les cinq scénarios de requêtes refusées avec les mêmes instructions.
- Pytest compte 5 tests pour cette fonction, car la liste CAS_REFUSES contient 5 jeux de paramètres. Chaque jeu de paramètres correspond à une exécution indépendante de la fonction de test.


## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
(.venv) PS C:\Users\dell\Desktop\GRP App Intelligente\Groupe-Samouh-Benchakroun-Halal-Bounjoume\Tps\Tp1\maintai-starter-tp1> ruff check .
UP017 [*] Use `datetime.UTC` alias
  --> maintai\train.py:58:36
   |
56 |         "target": TARGET,
57 |         "threshold": settings.threshold,
58 |         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
59 |         "sklearn_version": sklearn.__version__,
   |
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

- ruff check . : vérifie la qualité du code Python (syntaxe, imports inutilisés, erreurs potentielles et respect des règles de style), sans exécuter le programme.

- python -m pytest : exécute les tests automatisés pour vérifier que le programme fonctionne correctement et retourne les résultats attendus.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
================================== 2 failed, 16 passed, 1 warning in 6.18s ===================================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

- test_missing_key_is_rejected : une requête sans clé API reçoit 200 OK au lieu de 401 Unauthorized.

- test_wrong_key_is_rejected : une requête avec une clé API incorrecte reçoit également 200 OK au lieu de 401 Unauthorized.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(
    x_api_key: str | None = Header(default=None)
) -> None:
    """Refuse la requête si la clé est absente ou fausse."""

    # Récupérer la clé API configurée sur le serveur
    api_key = get_settings().api_key

    # Vérifier que le serveur possède une clé API
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur"
        )

    # Vérifier que la clé reçue est présente et correcte
    if x_api_key is None or not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide"
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(require_api_key)]
)
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

- Après avoir écrit security.py 2 test échouent, parce que la fonction require_api_key() existe dans security.py, mais elle n'est pas encore appelée par le router. Les routes /v1 restent donc accessibles sans vérification de la clé API et retournent 200 OK au lieu de 401 Unauthorized.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================================================================= 18 passed, 1 warning in 40.48s =======================================================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé |200|"status": "ok","model_loaded": false |
| `POST /v1/predict`, relevé normal, sans clé |401|"detail": "Clé API absente ou invalide" |
| `POST /v1/predict`, relevé normal, fausse clé |401|"detail": "Clé API absente ou invalide" |
| `POST /v1/predict`, relevé normal, bonne clé |503|"failure_probability": 0.9553,"alert": true,"threshold": 0.3,"model_version": "2026-11-04T20:44:30Z"|
| `POST /v1/predict`, 500 °C, sans clé |401|"detail": "Clé API absente ou invalide"|
| `POST /v1/predict`, 500 °C, bonne clé |422|{"detail": [{"type": "less_than_equal","loc": ["body","temperature_c"],"msg": "Input should be less than or equal to 150","input": 500,"ctx": {"le": 150}}]}|

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

- Sans clé API (401) : l'API refuse la requête immédiatement, car la clé est absente. Elle ne vérifie donc pas la température.
- Avec une bonne clé API (422) : l'authentification réussit, puis FastAPI vérifie les données. La température de 500 °C dépasse la limite autorisée de 150 °C, donc la requête est rejetée.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

- 500 | "detail": "Clé API non configurée sur le serveur" , Ce n'est pas 401, car 401 signifie que la clé reçue est absente ou incorrecte

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {

  const reading = Object.fromEntries(
    FEATURES.map(f => [
      f,
      Number(document.getElementById(f).value)
    ])
  );

  // Récupérer l'URL et la clé API
  const url = document.getElementById("url").value.trim();
  const cle = document.getElementById("key").value.trim();

  try {
    // Envoyer le relevé à l'API
    const resp = await fetch(`${url}/v1/predict`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "X-API-Key": cle
      },

      body: JSON.stringify(reading)
    });

    // Récupérer la réponse JSON
    const data = await resp.json();

    // Vérifier les erreurs HTTP
    if (!resp.ok) {
      show("err", `Erreur ${resp.status} : ${
        data.detail || "Une erreur est survenue"
      }`);
      return;
    }

    // Afficher les résultats de prédiction
    const message =
      `Probabilité de panne : ${data.failure_probability}\n` +
      `Alerte : ${data.alert}`;

    // Afficher selon le niveau d'alerte
    show(data.alert ? "alert" : "ok", message);

  } catch (e) {
    // API arrêtée ou erreur CORS
    show("err", `Erreur de connexion : ${e.message}`);
  }

});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé |Probabilité de panne : 0.9475 Alerte : true|
| 500 °C, bonne clé |Erreur 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}]|
| relevé normal, fausse clé |Erreur 401 : Clé API absente ou invalide|

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

- Impossible de contacter l'API. Vérifiez le serveur et la configuration CORS. Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

- Avec `curl.exe` : la requête est envoyée directement à FastAPI, et avec le navigateur (port 5501) : le navigateur applique la politique CORS. 

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

================================== 4 failed, 19 passed, 1 warning in 13.95s ==================================

- Sans headers=HEADERS, 4 tests échouent avec le code 401 car la clé API est absente. Le cinquième test (mauvaise route) passe avec le code 404, car l'URL /v1/doc n'existe pas et la route est vérifiée avant l'authentification.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
====================== 23 passed, 1 warning in 12.64s ======================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?

- 401 : indique que l'authentification a échoué, car la clé API est manquante ou incorrecte.

- 422 : signifie que les informations transmises ne respectent pas les critères de validation attendus.

- 403 : indique que l'utilisateur est bien authentifié, mais qu'il ne possède pas les permissions nécessaires.

2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
- Pour garantir la confidentialité de la clé API et empêcher son accès par des personnes non autorisées.

- .env : stocke la véritable clé API et reste exclu du dépôt Git.

- .env.example : présente les variables nécessaires avec des valeurs fictives et peut être partagé sur Git.

3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?

- Parce que les en-têtes HTTP permettent de transmettre les informations d'authentification sans les afficher directement dans l'adresse, ce qui réduit les risques de fuite dans les historiques et les journaux.

4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?

- Il permet de comparer deux valeurs sensibles en limitant les variations du temps de comparaison, afin de mieux se protéger contre les timing attacks.

5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?

- Une origine correspond à l'association de trois éléments : le protocole, le nom d'hôte et le numéro de port. Ces deux adresses représentent donc des origines différentes puisque leurs numéros de port ne sont pas les mêmes.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui / non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 9. Ce qui reste flou

Rien.
