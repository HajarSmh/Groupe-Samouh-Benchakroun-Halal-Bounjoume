# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** G6  ·  **Membres :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]  ·  **Date :** 25/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
=================================== 5 failed, 27 passed, 2 warnings in 24.51s =====================================
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` échouent : `test_training_creates_a_run`, `test_run_records_metrics`, `test_run_records_data_version`, `test_run_stores_the_model` et `test_options_change_the_run`. Les 27 autres tests passent.

Ils échouent tous avec le même message : `AssertionError: aucun run MLflow : log_run n'a rien enregistré`. La fonction `log_run` de `maintai/tracking.py` n'est pas encore écrite : elle se contente de renvoyer une chaîne vide (`return ""`). L'entraînement se déroule normalement (le modèle est entraîné, évalué et sauvegardé), mais aucun run n'est enregistré dans MLflow. On le voit dans la sortie : la ligne `Run MLflow :` n'est suivie d'aucun identifiant, et MLflow avertit `Cannot retrieve experiment by name maintai`, car l'expérience `maintai` n'a jamais été créée. Les tests cherchent ce run (`mlflow.search_runs`) et n'en trouvent aucun.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant:
C:\Users\PC\Desktop\Groupe App Intelligente\Tps\Tp4\Hajar_Samouh\TP4\maintai\__init__.py
Après:
C:\Users\PC\Desktop\Groupe App Intelligente\Tps\Tp5\Hajar_Samouh\TP5\maintai\__init__.py

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
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
        run_id = run.info.run_id
    return run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
=========================================== 32 passed, 4 warnings in 27.36s =======================================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` |0.75 |0.622 |0.904 |
| `python -m maintai.train --C 0.01` |0.691 |0.653 |0.908 |
| `python -m maintai.train --threshold 0.2` |0.838 |0.543 |0.882 |
| `python -m maintai.train --model forest` |0.728 |0.562 |0.886 |
| `python -m maintai.train --threshold 0.1` |0.919 |0.434 | 0.826|

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je choisirais --threshold 0.2 (recall 0.838, precision 0.543). Une panne manquée coûte plus cher qu'une fausse alerte, donc on privilégie le recall : on gagne environ 9 points par rapport au seuil 0.3 (0.75) pour une baisse de précision acceptable. Le seuil 0.1 a le meilleur recall (0.919) mais sa précision tombe à 0.434, soit plus d'une alerte sur deux fausse, ce qui devient trop coûteux. La forêt aléatoire n'est pas meilleure : son recall (0.728) et sa precision (0.562) sont inférieurs à ceux de la régression logistique (0.75 / 0.622) avec les mêmes réglages.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

`scikit-learn==1.8.0 `
Cela règle le problème du TP4 (InconsistentVersionWarning) : MLflow enregistre avec chaque modèle les versions exactes des bibliothèques qui l'ont produit, donc on sait toujours quelle version installer pour le relire correctement.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Dans le dossier TP5 : la base SQLite mlflow.db (paramètres, métriques, étiquettes) et le dossier mlruns/ (les modèles et leurs fichiers, dont requirements.txt). Ils ne vont pas dans Git : ils sont exclus par le .gitignore, car ce sont des fichiers générés, volumineux, propres à chaque machine et que l'on peut recréer en ré-entraînant.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Les deux valeurs sont identiques. file_md5() de tracking.py calcule la même empreinte que DVC : c'est ce qui relie un run à une version précise des données.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Git gère mal les gros fichiers de données et garde chaque version pour toujours. DVC garde le fichier hors de Git (dans son cache, puis dans le stockage) et ne met dans Git qu'un petit reçu de quelques lignes (md5, taille). Le reçu suffit à retrouver exactement la bonne version du fichier.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:                                                                                                               
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 |213ccdb6 |73e0b7cb |5000 |
| v2 |87bf7959 |93fdeef2 |8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après le retour à la v1, data/sensors.csv contient 5000 lignes : Git a rétabli l'ancien reçu et DVC a ramené le fichier correspondant. Après git checkout HEAD -- data/sensors.csv.dvc et dvc checkout, on retrouve les 8000 lignes de la v2.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

`1 file fetched and 1 file added`
dvc pull récupère le fichier depuis le stockage (le dossier dvc-stockage), reconstruit le cache .dvc/cache, puis restaure data/sensors.csv. C'est ce que ferait un coéquipier qui n'a pas les données.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 |73e0b7cb |4000 |0.75 |0.622 |
| v2 |93fdeef2 |6400 |0.741 |0.65 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non : le recall de la v2 (0.741) est même légèrement inférieur à celui de la v1 (0.75). La precision est un peu meilleure (0.65 contre 0.622), mais l'écart est trop faible pour conclure.
Il faut de plus être prudent : les deux runs n'ont pas les mêmes données d'entraînement (5000 contre 8000 relevés, autre graine) ni le même jeu de test. Un écart de recall peut venir d'un jeu de test plus facile ou de plus de données, pas d'un meilleur modèle. Une comparaison n'est valable qu'à données identiques (même data_md5) ; c'est pourquoi on enregistre l'empreinte des données dans chaque run.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   > Git versionne le code (et le petit reçu .dvc de chaque fichier de données). DVC versionne les fichiers de données, gardés dans un cache et un stockage hors de Git. MLflow garde la trace de chaque entraînement : paramètres, empreinte des données, métriques, modèle et versions exactes des bibliothèques.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   > Le chemin d'un dossier de notre PC (%USERPROFILE%\dvc-stockage) est propre à notre machine et ne doit pas aller dans Git : avec --local, il est écrit dans .dvc/config.local, qui est ignoré par Git. Pour partager les données, il faudrait un stockage accessible à tout le groupe (S3, Google Drive, un serveur SSH, Azure…), déclaré dans la configuration commitée ; chacun ferait alors dvc push et dvc pull vers ce même stockage.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   > Le code : dans Git (et dans le wheel du TP4). Le modèle : dans MLflow, sous la forme d'un run identifié par son identifiant. Les versions exactes des bibliothèques : dans le requirements.txt enregistré avec le modèle par MLflow. S'y ajoutent les données, versionnées par DVC (le reçu dans Git, le fichier dans le stockage).

## 7. Le rendu Git

- Lien de la pull request : https://github.com/HajarSmh/Groupe-Samouh-Benchakroun-Halal-Bounjoume/tree/dev/Tps/Tp5/Hajar_Samouh/TP5
- Le tag `tp5` existe sur GitHub : non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non

## 8. Ce qui reste flou

Tout est clair.
