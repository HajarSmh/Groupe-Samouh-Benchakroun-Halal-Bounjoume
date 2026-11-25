# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
================ 2 failed, 25 passed, 1 warning in 7.09s ================
```

Quels sont les deux tests qui échouent, et pourquoi ?

- `test_installed_version_matches_the_code` : `PackageNotFoundError`. Le package `maintai`
  n'est pas encore installé
- `test_command_is_declared` : la commande `maintai-predict` n'existe pas.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "pandas>=2.2",
    "numpy>=1.26",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

`dependencies` contient seulement ce dont le code de `maintai/` a besoin pour fonctionner.
`pytest` sert seulement aux développeurs pour tester, et `fastapi` seulement pour lancer l'API.
Ils sont dans des groupes optionnels (`dev`, `api`) : on les installe seulement si on en a besoin.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne de machines à partir de relevés de capteurs
Home-page: 
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
===================== 27 passed, 1 warning in 7.71s =====================
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

Depuis `C:\Users\Imane\AppData\Local\Temp`, les deux commandes fonctionnent :

- `maintai-predict 72 6 85 15000` affiche `Probabilité de panne : 95 % (ALERTE)`.
- `maintai.__file__` affiche
  `...\Tps\Tp4\Imane_Benchakroun\maintai-starter-tp4\maintai\__init__.py`.

Python trouve le code dans notre dossier TP4. `pip install -e .` n'a pas copié le code : il a
mis dans le `.venv` un lien vers le dossier du projet. Comme le package est installé, la commande
marche depuis n'importe quel dossier.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui, le nouveau message (`Risque de panne : 95 % (ALERTE)`) s'affiche tout de suite, sans
réinstaller. Avec `pip install -e .`, le `.venv` contient seulement un lien vers notre dossier :
Python lit toujours nos fichiers, donc chaque modification est visible au lancement suivant.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
Mode                 LastWriteTime         Length Name                   
----                 -------------         ------ ----                   
-a----        11/11/2026   6:01 PM          11625 maintai-0.2.0-py3-none-
                                                  any.whl                
-a----        11/11/2026   6:01 PM          12231 maintai-0.2.0.tar.gz 
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```
non,car `packages.find` n'inclut que le dossier `maintai/`. Le wheel contient
donc seulement le code du package, plus ses informations (`dist-info`)

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : ...\essai\.venv\Lib\site-packages\models\model.joblib` : le wheel ne contient pas le modèle |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | `Probabilité de panne : 95 % (ALERTE)`, mais avec 3 avertissements `InconsistentVersionWarning` (modèle écrit avec scikit-learn 1.8.0, lu avec 1.9.1) |
| après `pip install scikit-learn==1.8.0` | `Probabilité de panne : 95 % (ALERTE)`, sans avertissement |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Le wheel demande seulement `scikit-learn>=1.5`, donc pip a installé la version la plus récente,
1.9.1. Mais le modèle a été entraîné et sauvegardé avec la version 1.8.0. scikit-learn prévient
qu'un modèle relu avec une autre version peut donner des résultats faux.
La ligne qui l'explique est `"sklearn_version": "1.8.0"`.
Pour livrer un modèle, il faut donc trois choses : le code (le wheel), le modèle (`models/`)
et les versions exactes (`requirements.txt`).

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?

   `dependencies` donne des versions minimales (`>=`) : le package peut s'installer à côté
   d'autres packages. `requirements.txt` donne les versions exactes (`==`) : on retrouve
   exactement l'environnement qui a entraîné le modèle.

2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?

   `pip install -e .` crée un lien vers notre dossier : chaque modification du code est visible
   tout de suite. C'est pour développer.
   Le wheel installe une copie du code : modifier le dossier TP4 ne change plus rien. C'est pour
   livrer le package à quelqu'un d'autre.

3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?

   C'est une commande qui appelle une fonction Python : `maintai-predict` appelle `main` dans
   `maintai/cli.py`. pip crée le fichier `maintai-predict.exe` à l'installation, dans le dossier
   `.venv\Scripts`.

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui / non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? oui / non

## 6. Ce qui reste flou

…
