# ADR 004 : choix du modèle et du seuil de décision pour MaintAI

Date : 25/11/2026 · Auteurs : Samouh Hajar, Benchakroune Imane, Halal Saad, Bounjoume Oussama

## Contexte
MaintAI prédit les pannes à partir des relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte, mais trop de fausses alertes finiraient par être ignorées : il faut choisir un modèle et un seuil de décision, et pouvoir justifier ce choix par un run MLflow et une version précise des données.

## Options étudiées
Grid Search de 25 cas sur les données v2 (`logreg` : C ∈ {0.01, 0.1, 1, 10} × seuil ∈ {0.15, 0.2, 0.3, 0.4, 0.5} ; `forest` : seuil ∈ {0.15, 0.2, 0.3, 0.4, 0.5}), tous enregistrés dans l'expérience `maintai` (tag `grid = gridsearch-1`). Parmi eux, 22 respectent la contrainte precision ≥ 0.50.

1. **Régression logistique, réglage par défaut** (recall 0.741, precision 0.650) : la plus précise, mais elle laisse passer environ une panne sur quatre. Insuffisant vu le coût d'une panne manquée.
2. **Forêt aléatoire** (meilleur cas admissible : seuil 0.2, recall 0.829, precision 0.526, accuracy 0.882) : plus lourde à entraîner et à livrer, et elle ne dépasse pas la régression logistique (recall inférieur de 3 points à notre choix, precision comparable).
3. **Régression logistique, C = 0.1, seuil 0.2** (recall 0.829, precision 0.559, accuracy 0.894) : meilleur compromis. Elle donne environ 5 points de precision en plus, mais détecte moins de pannes (environ 6 à 7 pannes de moins sur le jeu de test).
4. **Régression logistique, C = 10, seuil 0.15** (recall 0.859, precision 0.507, accuracy 0.875) : détecte le plus de pannes parmi les cas admissibles, au prix de nombreuses fausses alertes.

## Décision
Nous retenons **la régression logistique avec C = 10 et un seuil de décision de 0.15** (option 4).

- Run MLflow : `eb9bbedc477242ee9a2ae70d7457ac24`
- Données : `data_md5` = `93fdeef2cac1893c4f720c16457eea75` (v2 sous DVC)
- Résultats : recall 0.859, precision 0.507, accuracy 0.875

Raison principale : une panne manquée coûte plus cher qu'une fausse alerte. Nous maximisons donc le recall, avec une précision plancher de 0.50 pour que les fausses alertes restent supportables. Sur 25 cas, 22 respectent cette contrainte, et c'est celui-ci qui a le meilleur recall.

## Conséquences
- **Facilite** : moins de pannes manquées. Le recall passe de 0.741 à 0.859 par rapport au réglage par défaut, soit environ 12 points de pannes détectées en plus. Le choix est reproductible : le run donne les réglages, et son `data_md5` permet de retrouver les données (`git checkout` du reçu `.dvc`, puis `dvc checkout`).
- **Rend plus difficile** : la precision passe de 0.650 à 0.507, donc environ une alerte sur deux est fausse, avec plus d'inspections inutiles pour les techniciens.
- **À surveiller** :
  - L'écart avec l'option 3 est faible : 3 points de recall contre 5 points de precision, et leurs scores F2 sont quasi identiques (0.754 et 0.756). Le choix de l'option 4 repose sur la priorité donnée au recall. Si les fausses alertes devenaient trop coûteuses, l'option 3 serait l'alternative.
  - Le run `C = 1` (seuil 0.15) donne le même résultat (recall 0.859, precision 0.506) : à ce seuil, la valeur de C a peu d'effet.
  - La precision de 0.507 est à peine au-dessus du plancher de 0.50, et le choix se trouve sur les bords de la grille (seuil le plus bas, C le plus élevé) : un autre plancher ou une grille plus large pourrait donner un autre résultat.
  - Le seuil et les hyperparamètres ont été choisis sur le jeu de test, donc le recall est un peu optimiste. Avec environ 200 pannes dans ce jeu, l'incertitude est de plusieurs points, et il faudrait un jeu de validation séparé pour confirmer.
  - Il faudra ré-évaluer le modèle si les données dérivent, en le ré-entraînant sur une nouvelle version DVC.