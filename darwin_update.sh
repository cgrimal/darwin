#!/bin/sh
###
### C'est un script bash très simple pour mettre à jour la base des épisodes, et la page web associée.
### Il suffit à la fin, de faire un cp (ou un scp, ou ftp) vers le répertoire de son site web.
### C'est donc la base du script croné sur mon serveur pour mettre à jour ma page :
### http://clementgrimal.fr/darwin/
###
PMONTH=`date --date="last month" +"%Y-%m"`
CMONTH=`date +"%Y-%m"`
python darwin_create_database.py -debut $PMONTH -fin $CMONTH
python darwin_create_webpage.py
### Déplacer les fichiers index.php et darwin_base.json sur votre serveur web !
