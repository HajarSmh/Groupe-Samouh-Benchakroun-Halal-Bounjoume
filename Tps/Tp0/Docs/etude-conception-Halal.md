# Étude de Conception : [MaintAI]

**Groupe :** [Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama]
**Version :** [finale]
**Date :** [21/10/2026]

## 1. Contexte et utilisateurs
- **Organisation ou situation :** Une usine de production avec plusieurs machines équipées de capteurs (température, vibration, charge). Aujourd'hui, le suivi est fait par des seuils fixes sur chaque capteur : les alarmes arrivent soit trop tard (panne déjà en cours), soit trop souvent (fausses alarmes ignorées par les équipes).
- **Utilisateur principal (un rôle précis) :** Le chef d'atelier / superviseur de production, qui doit décider en cours de journée s'il laisse tourner une machine, la surveille de près ou programme son arrêt, en tenant compte du planning de production.

## 2. Problème et décision
- **Décision que l'utilisateur prend avec le système :** Quelle action prendre pour cette machine dans les prochaines 24 heures ? Trois niveaux : **Vert** (RAS), **Orange** (surveillance renforcée / inspection à la prochaine pause), **Rouge** (arrêt et intervention planifiés). Le système répond à la question de base : *la machine va-t-elle tomber en panne, oui ou non ?*, mais sous forme d'une probabilité de panne dans les 24h, transformée en niveau d'alerte.
- **Fréquence :** Un score recalculé toutes les heures à partir des relevés de température, vibration et charge.
- **Conséquence d'une erreur, et pour qui :**
  - *Faux positif (alerte rouge sans panne réelle) :* arrêt inutile, production perdue ; supporté par la direction (coût) et le chef d'atelier (perte de confiance dans l'outil).
  - *Faux négatif (aucune alerte, panne réelle) :* casse matérielle, arrêt de ligne non planifié, risque pour la sécurité des opérateurs.
  - *Fatigue d'alerte :* trop de fausses alarmes orange/rouge conduisent les équipes à ignorer le système, ce qui revient à accroître les faux négatifs.

## 3. Approche par sous-problème
- **Approche (règles / ML / DL / LLM / RAG) :** **ML supervisé** sur données tabulaires avec **variables temporelles**, complété par une détection d'anomalies non supervisée.
  - *Sous-problème 1 – Préparation :* construire à partir des 3 capteurs des variables de tendance (moyenne et écart-type glissants sur 6 h / 24 h, pente de la température, ratio vibration/charge).
  - *Sous-problème 2 – Prédiction :* classification binaire « panne dans les 24 h : oui/non » (Gradient Boosting, ex. LightGBM ou XGBoost) qui renvoie une probabilité.
  - *Sous-problème 3 – Décision :* deux seuils sur la probabilité (orange et rouge), choisis en fonction du coût d'une panne par rapport au coût d'un arrêt inutile.
  - *Sous-problème 4 – Filet de sécurité :* Isolation Forest (non supervisé) pour signaler un comportement inhabituel même si le modèle supervisé ne le reconnaît pas.
- **Pourquoi pas une approche plus simple :** Des seuils fixes (`SI temp > 80 ALORS alerte`) ne voient qu'une variable à la fois et réagissent **après** le dépassement. Une panne se prépare souvent par une dérive lente (la température monte de 2 °C par jour avec une vibration croissante à charge constante) que seules des variables de tendance combinées détectent. Un modèle de type DL (LSTM) serait inutilement lourd pour 3 capteurs et peu de pannes.

## 4. Données
- **Jeu de données :** Relevés horodatés de **Température**, **Vibration**, **Charge** par machine, avec l'étiquette « panne dans les 24 h suivantes » (0/1) construite à partir de l'historique des pannes.
- **Source et licence :** Données simulées ou dataset public (ex : Kaggle *Predictive Maintenance*, AI4I 2020, CC0 / licence ouverte). À vérifier avant usage.
- **Volume :** Environ 10 000 à 50 000 relevés horaires sur plusieurs machines, avec 3 à 5 % de lignes positives.
- **Découpage :** **Chronologique** (entraînement sur le passé, test sur la période la plus récente) et non aléatoire, pour éviter que le modèle voie le futur.
- **Données personnelles ? :** Non, uniquement des mesures physiques. Aucun RGPD à appliquer (veiller à ne pas ajouter l'identifiant de l'opérateur).

## 5. Métriques, baseline et critères d'acceptation
- **Baselines :**
  1. *Toujours « 0 »* : 95 % d'exactitude mais 0 % de rappel.
  2. *Règle à seuils fixes* (ex : température > 80 °C OU vibration > seuil) : sert de point de comparaison réaliste, car c'est ce qui existe aujourd'hui.
- **Métriques principales et pourquoi :**
  - **Rappel sur la classe « panne »** : rater une panne coûte le plus cher.
  - **Nombre de fausses alertes par machine et par semaine** : mesure la fatigue d'alerte.
  - **Coût total estimé** = (coût panne × FN) + (coût arrêt inutile × FP), avec par exemple un coût de panne 10 fois supérieur.
  - **PR-AUC** pour comparer les modèles malgré le déséquilibre (l'accuracy est écartée).
  - **Délai d'anticipation** : temps moyen entre la première alerte et la panne.
- **Critères d'acceptation :** sur un jeu de test chronologique d'au moins 2 000 lignes :
  - Rappel ≥ **0,80** sur les pannes ;
  - au plus **1 fausse alerte rouge par machine et par semaine** ;
  - **coût total réduit d'au moins 30 %** par rapport à la règle à seuils fixes ;
  - délai d'anticipation moyen ≥ **12 h**.