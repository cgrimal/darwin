#!/usr/bin/env python

"""
Donc le flow normal est :
    - darwin_create_database.py: mise à jour de la base
    - darwin_create_webpage.py: à partir de la base, création de la page web public
    - darwin_download.py: à partir de la base, téléchargement des mp3
"""

# Python standard lib
import argparse
import json
import os
import re

# Third party
import dateparser
from pyquery import PyQuery as pq

#####################################################################


def getMonths(mois_start, mois_end):
    if mois_start > mois_end:
        print("Les mois ne sont pas cohérents...")
        exit(1)
    else:
        a_start, m_start = int(mois_start[:4]), int(mois_start[-2:])
        a_end, m_end = int(mois_end[:4]), int(mois_end[-2:])

        mois_list = []
        if a_start == a_end:
            for mois in range(m_start, m_end + 1):
                mois_str = str(mois)
                if mois < 10:
                    mois_str = "0" + str(mois)
                mois_list.append(str(a_start) + "-" + mois_str)
        else:
            for annee in range(a_start, a_end + 1):
                for mois in range(1, 13):
                    if (
                        annee == a_start
                        and mois >= m_start
                        or annee == a_end
                        and mois <= m_end
                        or annee > a_start
                        and annee < a_end
                    ):
                        mois_str = str(mois)
                        if mois < 10:
                            mois_str = "0" + str(mois)
                        mois_list.append(str(annee) + "-" + mois_str)
    return mois_list


def extractData(data, d):
    for bb in d(".card.highlight, .card-elements.stack .tile"):

        emission_data = {}

        title = pq(bb).find(".card-text .card-text-sub").text()
        emission_data["titre"] = title

        date_text = pq(bb).find(".card-text .date").text()

        date = dateparser.parse(date_text)

        # jour, mois, annee = match.group(1), match.group(2), match.group(3)
        jour, mois, annee = (
            str(date.day).zfill(2),
            str(date.month).zfill(2),
            str(date.year).zfill(4),
        )

        print(f"{jour}-{mois}-{annee} - {title}")

        if annee + "-" + mois in mois_list:

            hash_list = [e["hash"] for e in data]

            emission_data["date"] = {"annee": annee, "mois": mois, "jour": jour}

            emission_hash = annee + "-" + mois + "-" + jour

            if force or emission_hash not in hash_list:

                emission_link = pq(bb).find("a.card-text-sub").attr("href")
                if emission_link[0] == "/":
                    emission_link = "https://www.franceinter.fr" + emission_link
                print(emission_link)
                emission_data["lien_emission"] = emission_link

                player_link = emission_link
                emission_data["lien_ecouter"] = player_link

                mp3_link = pq(bb).find("button.replay-button").attr("data-url")
                emission_data["lien_mp3"] = mp3_link

                if (
                    re.match(r".*rediffusion.*", title, re.IGNORECASE)
                    or title in titles_list
                ):
                    emission_data["rediffusion"] = 1
                else:
                    emission_data["rediffusion"] = 0

                if emission_hash in hash_list:
                    index = [data.index(e) for e in data if e["hash"] == emission_hash][
                        0
                    ]
                    data[index] = {"hash": emission_hash, "infos": emission_data}
                    print("Emission mise à jour.")
                else:
                    data.append({"hash": emission_hash, "infos": emission_data})
                    print("Emission ajoutée.")
                titles_list.append(title)

            else:
                print("Emission déjà dans la base !")

        else:
            print("Pas dans l'intervalle !")
            pass

    return data


#####################################################################

parser = argparse.ArgumentParser(
    description="Création (ou mise à jour) d'une base de données JSON pour une émission de France Inter."
)
parser.add_argument(
    "-id",
    metavar="emission_id",
    help="L'identifiant de l'émission",
    default="sur-les-epaules-de-darwin",
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
    default="2014-08",
)
parser.add_argument(
    "-dest",
    metavar="fichier JSON",
    help="Le fichier JSON dans lequel enregistrer la base de données.",
    default="./output/darwin_base.json",
)
parser.add_argument(
    "--force", help="Pour forcer la mise a jour des infos", action="store_true"
)
parser.add_argument(
    "--all", help="Pour aller chercher dans toutes les pages", action="store_true"
)
args = parser.parse_args()

radio_nom = "franceinter"
emission_id = args.id
mois_start = args.debut
mois_end = args.fin
force = args.force
all_pages = args.all

emission_url = f"https://www.{radio_nom}.fr/emissions/{emission_id}"
print(emission_url)

mois_list = getMonths(mois_start, mois_end)

json_file = args.dest

#####################################################################

if os.path.isfile(json_file):
    input_json = open(json_file, "r")
    data = json.load(input_json)
    input_json.close()
    data = data["emissions"]
else:
    data = []

titles_list = [d["infos"]["titre"] for d in data]

d = pq(url=emission_url)
if all_pages:
    url_last_page = d(".pager-item.last a").attr("href")
    nb_pages = int(re.search(r"p=([0-9]+)", url_last_page).group(1))
    print(("{} pages trouves".format(nb_pages)))
    for p in range(1, nb_pages + 1):
        url = emission_url + "?p=" + str(p)
        print(("Chargement de la page : " + url))
        new_data = extractData(data, pq(url=url))
else:
    new_data = extractData(data, d)

data.sort(key=lambda e: e["hash"])

data_v2 = {"emissions": data}

output_json = open(json_file, "wb")
json_str = json.dumps(data_v2, indent=4, separators=(",", ": "), sort_keys=True)
output_json.write(json_str.encode())
output_json.close()

print(("\n" + str(len(data)) + " émissions."))
print(("Base de données exportée : " + json_file))
