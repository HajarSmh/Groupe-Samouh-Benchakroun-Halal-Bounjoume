# Choix du modèle

Date : 27/10/2026 · Équipe : [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]

## Contexte
L'objectif est d'anticiper les pannes de machines en s'appuyant sur des relevés de capteurs. Nous privilégions le recall comme indicateur principal, car laisser passer une vraie panne est plus coûteux que déclencher une alerte à tort.

## Données et découpage
Les données proviennent du fichier `data/exemple_pannes.csv`, qui compte environ 5 000 observations. Quatre variables explicatives sont utilisées : `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours`. La séparation est aléatoire et stratifiée selon la cible : 20 % des observations sont réservées au test, avec une graine fixée à 42. Les pannes représentent à peu près 17,6 % de l'ensemble, proportion déduite de l'accuracy de la baseline (0,824).

## Résultats sur le jeu de test

| Modèle | Indicateur principal (recall) | Indicateurs complémentaires |
|---|---|---|
| Baseline (classe majoritaire) | 0,000 | accuracy 0,824 · precision 0,000 · f1 0,000 |
| Régression logistique | **0,847** | accuracy 0,839 · precision 0,527 · f1 0,649 |
| Arbre de décision | 0,722 | accuracy 0,825 · precision 0,502 · f1 0,592 |
| Forêt aléatoire | 0,540 | accuracy 0,882 · precision 0,720 · f1 0,617 |

## Décision
Nous retenons la régression logistique. Elle affiche le recall le plus élevé (0,847), indicateur sur lequel repose notre sélection : environ 85 % des pannes présentes dans le jeu de test sont identifiées. À titre de comparaison, la baseline ne repère aucune panne (recall de 0,000), ce qui représente un gain de 0,847 point. La régression logistique obtient en outre le meilleur f1 (0,649).

Cette performance a un coût : avec une precision de 0,527, près d'une alerte sur deux est injustifiée. Random forest se montre plus fiable dans ses alertes (precision de 0,720) et atteint la meilleure accuracy (0,882). Toutefois, elle manque presque une panne sur deux (recall de 0,540), ce qui contredit notre priorité.

## Limites
- Le jeu de test comporte 1 000 lignes, dont environ 176 pannes : l'estimation du recall reste peu précise, et un écart de quelques points d'un tirage à l'autre serait normal.
- Nous avons utilisé un seul découpage, sans validation croisée, et le modèle a été sélectionné sur ce même jeu de test ; le score obtenu peut donc être un peu trop favorable.
- Comme une alerte sur deux est une fausse alerte, il faut s'assurer que les équipes concernées sont en mesure de traiter ce volume.
- Le seuil de décision est resté à sa valeur par défaut (0,5). Le modifier permettrait de choisir un compromis différent entre recall et precision.
