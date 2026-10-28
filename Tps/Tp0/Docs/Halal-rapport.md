# TP0 : MaintAI

**Nom :** Halal Saad · **Groupe :** [Samouh - Benchakroune - Halal - Bounjoume]

## Le problème

L'objectif est d'anticiper une panne à partir de quatre mesures de capteurs : la température, la vibration, la charge et les heures de fonctionnement. L'enjeu est important, car une panne non détectée immobilise toute une ligne de production.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---|---|---|
| baseline | 0.824 | 0.000 | 0.000 |
| régression logistique | 0.839 | 0.847 | 0.527 |
| arbre de décision | 0.825 | 0.722 | 0.502 |
| forêt aléatoire | 0.882 | 0.540 | 0.720 |

## Mon choix, et pourquoi

J'ai retenu la régression logistique, pour les raisons suivantes :

- C'est elle qui obtient le meilleur rappel (0.847), ce qui signifie qu'elle repère environ 85 % des pannes. Ce critère prime ici, puisqu'une panne ratée coûte l'arrêt d'une ligne.
- La baseline atteint une accuracy de 0.824 simplement en répondant toujours « pas de panne ». Son rappel est pourtant nul (0.000) : elle ne détecte absolument rien.
- La forêt aléatoire affiche la meilleure accuracy (0.882) ainsi que la meilleure précision (0.720). En revanche, son rappel ne dépasse pas 0.540, ce qui veut dire qu'une panne sur deux environ lui échappe. L'accuracy seule n'est donc pas un bon guide dans ce contexte.
- Cette performance a un coût : la précision de la régression logistique est de 0.527, autrement dit près d'une alerte sur deux est une fausse alerte.

## Le critère (rappel >= 0,75) est-il atteint ?

**Oui.** Avec un rappel de 0.847, la régression logistique dépasse l'objectif de 0.75 d'environ 10 points. Elle franchit également le seuil de 0,80 que nous avions fixé lors de l'étude de conception.

Il faut toutefois relativiser : le jeu de test comporte environ 176 pannes, si bien que le rappel est estimé avec une marge d'environ ± 5 points.

## Ce qui reste flou

- Une alerte sur deux étant fausse, il n'est pas certain que les équipes puissent traiter cette charge sans finir par ignorer le système.
- Le seuil de décision (0,5 par défaut) n'a pas été réglé. L'augmenter ou le diminuer modifierait l'équilibre entre rappel et précision.
- Je n'ai utilisé qu'un seul découpage du jeu de test : un autre tirage pourrait donner un résultat légèrement différent.


# TP0 : CantineAI

**Nom :** Halal Saad · **Groupe :** [Samouh - Benchakroune - Halal - Bounjoume]

## Le problème

Il s'agit de prévoir combien de repas seront servis chaque jour à la cantine, en s'appuyant sur le calendrier et sur le contexte : nombre d'inscrits, menu, météo, examens, sorties scolaires et veilles de vacances. C'est un problème de **régression** sur une série temporelle, puisque l'on cherche à prédire une quantité et que les jours s'enchaînent. Une bonne prévision permet d'éviter à la fois le gaspillage (trop de repas préparés) et les ruptures (pas assez de repas).

## Réglages utilisés

Le code reste celui de MaintAI. Seul le fichier `config.py` est modifié, ainsi que la liste des modèles de régression dans `models.py` :

| Réglage | Valeur |
|---|---|
| `TARGET` | `repas_servis` |
| `TASK` | `regression` |
| `MAIN_METRIC` | `mae` |
| `SPLIT` | `chronologique` |
| `TIME_COLUMN` | `date` |

Quatre modèles ont été comparés : la baseline (moyenne), la régression linéaire, la forêt aléatoire et le gradient boosting.

## Résultats sur le jeu de test

Le jeu de test correspond aux 20 % de jours les plus récents.

| Modèle | MAE (repas) | RMSE | R² |
|---|---|---|---|
| baseline (moyenne) | 70.271 | 88.416 | -0.151 |
| régression linéaire | 22.239 | 28.170 | 0.883 |
| forêt aléatoire | 31.825 | 41.647 | 0.745 |
| gradient boosting | 29.852 | 37.727 | 0.790 |

## Mon choix, et pourquoi

J'ai retenu la régression linéaire, car :

- Elle présente l'erreur la plus faible : une MAE de 22,2 repas, contre 70,3 pour la baseline.
- Elle se trompe ainsi environ trois fois moins que la baseline, soit 48 repas de moins par jour en moyenne.
- Son R² de 0.883 montre qu'elle rend compte de l'essentiel des variations du nombre de repas. Celui de la baseline est négatif, ce qui signifie qu'elle fait pire que la simple moyenne du jeu de test.
- Elle devance aussi le gradient boosting (29,9) et la forêt aléatoire (31,8). Avec environ 340 jours de données, un modèle simple généralise mieux, d'autant que les effets étudiés (inscrits, examens, sorties, veille de vacances) sont plutôt additifs.

## Pourquoi un découpage chronologique ?

Les repas sont servis jour après jour, et chaque journée ressemble à la veille comme au lendemain. Avec un tirage aléatoire, le jeu de test contiendrait des jours voisins de jours d'entraînement : le modèle aurait en quelque sorte déjà aperçu la réponse, et la MAE serait trop flatteuse. Dans la réalité, on prédit l'avenir à partir du passé. Le test doit donc être constitué des jours les plus récents.

## Le résultat est-il satisfaisant ?

Le meilleur modèle surpasse nettement la baseline (22,2 repas d'erreur contre 70,3), ce qui prouve que les variables utilisées apportent une réelle information. Le sujet ne définit aucun seuil de réussite. Une erreur de 22,2 repas équivaut à environ 4 à 5 % pour une cantine servant près de 500 repas par jour, mais je ne peux pas dire si c'est acceptable pour la cuisine sans connaître le coût d'un repas en trop ou en moins.

## Ce qui reste flou

- La colonne `repas_semaine_precedente` compte 60 valeurs manquantes sur 340. Le code les remplace par la médiane, ce qui n'est pas idéal : un jour sans donnée n'est pas forcément un jour « médian ».
- Le test ne couvre qu'une courte période (environ 68 jours), et l'erreur pourrait être différente à un autre moment de l'année.
- Le gradient boosting a été utilisé avec ses réglages par défaut. Une fois réglé, il pourrait se rapprocher de la régression linéaire.
- Je ne connais pas l'erreur que la cuisine peut tolérer : sans cet objectif, impossible de juger si 22,2 repas est suffisant.