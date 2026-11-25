# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G6  ·  **Réalisateur : Oussama Bounjoume**  **Membres :** Oussama Bounjoume - Samouh Hajar - Benchakroune Imane - Halal Saad  ·  **Date :** 11/11/2026

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
========================== 2 failed, 25 passed, 1 warning in 6.71s ================================
```

**Quels sont les deux tests qui échouent, et pourquoi ?**

- `test_installed_version_matches_the_code` : `importlib.metadata.PackageNotFoundError: No package metadata was found for maintai`. Le test demande à Python la version installée de maintai (`version("maintai")`), mais pip ne connaît aucun package de ce nom.
- `test_command_is_declared` : `AssertionError: assert 'maintai-predict' in [...]`. La commande `maintai-predict` n'existe pas dans la liste des commandes (`console_scripts`) installées.

Dans les deux cas, la cause est que maintai n'est pas encore installé comme package : il n'y a pas eu de `pip install -e .`, et `pyproject.toml` n'avait pas encore de `[project.scripts]`. Les autres tests passent, car ils importent simplement le code depuis le dossier du projet.

---

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

**Vos sections `dependencies` et `[project.scripts]` :**

```toml
dependencies = [
    "numpy>=1.26",
    "pandas>=2.2",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

**Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?**

`dependencies` ne contient que ce dont le code de maintai a besoin pour fonctionner chez tout utilisateur (charger le modèle, prédire, appeler l'API). Un collègue qui lance seulement `maintai-predict` n'a pas besoin de `pytest` (outil de développement) ni de `fastapi` (nécessaire seulement pour héberger l'API). Ils sont donc dans des groupes optionnels (`dev`, `api`, `ui`) installés à la demande, par exemple `pip install -e ".[api,dev]"`. Cela garde l'installation légère et évite d'imposer des bibliothèques inutiles.

**Sortie de `pip show maintai` (les quatre premières lignes) :**

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne de machines à partir de relevés de capteurs : modèle, API, client et commande maintai-predict
```

**Dernière ligne de `python -m pytest` à la fin du sprint 1 :**

```
============================ 27 passed, 1 warning in 6.12s ==================================
```

**Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de maintai ?**

```
Probabilité de panne : 95 % (ALERTE)
C:\Users\PC\Desktop\Groupe App Intelligente\Tps\Tp4\Hajar_Samouh\maintai-starter-tp4\maintai\__init__.py
```

Même depuis un autre dossier, la commande fonctionne et `maintai.__file__` pointe vers le dossier du projet. `pip install -e .` a écrit dans `.venv\Lib\site-packages` un lien vers ce dossier ; Python trouve donc maintai partout, sans dépendre du dossier courant.

**Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?**

```
Probabilité de panne estimée : 95 % (ALERTE)
```

Oui, le nouveau message s'affiche tout de suite. L'installation « éditable » ne copie pas le code : elle crée seulement un lien vers votre dossier. Le programme exécute donc toujours la version actuelle du fichier, sans réinstallation.

---

## 3. Sprint 2 : construire et installer le wheel

**Sortie de `dir dist` après `python -m build` :**

```
Répertoire : C:\Users\PC\Desktop\Groupe App Intelligente\Tps\Tp4\Hajar_Samouh\maintai-starter-tp4\dist

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        11/11/2026     17:36          11647 maintai-0.2.0-py3-none-any.whl
-a----        11/11/2026     17:36          12262 maintai-0.2.0.tar.gz
```

**Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?**

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

Non : ni le modèle (`models/`), ni les tests (`tests/`), ni `ui/` ne sont dans le wheel. Dans `pyproject.toml`, `[tool.setuptools.packages.find]` avec `include = ["maintai*"]` limite le package au seul dossier `maintai/` (le code). Le wheel contient donc les fichiers `maintai/...` et les métadonnées. Le modèle est un fichier de données produit par l'entraînement : il doit être livré à part.

**Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :**

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | Modèle introuvable |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | Probabilité de panne estimée : 95 % (ALERTE) |
| après `pip install scikit-learn==1.8.0` | Probabilité de panne estimée : 95 % (ALERTE) |

**D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?**

Le modèle a été sauvegardé (joblib) avec une certaine version de scikit-learn, mais l'environnement neuf a installé une autre version. Relire un modèle avec une version différente peut donner des résultats faux, d'où l'avertissement. La ligne `"sklearn_version"` de `models/model_info.json` indique la version qui a écrit le modèle : c'est celle qu'il faut réinstaller.

---

## 4. Questions de compréhension

**Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?**

`requirements.txt` fixe des versions exactes (`==`) pour reproduire l'environnement identique, ce qui est indispensable pour relire un modèle avec la version qui l'a écrit. `dependencies` liste ce que le package importe avec une version minimale (`>=`), pour qu'il puisse s'installer à côté d'autres bibliothèques sans conflit.

**Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?**

`pip install -e .` (éditable) crée un lien vers votre dossier : les modifications du code sont visibles immédiatement ; on l'utilise pendant le développement. Installer le wheel installe une copie du code dans `site-packages` : elle ne change plus si on modifie le dossier du projet ; on l'utilise pour livrer le package à quelqu'un d'autre.

**Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?**

C'est une ligne `nom-de-la-commande = "module:fonction"` qui déclare une commande à créer. À l'installation, pip génère un petit exécutable `maintai-predict.exe` dans le dossier `Scripts` de l'environnement virtuel (`.venv\Scripts`), ce qui rend la commande disponible dans ce `.venv` activé.

---

## 5. Le rendu Git

**Lien de la pull request :** [https://github.com/HajarSmh/Groupe-Samouh-Benchakroun-Halal-Bounjoume/tree/dev/Tps/Tp4/Hajar_Samouh/maintai-starter-tp4](https://github.com/HajarSmh/Groupe-Samouh-Benchakroun-Halal-Bounjoume/tree/dev/Tps/Tp4/Hajar_Samouh/maintai-starter-tp4)

**Le tag `tp4` existe sur GitHub :** oui

**`git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ?** non

---

## 6. Ce qui reste flou

Tout est clair.
