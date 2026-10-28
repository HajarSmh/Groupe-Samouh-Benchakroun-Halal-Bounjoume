# Choix du modèle

Date : 21/10/2026 · Groupe : [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]

## Contexte
Nous voulons prédire si une machine tombe en panne (colonne `failure`) à partir de mesures de capteurs. La métrique principale est le recall : manquer une vraie panne coûte plus cher qu'une fausse alerte. [Vérifier que cela correspond à la section 5 de l'étude de conception.]

## Données et découpage
Fichier `data/exemple_pannes.csv`, 5 000 lignes environ [à confirmer avec `len(df)`]. Colonnes utilisées : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`. Découpage aléatoire stratifié sur la cible, 20 % des données pour le test (1 000 lignes), graine 42. Les pannes représentent environ 17,6 % des lignes (déduit de l'accuracy de la baseline, 0,824).

## Résultats sur le jeu de test

| Modèle | Métrique principale (recall) | Autres métriques |
|---|---|---|
| Baseline (classe majoritaire) | 0,000 | accuracy 0,824 · precision 0,000 · f1 0,000 |
| Régression logistique | **0,847** | accuracy 0,839 · precision 0,527 · f1 0,649 |
| Arbre de décision | 0,722 | accuracy 0,825 · precision 0,502 · f1 0,592 |
| Forêt aléatoire | 0,540 | accuracy 0,882 · precision 0,720 · f1 0,617 |

## Décision
Modèle retenu : la régression logistique, car elle obtient le meilleur recall (0,847), la métrique principale : elle détecte environ 85 % des pannes du jeu de test. Elle bat largement la baseline, qui ne détecte aucune panne (recall 0,000), soit +0,847 point de recall. Elle a aussi le meilleur f1 (0,649).

Le prix à payer est une precision de 0,527 : environ une alerte sur deux est une fausse alerte. La forêt aléatoire est plus précise (0,720) et a la meilleure accuracy (0,882), mais elle laisse passer près d'une panne sur deux (recall 0,540), ce qui va à l'encontre de l'objectif.

Le critère d'acceptation « [recopier la section 5] » est [atteint / non atteint].

## Limites
- Le jeu de test contient 1 000 lignes dont environ 176 pannes : le recall est estimé avec une précision limitée (quelques points d'écart seraient normaux d'un tirage à l'autre).
- Un seul découpage, sans validation croisée, et le modèle est choisi sur ce même jeu de test, ce qui peut rendre le score légèrement optimiste.
- Une alerte sur deux est fausse : il faut vérifier que les utilisateurs peuvent absorber cette charge.
- Le seuil de décision (0,5 par défaut) n'a pas été ajusté ; il permettrait d'arbitrer entre recall et precision.
- [Données manquantes, plages de mesure mal couvertes, etc.]