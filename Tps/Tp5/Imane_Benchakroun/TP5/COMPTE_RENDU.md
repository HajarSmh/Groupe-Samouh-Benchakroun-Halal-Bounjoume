# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
================== 5 failed, 27 passed, 2 warnings in 22.58s ===================
```

Quels tests échouent, et pourquoi ?
FAILED tests/test_tracking.py::test_training_creates_a_run - AssertionError: aucun run MLflow : log_run n'a rien enregistré
FAILED tests/test_tracking.py::test_run_records_metrics - AssertionError: aucun run MLflow : log_run n'a rien enregistré
FAILED tests/test_tracking.py::test_run_records_data_version - AssertionError: aucun run MLflow : log_run n'a rien enregistré
FAILED tests/test_tracking.py::test_run_stores_the_model - AssertionError: aucun run MLflow : log_run n'a rien enregistré
FAILED tests/test_tracking.py::test_options_change_the_run - AssertionError: aucun run MLflow : log_run n'a rien enregistré


Les 5 tests de `tests/test_tracking.py` échouent, tous avec la même erreur :
`AssertionError: aucun run MLflow : log_run n'a rien enregistré`.

La fonction `log_run` de `maintai/tracking.py` n'est pas encore écrite : elle
renvoie seulement `""` sans rien enregistrer dans MLflow. Les tests ne trouvent donc aucun run.
Les 27 autres tests viennent du TP4 et passent.
…

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?
Avant, `maintai` pointait vers le dossier du TP4
Après, il pointe vers le dossier du TP5
…

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, name="model", input_example=X_example,
                                    skops_trusted_types=TRUSTED_TYPES)
    return run.info.run_id

```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================= 32 passed, 4 warnings in 59.69s ========================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` |0.750 | 0.622 | 0.904|
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| (votre essai) | | | |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)
Nous choisissons le run `--threshold 0.2` car Une panne manquée
coûte plus cher qu'une fausse alerte, donc on regarde surtout le recall.
…

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Dans le `requirements.txt` du modèle (run `illustrious-ram-118`), on lit `scikit-learn==1.8.0`.
MLflow enregistre avec chaque modèle les versions exactes des bibliothèques utilisées pour l'entraîner. Au TP4, le wheel avait installé scikit-learn 1.9.1 et le modèle, écrit avec la 1.8.0, donnait un `InconsistentVersionWarning`. Avec MLflow, on sait directement quelle version installer pour relire le modèle.
…

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les runs dans le dossier `TP5` :
- `mlflow.db` : une base SQLite avec les paramètres, les métriques et les tags de chaque run ;
- `mlruns\` : les fichiers de chaque run.

Ces fichiers ne vont pas dans Git : le `.gitignore` les exclut. Ils changent à chaque entraînement, ils peuvent devenir lourds. …

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

C'est la même valeur (`73e0b7cb3c6f795c70c3ddf970b99c15`) : MLflow et DVC calculent la même
empreinte du fichier. On sait donc exactement sur quelles données chaque modèle a été entraîné,
et on peut retrouver ces données avec DVC.
…

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Un fichier de données peut être très lourd, et Git garde chaque version pour toujours. DVC garde
donc le fichier hors de Git (dans son cache et dans le stockage). Dans Git, on met seulement
`sensors.csv.dvc` : un petit reçu avec le md5 et la taille du fichier.
…

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | 4b7079c | 73e0b7cb | 5000 |
| v2 | 17fcc0c | 93fdeef2 | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout 4b7079c -- data/sensors.csv.dvc` puis `dvc checkout`, `data/sensors.csv` contient 5000 lignes : on a bien retrouvé la v1. Git a remis l'ancien reçu, et DVC a remis le
fichier qui correspond à ce reçu. Après `git checkout HEAD -- data/sensors.csv.dvc` et
`dvc checkout`, on retrouve la v2 avec 8000 lignes.
…

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

`dvc pull` affiche `1 file fetched and 1 file added` : DVC a récupéré le fichier dans le
stockage et l'a remis dans `data/`. Le fichier contient de nouveau 8000 lignes.
…

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 (a7a471ce) | 73e0b7cb | 4000 | 0.750 | 0.622 |
| v2 (5b837212) | 93fdeef2 | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le run v2 a une meilleure precision (0.650 contre 0.622) mais un recall un peu plus bas
(0.741 contre 0.750), et le recall est le plus important pour MaintAI. Surtout, les deux runs
ne sont pas évalués sur les mêmes données : le test de la v1 a 1000 relevés, celui de la v2 en
a 1600, tirés d'un autre jeu de données. Les écarts peuvent venir des données de test, pas du
modèle. Pour comparer deux modèles, il faut les évaluer sur le même jeu de test.
…

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## Grid Search des hyperparamètres

Toutes les combinaisons ont été entraînées sur les mêmes données (v2, 8000 relevés,
`data_md5` = `93fdeef2cac1893c4f720c16457eea75`).
Chaque combinaison est un run MLflow de l'expérience `maintai`.

### Marges de variation et valeurs testées

| Hyperparamètre | Valeurs testées | Pourquoi cette marge |
|---|---|---|
| `model` | `logreg`, `forest` | les deux modèles proposés par `train.py` |
| `C` (logreg seulement) | 0.01, 0.1, 1.0, 10.0 | de 0.01 (forte régularisation) à 10 (faible), par facteur 10 |
| `threshold` | 0.15, 0.2, 0.3, 0.4, 0.5 | de 0.5 (seuil par défaut) vers le bas, pour favoriser le recall |

Nombre de combinaisons : logreg 4 × 5 = 20, forêt 5 (pas de `C`), soit **25 runs**.

### Code de la boucle (`grid_search.py`)

```python
C_VALUES = [0.01, 0.1, 1.0, 10.0]
THRESHOLDS = [0.15, 0.2, 0.3, 0.4, 0.5]

combinaisons = [("logreg", c, t) for c, t in itertools.product(C_VALUES, THRESHOLDS)]
combinaisons += [("forest", None, t) for t in THRESHOLDS]
assert len(combinaisons) <= 30

env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
resultats = []

for i, (model, c, t) in enumerate(combinaisons, 1):
    cmd = [sys.executable, "-m", "maintai.train", "--model", model, "--threshold", str(t)]
    if c is not None:
        cmd += ["--C", str(c)]
    print(f"[{i}/{len(combinaisons)}] model={model} C={c} threshold={t}", flush=True)

    sortie = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                            env=env, check=True).stdout
    metriques = json.loads(sortie[sortie.index("{"):sortie.rindex("}") + 1])["model"]
    run_id = sortie.split("Run MLflow :")[-1].strip()

    resultats.append({
        "model": model, "C": c if c is not None else "-", "threshold": t,
        "recall": metriques["recall"], "precision": metriques["precision"],
        "accuracy": metriques["accuracy"], "run_id": run_id,
    })

# Règle de choix : le meilleur recall, avec une precision d'au moins 0.5
candidats = [r for r in resultats if r["precision"] >= 0.5] or resultats
meilleur = max(candidats, key=lambda r: (r["recall"], r["precision"]))
```

### Résultats détaillés de 5 runs

| Run MLflow | model | C | threshold | recall | precision | accuracy |
|---|---|---|---|---|---|---|
| 0e3226a6 | logreg | 10.0 | 0.15 | **0.859** | 0.507 | 0.875 |
| 78035ac2 | logreg | 0.01 | 0.15 | 0.893 | 0.470 | 0.858 |
| 21ed28cd | forest | - | 0.15 | 0.878 | 0.481 | 0.863 |
| afb97b04 | logreg | 1.0 | 0.2 | 0.824 | 0.567 | 0.897 |
| 8f94f597 | logreg | 1.0 | 0.3 | 0.741 | 0.650 | 0.916 |

- **Le seuil a le plus d'effet** : en le baissant de 0.5 à 0.15, le recall passe d'environ
  0.58 à 0.86 (logreg, C = 1), mais la precision baisse d'environ 0.77 à 0.51.
- **`C` a peu d'effet** au-delà de 0.1 : C = 1.0 et C = 10.0 donnent presque les mêmes résultats.
  C = 0.01 (forte régularisation) change davantage les résultats.
- **La forêt aléatoire n'est pas meilleure** : à seuil égal, elle a un recall proche de la
  régression logistique mais une precision plus basse.

### Meilleure combinaison

Règle de choix : **le meilleur recall, avec une precision d'au moins 0.5** (au moins une alerte
sur deux doit être une vraie panne).

Résultat : **logreg, C = 10.0, threshold = 0.15** : recall 0.859, precision 0.507, accuracy 0.875
(run `0e3226a65db9439a8308f27ee8486d48`).

Le run logreg C = 0.01, seuil 0.15 a un recall plus haut (0.893), mais sa precision (0.470) est
sous 0.5 : plus d'une alerte sur deux serait fausse.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?

   Git versionne le code, et les petits reçus `.dvc` des données.
   DVC versionne les fichiers de données : il les garde dans son cache et dans un stockage.
   MLflow garde chaque entraînement : les paramètres, les métriques, le `data_md5` et le modèle
   avec les versions exactes des bibliothèques.

2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?

   Le stockage est un dossier de mon PC (`C:\Users\Imane\dvc-stockage`). Ce chemin n'existe pas
   chez les autres, donc il ne doit pas aller dans Git : `--local` l'écrit dans
   `.dvc\config.local`, qui est ignoré par Git. Pour partager les données, il faudrait un stockage
   commun accessible par tous (S3, Google Drive, un serveur), ajouté sans `--local`.

3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?

   - le code : dans Git (et le wheel du TP4) ;
   - le modèle : dans MLflow, retrouvé par l'identifiant du run ;
   - les versions exactes : dans MLflow, le `requirements.txt` enregistré avec le modèle.
   En plus, les données sont maintenant retrouvables avec DVC : le reçu dans Git, le fichier
   dans le stockage.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui / non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? oui / non

## 8. Ce qui reste flou

…
