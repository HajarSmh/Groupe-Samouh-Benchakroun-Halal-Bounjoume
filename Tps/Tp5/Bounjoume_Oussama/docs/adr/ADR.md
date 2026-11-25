# ADR 004 : Choix du modèle et du seuil d'alerte pour MaintAI

Date : 25/11/2026 · Auteurs : Oussama Bounjoume (Hajar Samouh, Saad Halal, Imane Benchakroune)

## Contexte

MaintAI doit détecter les pannes potentielles de machines à partir de relevés de capteurs, sachant qu'une panne manquée coûte plus cher qu'une fausse alerte[cite: 67, 77, 78]. Il faut choisir un modèle et un seuil justifiés par des runs MLflow traçables et reliés à une version de données suivie par DVC[cite: 77, 81].

## Options étudiées

1. **Régression logistique (`logreg`, `C=1.0`, seuil `0.3`)** : `recall = 0.75`, `precision = 0.622`, `accuracy = 0.904` (run `dabbb96f26a748b58979caf3fc271b08` / `wise-lark-705`)[cite: 106]. Bon équilibre général, mais `recall` inférieur au seuil `0.2`.
2. **Régression logistique (`logreg`, `C=0.01`, seuil `0.3`)** : `recall = 0.691`, `precision = 0.653`, `accuracy = 0.908` (run `7671b202c7044c649b118c25f9aaf59b` / `masked-crane-447`)[cite: 106]. Meilleure précision et accuracy, mais `recall` plus faible.
3. **Régression logistique (`logreg`, `C=1.0`, seuil `0.2`)** : `recall = 0.838`, `precision = 0.543`, `accuracy = 0.882` (run `3d27ffebd7134c11ba9d27f3e42af60a` / `glamorous-gull-233`)[cite: 106]. Maximise le `recall` pour capter davantage de pannes potentielles.
4. **Forêt aléatoire (`forest`, seuil `0.3`)** : `recall = 0.728`, `precision = 0.562`, `accuracy = 0.886` (run `b1c8518c5d6b40d3aeddcb4ea8d7a720` / `capricious-shark-462`)[cite: 106]. Plus complexe, avec un `recall` et une `precision` inférieurs à la régression logistique (`C=1.0`, seuil `0.3` ou `0.2`) sur ces données.

## Décision

Nous retenons la **régression logistique (`model=logreg`, `C=1.0`) avec le seuil `threshold=0.2`** (run MLflow `3d27ffebd7134c11ba9d27f3e42af60a` / `glamorous-gull-233`), entraînée sur la version v1 des données (`data_md5` : `73e0b7cb3c6f795c70c3ddf970b99c15`). Parce qu'une panne manquée coûte plus cher qu'une fausse alerte, le `recall` le plus élevé (`0.838`) est prioritaire.

## Conséquences

- **Ce que cela facilite :** la détection des situations à risque est maximisée (`recall = 0.838`), et l'identifiant du run MLflow couplé au `data_md5` permet de retrouver exactement le modèle et la version des données.
- **Ce que cela rend plus difficile :** la précision diminue (`0.543`), ce qui entraîne davantage de fausses alertes à vérifier par la maintenance[cite: 106].
- **Ce qu'il faudra surveiller :** la stabilité du `recall` et de la `precision` lorsque de nouvelles données arrivent (dérive des données) via DVC et MLflow[cite: 76, 81].
