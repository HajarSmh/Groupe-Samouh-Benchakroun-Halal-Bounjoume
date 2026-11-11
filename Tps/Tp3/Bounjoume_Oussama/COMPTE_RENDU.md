# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** Groupe 6  ·  **Auteur :** Bounjoume Oussama  ·  **Membres :** Bounjoume Oussama, Samouh Hajar, Benchakroune Imane, Halal Saad  ·  **Date :** 2026-11-11

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
FAILED tests/test_client.py::test_client_returns_prediction - NotImplementedError: TP3 sprint 2 : MaintaiClient.predict
FAILED tests/test_ui.py::test_ui_shows_the_prediction - AssertionError: assert len(at.error) > 0
=================== 5 failed, 18 passed in 2.14s ===================
```

**Quels fichiers de tests échouent, et quelle erreur donnent-ils ?**

`tests/test_client.py` échoue car la méthode `predict` du client lève une `NotImplementedError`, et `tests/test_ui.py` échoue car l'onglet de prédiction n'a pas encore le code pour afficher le résultat de l'API.

---

## 2. Lancer Streamlit

**Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?**

```
ModuleNotFoundError: No module named 'maintai'
```

**Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?**

`python -m` ajoute le dossier courant (`TP\TP3`) au `PYTHONPATH` (`sys.path`), ce qui permet à Python de trouver le package local `maintai`. La première commande cherche uniquement dans le dossier du script (`ui/`), où `maintai` n'existe pas en tant que module global.

---

## 3. Sprint 1 : l'onglet « Données »

**Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :**

```python
    c1, c2, c3 = st.columns(3)
    c1.metric("Relevés", len(df))
    c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
    c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

    variable = st.selectbox("Variable", FEATURES)
    tranches = pd.cut(df[variable], bins=10)
    taux = df.groupby(tranches, observed=True).failure.mean()
    taux.index = [round(i.mid) for i in taux.index]  # le milieu de chaque tranche
    st.subheader(f"Taux de panne selon {variable}")
    st.bar_chart(taux)

    st.subheader("Température et vibration (500 relevés)")
    echantillon = df.sample(500, random_state=0).assign(panne=lambda d: d.failure.map({0: "non", 1: "oui"}))
    st.scatter_chart(echantillon, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6 % |
| Température moyenne | 59.8 °C |

**Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?**

Le taux de panne augmente fortement et de manière quasi-monotone à mesure que la vibration s'élève (les fortes vibrations sont des indicateurs majeurs de panne).

**Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?**

Le mot « relance » s'imprime à nouveau dans le terminal à chaque interaction avec un widget. Cela montre que Streamlit réexécute l'intégralité du script Python de haut en bas dès qu'une valeur change dans l'interface.

**À quoi sert `@st.cache_data` sur la fonction `charger` ?**

Il permet de conserver le DataFrame en mémoire cache après la première lecture du fichier CSV, évitant ainsi de relire le fichier sur le disque à chaque réexécution du script provoquée par les interactions de l'utilisateur.

---

## 4. Sprint 2 : l'onglet « Prédiction »

**Méthode `predict` (`maintai/client.py`) :**

```python
    def predict(self, reading: dict) -> dict:
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        r = self.http.post("/v1/predict", json=reading, headers=headers)
        if r.status_code != 200:
            raise APIError(r.status_code, r.json().get("detail"))
        return r.json()
```

**Dernière ligne de `python -m pytest` à la fin du sprint 2 :**

```
=================== 23 passed in 5.56s ===================
```

**Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :**

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne : 95 % + encadré d'alerte rouge |
| valeurs par défaut, fausse clé | Avertissement : Erreur 401 : Clé API absente ou invalide |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Erreur : API injoignable : uvicorn est-il lancé ? |

**Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?**

CORS est une règle de sécurité imposée par les navigateurs web lors des requêtes HTTP asynchrones (comme les appels `fetch` front-end du TP2). Dans le TP3, la requête est exécutée directement par le serveur Python via `httpx`, en arrière-plan, et non par le navigateur web lui-même. Les restrictions CORS ne s'appliquent donc pas.

---

## 5. Questions de compréhension

**Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**

Dans le TP2, c'est le navigateur web du client via JavaScript (`fetch`). Dans le TP3, c'est le serveur Python de Streamlit via la bibliothèque `httpx`.

**Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?**

Parce qu'ils injectent un `TestClient` FastAPI directement dans l'attribut `http` du client de test, simulant les requêtes entièrement en mémoire sans lancer de serveur réseau réel.

**Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?**

Streamlit est parfait pour une démonstration rapide ou un outil interne de maintenance car il permet de concevoir des interfaces riches en quelques lignes de Python. Pour une application finale destinée au grand public, une application web dédiée (HTML/JS/React) offre une maîtrise complète de l'ergonomie et du design UI.

---

## 6. Ce qui reste flou

Rien de particulier, l'architecture client/API avec Streamlit est claire.
