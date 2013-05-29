#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
TODO:
	- creer un script darwin_download.py qui charge le json et télécharge les mp3
Donc le flow normal est :
	- darwin_create_database.py: mise à jour de la base
	- darwin_create_webpage.py: à partir de la base, création de la page web public
	- darwin_download.py: à partir de la base, téléchargement des mp3
"""

import urllib
import re
from os.path import isfile
import datetime
import os
import json
from pyquery import PyQuery as pq
from lxml import etree
import argparse
import requests

import codecs,sys
sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

#####################################################################

def url_to_mp3(url):
	page = requests.get(url)
	regexp = re.compile(r"sites%2Fdefault.+\.mp3")
	for line in page.text.split('\n'):
		match = regexp.search(line)
		if match:
			mp3 = match.group(0)
			mp3_url = "http://www.franceinter.fr/" + urllib.unquote(mp3)
			return mp3_url
	return False

#####################################################################

parser = argparse.ArgumentParser(description='Création (ou mise à jour) d\'une base de données JSON pour une émission de France Inter.')

parser.add_argument('-id', metavar='emission_id', help='L\'identifiant de l\'émission', default='137151')
parser.add_argument('-debut', metavar='mois_debut', help='Le mois de départ au format YYYY-MM. Exemple : "2010-09"', default='2010-09')
parser.add_argument('-fin', metavar='mois_fin', help='Le mois de fin au format YYYY-MM. Exemple : "2013-02"', default='2013-08')
parser.add_argument('-dest', metavar='fichier JSON', help='Le fichier JSON dans lequel enregistrer la base de données.', default=u"./output/darwin_base.json")
parser.add_argument('-force', help='Pour forcer la mise a jour des infos', action='store_true')
args = parser.parse_args()

radio_nom = "franceinter"
emission_id = args.id
mois_start = args.debut
mois_end = args.fin
force = args.force


emission_url = "http://www."+radio_nom+".fr/reecouter-diffusions/"+emission_id+"/"

if mois_start>mois_end:
	print u"Les mois ne sont pas cohérents..."
	exit(1)
else:
	a_start,m_start = int(mois_start[:4]),int(mois_start[-2:])
	a_end,m_end = int(mois_end[:4]),int(mois_end[-2:])

	mois_list = []
	if a_start==a_end:
		for mois in range(m_start,m_end+1):
			if mois < 10:
				mois_str = '0'+str(mois)
			mois_list.append(str(a_start)+"-"+ mois_str)
	else:
		for annee in range(a_start,a_end+1):
			for mois in range(1,13):
				if annee == a_start and mois >= m_start or annee == a_end and mois <= m_end or annee > a_start and annee < a_end:
					# print mois
					mois_str = str(mois)
					if mois < 10:
						mois_str = '0'+str(mois)
					mois_list.append(str(annee)+"-"+ mois_str)

print mois_list

json_file = args.dest

#####################################################################

if os.path.isfile(json_file) :
	input_json = open(json_file, 'r')
	data = json.load(input_json)
	input_json.close()
	data = data['emissions']
else:
	data = []

titles_list = [d['infos']['titre'] for d in data]
titles_list = []

regexp_date = re.compile(r"([0-9]{2})/([0-9]{2})/([0-9]{4})")

d = pq(url=emission_url)

for bb in d('.bloc'):

	emission_data = {}

	title =  pq(bb).find('.content h3').text()
	#print title
	emission_data['titre'] = title

	date =  pq(bb).find('.date').text()

	match = regexp_date.search(date)
	jour,mois,annee = match.group(1),match.group(2),match.group(3)
	#print jour,mois,annee

	if annee+'-'+mois in mois_list:

		print title
		print jour,mois,annee

		emission_data['date'] = {'annee':annee, 'mois':mois, 'jour':jour}

		emission_hash = annee + "-" + mois + "-" + jour

		if force or (not emission_hash in [e['hash'] for e in data]):

			emission_link = "http://www.franceinter.fr" + pq(bb).find('.content h3 a').attr('href')
			print emission_link
			emission_data['lien_emission'] = emission_link

			if pq(bb).find('.ecouter a:first'):

				player_link = "http://www.franceinter.fr" + pq(bb).find('.ecouter a:first').attr('href')
				print player_link
				emission_data['lien_ecouter'] = player_link

				mp3_link = url_to_mp3(player_link)
				print mp3_link
				emission_data['lien_mp3'] = mp3_link

			if re.match(r'.*rediffusion.*', title, re.IGNORECASE) or title in titles_list:
				emission_data['rediffusion'] = 1
			else:
				emission_data['rediffusion'] = 0

			if emission_hash in [e['hash'] for e in data]:
				index = [data.index(e) for e in data if e['hash']==emission_hash][0]
				data[index] = {'hash': emission_hash, 'infos': emission_data}
			else:
				data.append({'hash': emission_hash, 'infos': emission_data})
			titles_list.append(title)

		else:
			print u"Emission déjà dans la base !"

	else:
		#print u"Pas dans l'intervalle !"
		pass


data.sort(key=lambda e: e['hash'])

data_v2 = {'emissions': data}
# data_v2 = {'emissions':[{'hash': emission_hash, 'infos': data[emission_hash]} for emission_hash in data]}

output_json = open(json_file, 'wb')
json_str = json.dumps(data_v2, indent=4, separators=(',', ': '), sort_keys=True)
output_json.write(json_str)
output_json.close()

print "\n" + str(len(data)) + u" émissions."
print u"Base de données exportée : "+json_file
