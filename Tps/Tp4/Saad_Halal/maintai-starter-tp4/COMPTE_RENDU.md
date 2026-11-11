# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
================================================= 2 failed, 25 passed, 1 warning in 24.99s ==================================================
```

Quels sont les deux tests qui échouent, et pourquoi ?

- Les deux tests échouent parce que le package `maintai` n'est pas encore correctement configuré et installé dans l'environnement virtuel. Le fichier `pyproject.toml` est incomplet et la commande `pip install -e .` n'a pas encore été exécutée.

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

- Les dépendances principales contiennent uniquement les bibliothèques nécessaires au fonctionnement de `maintai`. Les outils de test (`pytest`) et le serveur web (`fastapi`) sont placés dans des groupes optionnels (`dev` et `api`) pour éviter d'installer des outils inutiles à chaque utilisateur.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne de machines industrielles à partir de relevés de capteurs.
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
====================================================== 27 passed, 1 warning in 25.13s =======================================================
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

- Probabilité de panne : 95 % (ALERTE)
- C:\Users\dell\Desktop\GRP App Intelligente\Groupe-Samouh-Benchakroun-Halal-Bounjoume\Tps\Tp4\Saad_Halal\maintai-starter-tp4\maintai\__init__.py
- La commande fonctionne depuis n'importe quel dossier et affiche une probabilité de panne de 95 %. Avec `pip install -e .`, le code n'est pas copié dans `.venv` : un lien vers le dossier du projet est créé dans `site-packages`, permettant à Python de retrouver directement le package `maintai`.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

- Probabilité de panne est : 95 % (ALERTE)
- Oui, le nouveau message apparaît tout de suite. L'installation éditable ne copie rien : elle relie l'environnement à notre dossier. La commande exécute donc le fichier cli.py tel qu'il est au moment du lancement, ce qui permet de développer sans réinstaller à chaque modification.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
    Répertoire: C:\Users\dell\Desktop\GRP App 
    Intelligente\Groupe-Samouh-Benchakroun-Halal-Bounjoume\Tps\Tp4\Saad_Halal\maintai-starter-tp4\dist


Mode                 LastWriteTime         Length Name                                                                                       
----                 -------------         ------ ----                                                                                       
-a----        11/11/2026   5:42 PM          11635 maintai-0.2.0-py3-none-any.whl                                                             
-a----        11/11/2026   5:41 PM          12256 maintai-0.2.0.tar.gz   
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
- Non : le wheel ne contient que le dossier maintai/ (les fichiers .py) et les métadonnées (maintai-0.2.0.dist-info, dont entry_points.txt). Dans pyproject.toml, packages.find ne retient que maintai*, donc ni les tests, ni ui/, ni models/ n'y entrent. Le modèle est un fichier de données produit par l'entraînement, pas du code : il se livre à côté du wheel.

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | Modèle introuvable : C:\Users\dell\AppData\Local\Temp\essai\.venv\Lib\site-packages\models\model.joblib
Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR.|
| avec `MAINTAI_MODELS_DIR` vers vos `models` | https://scikit-learn.org/stable/model_persistence html#security-maintainability-limitations warnings.warn Probabilité de panne est : 95 % (ALERTE) |
| après `pip install scikit-learn==1.8.0` | Probabilité de panne est : 95 % (ALERTE) |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

- Le modèle a été entraîné avec une version précise de scikit-learn (1.8.0), mais l'installation du package peut utiliser une autre version. Cette différence peut provoquer des problèmes lors du chargement du modèle, d'où l'avertissement. La version utilisée à l'entraînement est indiquée dans `model_info.json`.

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   - dependencies définit les versions minimales (>=) nécessaires au fonctionnement du package. requirements.txt fixe les versions exactes (==) pour garantir la compatibilité, notamment avec le modèle entraîné.
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   - pip install -e . : installation éditable, les modifications du code sont prises en compte immédiatement.
   - Installation du wheel : installe une copie du package ; toute modification nécessite de reconstruire et réinstaller le wheel
3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   - Il associe une commande à une fonction Python (ex. maintai-predict = "maintai.cli:main"). Pip crée l'exécutable maintai-predict.exe dans le dossier .venv\Scripts.

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui / non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? oui / non

## 6. Ce qui reste flou

Rien.
