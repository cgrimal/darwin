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
