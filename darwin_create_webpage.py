#!/usr/bin/env python

# Python standard lib
import argparse
import codecs
import json
import re

# Third party
from slugify import slugify

#####################################################################


def str2filename(string):
    filename = re.sub(r'[<>:"/\|?*]', "-", string)
    filename = filename.strip(". ")
    filename = slugify(filename)
    return filename


def create_webpage(data, template_path, filename):
    html_code = ""
    current_month = ""
    new_season = True
    new_month = True

    months = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]

    html_code += '<div data-role="collapsible-set" data-inset="false">'

    for emission_data in data:

        emission_data = emission_data["infos"]

        titre = emission_data["titre"]
        jj, mm, aa = (
            emission_data["date"]["jour"],
            emission_data["date"]["mois"],
            emission_data["date"]["annee"],
        )
        pagelink = emission_data["lien_emission"]

        if "lien_ecouter" in emission_data:
            player_link = emission_data["lien_ecouter"]
            mp3link = emission_data["lien_mp3"]
        else:
            player_link = ""
            mp3link = ""

        new_month = False
        print(titre)

        if mm == "09" and new_season:
            if current_month != "":
                html_code += """
                                    </ul>
                                </div> <!-- 3 -->
                            </div> <!-- saison last month -->
                        </div> <!-- saison -->
                    </div> <!-- saison -->
                """
                new_month = False
            html_code += """
                <div data-role="collapsible" data-collapsed-icon="carat-r" data-expanded-icon="carat-d">
                <h2>Saison {a1}-{a2}</h2>
                <div class="saison" data-role="collapsible-set" data-inset="false">
            """.format(
                a1=str(aa),
                a2=str(int(aa) + 1),
            )
            new_season = False
        else:
            new_month = True

        if mm != "09":
            new_season = True

        if aa + mm != current_month:
            if current_month != "" and new_month:
                html_code += """
                            </ul>
                        </div> <!-- mois -->
                    </div> <!-- collapsible mois -->
                """
            html_code += """
                <div data-role="collapsible" data-collapsed-icon="carat-r" data-expanded-icon="carat-d">
                <h3>{mm} {aa}</h3>
                <div class="mois">
                    <ul>
            """.format(
                mm=months[int(mm) - 1],
                aa=str(aa),
            )
            current_month = aa + mm

        line = "    <li>"
        line += "<table><tr>"
        link_name = aa + "-" + mm + "-" + jj + " - " + titre

        if player_link and mp3link:

            # TEST
            title = str2filename(titre)
            mp3link = "./files/{aa}-{mm}-{jj} - {title}.mp3".format(
                aa=aa,
                mm=mm,
                jj=jj,
                title=title,
            )
            # ENDOF TEST

            line += """
                <td>
                <a class="play-link" href="{plink}" >Ecouter</a>
                </td>
                <td>
                <a class="download-link" href="{mlink}" download="{lname}" >Télécharger</a>
                </td>
            """.format(
                plink=str(player_link),
                mlink=str(mp3link),
                lname=str(link_name),
            )
        elif int(aa) < 2011 or (int(aa) == 2011 and int(mm) == 1):  # janvier 2011
            pascal_link = """
                http://prevost.pascal.free.fr/public/podcast/sur_les_epaules_de_darwin/Jean-Claude%20Ameisen%20-%20SUR%20LES%20EPAULES%20DE%20DARWIN%20{jj}.{mm}.{aa}.mp3
            """.format(
                jj=jj,
                mm=mm,
                aa=aa,
            )
            line += """
                <td>
                <a class="download-link" href="{plink}" download="{lname}" >Télécharger (via prevost.pascal.free.fr)</a>
                </td>
            """.format(
                plink=str(pascal_link),
                lname=str(link_name),
            )

        line += """
            <td>
            <span style="vertical-align:middle;float:left;"><a class="link" href="{plink}" >{ptitre}</a>, diffusée le {date}</span>
            </td>
        """.format(
            plink=str(pagelink),
            ptitre=str(titre),
            date=str(int(jj)) + " " + months[int(mm) - 1] + " " + str(aa),
        )

        line += "</tr></table>"
        line += "</li>\n"
        html_code += line

    html_code += """
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

    template_file = codecs.open(template_path, "r", "utf-8")
    template = template_file.read()
    template_file.close()

    template = template.replace("%content", html_code)

    result_file = codecs.open(filename, "w", "utf-8")
    result_file.write(template)
    result_file.close()


#####################################################################

parser = argparse.ArgumentParser(
    description="Création d'une page web à partir d'une base de données JSON pour une émission de France Inter."
)

parser.add_argument(
    "-base",
    metavar="fichier JSON",
    help="Le fichier JSON qui contient la base de données.",
    default="./output/darwin_base.json",
)
parser.add_argument(
    "-web",
    metavar="page web",
    help="Le fichier contenant la page web créee.",
    default="./output/index.html",
)
parser.add_argument(
    "-template",
    metavar="template",
    help="Le fichier de template de la page web.",
    default="./output/temp_public.2017.html",
)
args = parser.parse_args()

template_path = args.template
json_file = args.base
result_file = args.web

#####################################################################

input_json = open(json_file, "r")
data = json.load(input_json)
input_json.close()

data = data["emissions"]

print("Création de la page web\n")

create_webpage(data, template_path, result_file)

print("\nPage web créée : " + result_file)
