# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :**  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
=============== 5 failed, 18 passed, 1 warning in 5.45s ===============
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?
FAILED tests/test_client.py::test_client_returns_prediction - NotImplementedError: TP3 sprint 2 : MaintaiClient.predict
FAILED tests/test_client.py::test_client_wrong_key_raises_401 - NotImplementedError: TP3 sprint 2 : MaintaiClient.predict
FAILED tests/test_client.py::test_client_bad_reading_raises_422 - NotImplementedError: TP3 sprint 2 : MaintaiClient.predict
FAILED tests/test_ui.py::test_ui_shows_the_data - IndexError: list index out of range
FAILED tests/test_ui.py::test_ui_shows_the_prediction - IndexError: list index out of range

…

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

Python ne cherche `maintai` que dans certains dossiers. Avec `streamlit run ui/app.py`, il
cherche dans `ui\`, où `maintai\` n'existe pas : erreur. Avec `python -m streamlit run ui/app.py`,
il cherche aussi dans le dossier où on se trouve (`TP3\`), qui contient `maintai\`

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
c1, c2, c3 = st.columns(3)
c1.metric("Relevés", len(df))
c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

variable = st.selectbox("Variable", FEATURES)
tranches = pd.cut(df[variable], bins=10)
taux = df.groupby(tranches, observed=True).failure.mean()
taux.index = [round(i.mid, 1) for i in taux.index]
st.bar_chart(taux)

nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```


| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6 |
| Température moyenne | 59.8 |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

…avec augmentation de vibrations le taux de panne augmente 

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

…avec chaque touche on voit "relance" qui s'affiche sur le terminal.Donc streamlit relance tous le script à chaque fois.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

…Comme le script est relancé à chaque clic, sans cache le fichier CSV serait relu à chaque fois.


## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
headers = {"X-API-Key": self.api_key} if self.api_key else {}
r = self.http.post("/v1/predict", json=reading, headers=headers)
if r.status_code != 200:
   raise APIError(r.status_code, r.json().get("detail"))
return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
=============== 1 failed, 22 passed, 1 warning in 6.10s ===============
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | 200 OK |
| valeurs par défaut, fausse clé | 401 Unauthorized |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Failed to fetch. |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

…CORS est une règle du navigateur. Au cas où le navigateur appelle l'API, il
vérifie CORS. Avec Streamlit, c'est le serveur Python qui appelle l'API, pas le navigateur, il n'y a donc pas de vérification CORS. La clé API reste quand même vérifiée.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
Dans le TP2, c'est le navigateur qui envoie la requête (avec `fetch` en JavaScript).
Dans Streamlit, c'est le serveur Python qui l'envoie (avec `MaintaiClient` et httpx) ;
le navigateur affiche seulement la page.     
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
Les tests donnent à `MaintaiClient` un client de test (`http=client`) qui envoie la requête
directement à l'application FastAPI, en mémoire, sans passer par le réseau.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
Pour une démonstration : Streamlit car On l'écrit vite en Python seulement et on a tout de
suite des graphiques et des onglets.
Pour l'application d'un technicien : la page HTML + JavaScript car On contrôle mieux son apparence.

## 6. Le rendu Git

- Lien de la pull request : …
- Le tag `tp3` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? oui / non

## 7. Ce qui reste flou

…
