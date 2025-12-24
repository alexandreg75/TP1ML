TP 3 - Machine Learning

# Contexte

À l’issue des TP précédents, nous disposons d’un pipeline de données structuré autour de snapshots mensuels, stockés dans PostgreSQL, couvrant les utilisateurs, leurs abonnements, leur usage, les paiements et le support client. Ces snapshots permettent de figer l’état des données à différentes dates (fin de mois), garantissant une cohérence temporelle pour l’analyse et l’entraînement de modèles.

L’objectif du TP3 est de connecter ces données existantes à un Feature Store (Feast) afin de centraliser la définition, la version et l’accès aux features. Nous cherchons à récupérer ces features en mode offline pour construire un jeu de données d’entraînement, mais aussi en mode online pour une exposition en temps réel. Ce TP constitue ainsi une étape clé vers la mise en production d’un modèle de churn dans le projet StreamFlow.

# Mise en place de Feast

Ajout de Feast à l'architecture Docker : 

![Image 1](./images_TP3/Image1.png)

![Image 2](./images_TP3/Image2.png)

Modification du docker compose : 

![Image 3](./images_TP3/Image3.png)

Construction des images et démarrage des services : 

![Image 4](./images_TP3/Image4.png)

Les services ont été démarrés avec la commande suivante :

docker compose up -d --build


Le conteneur feast héberge la configuration du Feature Store Feast, située dans le dossier /repo à l’intérieur du conteneur, monté depuis services/feast_repo/repo du projet.
Il est utilisé pour appliquer la configuration du Feature Store (feast apply), matérialiser les features dans l’online store (feast materialize) et interroger Feast via docker compose exec feast ....

# Définition du Feature Store

![Image 5](./images_TP3/Image5.png)

Une Entity dans Feast représente un objet métier central (ici un utilisateur) sur lequel sont définies et jointes les features.

Le champ user_id est un bon choix de clé de jointure pour StreamFlow car il identifie de façon unique chaque client et est présent dans toutes les tables de snapshots (abonnements, usage, paiements, support).

![Image 6](./images_TP3/Image6.png)

![Image 7](./images_TP3/Image7.png)

Exemple de table snapshot : usage_agg_30d_snapshots.

Elle contient notamment les features watch_hours_30d, avg_session_mins_7d, unique_devices_30d, skips_7d et rebuffer_events_7d, décrivant l’intensité et la qualité d’usage de la plateforme par utilisateur.

![Image 8](./images_TP3/Image8.png)

![Image 9](./images_TP3/Image9.png)

Définition des FeatureViews : 

J'ai eu une erreur liée au fait que la table de support des snapshots sur 90 jours n'existait pas encore dans ma base : 

![Image 10](./images_TP3/Image10.png)

J'ai donc executé le flow Prefect avec les snapshots activés :

![Image 11](./images_TP3/Image11.png)

et ensuite relancé Feast : 

![Image 12](./images_TP3/Image12.png)

Le fichier registry.db a bien été créé : 

![Image 13](./images_TP3/Image13.png)

P.S :

J'ai pu outpass les warnings qui sont sortis lors du lancement de Feast en modifiant entities.py comme tel : 

![Image 14](./images_TP3/Image14.png)

Concernant feast apply, ca enregistre les Entities / DataSources / FeatureViews dans le registre Feast (registry.db) et configure l’infrastructure associée (offline/online store). 

Cette étape permet ensuite d’interroger Feast de façon cohérente en offline (training set) et en online (features à servir en prod), en s’appuyant sur la définition versionnée du Feature Store.

# Récupération offline & online

Après avoir créé le répertoire data/processed et modifié docker-compose.yml, j'ai redemarré les services : 

![Image 15](./images_TP3/Image15.png)

Voici le script python services/prefect/build_training_dataset.py complété : 

![Image 16](./images_TP3/Image16.png)

![Image 17](./images_TP3/Image17.png)

Voici les 5 premières lignes de data/processed/training_df.csv ainsi que la commande qui a permis de créer ce fichier:

![Image 18](./images_TP3/Image18.png)

Feast garantit la point-in-time correctness car chaque DataSource déclare timestamp_field = "as_of" : lors du get_historical_features, Feast ne joint les features que pour l’entité user_id à la date event_timestamp fournie. Comme notre entity_df contient (user_id, event_timestamp) dérivé du snapshot as_of = 2024-01-31, on récupère exactement l’état des features à cette date, sans “voir le futur”.

Matérialisation & récupération online :

![Image 19](./images_TP3/Image19.png)

Création de services/feast_repo/repo/debug_online_features.py :

![Image 20](./images_TP3/Image20.png)

Execution dans le conteneur feast : 

![Image 21](./images_TP3/Image21.png)

Dictionnaire retourné par get_online_features pour l'utilisateur 7590-VHVEG :

![Image 22](./images_TP3/Image22.png)

Si on interroge un user_id sans features matérialisées (utilisateur inexistant ou hors fenêtre de matérialisation), Feast renvoie des valeurs None/vides pour ces features, car l’Online Store ne contient aucune ligne correspondante pour cette entité.

Intégration minimale de Feast dans l’API : 

Mise à jour de docker compose :

![Image 23](./images_TP3/Image23.png)

Mise à jour de Dockerfile :

![Image 24](./images_TP3/Image24.png)

Création de api/requirements.txt :

![Image 25](./images_TP3/Image25.png)

Modification de api/app.py : 

![Image 26](./images_TP3/Image26.png)

L'api est bien démarrée : 

![Image 27](./images_TP3/Image27.png)

Test de l'endpoint /health : 

![Image 28](./images_TP3/Image28.png)

Test de l'endpoint /features/7590-VHVEG :

![Image 29](./images_TP3/Image29.png)

# Réflexion

L’endpoint /features/{user_id} aide à réduire le training-serving skew car il sert exactement les mêmes features (mêmes définitions Feast, mêmes transformations, mêmes sources) que celles utilisées pour générer le dataset d’entraînement via get_historical_features.

On évite ainsi d’avoir du code de features dupliqué entre “offline training” et “online serving”. En production, le modèle consomme les mêmes champs, avec la même logique et le même schéma, ce qui stabilise les performances et diminue les bugs de drift de pipeline.

Le dépôt a été tagué avec tp3.
    
