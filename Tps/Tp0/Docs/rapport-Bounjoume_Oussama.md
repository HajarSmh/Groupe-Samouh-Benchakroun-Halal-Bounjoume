# TP0 : MaintAI

**Nom :** Bounjoume Oussama · **Groupe :** [Samouh - Benchakroune - Halal - Bounjoume]

## 1. Le problème

Une usine veut prédire les pannes de ses équipements à partir de mesures capteurs, avant qu'elles n'arrivent. Quatre variables sont disponibles à chaque relevé : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`. La cible est binaire (`failure` : 0 = pas de panne, 1 = panne).

Le coût des deux types d'erreur est asymétrique :

- **Faux négatif** (on prédit « pas de panne », la machine tombe en panne) : arrêt de la ligne de production, casse matérielle, coûts de réparation, risque pour la sécurité des opérateurs. C'est l'erreur la plus grave.
- **Faux positif** (on prédit « panne », mais il n'y en a pas) : arrêt inutile de la machine, perte de temps et d'argent, mais récupérable.

Conséquence directe : on cherche à **maximiser le rappel** sur la classe « panne », quitte à accepter une précision plus faible. C'est l'arbitrage assumé de bout en bout dans ce rapport.

## 2. Données et découpage

- **Fichier :** `data/exemple_pannes.csv`
- **Variables :** `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`
- **Cible :** `failure` — classification binaire, **déséquilibrée ≈ 82 % / 18 %** (les pannes sont minoritaires).
- **Découpage :** aléatoire **stratifié**, `test_size = 0.2`, `random_state = 42` (la stratification est nécessaire pour que la proportion de pannes soit respectée dans le test).
- **Taille du test :** ~ 950 lignes, dont **environ 176 pannes**.

Ce faible volume de pannes dans le test est important pour lire la suite : le rappel est estimé avec une précision de l'ordre de **± 5 points**. Un écart de 2 ou 3 points entre deux modèles n'est pas significatif.

## 3. Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision | F1 |
|---|---|---|---|---|
| Baseline (classe majoritaire) | 0.824 | 0.000 | 0.000 | 0.000 |
| Régression logistique | 0.839 | **0.847** | 0.527 | **0.649** |
| Arbre de décision | 0.825 | 0.722 | 0.502 | 0.592 |
| Forêt aléatoire | **0.882** | 0.540 | **0.720** | 0.617 |

**Lecture rapide.** Trois modèles se détachent de la baseline, mais aucun ne gagne sur *toutes* les métriques. C'est précisément le piège : l'accuracy et le rappel racontent deux histoires différentes, et c'est la métrique principale (le rappel) qui doit trancher.

## 4. Mon choix, et pourquoi

**Je choisis la régression logistique.**

- Elle obtient le **meilleur rappel (0.847)** : elle détecte environ 85 % des pannes du test, soit 149 pannes sur les 176 présentes.
- Elle obtient aussi le **meilleur F1 (0.649)**, ce qui signifie qu'elle offre le meilleur compromis global entre rappel et précision, une fois le déséquilibre pris en compte.
- Elle bat largement la baseline : +0.847 de rappel, alors que la baseline (qui prédit toujours « pas de panne ») ne détecte **aucune** panne.
- Elle devance l'arbre de décision (rappel 0.722) de plus de 12 points de rappel, pour une précision quasi identique.

Le prix à payer est une **précision de 0.527** : environ **une alerte sur deux est fausse**. C'est un coût réel pour les équipes de maintenance, mais acceptable au regard du coût d'une panne manquée.

## 5. Pourquoi pas la forêt aléatoire, malgré sa meilleure accuracy ?

C'est le point le plus important du rapport. La forêt aléatoire a :

- la meilleure **accuracy (0.882)**,
- la meilleure **précision (0.720)**,
- mais un **rappel de 0.540 seulement** : elle **laisse passer près d'une panne sur deux**.

C'est exactement le piège dénoncé dans l'étude de conception : sur un jeu déséquilibré, **l'accuracy est trompeuse**. La baseline atteint 0.824 d'accuracy sans rien détecter. La forêt aléatoire gagne 6 points d'accuracy sur la régression logistique, mais elle sacrifie 30 points de rappel — l'inverse de l'objectif métier. Dans une usine, cette accuracy plus élevée se traduirait par **plus de lignes arrêtées en panne imprévue**, pas par moins.

L'arbre de décision seul est un peu meilleur que la forêt sur le rappel (0.722 vs 0.540), mais reste en dessous de la régression logistique. Il souffre d'un biais : un arbre unique sur-apprend et généralise mal sur un petit jeu.

## 6. Le critère d'acceptation est-il atteint ?

L'étude de conception fixait **deux** critères simultanés :

| Critère | Seuil | Résultat LR | Statut |
|---|---|---|---|
| Rappel | ≥ 0.85 | 0.847 | **à 0.3 point près** |
| Précision | > 0.70 | 0.527 | ❌ **non atteint** |

**Bilan honnête.** Le rappel est *presque* au seuil (0.847 vs 0.85), l'écart est inférieur à la précision de mesure (± 5 points) — on peut donc dire qu'il est *statistiquement* au niveau visé, même s'il ne le dépasse pas nominalement. En revanche, la **précision de 0.527 est loin des 0.70 attendus** : c'est le critère qui n'est réellement pas tenu.

Si l'on se réfère au seuil **assoupli de 0.75** évoqué en cours, le rappel le dépasse confortablement (+10 points). La lecture dépend donc du référentiel : **oui** au seuil relâché, **presque** au seuil strict pour le rappel, **non** pour la précision.

## 7. Ce qui reste flou / Limites

- **Une alerte sur deux est fausse.** Les équipes de maintenance pourront-elles absorber cette charge sans finir par ignorer le système ? C'est le vrai risque opérationnel : un système qu'on n'écoute plus ne détecte plus rien, quelle que soit sa précision théorique.
- **Le seuil de décision (0,5) n'a pas été ajusté.** Le modèle renvoie une probabilité ; on la coupe à 0,5 par défaut. Le baisser augmenterait encore le rappel au prix de la précision ; le monter ferait l'inverse. Un réglage explicite du seuil — par exemple à 0,3 ou 0,4 — permettrait de calibrer l'arbitrage coût FN / coût FP au lieu de le subir.
- **Un seul découpage du test (random_state = 42).** Avec ~176 pannes, le rappel varie de quelques points d'un tirage à l'autre. Une **validation croisée stratifiée k-fold** donnerait un intervalle de confiance plutôt qu'un chiffre unique.
- **Baseline trompeuse.** Son rappel de 0 est un artefact du `DummyClassifier(strategy="most_frequent")` sur une cible déséquilibrée. Une baseline `stratified` donnerait un rappel non nul et un écart plus honnête à afficher.
- **Jeu synthétique.** Les chiffres peuvent bouger sur des données réelles de capteurs (bruit, dérive, valeurs aberrantes), non représentées ici.
- **Pas de données manquantes** dans l'exemple fourni : la robustesse du pipeline face aux NaN n'est donc **pas testée**.
- **Pas de coût chiffré.** Sans estimation du coût d'une panne (€/heure d'arrêt) et du coût d'une intervention inutile, il est impossible de dire si 0.527 de précision est *assez bon* — seulement qu'il est *meilleur* que les alternatives sur le rappel.

## 8. Recommandations / prochaines étapes

1. **Ajuster le seuil de décision** de la régression logistique, en traçant la courbe précision-rappel et en choisissant le point qui maximise le rappel sous une contrainte de précision acceptable pour les équipes.
2. **Passer à une validation croisée stratifiée** pour donner un intervalle de confiance sur le rappel (± quelques points) au lieu d'une estimation ponctuelle.
3. **Tester un modèle hybride** : garder la régression logistique comme détecteur principal (haut rappel) et n'utiliser la forêt aléatoire qu'en second filtre de confirmation sur les alertes — ce qui réduirait les faux positifs sans faire chuter le rappel.
4. **Chiffrer les coûts** (coût d'une panne, coût d'une intervention inutile) pour transformer l'arbitrage rappel/précision en **seuil métier** plutôt qu'en choix technique.
5. **Compléter par du rééchantillonnage** (SMOTE, `class_weight="balanced"`) pour voir si le rappel peut être poussé au-delà de 0.85 sans dégrader davantage la précision.

---

**En une phrase.** Sur ce jeu de données, la régression logistique est le seul modèle qui respecte l'objectif métier (détecter les pannes, pas maximiser l'accuracy) ; elle atteint un rappel de 0.847 — quasiment le seuil de 0.85 de l'étude de conception — au prix d'une précision de 0.527, et c'est cet arbitrage qu'il faut maintenant calibrer avec les équipes de maintenance.