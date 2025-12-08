TP 1 – Machine Learning

Exercice 1 :

Question 1.a/b : 

Image 1.png

Question 1.c : 

Image 2.png


La commande « docker ps -a » affiche la liste de tous les conteneurs présents sur ma machine, qu’ils soient en cours d’exécution ou arrêtés.

Exercice 2 :

Question 2.a : 
Une image Docker est un modèle qui contient tout l’environnement nécessaire pour exécuter un programme.
Un conteneur est l’instance de cette image quand elle tourne réellement.
En résumé : l’image c’est le modèle, le conteneur c’est l’exécution du modèle.
Question 2.b : 

Image 3.png

Après l’exécution de cette commande, le message s’affiche, puis le conteneur s’arrête immédiatement car il n’avait qu’une seule commande à exécuter.

Question 2.c : 

Image 4.png

Le conteneur Alpine apparaît avec un statut Exited car il s’est arrêté juste après avoir exécuté la commande echo. Il n’avait plus rien à faire.

Question 2.d : 
On se retrouve dans un shell Linux minimal. ls montre les dossiers du système, uname -a affiche des infos sur le noyau. Quand on tape exit, le conteneur s’arrête.

Image 5.png

Exercice 3 :

Question 3.a : 

Image 6.png

Question 3.b : 

Image 7.png

Question 3.c : 

Image 8.png

J’ai construit l’image Docker avec la commande docker build -t simple-api .
La construction s’est terminée sans erreur : Docker a téléchargé l’image de base Python, copié app.py, installé FastAPI et Uvicorn, puis créé l’image simple-api.

Exercice 4 :

Question 4.a :

Image 9.png

L’option « -p 8000:8000 » sert à mapper un port du conteneur sur un port de ma machine.
Ici, le port 8000 du conteneur (où tourne FastAPI) est accessible depuis le port 8000 de l’hôte, via http://localhost:8000.

Question 4.b :

Image 10.png

Quand j’appelle http://localhost:8000/health,  l’API répond bien avec le JSON :
{"status": "ok"}
Ce qui confirme que l’API FastAPI tourne correctement dans le conteneur Docker et que le mapping de ports fonctionne.

Question 4.c :

Image 11.png

La ligne correspondant au conteneur simple-api est la première : 
Le nom du conteneur est : funny_kapitsa
L’image utilisée est bien simple-api
Le port mappé est bien « 0.0.0.0:8000->8000/tcp » (port 8000 de l’hôte vers le port 8000 du conteneur)
Question 4.d :
On voit bien que le conteneur est arrêté et non visible dans docker ps mais bien visible dans docker ps -a : 

Image 12.png

- docker ps n’affiche plus ce conteneur, car il ne montre que les conteneurs en cours d’exécution.
- docker ps -a l’affiche car cette commande liste tous les conteneurs, même ceux qui sont arrêtés.

Exercice 5 :

Question 5.a/b :

Image 13.png

Question 5.c :

Image 14.png

Après docker compose up -d, les deux services db et api apparaissent dans docker compose ps.

Question 5.d :
C’est toujours accessible : 

Image 15.png

Question 5.e :

Image 16.png

- docker compose down arrête tous les conteneurs gérés par ce compose et les supprime.
- Alors que docker stop <id> ne concerne qu’un seul conteneur et ne le supprime pas.

Exercice 6 :

Question 6.a :

Image 17.png

- docker compose exec : exécute une commande à l’intérieur d’un conteneur déjà lancé.
- db : nom du service/contener défini dans docker-compose.yml 
- psql : client en ligne de commande pour PostgreSQL.
- -U demo : utilisateur PostgreSQL utilisé pour la connexion (demo).
- -d demo : base de données à laquelle on se connecte (demo).

Question 6.b :

Image 18.png

Question 6.c :
Un autre service Docker (par exemple l’API) pourrait se connecter à la base de données PostgreSQL en utilisant les infos suivantes :
- hostname : db
(c’est le nom du service dans docker-compose.yml, résolu automatiquement par Docker)
- port : 5432
(port interne du conteneur PostgreSQL ; le mapping 5434:5432 ne concerne que l’hôte)
- utilisateur : demo
- mot de passe : demo
- base : demo

Question 6.d :

Image 19.png

Avec l’option -v, on repart d’une base vide la prochaine fois qu’on relancera docker compose up (puisque les volumes qui contiennent les données persistantes sont aussi supprimées).

Exercice 7 :

Question 7.a :

Image 20.png

docker compose logs -f api affiche les logs du service api en temps réel.
- Quand l’API démarre correctement, on voit les messages de démarrage
- Quand j’appelle /health, une ligne de log supplémentaire apparaît avec la méthode (GET) et le chemin (/health), ce qui confirme que la requête est bien reçue par l’API.

Question 7.b :

Image 21.png

La commande docker compose exec api sh ouvre un shell à l’intérieur du conteneur de l’API.

- ls montre le contenu du répertoire de travail
- python --version affiche la version de Python installée dans le conteneur (celle définie dans l’image).
- exit ferme le shell et me renvoie au terminal de l’hôte.

Question 7.c :
J’ai bien redémarré l’API : 

Image 22.png

L’API est toujours accessible sur /health : 

Image 23.png

Un redémarrage est utile quand :
- on a modifié le code de l’API sans reconstruire l’image,
- l’API est bloquée ou en erreur temporaire,
- on veut repartir d’un état propre sans tout arrêter.

Question 7.d :
J’ai changé app.py en remplacant app = FastAPI() par app = FastAPII() :


Image 24.png


Après avoir reconstruit l’image et et relancé Docker Compose :

Image 25.png

J’observe ceci dans les logs : 


Image 26.png

Image 27.png


Après avoir introduit volontairement une erreur dans app.py et relancé docker compose up -d --build, le service api ne démarre plus correctement.
Avec docker compose logs -f api, on voit une trace d’erreur Python indiquant que le nom FastAPII n’existe pas .
C’est en lisant ces logs que j’ai pu identifier la cause : une erreur dans le code de app.py.

Question 7.e :

Image 28.png

- docker container prune supprime tous les conteneurs arrêtés (status Exited), qui ne servent plus.
- docker image prune supprime les images inutilisées
C’est utile de nettoyer régulièrement son environnement Docker pour libérer de l’espace disque, éviter d’accumuler des versions d’images obsolètes ou garder un environnement plus lisible et plus simple à gérer.


Exercice 8 :

Question 8.a :
Un notebook Jupyter n’est généralement pas adapté pour déployer un modèle de Machine Learning en production car il crée des états cachés (on peut exécuter des cellules dans n’importe quel ordre), ce qui rend la reproductibilité difficile, il n’assure pas un environnement maîtrisé : les dépendances peuvent varier d’une machine à l’autre et il n’est pas conçu pour être automatisé ni pour tourner en continu.
Au contraire, en production, on a besoin de pipelines fiables, versionnés et exécutables dans des environnements contrôlés (comme avec Docker dans ce TP).
Question 8.b :
Docker Compose est un outil essentiel lorsque l’on manipule plusieurs services (API, base de données…) car il permet de démarrer toute l’architecture avec une seule commande (docker compose up -d), de gérer le réseau entre les services automatiquement, et d’assurer un environnement reproductible. 
C’est indispensable en MLOps car un modèle utilise toujours plusieurs briques qui doivent fonctionner ensemble.

