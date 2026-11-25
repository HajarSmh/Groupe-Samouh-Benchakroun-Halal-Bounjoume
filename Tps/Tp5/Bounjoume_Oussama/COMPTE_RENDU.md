# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** G6  ·  **Réalisateur : Oussama Bounjoume**  **Membres :** Oussama Bounjoume - Samouh Hajar - Benchakroune Imane - Halal Saad  ·  **Date :** 25/11/2026 **Heure :** 18:15

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
=========================================== 32 passed, 3 warnings in 36.69s ===========================================
```

Quels tests échouent, et pourquoi ?

Avant d'installer le package en mode éditable (`pip install -e .`), les 2 tests de `tests/test_package.py` (`test_installed_version_matches_the_code` et `test_command_is_declared`) échouaient car `maintai` n'était pas encore installé dans l'environnement (`PackageNotFoundError` et commande `maintai-predict` absente), et les 5 tests de `tests/test_tracking.py` échouaient tant que `log_run` retournait `""` au lieu d'enregistrer un run MLflow. Une fois `log_run` complété et `pip install -e .` exécuté, les 32 tests passent.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant `pip install -e .`, `maintai` n'avait pas de métadonnées ni de commande installées dans l'environnement `ai0_clean`. Après `pip install -e .`, il pointe via un lien éditable vers le dossier `maintai` de `TP5`.

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
=========================================== 32 passed, 3 warnings in 36.69s ===========================================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
| --- | --- | --- | --- |
| `python -m maintai.train` | 0.75 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train` (sur v2, 8000 relevés) | 0.741 | 0.65 | 0.916 |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je choisirais le run `logreg` avec `C=1.0` et `--threshold 0.2` (`3d27ffebd7134c11ba9d27f3e42af60a` / `glamorous-gull-233`), car il obtient le meilleur `recall` (`0.838`), ce qui réduit le risque de manquer une panne critique.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Le fichier `requirements.txt` du modèle loggé indique `scikit-learn==1.8.0` (la version utilisée lors de l'entraînement). Cela règle le problème d'`InconsistentVersionWarning` du TP4 en enregistrant la version exacte de `scikit-learn` utilisée lors de l'entraînement.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les métadonnées dans `mlflow.db` et les artefacts/modèles dans `mlruns/` (dans le dossier courant `TP5`). Ils ne vont pas dans Git (ignorés par `.gitignore`) car ce sont des fichiers d'exécution locaux et volumineux.

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

Pour la v1, la valeur `md5` (`73e0b7cb3c6f795c70c3ddf970b99c15`) est identique au paramètre `data_md5` enregistré dans MLflow (`73e0b7cb3c6f795c70c3ddf970b99c15`). Cela relie chaque run MLflow à la version exacte du fichier de données.

Pourquoi `data/sensors.csv` ne va-t-il pas dans Git, alors que `data/sensors.csv.dvc` y va ?

`data/sensors.csv` est le fichier de données géré par DVC dans le cache puis le stockage distant ; `data/sensors.csv.dvc` est le petit fichier reçu (MD5, taille, chemin) qui permet à Git de suivre quelle version des données correspond à chaque commit.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
| --- | --- | --- | --- |
| v1 | `5c7e61c` | `73e0b7cb` | 5000 |
| v2 | `796858c` | `93fdeef2` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout 5c7e61c -- data/sensors.csv.dvc` et `dvc checkout`, `data/sensors.csv` contient **5000** lignes ; après `git checkout HEAD -- data/sensors.csv.dvc` et `dvc checkout`, il contient à nouveau **8000** lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

DVC récupère le fichier depuis le stockage (`$env:USERPROFILE\dvc-stockage`), reconstitue le cache et restaure `data/sensors.csv` (`1 file fetched and 1 file added`).

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
| --- | --- | --- | --- | --- |
| v1 (`logreg`, `C=1.0`, `threshold=0.3`) | `73e0b7cb` | 4000 | 0.75 | 0.622 |
| v2 (`logreg`, `C=1.0`, `threshold=0.3`) | `93fdeef2` | 6400 | 0.741 | 0.65 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

On ne peut pas affirmer simplement qu'un modèle est « meilleur » uniquement d'après ces chiffres car l'entraînement et le test n'ont pas été réalisés sur le même jeu de données (`5000` relevés, `seed=42` vs `8000` relevés, `seed=7`). La variation de `recall` (`0.75` vs `0.741`) et de `precision` (`0.622` vs `0.65`) dépend aussi de l'échantillon et de la répartition des classes.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

Voir `docs/adr/004-choix-du-modele.md` : modèle `logreg` (`C=1.0`), seuil `0.2`, run `3d27ffebd7134c11ba9d27f3e42af60a` (`glamorous-gull-233`), `data_md5` : `73e0b7cb3c6f795c70c3ddf970b99c15`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code source, la configuration et les fichiers `.dvc` ; DVC versionne les jeux de données via leur empreinte et le stockage ; MLflow suit les runs d'entraînement (paramètres, métriques, `data_md5` et modèles/artefacts).
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   `--local` écrit le chemin dans `.dvc/config.local` (ignoré par Git) car il pointe vers un dossier local à la machine (`%USERPROFILE%\dvc-stockage`). Pour partager les données en équipe, il faut un remote partagé (S3, Google Drive, SSH, serveur commun).
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code (Git et package `maintai`), les données/modèles (données sous DVC et modèle/artefacts dans MLflow / `models/`), et les versions exactes des dépendances (`requirements.txt` et `requirements.txt` de l'artefact modèle MLflow).

## 7. Le rendu Git

- Lien de la pull request : `https://github.com/HajarSmh/Groupe-Samouh-Benchakroun-Halal-Bounjoume/tree/dev`
- Le tag `tp5` existe sur GitHub : oui
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non

## 8. Ce qui reste flou

Rien de particulier, l'ensemble du flux MLflow + DVC + ADR est clair.
