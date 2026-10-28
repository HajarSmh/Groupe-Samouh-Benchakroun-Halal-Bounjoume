# Choix du modèle

Date : 21/10/2026 · Groupe : [Oussama Bounjoume]

## Contexte

Le projet vise à prédire les pannes d'équipements industriels à partir de mesures
capteurs (température, vibration, charge, heures de fonctionnement). La métrique
principale est le **recall** sur la classe « panne » : manquer une panne coûte
beaucoup plus cher qu'une fausse alerte, donc on privilégie la détection au
détriment de la précision.

## Données et découpage

- Fichier : `data/exemple_pannes.csv`
- Colonnes utilisées : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`
- Cible : `failure` (classification binaire, déséquilibrée ≈ 82 % / 18 %)
- Découpage : aléatoire stratifié, `test_size = 0.2`, `random_state = 42`
- Taille du jeu de test : 20 % des lignes (≈ 950 lignes)

## Résultats sur le jeu de test

| Modèle | Métrique principale (recall) | Autres métriques |
|---|---|---|
| Baseline (classe majoritaire) | 0,000 | accuracy 0,824 · precision 0,000 · f1 0,000 |
| Régression logistique | **0,847** | accuracy 0,839 · precision 0,527 · f1 0,649 |
| Arbre de décision | 0,722 | accuracy 0,825 · precision 0,502 · f1 0,592 |
| Forêt aléatoire | 0,540 | accuracy 0,882 · precision 0,720 · f1 0,617 |

## Décision

Modèle retenu : la régression logistique, car elle obtient le meilleur recall (0,847), la métrique principale : 
elle détecte environ 85 % des pannes du jeu de test. Elle bat largement la baseline, qui ne détecte aucune panne 
(recall 0,000), soit +0,847 point de recall. Elle a aussi le meilleur f1 (0,649).

Le prix à payer est une precision de 0,527 : environ une alerte sur deux est une fausse alerte. 
La forêt aléatoire est plus précise (0,720) et a la meilleure accuracy (0,882), mais elle laisse passer près 
d'une panne sur deux (recall 0,540), ce qui va à l'encontre de l'objectif.

. Le critère d'acceptation (recall
nettement supérieur à celui de la baseline) est atteint.

## Limites

- **Le jeu de test contient 1 000 lignes dont environ 176 pannes** : le recall est estimé avec une précision limitée 
(quelques points d'écart seraient normaux d'un tirage à l'autre).
- **Baseline trompeuse** : son recall de 0 est un artefact du `most_frequent` sur
  une cible déséquilibrée. Un `DummyClassifier(strategy="stratified")` donnerait
  un recall non-nul et un écart plus honnête.
- **Jeu de test petit (~950 lignes) et synthétique** : les chiffres peuvent bouger
  de quelques points avec un autre `random_state`. Idéalement, faire une
  validation croisée stratifiée (k-fold) pour des intervalles de confiance.
- **Pas de données manquantes** dans l'exemple fourni — la robustesse du pipeline
  face aux NaN n'est donc pas réellement testée.
