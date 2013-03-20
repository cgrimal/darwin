==========================================================
 ``Darwin`` -- Utilitaires autour du suivi de l'émission
==========================================================

Sur les épaules de Darwin, émission proposée par Jean-Claide Ameisen.
Diffusée sur France Inter tous les samedi matin de 11h à 12h, depuis Septembre 2009.

Ce projet contient les scripts python que j'utilise pour générer la page http://clementgrimal.fr/darwin/
Il est composé de 3 scripts :

- ``darwin_create_database.py`` : qui construit et exporte une base de données (dans un fichier json)
- ``darwin_create_database.py`` : qui construit la page web à partir de la base de données (et d'un template)
- ``darwin_download.py`` : qui télécharge les fichiers mp3 à partir de la base de données

Pré-requis
==========
- python
- python-pyquery
- python-lxml
- python-pip
- requests

Pour tout installer, sur une distribution de type Debian/Ubuntu :

    sudo apt-get install python-pyquery python-lxml python-pip

    sudo pip install requests

Utilisation
===========


Création de la base
-------------------

Il faut commencer par créer une base de données de toutes les émissions :

    python darwin_create_database.py

Cette commande va exporter dans ``output/darwin_base.json`` la liste des épisodes et des données suivantes :

- date de diffusion
- lien vers le lecteur flash de France Inter pour ré-écouter l'émission
- lien vers la page de l'épisode
- lien direct vers le fichier mp3 de l'épisode
- titre
- rediffusion : nombre de diffusions antérieures de cet épisode (En cours)

Les paramètres (et valeurs par défaut) de ce script sont les suivants :

- ``-id`` : l'identifiant de l'émission. Défaut : ``137151``
- ``-debut`` : le mois de départ au format YYYY-MM. Défaut : ``2010-09``
- ``-fin`` : le mois de fin au format YYYY-MM. Défaut : ``2013-08``
- ``-dest`` : Le fichier JSON dans lequel enregistrer la base de données. Défaut : ``./output/darwin_base.json``


Création de la page web
-----------------------

On peut ensuite générer la page web à partir de la base de données JSON :

    python darwin_create_webpage.py

Cette commande va se baser sur la base de données JSON pour générer une page web, utilisant un template. Les paramètres (et valeurs par défaut) de ce script sont les suivants :

- ``-base`` : le fichier JSON qui contient la base de données. Défaut : ``./output/darwin_base.json``
- ``-web`` : le fichier contenant la page web créee. Défaut : ``./output/index.php``
- ``-template`` : le fichier de template de la page web. Défaut : ``./output/index_public.html``


Téléchargement des épisodes
---------------------------

C'est un peu bonus (et pourtant j'ai fait tout ça pour ça au départ !), mais on peut également télécharger tous les épisodes que l'on souhaite avec :

    python darwin_download.py

Cette commande va se baser sur les liens mp3 de la base de données JSON pour télécharger les épisodes. Les paramètres (et valeurs par défaut) de ce script sont les suivants :

- ``-base`` : le fichier JSON qui contient la base de données. Défaut : ``./output/darwin_base.json``
- ``-dossier`` : le dossier qui contient les fichiers mp3. Défaut : ``/media/cgrimal/Data/darwin/mp3/`` !!A CHANGER!!
- ``-debut`` : le mois de départ au format YYYY-MM. Défaut : ``2010-09``
- ``-fin`` : le mois de fin au format YYYY-MM. Défaut : ``2013-08``