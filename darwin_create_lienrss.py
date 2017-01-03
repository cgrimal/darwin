#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
import json
import argparse
import datetime
import urllib2

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

#####################################################################


def get_remote_file_size(url):
    # in bytes
    usock = urllib2.urlopen(url)
    size  = usock.info().get('Content-Length')
    if size is None:
        size = 0
    return float(size)


def create_rsslien(data, rss_template_path, rss_filename):
    rss_code = ''

    for emission_data in data:

        # emission_data = data[hash_dummy]
        emission_data = emission_data['infos']

        # print emission_data

        titre      = emission_data['titre']
        jj, mm, aa = emission_data['date']['jour'], emission_data['date']['mois'], emission_data['date']['annee']
        # pagelink   = emission_data['lien_emission']
        # rediff     = emission_data['rediffusion']

        if 'lien_ecouter' in emission_data:
            mp3link = emission_data['lien_mp3']
        else:
            mp3link = ''

        # rss code
        # print titre
        rss_pdate = jj + '-' + mm + '-' + aa
        rss_pubdate = datetime.datetime.strptime(rss_pdate, '%d-%m-%Y')
        rss_line = u'\t<item>'
        rss_line += u'''
            <title>{titre}</title>
            <description>
                Sur les épaules de Darwin - par : Jean-Claude Ameisen - réalisé par : Christophe IMBERT
            </description>
            <category>Science &amp; Medicine</category>
            <pubDate>{pubdate1}, {pubdate2} 19:00:00 +0100 </pubDate>
        '''.format(
            titre    = unicode(titre),
            pubdate1 = rss_pubdate.strftime('%a'),
            pubdate2 = rss_pubdate.strftime('%d %b %Y'),
        )

        # itune
        rss_line += u'''
            <itunes:author>Jean-Claude Ameisen</itunes:author>
            <itunes:explicit>no</itunes:explicit>
            <itunes:subtitle>
                Émission du {mm}.{jj}.{aa} {titre}
            </itunes:subtitle>
            <itunes:summary>Jean-Claude Ameisen - réalisé par : Christophe IMBERT</itunes:summary>
        '''.format(
            mm = mm,
            jj = jj,
            aa = aa,
            titre = unicode(titre),
        )

        if mp3link:

            # TEST
            title   = str2filename(titre)
            mp3link = u'http://www.clementgrimal.fr/darwin/files/{aa}-{mm}-{jj} - {title}.mp3'.format(
                aa    = aa,
                mm    = mm,
                jj    = jj,
                title = title,
            )
            # ENDOF TEST

            rss_line += u'''
                <guid>{mp3link}</guid><enclosure length="{file_size}" url="{mp3link}" type="audio/mpeg"/>
            '''.format(
                mp3link = unicode(mp3link),
                file_size = unicode(get_remote_file_size(mp3link)),
            )
        elif int(aa) < 2011 or (int(aa) == 2011 and int(mm) == 1):  # janvier 2011
            pascal_link = '''
            http://prevost.pascal.free.fr/public/podcast/sur_les_epaules_de_darwin/Jean-Claude%20Ameisen%20-%20SUR%20LES%20EPAULES%20DE%20DARWIN%20{jj}.{mm}.{aa}.mp3
            '''.format(
                mm = mm,
                jj = jj,
                aa = aa,
            )
            rss_line += u'''
                <guid>{pascal_link}</guid><enclosure length="0" url="{pascal_link}" type="audio/mpeg"/>
             '''.format(
                pascal_link = unicode(pascal_link),
            )
        rss_line += u'\t</item>\n'
        rss_code += rss_line
        print titre


    # rss_code
    rss_template_file = codecs.open(rss_template_path, "r", "utf-8")
    # template_file = open(template_path)
    rss_template = rss_template_file.read()
    rss_template_file.close()

    rss_template = rss_template.replace("%rss_content", rss_code)

    rss_result_file = codecs.open(rss_filename, "w", "utf-8")
    rss_result_file.write(rss_template)
    rss_result_file.close()

#####################################################################

parser = argparse.ArgumentParser(
    description='Création d\'un lien rss à partir d\'une base de données JSON pour une émission de France Inter.'
)

parser.add_argument(
    '-base',
    metavar = 'fichier JSON',
    help    = 'Le fichier JSON qui contient la base de données.',
    default = u'./output/darwin_base.json',
)
parser.add_argument(
    '-rss_template',
    metavar = 'template',
    help    = 'Le fichier de template du fichier rss.',
    default = u'./output/temp_public.rss'
)
parser.add_argument(
    '-rss',
    metavar = 'lien rss',
    help    = 'Le fichier contenant le fichier rss créee.',
    default = u'./output/darwin.rss'
)
args = parser.parse_args()

json_file = args.base
# json_file = "./output/darwin_base.json"

rss_template_path = args.rss_template
# template_path = "./output/temp_public.rss"

rss_result_file = args.rss
# rss_result_file = "/output/lien.rss"
#####################################################################

input_json = open(json_file, 'r')
data = json.load(input_json)
input_json.close()

data = data['emissions']
# print data

# keys = [e['hash'] for e in data]
# keys.sort()
# print keys
# sorted_data = [data['infos'] for key in keys]
# print sorted_data

print u'Création du lien rss\n'

create_rsslien(data, rss_template_path, rss_result_file)

print u'\nlien rss créée : ' + rss_result_file
