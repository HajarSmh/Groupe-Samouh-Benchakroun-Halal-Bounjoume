# TP0 : MaintAI

**Nom :** Samouh Hajar · **Groupe :** [Samouh - Benchakroune - Halal - Bounjoume]

## Le problème

Prédire une panne à partir de 4 capteurs (température, vibration, charge, heures de fonctionnement) ; une panne manquée arrête une ligne.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---|---|---|
| baseline | 0.824 | 0.000 | 0.000 |
| régression logistique | 0.839 | 0.847 | 0.527 |
| arbre de décision | 0.825 | 0.722 | 0.502 |
| forêt aléatoire | 0.882 | 0.540 | 0.720 |

## Mon choix, et pourquoi

Je choisis la régression logistique.

- Elle a le meilleur rappel (0.847) : elle détecte environ 85 % des pannes, alors qu'une panne manquée arrête une ligne.
- La baseline a 0.824 d'accuracy en répondant toujours « pas de panne », mais son rappel est de 0.000 : elle ne détecte rien.
- La forêt aléatoire a la meilleure accuracy (0.882) et la meilleure précision (0.720), mais son rappel n'est que de 0.540 : elle laisse passer près d'une panne sur deux. L'accuracy ne suffit donc pas pour choisir ici.
- Le prix à payer : la précision de la régression logistique est de 0.527, soit environ une alerte sur deux qui est fausse.

## Le critère (rappel >= 0,75) est-il atteint ?

**Oui.** Le rappel de la régression logistique est de 0.847, soit environ 10 points au-dessus de l'objectif de 0.75. Il dépasse aussi le seuil de 0,80 fixé dans notre étude de conception.

Ce résultat est à nuancer : le jeu de test contient environ 176 pannes, donc le rappel est connu à environ ± 5 points près.

## Ce qui reste flou

- Une alerte sur deux est fausse : les équipes pourront-elles absorber cette charge sans ignorer le système ?
- Le seuil de décision (0,5 par défaut) n'a pas été ajusté : le baisser ou le monter changerait l'équilibre entre rappel et précision.
- Un seul découpage du jeu de test : le résultat pourrait légèrement changer avec un autre tirage.


# TP0 : CantineAI

**Nom :** Samouh Hajar · **Groupe :** [Samouh - Benchakroune - Halal - Bounjoume]

## Le problème

Prédire le nombre de repas servis chaque jour à la cantine, à partir du calendrier et du contexte (nombre d'inscrits, menu, météo, examens, sorties scolaires, veille de vacances). C'est un problème de **régression** sur une série temporelle : on prédit un nombre, et les jours se suivent. Une bonne prédiction évite le gaspillage (trop de repas préparés) et les ruptures (pas assez).

## Réglages utilisés

Le code est celui de MaintAI. Seul `config.py` change, plus la liste des modèles de régression dans `models.py` :

| Réglage | Valeur |
|---|---|
| `TARGET` | `repas_servis` |
| `TASK` | `regression` |
| `MAIN_METRIC` | `mae` |
| `SPLIT` | `chronologique` |
| `TIME_COLUMN` | `date` |

Modèles comparés : baseline (moyenne), régression linéaire, forêt aléatoire, gradient boosting.

## Résultats sur le jeu de test

Le jeu de test est formé des 20 % de jours les plus récents.

| Modèle | MAE (repas) | RMSE | R² |
|---|---|---|---|
| baseline (moyenne) | 70.271 | 88.416 | -0.151 |
| régression linéaire | 22.239 | 28.170 | 0.883 |
| forêt aléatoire | 31.825 | 41.647 | 0.745 |
| gradient boosting | 29.852 | 37.727 | 0.790 |

## Mon choix, et pourquoi

Je choisis la régression linéaire.

- C'est le modèle avec la plus petite erreur : MAE de 22,2 repas, contre 70,3 pour la baseline.
- Elle se trompe donc environ trois fois moins que la baseline, soit 48 repas de moins par jour en moyenne.
- Son R² est de 0.883 : elle explique la grande majorité des variations du nombre de repas. La baseline a un R² négatif : elle fait moins bien que prédire la moyenne du jeu de test.
- Elle bat aussi le gradient boosting (29,9) et la forêt aléatoire (31,8). Avec environ 340 jours de données, un modèle simple généralise mieux, et les effets (inscrits, examens, sorties, veille de vacances) sont plutôt additifs.

## Pourquoi un découpage chronologique ?

Les repas sont servis jour après jour : un jour ressemble à la veille et au lendemain. Avec un découpage aléatoire, le test contiendrait des jours voisins de jours d'entraînement, et le modèle aurait en quelque sorte déjà vu la réponse. La MAE serait trop optimiste. En réalité, on prédit le futur à partir du passé, donc le test doit être composé des jours les plus récents.

## Le résultat est-il satisfaisant ?

Le meilleur modèle bat nettement la baseline (22,2 contre 70,3 repas d'erreur), donc les variables apportent une vraie information. Le sujet ne fixe pas de seuil de réussite : une erreur de 22,2 repas représente environ 4 à 5 % si la cantine sert environ 500 repas par jour, mais je ne peux pas dire si elle est acceptable pour la cuisine sans connaître le coût d'un repas en trop ou en moins.

## Ce qui reste flou

- La colonne `repas_semaine_precedente` a 60 valeurs manquantes sur 340. Le code les remplace par la médiane. Ce n'est pas idéal : un jour manquant n'est pas un jour « médian ».
- Le test ne couvre qu'une période courte (environ 68 jours) : l'erreur pourrait être différente sur une autre période de l'année.
- Le gradient boosting est utilisé avec ses réglages par défaut : mieux réglé, il pourrait se rapprocher de la régression linéaire.
- Quelle erreur la cuisine peut-elle tolérer ? Sans cet objectif, je ne peux pas dire si 22,2 repas est assez bon.