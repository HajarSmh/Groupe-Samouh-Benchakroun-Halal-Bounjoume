# ADR 004 : Choix du modèle et du seuil de MaintAI

Date : 25/11/2026 · Auteurs : Hajar Samouh, Imane Benchakroun, Saad Halal, Oussama Bounjoume

## Contexte
MaintAI doit prévenir les pannes des machines. Une panne manquée coûte beaucoup plus cher
(arrêt de production, réparation) qu'une fausse alerte (une inspection inutile) : le recall
est donc la métrique la plus importante.

## Options étudiées
Quatre entraînements comparés dans MLflow, sur les mêmes données (v1, 5000 relevés) :

1. Régression logistique, C = 1.0, seuil 0.3 : recall 0.750, precision 0.622, accuracy 0.904.
   Bon équilibre, mais une panne sur quatre est manquée.
2. Régression logistique, C = 0.01, seuil 0.3 : recall 0.691, precision 0.653, accuracy 0.908.
   Meilleure accuracy, mais le plus mauvais recall.
3. Régression logistique, C = 1.0, seuil 0.2 : recall 0.838, precision 0.543, accuracy 0.882.
   Le meilleur recall, mais plus de fausses alertes.
4. Forêt aléatoire, seuil 0.3 : recall 0.728, precision 0.562, accuracy 0.886.
   Moins bonne que la régression logistique sur le recall et la precision, et plus lourde.

## Décision
Nous retenons l'option 3 : régression logistique (C = 1.0) avec un seuil de 0.2.
C'est le modèle qui détecte le plus de pannes (83.8 %), ce qui répond à la contrainte principale :
ne pas manquer de panne.

- Run MLflow : `6813f91e94ab40969e1c1ae3f5edb4b1`
- Données : v1, `data_md5` = `73e0b7cb3c6f795c70c3ddf970b99c15` (commit Git `4b7079c`)

## Conséquences
- On accepte plus de fausses alertes : environ une alerte sur deux est fausse (precision 0.543).
  Les techniciens feront plus d'inspections inutiles.
- Le modèle reste simple et rapide, et ses résultats sont faciles à expliquer.
- Avec l'identifiant du run et le `data_md5`, on peut retrouver le modèle (MLflow), les données
  (DVC) et les versions exactes des bibliothèques.
- À surveiller : si les données changent (dérive), il faudra ré-entraîner et comparer les runs
  sur un même jeu de test. Le seuil pourra aussi être ajusté si les fausses alertes gênent trop
  les techniciens.