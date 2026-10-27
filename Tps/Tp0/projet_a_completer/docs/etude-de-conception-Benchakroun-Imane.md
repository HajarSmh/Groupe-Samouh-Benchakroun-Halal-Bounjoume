# Étude de conception — [MaintAI]

Groupe : [Benchakroun Imane - Samouh Hajar - Halal Saad - Bounjoume Oussama] · Version : [finale] · Date : [27/10/2026]

## 1. Contexte et utilisateurs

- **Organisation ou situation :** Une usine de production industrielle ou un atelier. Actuellement, la maintenance est soit préventive (systématique et parfois inutile), soit corrective (intervention après la panne, ce qui coûte cher).
- **Utilisateur principal (un rôle précis) :** Le responsable de maintenance ou le technicien d'atelier. Son rôle est de planifier les interventions sur les machines.

## 2. Problème et décision

- **Décision que l'utilisateur prend avec le système :** Doit-on planifier une intervention de maintenance préventive sur la machine aujourd'hui (ou arrêter la machine) ? (Oui / Non).
- **Fréquence :** À chaque nouveau relevé des capteurs (par exemple, une fois par jour ou toutes les heures).
- **Conséquence d'une erreur, et pour qui :**
  - *Faux positif (l'IA prédit une panne, mais il n'y en a pas) :* Arrêt inutile de la machine, perte de temps et d'argent pour l'entreprise.
  - *Faux négatif (l'IA prédit 0, mais la machine tombe en panne) :* Casse matérielle grave, arrêt de la chaîne de production, coûts de réparation élevés et risque pour la sécurité des opérateurs.
- **Pour qui :** Pour les équipes de maintenance et la direction de l'usine (pour la gestion des coûts).

## 3. Approche par sous-problème

- **Approche (règles / ML / DL / LLM / RAG) :** **ML (Machine Learning)** supervisé. Plus précisément, un modèle de **classification binaire** (Régression Logistique, Random Forest ou XGBoost).
- **Pourquoi pas une approche plus simple :** Une approche par règles simples (ex: `SI temp > 80°C ALORS panne = 1`) serait trop rigide. Elle ne capturerait pas les interactions complexes entre les trois variables (ex: une vibration élevée combinée à une charge moyenne mais une température basse). Le ML permet de trouver ces corrélations cachées dans les données historiques.

## 4. Données

- **Jeu de données :** Données historiques des capteurs de la machine (**Température**, **Vibration**, **Charge**) associées à l'étiquette "Panne" (0 ou 1).
- **Source et licence :** Données internes simulées ou issues d'un dataset public (ex: Kaggle - *Predictive Maintenance*), Licence Open Data (CC0).
- **Volume :** Par exemple, 10 000 lignes d'historique (représentant plusieurs mois de fonctionnement).
- **Données personnelles ? :** Non, ce sont uniquement des données physiques/mécaniques de la machine. Aucun RGPD à appliquer ici.

## 5. Métriques, baseline et critères d'acceptation

- **Baseline et son résultat :** La baseline consiste à prédire **toujours "0" (pas de panne)**. Puisque les pannes sont rares (par exemple 5% du dataset), cette baseline aurait une exactitude (accuracy) de 95%, mais un rappel de 0% (elle ne détecte aucune panne).
- **Métrique principale et pourquoi :** Le **Rappel (Recall)** sur la classe "1" (Panne) ou le **F1-Score**. Pourquoi ? Parce que les classes sont déséquilibrées et qu'un Faux Négatif (rater une panne) coûte beaucoup plus cher qu'un Faux Positif. On veut maximiser la détection des pannes.
- **Critères d'acceptation :** Le modèle doit atteindre un **Rappel d'au moins 0,85** (85%) sur un jeu de test de 2 000 lignes, tout en gardant une précision supérieure à 0,70.


