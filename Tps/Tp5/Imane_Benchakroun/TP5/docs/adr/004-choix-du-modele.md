# ADR 004 : Choix du modèle et du seuil de MaintAI

Date : 25/11/2026 · Auteurs : Hajar Samouh, Imane Benchakroun, … Halal, … Bounjoume

## Contexte
MaintAI doit prévenir les pannes des machines. Une panne manquée coûte beaucoup plus cher
(arrêt de production, réparation) qu'une fausse alerte (une inspection inutile) : le recall
est donc la métrique la plus importante. Mais trop de fausses alertes feraient perdre
confiance aux techniciens : nous voulons qu'au moins une alerte sur deux soit vraie
(precision ≥ 0.5).

## Options étudiées
Un Grid Search de 25 combinaisons, toutes entraînées sur les mêmes données (v2, 8000 relevés) :
modèle (`logreg`, `forest`) × `C` (0.01, 0.1, 1.0, 10.0, pour logreg) × seuil (0.15, 0.2, 0.3,
0.4, 0.5). Les options les plus intéressantes :

1. Logreg, C = 0.01, seuil 0.15 : recall 0.893, precision 0.470.
   Le meilleur recall, mais plus d'une alerte sur deux est fausse.
2. Logreg, C = 10.0, seuil 0.15 : recall 0.859, precision 0.507, accuracy 0.875.
   Le meilleur recall avec une precision au-dessus de 0.5.
3. Logreg, C = 1.0, seuil 0.2 : recall 0.824, precision 0.567, accuracy 0.897.
   Plus équilibré, mais manque environ 3.5 % de pannes en plus que l'option 2.
4. Forêt aléatoire, seuil 0.15 : recall 0.878, precision 0.481.
   Precision sous 0.5, et à seuil égal elle n'est pas meilleure que la régression logistique.
5. Seuils 0.4 et 0.5 : precision élevée (jusqu'à 0.83), mais le recall descend entre 0.46 et 0.67 :
   trop de pannes manquées.

## Décision
Nous retenons l'option 2 : **régression logistique, C = 10.0, seuil 0.15**.
C'est la combinaison qui détecte le plus de pannes (85.9 %) tout en gardant au moins une alerte
vraie sur deux (precision 0.507). Elle répond à la contrainte principale du projet : ne pas
manquer de panne, sans noyer les techniciens sous les fausses alertes.

- Run MLflow : `0e3226a65db9439a8308f27ee8486d48`
- Données : v2, `data_md5` = `93fdeef2cac1893c4f720c16457eea75` (commit Git `17fcc0c`)

## Conséquences
- On accepte beaucoup de fausses alertes : environ une alerte sur deux est fausse.
  Les techniciens feront plus d'inspections inutiles.
- La precision (0.507) est juste au-dessus de notre limite : si les fausses alertes gênent trop
  sur le terrain, on pourra passer au seuil 0.2 (option 3), en acceptant de manquer un peu plus
  de pannes.
- C = 1.0 donne presque les mêmes résultats que C = 10.0 : le choix de `C` compte peu ici.
- La régression logistique reste simple, rapide et facile à expliquer.
- Avec l'identifiant du run et le `data_md5`, on retrouve le modèle (MLflow), les données (DVC)
  et les versions exactes des bibliothèques.
- À surveiller : si les données changent (dérive), relancer le Grid Search sur les nouvelles
  données et comparer les runs sur un même jeu de test.