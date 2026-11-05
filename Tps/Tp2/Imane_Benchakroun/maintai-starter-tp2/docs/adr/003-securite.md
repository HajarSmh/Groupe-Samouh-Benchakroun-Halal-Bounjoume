# ADR 003 : Sécurité de l'API (clé API et CORS)

Date : 05/11/2026 · Auteurs : Imane Benchakroun

## Contexte
L'API MaintAI ne doit répondre qu'aux programmes autorisés. Une page web
servie sur http://localhost:5500 doit pouvoir l'appeler, une page servie
ailleurs non. La clé ne doit jamais apparaître dans le code ni dans Git.

## Décision 1 : où transmettre la clé

### Options étudiées
1. Dans l'en-tête X-API-Key : la clé ne fait pas partie de l'adresse et
   n'est pas enregistrée avec elle.
2. Dans l'URL (?key=...) : simple à tester dans un navigateur, mais l'URL
   est enregistrée partout (journaux du serveur, historique du navigateur,
   liens copiés), donc la clé fuit.
3. Dans le corps de la requête : la clé serait mélangée aux données du
   relevé et le schéma Pydantic devrait la connaître ; on ne pourrait plus
   protéger toutes les routes au même endroit, ni protéger un GET sans corps.

### Décision
La clé voyage dans l'en-tête X-API-Key, vérifiée par une dépendance du
router (Depends(require_api_key)) qui protège toutes les routes /v1.
/health reste public.

### Conséquences
Toutes les routes /v1 sont protégées par une seule ligne, et /docs affiche
un champ x-api-key. Les clients (page web, curl, Java) doivent ajouter un
en-tête à chaque requête. Le serveur répond 401 si la clé est absente ou
fausse, et 500 s'il n'a pas de clé configurée.

## Décision 2 : quelles origines autoriser (CORS)

### Options étudiées
1. Une liste précise d'origines, configurée dans .env
   (MAINTAI_CORS_ORIGINS) : seules les pages de ces origines peuvent
   appeler l'API depuis un navigateur. Il faut redémarrer uvicorn pour
   changer la liste.
2. L'étoile * : toutes les origines sont autorisées. Pratique, mais
   n'importe quel site pourrait faire appeler l'API par le navigateur d'un
   utilisateur : on perd la protection que CORS apporte à l'utilisateur.
3. Liste écrite en dur dans le code : elle ne se change pas sans modifier
   et recommitter le code, et elle diffère mal entre machine locale et
   production.

### Décision
Liste d'origines dans .env (http://localhost:5500 et http://127.0.0.1:5500),
lue au démarrage.

### Conséquences
Une page servie sur le port 5501 est bloquée par le navigateur. CORS ne
protège pas l'API elle-même : curl ou un programme Java passent sans
question de CORS, seule la clé les arrête. La liste devra être mise à jour
quand l'application sera déployée (séance 8).