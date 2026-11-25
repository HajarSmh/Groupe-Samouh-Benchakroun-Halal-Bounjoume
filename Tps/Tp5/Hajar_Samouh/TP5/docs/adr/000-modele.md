# ADR 004 : choix du modèle et du seuil de décision

Date : 25/11/2026 · Auteurs : Samouh Hajar, Benchakroune Imane, Halal Saad, Bounjoume Oussama

## Contexte
MaintAI prédit les pannes à partir de relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte : il faut donc privilégier le recall, sans que la precision rende les alertes inutilisables. Les entraînements sont tracés dans MLflow et les données versionnées avec DVC, ce qui permet de justifier le choix.

Des essais manuels sur la v1 (5000 relevés, data_md5 `73e0b7cb`) ont montré que le seuil règle le compromis entre recall et precision, et que la forêt aléatoire n'améliore pas la régression logistique. Ces essais portent sur d'autres données : ils ne sont pas comparables au grid search et ne fondent pas la décision.

## Options étudiées
Un grid search de 30 cas a été lancé sur la v2 des données (8000 relevés, 6400 en entraînement, 1600 en test, data_md5 `93fdeef2cac1893c4f720c16457eea75`). Chaque cas est un run MLflow. Détail dans `COMPTE_RENDU.md` (§5 bis) et `grid_results.csv`.

| Modèle | C | threshold | Cas |
|---|---|---|---|
| logreg | 0.01 · 0.1 · 1.0 · 10.0 | 0.1 · 0.15 · 0.2 · 0.25 · 0.3 · 0.4 | 24 |
| forest | (sans objet) | 0.1 · 0.15 · 0.2 · 0.25 · 0.3 · 0.4 | 6 |

Critère fixé avant les résultats : recall maximal avec precision ≥ 0.50. 22 cas sur 30 le respectent.

| Rang | Modèle | C | Seuil | Recall | Precision | Accuracy | Run |
|---|---|---|---|---|---|---|---|
| 1 | logreg | 10.0 | 0.15 | 0.859 | 0.507 | 0.875 | `024a26966b674c06a77435e35f5c728f` |
| 2 | logreg | 1.0 | 0.15 | 0.859 | 0.506 | 0.874 | `fdffc943a36d44e0a5d341b3886ab7ff` |
| 3 | logreg | 0.1 | 0.2 | 0.829 | 0.559 | 0.894 | `8a886a399ac14af18bd881ce00582bc7` |
| 4 | logreg | 0.01 | 0.2 | 0.829 | 0.547 | 0.890 | `083844c3ffa44f1ead266f59c612b094` |
| 5 | forest | – | 0.2 | 0.829 | 0.526 | 0.882 | `76e4cf7662424149bdb3f0aed907f98f` |

- Rang 1 (C = 10, seuil 0.15) : retenu.
- Rang 2 (C = 1, seuil 0.15) : équivalent au rang 1 en pratique ; écarté pour 0.001 de precision en moins.
- Rang 3 (C = 0.1, seuil 0.2) : 3 points de recall en moins mais meilleure precision. Alternative si les fausses alertes deviennent trop coûteuses.
- Seuils 0.1 : recall jusqu'à 0.966 mais precision de 0.38 à 0.46, soit plus d'une alerte sur deux fausse. Écartés.
- Seuils 0.3 et 0.4 : trop de pannes manquées (recall de 0.57 à 0.74).
- Forêt aléatoire : meilleur cas au seuil 0.2 (recall 0.829, precision 0.526). Moins bonne que la régression logistique à seuil égal, et plus lourde.
- Le seuil pèse beaucoup plus que C : C = 1 et C = 10 donnent des résultats presque identiques.

## Décision
Nous retenons le rang 1 du grid search : **régression logistique, C = 10, seuil 0.15**, entraînée sur la v2.
- Run MLflow : `024a26966b674c06a77435e35f5c728f`
- data_md5 : `93fdeef2cac1893c4f720c16457eea75`
- Résultats sur le jeu de test (1600 relevés) : recall 0.859, precision 0.507, accuracy 0.875.

Justification : la contrainte du projet est qu'une panne manquée coûte plus cher qu'une fausse alerte. Ce run a le plus haut recall parmi les 22 cas qui respectent la precision minimale. Il détecte environ 86 % des pannes, contre 74 % pour la même régression logistique au seuil 0.3 (recall 0.741), soit environ 24 pannes de plus sur les quelque 205 du jeu de test. Face au rang 3 (seuil 0.2), il détecte environ 6 pannes de plus, au prix d'une precision plus faible de 5 points.

## Conséquences
- Facilite : davantage de pannes détectées (86 sur 100 contre 74 au seuil 0.3) ; modèle simple, rapide et explicable.
- Rend plus difficile : environ 49 % d'alertes fausses, donc beaucoup d'inspections inutiles.
- Limites : la precision (0.507) est à peine au-dessus du minimum fixé, et l'écart avec les rangs 2 et 3 est de l'ordre du bruit statistique. Le seuil et les hyperparamètres ont été choisis en regardant le jeu de test, donc les chiffres sont légèrement optimistes. Une validation croisée ou un jeu de validation séparé donnerait une estimation plus honnête.
- À surveiller : la precision des alertes en production et la dérive des données. Si le coût des fausses alertes devient trop élevé, passer au rang 3 (seuil 0.2, C = 0.1, precision 0.559). En cas de nouvelles données, ré-entraîner et comparer à data_md5 identique.
- Traçabilité : `git checkout` du reçu `.dvc` puis `dvc checkout` redonne les données exactes du run.