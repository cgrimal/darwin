#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse

import codecs,sys
sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

#####################################################################

def create_webpage(data,template_path,filename):
    html_code = ""
    current_month = ""
    new_season = True
    new_month = True

    months = [
        u"Janvier",
        u"Février",
        u"Mars",
        u"Avril",
        u"Mai",
        u"Juin",
        u"Juillet",
        u"Août",
        u"Septembre",
        u"Octobre",
        u"Novembre",
        u"Décembre"
    ]

    for emission_data in data:

        # emission_data = data[hash_dummy]
        emission_data = emission_data['infos']

        # print emission_data

        titre = emission_data['titre']
        jj,mm,aa = emission_data['date']['jour'],emission_data['date']['mois'],emission_data['date']['annee']
        pagelink = emission_data['lien_emission']
        rediff = emission_data['rediffusion']

        if 'lien_ecouter' in emission_data:
            player_link = emission_data['lien_ecouter']
            mp3link = emission_data['lien_mp3']
        else:
            player_link = ''
            mp3link = ''

        new_month = False
        print titre
        # jj,mm,aa = date
        month = months[int(mm)-1]

        if mm == "09" and new_season:
            if current_month != "":
                html_code += "</ul></div>\n</div>\n"
                new_month = False
            html_code += "<h2>Saison " + aa + "-" + str(int(aa)+1) + "</h2>\n<div class='saison'>\n"
            new_season = False
        else:
            new_month = True

        if mm != "09":
            new_season = True
            

        if aa+mm != current_month:
            if current_month != "" and new_month:
                html_code += "</ul></div>\n"
            html_code += "<h3>" + months[int(mm)-1] + " " + aa + "</h3>\n<div class='mois'>\n"
            html_code += "<ul>\n"
            current_month = aa+mm

        line =  u'\t<li>'
        line += u'<a class="link" href="' + unicode(pagelink) + '" >' + unicode(titre) + u'</a>, diffusée le ' + str(int(jj)) + u' ' + months[int(mm)-1]
        link_name = aa+'-'+mm+'-'+jj+' - '+titre
        if player_link and mp3link:
            line += u' <a class="mp3link" href="' + unicode(player_link) + u'" >Ecouter</a> '
            line += u' <a class="mp3link" href="' + unicode(mp3link) + u'" download="' + unicode(link_name) + u'" >Télécharger</a>\n'
        elif int(aa)<2011 or (int(aa)==2011 and int(mm)==1): #janvier 2011
            pascal_link = "http://prevost.pascal.free.fr/public/podcast/sur_les_epaules_de_darwin/Jean-Claude%20Ameisen%20-%20SUR%20LES%20EPAULES%20DE%20DARWIN%20"+jj+"."+mm+"."+aa+".mp3"
            line += u' <a class="mp3link" href="' + unicode(pascal_link) + u'" download="' + unicode(link_name) + u'" >Télécharger (via prevost.pascal.free.fr)</a>\n'
        line += u'</li>\n'
        # line = u'\t<li><a href="' + player_link + '" >' + unicode(titre) + u'</a>, diffusée le ' + str(int(jj)) + u' ' + months[int(mm)-1] + u'</br>' + flash_player + u'</li>\n'
        html_code += line

    html_code += "</ul></div></div>"

    template_file = codecs.open(template_path, "r", "utf-8")
    # template_file = open(template_path)
    template = template_file.read()
    template_file.close()

    template = template.replace("%content", html_code)

    result_file = codecs.open(filename, "w", "utf-8")
    result_file.write(template)
    result_file.close()


#####################################################################

parser = argparse.ArgumentParser(description='Création d\'une page web à partir d\'une base de données JSON pour une émission de France Inter.')

parser.add_argument('-base', metavar='fichier JSON', help='Le fichier JSON qui contient la base de données.', default=u"./output/darwin_base.json")
parser.add_argument('-web', metavar='page web', help='Le fichier contenant la page web créee.', default=u"./output/index.php")
parser.add_argument('-template', metavar='template', help='Le fichier de template de la page web.', default=u"./output/temp_public.html")
args = parser.parse_args()

template_path = args.template
# template_path = "./output/temp3.html"

json_file = args.base
# json_file = "./output/darwin_base.json"

result_file = args.web
# result_file = "./output/index.php"

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

print u"Création de la page web\n"

create_webpage(data, template_path, result_file)

print u"\nPage web créée : "+result_file
