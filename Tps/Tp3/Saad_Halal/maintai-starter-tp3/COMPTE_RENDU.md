# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G6 ·  **Membres :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama] ·  **Date :** 11/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
========================================================== 5 failed, 18 passed, 1 warning in 20.70s ==========================================================
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

- Les échecs viennent de tests/test_client.py (3 tests) et de tests/test_ui.py (2 tests), soit 5 échecs. Les tests du client échouent avec NotImplementedError, car MaintaiClient.predict n'est pas encore écrite. Les tests de l'interface échouent parce que ui/app.py n'affiche pour l'instant que des messages d'information : il n'y a ni indicateur, ni résultat de prédiction.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'

File "C:\Users\dell\Desktop\GRP App Intelligente\Groupe-Samouh-Benchakroun-Halal-Bounjoume\Tps\Tp3\Saad_Halal\maintai-starter-tp3\ui\app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

- Python recherche les modules dans les dossiers définis par `sys.path`, qui dépend de la commande utilisée pour lancer le programme. Avec `streamlit run ui/app.py`, Python cherche d'abord dans `TP3\ui\`, où le dossier `maintai\` est introuvable. En revanche, avec `python -m`, le dossier racine `TP3\` est ajouté à `sys.path`, ce qui permet de trouver et d'importer correctement `maintai`.

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
# 1. Trois indicateurs côte à côte (le premier est le nombre de relevés)
    c1, c2, c3 = st.columns(3)
    c1.metric("Relevés", len(df))
    c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
    c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")
 
    # 2. Choix d'une variable
    variable = st.selectbox("Variable", FEATURES)
 
    # 3. Taux de panne par tranche de cette variable
    tranches = pd.cut(df[variable], bins=10)
    taux = df.groupby(tranches, observed=True).failure.mean()
    taux.index = [round(i.mid, 1) for i in taux.index]  # des nombres, pas du texte
    st.subheader(f"Taux de panne selon {variable}")
    st.bar_chart(taux)
 
    # 4. Nuage de points température / vibration, coloré selon la panne
    nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
    st.subheader("Température et vibration")
    st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6% |
| Température moyenne | 59.8°C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

- Le taux de panne augmente progressivement avec la vibration. Il passe de presque 0 pour les faibles vibrations à 1 (100 %) à partir de 12,2 mm/s. Cela montre qu'une vibration élevée est fortement associée à un risque de panne important.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

- Le mot « relance » s'affiche dans le terminal à chaque interaction avec un widget. Cela montre que Streamlit réexécute tout le script ui/app.py, de la première à la dernière ligne, à chaque fois que l'on touche un widget, puis renvoie la nouvelle page au navigateur.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

- @st.cache_data permet de mettre en cache les données CSV pour éviter de les relire à chaque interaction. Le fichier est chargé une seule fois, puis les données sont réutilisées depuis la mémoire, ce qui accélère l'application Streamlit.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
def predict(self, reading: dict) -> dict:
        """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        r = self.http.post("/v1/predict", json=reading, headers=headers)
        if r.status_code != 200:
            raise APIError(r.status_code, r.json().get("detail"))
        return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
====================================================== 23 passed, 1 warning in 50.99s =======================================================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne 95 % |
| valeurs par défaut, fausse clé | Erreur 401 : Clé API absente ou invalide |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | API injoignable : uvicorn est-il lancé ? |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

- CORS est une sécurité appliquée par le navigateur pour contrôler les requêtes entre différentes origines. Avec Streamlit, les requêtes sont envoyées directement par le serveur Python via `httpx`, donc aucune vérification CORS n'est nécessaire. En revanche, la clé API reste obligatoire pour sécuriser l'accès à l'API.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   - Dans le TP2, le navigateur envoie la requête via JavaScript (fetch). Dans Streamlit, c'est le serveur Python qui l'envoie via httpx.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   - Parce qu'ils utilisent TestClient de FastAPI pour tester directement l'application, sans démarrer de serveur ni utiliser le réseau.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   - Pour une démonstration à un client, je choisirais HTML + JavaScript pour sa personnalisation et son aspect professionnel. Pour un technicien de maintenance, je choisirais Streamlit pour sa simplicité, sa rapidité de développement et ses fonctionnalités d'exploration des données et de prédiction.

## 6. Le rendu Git

- Lien de la pull request : …
- Le tag `tp3` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? oui / non

## 7. Ce qui reste flou

Rien.
