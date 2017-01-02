#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Ajouter options pour écraser automatiquement,
    chosir les dates...
'''

import sys
import re
import json
import codecs
import argparse
import urllib2
import subprocess

from slugify import slugify
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.id3 import TPE1
from mutagen.id3 import TALB
from mutagen.id3 import TDRC
from os.path import isfile

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

#####################################################################


def download_file(url, filename):
    u = urllib2.urlopen(url)
    f = open(filename.encode('utf-8'), 'wb')
    meta = u.info()
    file_size = int(meta.getheaders('Content-Length')[0])
    print u'\rTéléchargement de %s (taille : %s)' % (unicode(filename), sizeof_fmt(float(file_size)))

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = '\t%3.1fMo  [%2d%%]' % (file_size_dl / (1024.**2), int(file_size_dl * 100. / file_size))
        status = status + chr(8) * (len(status) + 1)
        print status,
    f.close()


def sizeof_fmt(num):
    for x in ['octets', 'Ko', 'Mo', 'Go']:
        if num < 1024.0:
            return '%3.1f%s' % (num, x)
        num /= 1024.0
    return '%3.1f%s' % (num, 'To')


def str2filename(string):
    filename = re.sub(r'[<>:"/\|?*]', '-', string)
    filename = filename.strip('. ')
    filename = slugify(filename)
    return filename


#####################################################################

parser = argparse.ArgumentParser(
    description='A partir d\'une base de données JSON pour une émission de France Inter, télécharge les mp3.'
)

parser.add_argument(
    '-base',
    metavar = 'fichier JSON',
    help    = 'Le fichier JSON qui contient la base de données.',
    default = './output/darwin_base.json'
)
parser.add_argument(
    '-dossier',
    metavar = 'dossier de reception',
    help    = 'Le dossier qui contient les fichiers mp3.',
    default = './'
)
parser.add_argument(
    '-debut',
    metavar = 'mois_debut',
    help    = 'Le mois de départ au format YYYY-MM. Exemple : "2010-09"',
    default = '2010-09'
)
parser.add_argument(
    '-fin',
    metavar = 'mois_fin',
    help    = 'Le mois de fin au format YYYY-MM. Exemple : "2013-02"',
    default = '2013-08'
)
parser.add_argument(
    '-mega_config',
    metavar = 'fichier de configuration MEGA',
    help    = 'Le fichier JSON qui contient la configuration pour accéder à votre compte MEGA',
    default = './mega_config.json'
)
args = parser.parse_args()


json_file = args.base
download_folder = args.dossier
mois_start = args.debut
mois_end = args.fin
mega_config = args.mega_config

if mois_start > mois_end:
    print u'Les mois ne sont pas cohérents...'
    exit(1)
else:
    a_start, m_start = int(mois_start[:4]), int(mois_start[-2:])
    a_end, m_end     = int(mois_end[:4]), int(mois_end[-2:])

    mois_list = []
    if a_start == a_end:
        for mois in range(m_start, m_end + 1):
            mois_str = str(mois)
            if mois < 10:
                mois_str = '0' + str(mois)
            mois_list.append(str(a_start) + '-' + mois_str)
    else:
        for annee in range(a_start, a_end + 1):
            for mois in range(1, 13):
                if annee == a_start and\
                   mois >= m_start or annee == a_end and\
                   mois <= m_end or annee > a_start and\
                   annee < a_end:
                    # print mois
                    mois_str = str(mois)
                    if mois < 10:
                        mois_str = '0' + str(mois)
                    mois_list.append(str(annee) + '-' + mois_str)

# print mois_list

#####################################################################

input_json = open(json_file, 'r')
data = json.load(input_json)
input_json.close()

data = data['emissions']

cpt = 0

for emission_data in data:

    e_infos = emission_data['infos']

    if 'lien_mp3' in e_infos:

        jj, mm, aa = e_infos['date']['jour'], e_infos['date']['mois'], e_infos['date']['annee']
        titre      = e_infos['titre']
        rediff     = e_infos['rediffusion'] > 0
        lien_mp3   = e_infos['lien_mp3']

        if aa + '-' + mm in mois_list:

            title = str2filename(titre)
            filename = u'{aa}-{mm}-{jj} - {title}.mp3'.format(
                aa    = aa,
                mm    = mm,
                jj    = jj,
                title = title,
            )

            print titre
            if isfile(download_folder + filename.encode('utf-8')):
                print u'\rLe fichier ' + filename + u' existe déjà.'
            elif lien_mp3 is None:
                print u'\rPas d\'emission ce jour.'
            else:
                download_file(lien_mp3, download_folder + filename)

                audio = MP3(download_folder + filename.encode('utf-8'))
                audio['TIT2'] = TIT2(encoding=3, text=[title])
                audio['TPE1'] = TPE1(encoding=3, text=u'Jean-Claude Ameisen')
                audio['TALB'] = TALB(encoding=3, text=u'Sur les épaules de Darwin')
                audio['TDRC'] = TDRC(encoding=3, text=aa)
                audio.save()

                if isfile(mega_config):
                    # upload to MEGA
                    subprocess.call(
                        ['megacmd', '-conf', mega_config, 'put', download_folder + filename, 'mega:/darwin/']
                    )
                    print u'\nEmission envoyée sur Mega'

            cpt += 1

print u'\n', cpt, u'émissions téléchargées dans', download_folder
