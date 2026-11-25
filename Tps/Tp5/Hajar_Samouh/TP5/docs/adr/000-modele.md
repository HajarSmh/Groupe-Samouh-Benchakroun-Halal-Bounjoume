# ADR 004 : choix du modèle et du seuil de décision

Date : 25/11/2026 · Auteurs : Samouh Hajar, Benchakroune Imane, Halal Saad, Bounjoume Oussama

## Contexte
MaintAI prédit les pannes à partir de relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte : il faut donc privilégier le recall, sans que la precision devienne inutilisable. Les entraînements sont maintenant tracés dans MLflow et les données versionnées avec DVC, ce qui permet de justifier le choix.

## Options étudiées
Comparaison faite avec MLflow sur la v1 des données (5000 relevés, data_md5 73e0b7cb) :
1. Régression logistique, seuil 0.3 : recall 0.75, precision 0.622. Compromis correct, mais encore 1 panne sur 4 manquée.
2. Régression logistique, seuil 0.2 : recall 0.838, precision 0.543. Détecte davantage de pannes, au prix de plus de fausses alertes.
3. Régression logistique, seuil 0.1 : recall 0.919, precision 0.434. Meilleur recall, mais plus d'une alerte sur deux est fausse : coût de maintenance inutile trop élevé.
4. Forêt aléatoire (seuil 0.3) : recall 0.728, precision 0.562. Moins bonne que la régression logistique sur les deux métriques, et plus lourde. Non retenue.

Sur la v2 (8000 relevés, data_md5 93fdeef2), la même tendance se confirme entre les seuils 0.3 (recall 0.741, precision 0.65) et 0.2 (recall 0.824, precision 0.567).

## Décision
Nous retenons la **régression logistique avec un seuil de 0.2**, entraînée sur la v2 des données.
- Run MLflow : `a1e0d2a0fec648a7977464d53e2ea63d`
- data_md5 : `93fdeef2cac1893c4f720c16457eea75`
- Résultats sur le jeu de test (1600 relevés) : recall 0.824, precision 0.567, accuracy 0.897.

La raison principale est la contrainte du projet : une panne manquée coûte plus cher qu'une fausse alerte. Le seuil 0.2 détecte environ 82 % des pannes, contre 74 % au seuil 0.3. Le seuil 0.1 est écarté car sa precision (autour de 0.43) rendrait les alertes peu crédibles.

## Conséquences
- Facilite : moins de pannes non détectées ; modèle simple, rapide et facile à expliquer.
- Rend plus difficile : davantage de fausses alertes (environ 4 alertes sur 10 sont fausses), donc des inspections inutiles.
- À surveiller : la précision des alertes en production et la dérive des données. Si les données changent, il faudra ré-entraîner et comparer les runs à données identiques (même data_md5) avant de rechanger de seuil.
- Traçabilité : le run et son data_md5 permettent de retrouver exactement le modèle, ses versions de bibliothèques et ses données (`git checkout` du reçu `.dvc`, puis `dvc checkout`).