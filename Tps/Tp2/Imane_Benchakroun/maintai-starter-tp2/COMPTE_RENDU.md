# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | champ manquant |422 | 422 Unprocessable Entity|
| 2 | valeur absurde |422 |422 Unprocessable Entity |
| 3 | texte au lieu d'un nombre |422 | 422 Unprocessable Entity |
| 4 | champ en trop |422 | 422 Unprocessable Entity |
| 5 | mauvaise route |422 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?
because la vérification de la route se fait en premier temps
…

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
======================================= 18 passed, 1 warning in 2.64s ========================================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

…parametrize permet d’écrire une seule fonction de test et de la faire exécuter une fois par ligne de la liste CAS_REFUSES

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
Found 2 errors.
ruff check . --fix
Found 4 errors (4 fixed, 0 remaining).
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

…python -m pytest exécute le code et vérifie ce qu’il fait : il envoie des requêtes à l’API et compare les réponses obtenues avec les réponses attendues. ruff check . lit le code sans l’exécuter et signale ce qui est mal écrit.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
=================== 2 failed, 16 passed, 1 warning in 4.31s ====================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

FAILED tests/test_security.py::test_missing_key_is_rejected - AssertionError: assert 200 == 401
FAILED tests/test_security.py::test_wrong_key_is_rejected - assert 200 == 401

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
expected_key = get_settings().api_key

    if expected_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )

    if x_api_key is None or not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?
deux tests échouent,car
…

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================================ 18 passed, 1 warning in 2.66s =============================================```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | | |
| `POST /v1/predict`, relevé normal, sans clé | | |
| `POST /v1/predict`, relevé normal, fausse clé | | |
| `POST /v1/predict`, relevé normal, bonne clé | | |
| `POST /v1/predict`, 500 °C, sans clé | | |
| `POST /v1/predict`, 500 °C, bonne clé | | |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

…Sans clé, la requête est refusée en 401 avant que le schéma ne soit examiné. Avec la clé, elle atteint la validation, qui rejette 500 °C en 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

…puisque on a obtené erreur 500 et non 401 donc le serveur ne lit pas la clé.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
  const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
  // TODO (TP2) : Envoyez reading en POST JSON ...
  const url = document.getElementById("url").value;
  const cle = document.getElementById("key").value;
  const adresse = url + "/v1/predict";

  try {
    const resp = await fetch(adresse, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cle },
      body: JSON.stringify(reading),
    });
    const data = await resp.json();

    if (!resp.ok) {
      show("err", "Erreur " + resp.status + " : " + JSON.stringify(data.detail));
    } else if (data.alert) {
      show("alert", "ALERTE : probabilité de panne = " + data.failure_probability);
    } else {
      show("ok", "OK : probabilité de panne = " + data.failure_probability);
    }
  } catch (e) {
    show("err", "API injoignable ou bloquée (CORS)");
  }
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | ALERTE : probabilité de panne = 0.9475|
| 500 °C, bonne clé |Erreur 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}] |
| relevé normal, fausse clé | Erreur 401 : "Clé API absente ou invalide"|

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

…la page : API injoignable ou bloquée (CORS)
console : has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

…CORS est une règle du navigateur, qui protège l’utilisateur. curl, Java ou Python ne l’appliquent pas. Seule la clé protège l’API.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

…============================== 4 failed, 19 passed, 1 warning in 4.06s ==============================
Sans headers=HEADERS, 4 tests échouent : champ manquant, valeur absurde, texte au lieu d’un nombre et champ en trop. Chacun reçoit 401 au lieu de 422, car la clé API est vérifiée avant les données.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
=================================== 23 passed, 1 warning in 4.99s ===================================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   …Le 401 signifie que l’API ne sait pas qui appelle : la clé est absente ou fausse. Le 422 signifie que l’appelant est accepté, mais que les données envoyées sont invalides.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   ….env contient la vraie clé de ma machine : il est ignoré par Git (.gitignore) et n’est jamais commité. .env.example contient une fausse valeur (changez-moi) : il dit quoi configurer sans révéler de secret. C’est lui qui est commité.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   …Une URL est enregistrée partout : journaux du serveur, historique du navigateur, liens copiés. Une clé placée dans l’URL se retrouverait donc stockée en clair à plusieurs endroits.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   …Avec ==, la comparaison s’arrête au premier caractère différent : la réponse est plus rapide quand la clé fausse commence par des caractères justes. En mesurant la durée de la réponse, un attaquant pourrait deviner la clé caractère par caractère. compare_digest compare toujours en un temps constant, quel que soit le nombre de caractères justes, donc la durée ne révèle rien.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   …Une origine est la combinaison d’un schéma (http), d’un domaine (localhost) et d’un port (5500). Deux adresses qui diffèrent sur l’un des trois sont deux origines différentes.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui / non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 9. Ce qui reste flou

…
