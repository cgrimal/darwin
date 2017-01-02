#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json
import codecs
import argparse

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

#####################################################################

def str2filename(string):
    filename = re.sub(r'[<>:"/\|?*]', '-', string)
    filename = filename.strip('. ')
    filename = slugify(filename)
    return filename

def create_webpage(data, template_path, filename):
    html_code = ''
    current_month = ''
    new_season = True
    new_month = True

    months = [
        u'Janvier',
        u'Février',
        u'Mars',
        u'Avril',
        u'Mai',
        u'Juin',
        u'Juillet',
        u'Août',
        u'Septembre',
        u'Octobre',
        u'Novembre',
        u'Décembre'
    ]

    for emission_data in data:

        # emission_data = data[hash_dummy]
        emission_data = emission_data['infos']

        # print emission_data

        titre = emission_data['titre']
        jj, mm, aa = emission_data['date']['jour'], emission_data['date']['mois'], emission_data['date']['annee']
        pagelink = emission_data['lien_emission']
        # rediff = emission_data['rediffusion']

        if 'lien_ecouter' in emission_data:
            player_link = emission_data['lien_ecouter']
            mp3link = emission_data['lien_mp3']
        else:
            player_link = ''
            mp3link = ''

        new_month = False
        print titre
        # jj,mm,aa = date
        # month = months[int(mm) - 1]

        if mm == '09' and new_season:
            if current_month != '':
                html_code += '''
                            </ul>
                        </div>
                    </div>
                '''
                new_month = False
            html_code += '''
                <h2>Saison {a1}-{a2}</h2>
                <div class='saison'>
            '''.format(
                a1 = str(aa),
                a2 = str(int(aa) + 1),
            )
            new_season = False
        else:
            new_month = True

        if mm != '09':
            new_season = True

        if aa + mm != current_month:
            if current_month != '' and new_month:
                html_code += '''
                        </ul>
                    </div>
                '''
            html_code += u'''
                <h3>{mm} {aa}</h3>
                <div class='mois'>
                    <ul>
            '''.format(
                mm = months[int(mm) - 1],
                aa = str(aa),
            )
            current_month = aa + mm

        line = '    <li>'
        line += u'''
            <a class="link" href="{plink}" >{ptitre}</a>,
            diffusée le {date}
        '''.format(
            plink  = unicode(pagelink),
            ptitre = unicode(titre),
            date   = str(int(jj)) + u' ' + months[int(mm) - 1] + u' ' + str(aa),
        )
        link_name = aa + '-' + mm + '-' + jj + ' - ' + titre

        if player_link and mp3link:

            # TEST
            title = str2filename(titre)
            mlink = u'./files/{aa}-{mm}-{jj} - {title}.mp3'.format(
                aa    = aa,
                mm    = mm,
                jj    = jj,
                title = title,
            )
            # ENDOF TEST

            line += u'''
                <a class="mp3link" href="{plink}" >Ecouter</a>
                <a class="mp3link" href="{mlink}" download="{lname}" >Télécharger</a>
            '''.format(
                plink = unicode(player_link),
                mlink = unicode(mp3link),
                lname = unicode(link_name),
            )
        elif int(aa) < 2011 or (int(aa) == 2011 and int(mm) == 1):  # janvier 2011
            pascal_link = '''
                http://prevost.pascal.free.fr/public/podcast/sur_les_epaules_de_darwin/Jean-Claude%20Ameisen%20-%20SUR%20LES%20EPAULES%20DE%20DARWIN%20{jj}.{mm}.{aa}.mp3
            '''.format(
                jj = jj,
                mm = mm,
                aa = aa,
            )
            line += u'''
                <a class="mp3link" href="{plink}" download="{lname}" >Télécharger (via prevost.pascal.free.fr)</a>
            '''.format(
                plink = unicode(pascal_link),
                lname = unicode(link_name),
            )
        line += u'</li>\n'
        html_code += line

    html_code += '''
                </ul>
            </div>
        </div>
    '''

    template_file = codecs.open(template_path, 'r', 'utf-8')
    template = template_file.read()
    template_file.close()

    template = template.replace('%content', html_code)

    result_file = codecs.open(filename, 'w', 'utf-8')
    result_file.write(template)
    result_file.close()


#####################################################################

parser = argparse.ArgumentParser(
    description='Création d\'une page web à partir d\'une base de données JSON pour une émission de France Inter.'
)

parser.add_argument(
    '-base',
    metavar = 'fichier JSON',
    help    = 'Le fichier JSON qui contient la base de données.',
    default = './output/darwin_base.json'
)
parser.add_argument(
    '-web',
    metavar = 'page web',
    help    = 'Le fichier contenant la page web créee.',
    default = './output/index.php'
)
parser.add_argument(
    '-template',
    metavar = 'template',
    help    = 'Le fichier de template de la page web.',
    default = './output/temp_public.html'
)
args = parser.parse_args()

template_path = args.template
# template_path = './output/temp3.html'

json_file = args.base
# json_file = './output/darwin_base.json'

result_file = args.web
# result_file = './output/index.php'

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

print u'Création de la page web\n'

create_webpage(data, template_path, result_file)

print u'\nPage web créée : ' + result_file
