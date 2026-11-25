# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

***Groupe :** G6  ·  **Membres :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]  ·  **Date :** 25/11/2026 17h55 

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
================================================================= 5 failed, 27 passed, 2 warnings in 52.37s ==================================================================
```

Quels tests échouent, et pourquoi ?

- Les 5 tests qui échouent sont ceux qui vérifient l'enregistrement des runs (tests/test_tracking.py, et ceux de l'entraînement qui attendent un identifiant de run). Ils échouent parce que la fonction log_run de maintai/tracking.py n'est pas écrite : elle ne fait rien et renvoie une chaîne vide, donc aucun run n'est créé dans MLflow et aucun identifiant n'est renvoyé.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

- Avant : C:\Users\dell\Desktop\GRP App Intelligente\Groupe-Samouh-Benchakroun-Halal-Bounjoume\Tps\Tp5\Halal_Saad\TP5\maintai\__init__.py
- Apres : C:\Users\dell\Desktop\GRP App Intelligente\Groupe-Samouh-Benchakroun-Halal-Bounjoume\Tps\Tp5\Halal_Saad\TP5\maintai\__init__.py

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
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
        return run.info.run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
========================================================= 32 passed, 4 warnings in 118.05s (0:01:58) =========================================================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.75 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --threshold 0.4` | 0.684 | 0.664 | 0.91 |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

- Je choisirais le run avec --threshold 0.2, car il offre le meilleur recall (0.838) et détecte davantage de pannes. Même si cela augmente les fausses alertes, éviter une panne manquée reste prioritaire.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

- La version indiquée est scikit-learn==1.8.0. Cela évite les problèmes de compatibilité (InconsistentVersionWarning) lors du chargement du modèle.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

- MLflow enregistre les runs dans mlflow.db et le dossier mlruns/. Ces fichiers sont exclus de Git car ils sont générés, volumineux et propres à chaque environnement. Git sert principalement à versionner le code.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv

```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

- Les deux valeurs sont identiques. file_md5() de tracking.py calcule la même empreinte que DVC : c'est ce qui relie un run MLflow à une version précise des données. À partir d'un run, on peut donc retrouver exactement les données qui ont servi à l'entraîner.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

- Un fichier de données peut peser 100 Mo : Git le gère mal et garde chaque version pour toujours, ce qui alourdit le dépôt. DVC garde le fichier hors de Git, dans son cache puis dans le stockage, et ne met dans Git qu'un reçu de quelques lignes (le md5 et la taille). Git versionne donc le reçu, et le reçu permet de retrouver le bon fichier.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:                                                                                                                                         
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | 5301f72 | 73e0b7cb | 5000 |
| v2 | 6176747 | 93fdeef2 | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

- La v1 contient 5 000 lignes et la v2 contient 8 000 lignes. Git restaure le fichier .dvc et DVC récupère les données correspondantes depuis son cache.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

- DVC récupère les données depuis le stockage distant, restaure le cache et recrée sensors.csv. Cela permet de partager les données sans les stocker dans Git.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | 73e0b7cb | 4000 | 0.75 | 0.622 |
| v2 | 93fdeef2 | 6400 | 0.741 | 0.65 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

- Non, on ne peut pas dire que le modèle v2 est meilleur. Sur le critère qui compte le plus pour MaintAI, le recall, la v2 n'est pas meilleure : elle fait 0.741 contre 0.75 pour la v1. Sa précision est un peu plus élevée (0.65 contre 0.622), mais l'écart est faible. Surtout, ces écarts (moins de 1 point de recall, environ 3 points de précision) sont trop petits pour être interprétés.

- Il faut être prudent parce que les deux runs ne sont pas comparables point à point. Ils n'ont pas les mêmes données d'entraînement (4000 relevés pour la v1, 6400 pour la v2, tirés avec une autre graine) et surtout pas le même jeu de test : 1000 relevés pour la v1 (environ 136 pannes) et 1600 pour la v2 (environ 218 pannes). Avec si peu de pannes, le recall n'est connu qu'à environ ± 6 ou 7 points près, soit bien plus que l'écart observé. Une différence de ce genre peut venir d'un jeu de test un peu plus facile ou du simple hasard du tirage, pas d'un modèle supérieur. Pour comparer vraiment, il faudrait évaluer les deux modèles sur le même jeu de test, et vérifier que l'écart dépasse l'incertitude statistique.

## Grid Search

### 1. Espace de recherche

| Hyperparamètre | Marge de variation | Valeurs testées |
|---|---|---|
| `model` | 2 modèles | `logreg`, `forest` |
| `C` (logreg seulement) | de 0.01 (forte régularisation) à 10 (faible), échelle logarithmique | [0.01, 0.1, 1.0, 10.0] |
| `threshold` | de 0.15 (très sensible) à 0.5 (seuil neutre) | [0.15, 0.2, 0.3, 0.4, 0.5] |

Total : 4 × 5 (logreg) + 5 (forest) = **25 cas** (maximum autorisé : 30). Tous les runs portent le tag MLflow `grid = gridsearch-1` et ont été entraînés sur les mêmes données (`data_md5` = `93fdeef2`).

### 2. Code de la boucle

```python
def run_grid(cases):
    """Boucle du Grid Search : un entraînement (donc un run MLflow) par cas."""
    results = []
    for i, case in enumerate(cases, 1):
        cmd = [sys.executable, "-m", "maintai.train",
               "--model", case["model"], "--threshold", str(case["threshold"])]
        if case["C"] is not None:
            cmd += ["--C", str(case["C"])]
        print(f"[{i}/{len(cases)}] {' '.join(cmd[2:])}", flush=True)
        out = subprocess.run(cmd, capture_output=True, text=True)
        found = re.search(r"Run MLflow\s*:\s*([0-9a-f]+)", out.stdout)
        if not found:
            print("   échec :", out.stderr[-300:])
            continue
        run_id = found.group(1)
        client.set_tag(run_id, "grid", GRID_TAG)
        data = client.get_run(run_id).data
        results.append({**case, "run_id": run_id,
                        "data_md5": data.params.get("data_md5", ""),
                        "n_train": data.params.get("n_train", ""),
                        "recall": data.metrics["recall"],
                        "precision": data.metrics["precision"],
                        "accuracy": data.metrics["accuracy"]})
    return results
```

### 3. Résultats détaillés : les 5 meilleurs runs (précision ≥ 0.5)

| Rang | model | C | threshold | recall | precision | accuracy | F2 | run_id |
|---|---|---|---|---|---|---|---|---|
| 1 | logreg | 10 | 0.15 | 0.859 | 0.507 | 0.875 | 0.754 | `eb9bbedc` |
| 2 | logreg | 1 | 0.15 | 0.859 | 0.506 | 0.874 | 0.754 | `8b058bb6` |
| 3 | logreg | 0.1 | 0.2 | 0.829 | 0.559 | 0.894 | 0.756 | `8ac21ca5` |
| 4 | logreg | 0.01 | 0.2 | 0.829 | 0.547 | 0.890 | 0.752 | `8bb80254` |
| 5 | forest | — | 0.2 | 0.829 | 0.526 | 0.882 | 0.743 | `45160725` |

Les 25 cas sont dans `grid_results.csv` ; 3 d'entre eux sont écartés car leur précision est sous 0.5.

### 4. Meilleure combinaison

Critère : recall maximal (une panne manquée coûte plus cher qu'une fausse alerte), sous la contrainte precision ≥ 0.5 pour ne pas noyer les techniciens sous les fausses alertes. Retenu : **logreg, C = 10, threshold = 0.15** (recall 0.859, precision 0.507, accuracy 0.875).

---

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   - Git versionne le code, et un petit reçu (.dvc) par fichier de données. DVC versionne les fichiers de données eux-mêmes, dans un cache et un stockage hors de Git. MLflow garde la trace de chaque entraînement : paramètres, métriques, modèle et versions exactes des bibliothèques.

2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   - Que faudrait-il pour que tout le groupe partage les mêmes données ? Parce que le dossier de stockage est un chemin de notre propre PC : il ne doit pas aller dans Git, où il serait faux pour les autres. L'option --local l'écrit dans .dvc\config.local, ignoré par Git. Pour partager les données, il faudrait un stockage commun accessible à toute l'équipe (un serveur, S3, Google Drive, un dossier partagé) et déclaré dans la configuration du dépôt.

3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   - C'est le code, le modèle et les versions exactes des bibliothèques. Le code est dans Git (et dans le wheel du TP4). Le modèle est dans MLflow, retrouvable par l'identifiant de son run. Les versions exactes sont dans le requirements.txt enregistré avec le modèle par MLflow. Les données, elles, sont dans DVC : le reçu est dans Git et le fichier dans le stockage.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui / non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? oui / non

## 8. Ce qui reste flou

- Rien
