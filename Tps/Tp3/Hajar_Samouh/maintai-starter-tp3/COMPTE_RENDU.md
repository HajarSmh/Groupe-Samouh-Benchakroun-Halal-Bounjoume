# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G6  ·  **Membres :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]  ·  **Date :** 11/11/2026
> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
=========================== 5 failed, 18 passed, 1 warning in 8.47s ===============================
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

> tests/test_client.py (3 tests : test_client_returns_prediction, test_client_wrong_key_raises_401, test_client_bad_reading_raises_422) : NotImplementedError: TP3 sprint 2 : MaintaiClient.predict, car la méthode predict du client n'est pas encore écrite.
> tests/test_ui.py (2 tests : test_ui_shows_the_data, test_ui_shows_the_prediction) : IndexError: list index out of range, car la page n'affiche encore aucun indicateur (st.metric) : seuls des st.info provisoires sont présents, donc at.metric[0] et at.metric[-1] n'existent pas.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
2026-11-11 16:21:53.882 Uncaught app execution
Traceback (most recent call last):
  File "C:\Users\PC\Desktop\Groupe App Intelligente\.venv\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "C:\Users\PC\Desktop\Groupe App Intelligente\.venv\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 924, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\PC\Desktop\Groupe App Intelligente\Tps\Tp3\Hajar_Samouh\maintai-starter-tp3\ui\app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient
ModuleNotFoundError: No module named 'maintai'
```
Dans le navigateur
ModuleNotFoundError: No module named 'maintai'

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

Python cherche les modules dans une liste de dossiers (sys.path) qui dépend de la façon de lancer le programme. Avec streamlit run ui/app.py, Python ajoute le dossier du script (TP3/ui/) : le dossier maintai/ n'y est pas, donc import maintai échoue. Avec python -m streamlit run ui/app.py, Python ajoute le dossier courant (TP3/), qui contient maintai/ : l'import réussit.

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
st.subheader(f"Taux de panne selon {variable}")
st.bar_chart(taux)

nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
st.subheader("Température et vibration")
st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés |5000 |
| Taux de panne |13.6% |
| Température moyenne |59.8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente avec la vibration : les premières tranches (vibration faible) ont un taux proche de 0 (1.1), les dernières (vibration élevée) un taux bien plus fort. (21.1)

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

relance s'affiche dans le terminal à chaque ouverture de la page et à chaque interaction avec un widget hors formulaire (changer la variable dans la liste déroulante, modifier l'URL ou la clé dans la barre latérale). Cela montre que Streamlit ré-exécute tout le script ui/app.py de la première à la dernière ligne à chaque interaction, avec la nouvelle valeur du widget, puis renvoie la nouvelle page.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Comme tout le script est relancé à chaque clic, sans cache le fichier CSV serait relu depuis le disque à chaque fois. Avec @st.cache_data, le CSV n'est lu qu'à la première exécution ; ensuite Streamlit renvoie le même tableau gardé en mémoire, ce qui rend la page rapide.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
def predict(self, reading: dict) -> dict:
    headers = {"X-API-Key": self.api_key} if self.api_key else {}
    r = self.http.post("/v1/predict", json=reading, headers=headers)
    if r.status_code != 200:
        raise APIError(r.status_code, r.json().get("detail"))
    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
================================== 23 passed, 1 warning in 7.00s ==================================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé |Probabilité de panne 95 % |
| valeurs par défaut, fausse clé |Erreur 401 : Clé API absente ou invalide |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) |API injoignable : uvicorn est-il lancé ? Vérifiez l'URL dans la barre latérale. |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

CORS est une règle appliquée par le navigateur : il bloque une page d'une origine (port 5500 au TP2) qui fait un fetch vers une autre origine (port 8000) si le serveur ne l'autorise pas. Ici, le navigateur ne contacte jamais l'API : il parle seulement à Streamlit (port 8501). C'est le serveur Streamlit, en Python, qui envoie la requête à l'API avec httpx, comme le feraient curl ou le programme Java. Il n'y a pas de navigateur, donc pas d'en-tête Origin et pas de contrôle CORS. La clé API, elle, reste vérifiée par l'API (401 si elle est fausse).

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   > Dans la page du TP2, c'est le navigateur de l'utilisateur, qui exécute le fetch en JavaScript. Dans Streamlit, c'est le serveur Streamlit (du code Python avec MaintaiClient et httpx) ; le navigateur affiche seulement la page.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   > Parce que MaintaiClient reçoit en paramètre (http=client) le TestClient de FastAPI. La requête est envoyée directement à l'application FastAPI, dans le même processus Python, sans réseau ni serveur lancé. C'est possible parce que predict utilise self.http.post(...) et non httpx.post(...).
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   > Pour une démonstration à un client, je choisirais la page HTML + JavaScript : on maîtrise entièrement l'apparence (identité visuelle, ergonomie), ce qui donne un rendu plus soigné, au prix de plus de travail. Pour le technicien de maintenance, je choisirais Streamlit : c'est un outil interne où l'on veut surtout voir les données et obtenir une prédiction ; il est rapide à écrire et à faire évoluer en Python (la langue de l'équipe), et la clé API reste côté serveur.

## 6. Le rendu Git

- Lien de la pull request : https://github.com/HajarSmh/Groupe-Samouh-Benchakroun-Halal-Bounjoume/tree/dev/Tps/Tp3/Hajar_Samouh/maintai-starter-tp3
- Le tag `tp3` existe sur GitHub : non
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? oui / non

## 7. Ce qui reste flou

Tout est clair
