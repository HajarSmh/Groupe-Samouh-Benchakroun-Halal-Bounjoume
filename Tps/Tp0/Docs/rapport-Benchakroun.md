# TP0 : MaintAI

**Nom :** Benchakroun Imane· **Groupe :** [Samouh - Benchakroun - Halal - Bounjoume]

## Le problème

Une usine veut savoir à l'avance si un équipement va tomber en panne, à partir de quatre mesures de capteurs : température, vibration, charge et heures de fonctionnement. La cible est binaire (panne ou non), et les deux erreurs possibles n'ont pas le même coût :

- **Panne non détectée (faux négatif)** : la ligne s'arrête de façon imprévue, avec casse et réparation. C'est l'erreur la plus coûteuse.
- **Fausse alerte (faux positif)** : on intervient pour rien, ce qui fait perdre du temps mais reste rattrapable.

Je me suis donc concentré sur le **rappel** de la classe « panne ». Les pannes ne représentent qu'environ 18 % des données, ce qui rend l'accuracy facile à mal interpréter.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---|---|---|
| baseline (toujours « pas de panne ») | 0.824 | 0.000 | 0.000 |
| régression logistique | 0.839 | 0.847 | 0.527 |
| arbre de décision | 0.825 | 0.722 | 0.502 |
| forêt aléatoire | 0.882 | 0.540 | 0.720 |

## Mon choix, et pourquoi

Je retiens la **régression logistique**.

- Son rappel est le plus élevé (0.847). Sur les quelque 176 pannes du test, elle en repère environ 149 et en rate environ 27.
- La baseline m'a servi de repère : elle obtient 0.824 d'accuracy sans détecter une seule panne. Dès le départ, j'ai donc considéré qu'une bonne accuracy ne voulait rien dire ici.
- Le classement change complètement selon la métrique. La forêt aléatoire est première en accuracy (0.882) et en précision (0.720), mais son rappel de 0.540 la place avant-dernière : elle ne trouve qu'environ 95 pannes sur 176. Elle gagne 4 points d'accuracy sur la régression logistique, mais perd plus de 30 points de rappel, ce qui ferait plus de 80 lignes en panne sans alerte. À mes yeux, l'échange n'est pas bon.
- L'arbre de décision (rappel 0.722) reste en dessous de la régression logistique avec une précision similaire.
- Contrepartie : avec 0.527 de précision, près d'une alerte sur deux est fausse (environ 134 fausses alertes pour 149 vraies détections).

## Le critère est-il atteint ?

**Oui, pour l'objectif de rappel ≥ 0,75** : 0.847 est environ 10 points au-dessus. Il faut le relativiser : avec ~176 pannes dans le test, le rappel est connu à ± 5 points, donc l'avance sur le seuil est réelle mais pas énorme.

La précision (0.527) est en revanche faible, et c'est le point qui me gênerait le plus pour un usage réel.

## Ce qui reste flou

- Les équipes de maintenance peuvent-elles gérer autant de fausses alertes sans cesser de faire confiance au système ?
- Le seuil de décision est resté à 0,5. Si je devais continuer, c'est par là que je commencerais (par exemple 0,3 ou 0,4), avant de tester d'autres modèles : c'est le moyen le plus simple de choisir l'équilibre rappel / précision.
- Un seul découpage train/test a été utilisé. Une validation croisée donnerait une estimation plus stable.
- Aucun coût chiffré (panne vs intervention inutile) : impossible de dire si 0.527 de précision est acceptable en pratique.


# TP0 : CantineAI

## Le problème

Il faut prédire le nombre de repas servis chaque jour à la cantine, à partir du calendrier et du contexte : inscrits, menu, météo, examens, sorties scolaires, veille de vacances. C'est une **régression** sur des données ordonnées dans le temps. Une bonne prévision limite à la fois le gaspillage et les ruptures.

## Réglages

Le code de MaintAI est réutilisé ; on modifie `config.py` et la liste des modèles dans `models.py` :

| Réglage | Valeur |
|---|---|
| `TARGET` | `repas_servis` |
| `TASK` | `regression` |
| `MAIN_METRIC` | `mae` |
| `SPLIT` | `chronologique` |
| `TIME_COLUMN` | `date` |

Modèles comparés : baseline (moyenne), régression linéaire, forêt aléatoire, gradient boosting.

## Résultats sur le jeu de test (20 % de jours les plus récents)

| Modèle | MAE (repas) | RMSE | R² |
|---|---|---|---|
| baseline (moyenne) | 70.271 | 88.416 | -0.151 |
| régression linéaire | 22.239 | 28.170 | 0.883 |
| forêt aléatoire | 31.825 | 41.647 | 0.745 |
| gradient boosting | 29.852 | 37.727 | 0.790 |

## Mon choix, et pourquoi

Je choisis la **régression linéaire**.

- Elle a la plus faible MAE (22,2 repas), soit environ 68 % d'erreur en moins que la baseline (70,3).
- Je m'attendais plutôt à voir gagner la forêt aléatoire ou le gradient boosting, puisque ce sont des modèles plus puissants. Ils font pourtant moins bien (31,8 et 29,9). Avec seulement ~340 jours de données, un modèle plus souple a du mal à généraliser, et les effets des variables (inscrits, examens, sorties, veille de vacances) s'additionnent à peu près, ce qui convient bien à un modèle linéaire.
- Son R² de 0.883 montre qu'elle capte l'essentiel de la variation. Celui de la baseline est négatif (-0.151) : la moyenne apprise sur le passé est moins bonne que la moyenne du test, donc prédire toujours la même valeur fait pire que rien.

## Pourquoi un découpage chronologique ?

Les jours consécutifs se ressemblent. Un tirage aléatoire mettrait dans le test des jours entourés de jours d'entraînement : le modèle les connaîtrait presque, et l'erreur serait sous-estimée. Comme en production on prédit le futur avec le passé, le test doit être la période la plus récente.

## Le résultat est-il satisfaisant ?

Il bat nettement la baseline, donc les variables sont utiles. Aucun seuil de réussite n'est fourni : 22,2 repas d'erreur représentent environ 4 à 5 % pour ~500 repas par jour, mais seule la cuisine peut dire si c'est tolérable, selon le coût d'un repas en trop ou en moins.

## Ce qui reste flou

- `repas_semaine_precedente` a 60 valeurs manquantes sur 340, remplacées par la médiane. C'est le point que je trouve le plus fragile, et le premier que je chercherais à améliorer, par exemple en testant une autre méthode d'imputation.
- Le test ne couvre qu'environ 68 jours ; l'erreur pourrait varier selon la saison.
- Le gradient boosting a gardé ses paramètres par défaut ; réglé, il pourrait rattraper la régression linéaire.
- L'erreur maximale acceptable par la cuisine n'est pas connue.
