#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
TODO:
	//- utiliser la lib argparse pour les arguments du script
	//- utiliser la lib requests pour ouvrir la page web
	//- modifier aussi le script darwin_create_webpage.py
	- creer un script darwin_download.py qui charge le json et télécharge les mp3
Donc le flow normal est :
	- darwin_create_database.py: mise à jour de la base
	- darwin_create_webpage.py: à partir de la base, création de la page web public
	- darwin_download.py: à partir de la base, téléchargement des mp3
"""

# Python standard lib
import argparse
import codecs
import datetime
import json
import os
import re
import sys
import urllib
from os.path import isfile

# Third party
import requests
from lxml import etree
from pyquery import PyQuery as pq

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#####################################################################


def url_to_mp3(url):
    page = requests.get(url)
    # page = urllib.urlopen(url)
    regexp = re.compile(r"sites%2Fdefault.+\.mp3")
    for line in page.text.split("\n"):
        match = regexp.search(line)
        if match:
            mp3 = match.group(0)
            mp3_url = "http://www.franceinter.fr/" + urllib.unquote(mp3)
            return mp3_url
    return False


#####################################################################

parser = argparse.ArgumentParser(
    description="Création (ou mise à jour) d'une base de données JSON pour une émission de France Inter."
)

parser.add_argument(
    "-id", metavar="emission_id", help="L'identifiant de l'émission", default="137151"
)
parser.add_argument(
    "-debut",
    metavar="mois_debut",
    help='Le mois de départ au format YYYY-MM. Exemple : "2010-09"',
    default="2010-09",
)
parser.add_argument(
    "-fin",
    metavar="mois_fin",
    help='Le mois de fin au format YYYY-MM. Exemple : "2013-02"',
    default="2013-08",
)
parser.add_argument(
    "-dest",
    metavar="fichier JSON",
    help="Le fichier JSON dans lequel enregistrer la base de données.",
    default=u"./output/darwin_base.json",
)
args = parser.parse_args()

radio_nom = "franceinter"
emission_id = args.id
# emission_id = "137151"
mois_start = args.debut
# mois_start = "2010-09"
mois_end = args.fin
# mois_end = "2013-08"
# download_folder = args.dest
# download_folder = u"/media/Data/darwin/mp3/"


emission = "http://www." + radio_nom + ".fr/archives-diffusions/" + emission_id + "/"
# emission = "http://www."+radio_nom+".fr/reecouter-diffusions/"+emission_id+"/"

if mois_start > mois_end:
    print u"Les mois ne sont pas cohérents..."
    exit(1)
else:
    a_start, m_start = int(mois_start[:4]), int(mois_start[-2:])
    a_end, m_end = int(mois_end[:4]), int(mois_end[-2:])

    mois_list = []
    if a_start == a_end:
        for mois in range(m_start, m_end + 1):
            mois_list.append(str(a_start) + "-" + str(mois))
    else:
        for annee in range(a_start, a_end + 1):
            # print annee
            for mois in range(1, 13):
                if (
                    annee == a_start
                    and mois >= m_start
                    or annee == a_end
                    and mois <= m_end
                    or annee > a_start
                    and annee < a_end
                ):
                    # for mois in range(int(m_start),int(m_end)+1):
                    # print mois
                    mois_list.append(str(annee) + "-" + str(mois))

    # mois_list.reverse()

####

print mois_list


json_file = args.dest
# json_file = "./output/darwin_base.json"
# json_file_v2 = "./output/darwin_base.v2.json"

#####################################################################

if os.path.isfile(json_file):
    input_json = open(json_file, "r")
    data = json.load(input_json)
    input_json.close()
    data = data["emissions"]
else:
    data = []

# print data
# print [d['titre'] for d in data.values()]
titles_list = [d["infos"]["titre"] for d in data]
# print titles_list

regexp_date = re.compile(r"([0-9]{2})/([0-9]{2})/([0-9]{4})")

for mois in mois_list:

    page_url = emission + mois

    print "\nMois :", mois, page_url

    d = pq(url=page_url)

    for bb in d(".bloc"):

        emission_data = {}

        # if bb.find('.content h3'):
        title = pq(bb).find(".content h3").text()
        print title
        # if
        emission_data["titre"] = title

        date = pq(bb).find(".date").text()
        # print date

        match = regexp_date.search(date)
        jour, mois, annee = match.group(1), match.group(2), match.group(3)
        print jour, mois, annee
        emission_data["date"] = {"annee": annee, "mois": mois, "jour": jour}

        emission_hash = annee + "-" + mois + "-" + jour

        if not emission_hash in [e["hash"] for e in data[:-5]]:

            emission_link = "http://www.franceinter.fr" + pq(bb).find(
                ".content h3 a"
            ).attr("href")
            print emission_link
            emission_data["lien_emission"] = emission_link

            if pq(bb).find(".ecouter a:first"):

                player_link = "http://www.franceinter.fr" + pq(bb).find(
                    ".ecouter a:first"
                ).attr("href")
                print player_link
                emission_data["lien_ecouter"] = player_link

                mp3_link = url_to_mp3(player_link)
                print mp3_link
                emission_data["lien_mp3"] = mp3_link

            if (
                re.match(r".*rediffusion.*", title, re.IGNORECASE)
                or title in titles_list
            ):
                emission_data["rediffusion"] = 1
            else:
                emission_data["rediffusion"] = 0

            if emission_hash in [e["hash"] for e in data]:
                index = [
                    data.index(e) for e in data[-5:] if e["hash"] == emission_hash
                ][0]
                data[index] = {"hash": emission_hash, "infos": emission_data}
            else:
                data.append({"hash": emission_hash, "infos": emission_data})
            # data[emission_hash] = emission_data
            titles_list.append(title)

        else:
            print u"Emission déjà dans la base !"

# print data

# print {'hash': emission_hash for emission_hash,emission_data in data}


# emissions = d('.bloc')
# for emission_bloc in emissions:
# 	title = emission.find('.content h3').text()
# 	print title


# print json.dumps(data, indent=4, separators=(',', ': '))

# data.reverse()

# output_pickle = open(pickle_file, 'wb')
# pickle.dump(data, output_pickle)
# output_pickle.close()

# output_json = open(json_file, 'wb')
# json_str = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True)
# output_json.write(json_str)
# output_json.close()

data.sort(key=lambda e: e["hash"])

data_v2 = {"emissions": data}
# data_v2 = {'emissions':[{'hash': emission_hash, 'infos': data[emission_hash]} for emission_hash in data]}

output_json = open(json_file, "wb")
json_str = json.dumps(data_v2, indent=4, separators=(",", ": "), sort_keys=True)
output_json.write(json_str)
output_json.close()

print "\n" + str(len(data)) + u" émissions."
print u"Base de données exportée : " + json_file

# print u"\n\nCréation de la page web\n"

# create_webpage(data, template_path, main_folder + "index.php")
