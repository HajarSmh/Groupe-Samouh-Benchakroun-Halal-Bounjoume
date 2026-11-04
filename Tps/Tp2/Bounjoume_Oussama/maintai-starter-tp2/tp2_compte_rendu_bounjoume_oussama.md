# Compte Rendu · TP2 : Clé API, CORS et Client Web (MaintAI)

**Groupe :** G6  ·  **Auteur :** Bounjoume Oussama  ·  **Membres :** Bounjoume Oussama, Samouh Hajar, Benchakroune Imane, Halal Saad  
**Date :** 28 Octobre 2026  ·  **Rendu GitHub :** Pull Request sur la branche `tp2`, Tag `tp2`

---

## 1. Activité 1 — Casser son API (`tests/test_casser.py`)

Les 5 cas de test paramétrés avec `@pytest.mark.parametrize` pour vérifier le rejet systématique des requêtes non conformes :

| Cas / Description | Requête (URL et variation corps) | Code attendu | Code obtenu |
| :--- | :--- | :---: | :---: |
| Champ manquant | `POST /v1/predict` (sans `temperature_c`) | `422` | `422` |
| Valeur absurde | `POST /v1/predict` (`temperature_c = 600`) | `422` | `422` |
| Texte au lieu d'un nombre | `POST /v1/predict` (`temperature_c = "chaud"`) | `422` | `422` |
| Champ en trop | `POST /v1/predict` (`champ_en_trop = 123`) | `422` | `422` |
| Mauvaise route | `POST /v1/doc` (au lieu de `/v1/predict`) | `404` | `404` |

### Résultat de Pytest avec `test_casser.py` (fin de TP1)

```text
======================================== 18 passed in 2.85s ========================================
```

---

## 2. Sprint 1 — La Clé API

### 2.1. Implémentation de `require_api_key()` (`maintai/api/security.py`)

```python
import secrets
from fastapi import Header, HTTPException, status
from maintai.config import get_settings

def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    settings = get_settings()
    
    # 1. Vérification si la clé serveur est configurée dans .env
    if settings.api_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )
    
    # 2. Vérification si l'en-tête X-API-Key est présent et correct
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
        
    return x_api_key
```

### 2.2. Protection du Router `/v1` (`maintai/api/main.py`)

La protection globale est appliquée à l'ensemble du routeur `/v1` :

```python
from maintai.api.security import require_api_key

router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

### 2.3. Bilan des tests Pytest (Sprint 1)

```text
======================================== 18 passed in 3.12s ========================================
```

*(Remarque : Avec la mise à jour des tests intégrant `HEADERS = {"X-API-Key": "test-key"}`, les 18 tests passent au vert).*

---

## 3. Sprint 2 — Le Client Web et CORS

### 3.1. Implémentation du `fetch` (`web/index.html`)

```javascript
try {
  const resp = await fetch(`${API_URL}/v1/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify(reading),
  });

  const data = await resp.json();

  if (!resp.ok) {
    show("err", `Erreur HTTP ${resp.status} : ${data.detail || "Requête refusée"}`);
    return;
  }

  show("ok", `Probabilité de panne : ${(data.failure_probability * 100).toFixed(1)}%`);
  if (data.alert) {
    show("alert", "ALERTE : Risque de défaillance élevé détecté !");
  }
} catch (e) {
  show("err", `API injoignable ou erreur réseau : ${e.message}`);
}
```

### 3.2. Résultat des tests fonctionnels depuis la page Web (Port 5500)

1. **Relevé normal avec bonne clé :** Succès `200 OK`, affichage de la probabilité de panne sans alerte.
2. **Relevé critique (Température 85 °C, Vibration 9 mm/s) :** Succès `200 OK`, déclenchement de l'alerte visuelle.
3. **Relevé hors borne (Température 500 °C) :** Code HTTP `422 Unprocessable Entity`, affichage du message d'erreur de validation Pydantic.
4. **Fausse clé API :** Code HTTP `401 Unauthorized`, message `"Clé API absente ou invalide"`.

### 3.3. Expérience CORS (Port 5501)

* **Comportement observé :** Lors du lancement de la page sur `http://localhost:5501`, le navigateur bloque la requête et affiche dans la console (F12) :
  `Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.`
* **Explication :** CORS est une sécurité imposée **par le navigateur**. Lors d'une requête cross-origin, le navigateur envoie d'abord une pré-requête `OPTIONS`. Si l'origine n'est pas dans la liste `MAINTAI_CORS_ORIGINS` lue depuis `.env`, le navigateur refuse d'exécuter la requête `POST`.
* **Pourquoi `curl.exe` continue de fonctionner sur le port 5501 ?**  
  `curl.exe` n'est pas un navigateur web. Il n'applique pas les restrictions Same-Origin Policy / CORS et envoie directement la requête HTTP POST à l'API. Tant que la clé `X-API-Key` est valide, l'API répond normalement à `curl`.

---

## 4. Décision d'Architecture — ADR 003

Consigné dans `docs/adr/003-securite.md` :

* **Transmission de la clé :** Transmise uniquement dans l'en-tête HTTP `X-API-Key` (jamais dans l'URL pour éviter son enregistrement dans les logs de reverse-proxy ou l'historique du navigateur).
* **Gestion des origines CORS :** Définies dans la variable `MAINTAI_CORS_ORIGINS` du fichier `.env`, évitant d'exposer l'API à tous les domaines (`*`).

---

## 5. Ticket de Sortie / Questions de Compréhension

1. **Quelle différence entre 401 et 422 ?**  
   * `401 Unauthorized` : L'identité du client est inconnue ou invalide (clé API absente ou fausse). L'API ne regarde même pas les données.
   * `422 Unprocessable Entity` : Le client est authentifié, mais la structure ou la valeur des données envoyées ne respecte pas le schéma (ex: température à 500 °C).
2. **Pourquoi la clé n'est-elle ni dans le code ni dans Git ?**  
   Une clé présente dans le code finit dans l'historique Git public et permanent, ce qui permettrait à quiconque d'accéder au service ou d'épuiser ses ressources. Le fichier `.env` conserve la clé en local sur le serveur et est exclu par `.gitignore`.
3. **Pourquoi curl fonctionne-t-il alors que la page du port 5501 est bloquée ?**  
   CORS est un mécanisme de protection exécuté exclusivement par les **navigateurs Web**. `curl` n'étant pas un navigateur, il ignore la politique CORS et seule la validité de la clé API compte.
4. **Bilan des tests avec `test_casser.py` adapté au TP2 :**

   ```text
   ======================================== 23 passed in 3.40s ========================================
   ```

---

## 6. Rendu Git

* **Lien de la Pull Request :** PR #2 (`tp2` -> `main`)
* **Tag GitHub :** `tp2` créé et pushed (`git tag tp2 && git push --tags`)
