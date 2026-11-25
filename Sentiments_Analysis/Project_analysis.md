# Étude de conception --- Darija YouTube Sentiment Analyzer

**Groupe :** \[Samouh Hajar - Benchakroune Imane - Halal Saad - Bounjoume Oussama\]\
**Version :** Brouillon\ (This version can be ajusted anytime through the project)
**Date :** 11 novembre 2026

## 1. Contexte et utilisateurs

-   **Organisation ou situation :** Projet académique ou indépendant
    d'analyse de sentiment sur les réseaux sociaux.
-   **Utilisateur principal :** Créateurs de contenu, agences marketing
    ou chercheurs souhaitant évaluer la réaction du public marocain face
    à une vidéo YouTube.

## 2. Problème et décision

-   **Décision prise avec le système :** Déterminer si une vidéo est
    globalement bien reçue (sentiment positif) ou mal reçue (sentiment
    négatif) par la communauté, afin d'aider les créateurs à adapter
    leur stratégie de contenu ou de communication.
-   **Fréquence d'utilisation :** À la demande, pour chaque vidéo
    analysée.
-   **Conséquences possibles d'une erreur :** Une mauvaise évaluation
    (faux positifs ou faux négatifs) peut induire les créateurs en
    erreur et les conduire à produire du contenu qui ne correspond pas
    aux attentes de leur audience. Pour les chercheurs, elle peut
    fausser les conclusions d'études sociologiques.

## 3. Approche par sous-problème

  -----------------------------------------------------------------------
  Sous-problème           Approche (règles / ML / Pourquoi ne pas choisir
                          DL / LLM / RAG)         une approche plus
                                                  simple ?
  ----------------------- ----------------------- -----------------------
  **Nettoyage et          Règles : expressions    Le ML serait
  normalisation**         régulières (Regex) et   disproportionné pour
                          dictionnaires de mots   des opérations standard
                          vides (stopwords) en    de nettoyage de texte.
                          darija et en arabe.     

  **Vectorisation du      ML : TF-IDF ; DL :      TF-IDF est rapide et
  texte**                 Darija-BERT ou          robuste. BERT permet de
                          Multilingual BERT.      mieux capturer le
                                                  contexte sémantique
                                                  complexe de la darija.

  **Classification        ML : Linear SVM et      SVM et régression
  (positif / négatif)**   régression logistique ; logistique constituent
                          DL : fine-tuning de     de bonnes références
                          BERT.                   pour des jeux de
                                                  données de taille
                                                  moyenne (moins de 10
                                                  000 exemples). BERT
                                                  pourra être envisagé si
                                                  le volume de données
                                                  augmente.

  **Agrégation du         Règles : calcul de      Un modèle ML n'est pas
  sentiment global**      pourcentages.           nécessaire pour
                                                  calculer la proportion
                                                  de commentaires
                                                  positifs et négatifs.
  -----------------------------------------------------------------------

## 4. Données

  -----------------------------------------------------------------------
  Jeu de données    Source et licence Volume estimé     Données
                                                        personnelles ?
  ----------------- ----------------- ----------------- -----------------
  **Commentaires    YouTube Data API  Environ 5 000     Oui,
  YouTube de        ; conditions      commentaires      potentiellement :
  Hespress**        d'utilisation et                    noms d'auteurs et
                    règles de                           identifiants. Ces
                    réutilisation de                    éléments doivent
                    YouTube                             être supprimés ou
                    applicables.                        anonymisés avant
                                                        toute
                                                        publication.

  **Stopwords       Fichiers texte    Environ 2 000     Non
  (darija /         open source ;     mots              
  arabe)**          licence à                           
                    vérifier selon la                   
                    source retenue.                     
  -----------------------------------------------------------------------

> **Remarque :** La disponibilité via l'API YouTube ne signifie pas
> automatiquement que les données sont libres de droits ou librement
> redistribuables. Il faudra vérifier les conditions applicables à la
> collecte, au stockage et à la publication des données.

## 5. Métriques, baseline et critères d'acceptation

-   **Baseline proposée :** TF-IDF (n-grammes de mots et de caractères)
    avec régression logistique.
-   **Résultat attendu de la baseline :** Environ 70 à 75 % de
    précision, à confirmer expérimentalement sur un jeu de test annoté.
    Cette valeur est une estimation, pas un résultat mesuré.
-   **Métrique principale :** **F1-score pondéré (Weighted F1-score)**.
    Cette métrique tient compte de la précision et du rappel de chaque
    classe, tout en pondérant les classes selon leur effectif. Elle est
    utile lorsque les classes sont déséquilibrées.
-   **Critères d'acceptation visés :**
    -   F1-score pondéré supérieur à 0,75 sur un jeu de test
        indépendant, comparé à des annotations humaines.
    -   Temps d'inférence inférieur à une minute pour 500 commentaires,
        sur l'environnement matériel retenu.

## 6. Architecture prévue

1.  **Entrée :** URL de la vidéo YouTube.
2.  **Ingestion :** Récupération des commentaires via l'API YouTube, à
    l'aide de `google-api-python-client`.
3.  **Prétraitement :** Nettoyage du texte (Regex et traitement des
    emojis), normalisation, suppression éventuelle des stopwords et
    translittération de l'Arabizi vers l'alphabet arabe lorsque cela est
    pertinent.
4.  **Vectorisation :** TF-IDF pour la baseline ou représentations
    issues de Darija-BERT pour une approche avancée.
5.  **Inférence :** Classification des commentaires par un modèle ML ou
    DL entraîné.
6.  **Sortie :** Répartition des sentiments (par exemple : 65 % positifs
    et 35 % négatifs), accompagnée de graphiques et d'indicateurs
    synthétiques.

## 7. Choix technologiques

  ----------------------------------------------------------------------------
  Besoin                  Outil                        Justification
  ----------------------- ---------------------------- -----------------------
  **Ingestion des         `google-api-python-client`   Client Python de l'API
  données**                                            officielle YouTube ;
                                                       utilisation soumise aux
                                                       quotas et conditions de
                                                       l'API.

  **Traitement du texte** `regex`, `numpy`, `pandas`   Outils courants pour le
                                                       nettoyage, la
                                                       manipulation et
                                                       l'analyse des données.

  **Modélisation ML**     `scikit-learn`               Bibliothèque
                                                       accessible, efficace et
                                                       adaptée aux modèles de
                                                       référence
                                                       interprétables.

  **Modélisation DL**     `transformers`, `torch`      Permet d'utiliser et
                                                       d'adapter des modèles
                                                       de type BERT.

  **Interface (évolution  `FastAPI` ou `Streamlit`     Permettrait de rendre
  future)**                                            l'outil accessible
                                                       depuis une interface
                                                       web ou une API.
  ----------------------------------------------------------------------------

## 8. Risques, éthique et confidentialité

1.  **Biais des données :** Les commentaires provenant d'une seule
    chaîne (Hespress) peuvent refléter le vocabulaire, les sujets et les
    opinions propres à cette audience. Le modèle risque donc de mal
    généraliser à d'autres communautés.
2.  **Sarcasme et ironie :** Ces formes d'expression sont difficiles à
    détecter pour les modèles classiques et peuvent également poser
    problème aux modèles BERT.
3.  **Confidentialité :** Les noms d'utilisateurs et identifiants
    doivent être supprimés ou anonymisés lorsque leur conservation n'est
    pas nécessaire. Les règles applicables à la protection des données
    doivent être respectées.
4.  **Évolution du langage :** La darija évolue rapidement, notamment
    avec l'apparition de nouveaux mots, expressions et usages de
    l'argot. Le modèle devra être réévalué périodiquement.
5.  **Faux positifs et contexte :** Un commentaire contenant des
    insultes ou des mots grossiers peut être positif dans un contexte
    amical ou humoristique. Le vocabulaire seul ne suffit donc pas à
    déterminer le sentiment.
6.  **Transparence :** Les résultats doivent être présentés comme une
    aide à la décision et non comme une vérité absolue sur l'opinion du
    public.
7.  **Dépendance à l'API :** Les quotas, limites d'accès et éventuelles
    évolutions de l'API YouTube peuvent affecter la collecte des
    commentaires.
8.  **Sécurité :** Les données collectées, les modèles et les
    éventuelles représentations vectorielles doivent être stockés et
    protégés de manière appropriée.

## 9. Limites et hors périmètre

-   **Limites :**
    -   Le système peut rencontrer des difficultés avec les commentaires
        qui mélangent l'arabe, le français et la darija écrite en
        alphabet latin (Arabizi).
    -   L'analyse porte uniquement sur le texte des commentaires. Le
        contenu visuel et audio de la vidéo n'est pas analysé.
    -   Les résultats dépendent de la qualité, de la représentativité et
        de l'annotation des données disponibles.
-   **Hors périmètre :**
    -   Analyse en temps réel ou traitement en streaming.
    -   Détection des bots et des faux comptes.
    -   Développement d'une application mobile.
