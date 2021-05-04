#!/usr/bin/env python

# Python standard lib
import argparse
import codecs
import datetime
import json
import re
import urllib.error
import urllib.parse
import urllib.request

# Third party
from slugify import slugify

#####################################################################


def str2filename(string):
    filename = re.sub(r'[<>:"/\|?*]', "-", string)
    filename = filename.strip(". ")
    filename = slugify(filename)
    return filename


def get_remote_file_size(url):
    try:
        # in bytes
        print(url)
        usock = urllib.request.urlopen(url)
        size = int(usock.headers["Content-Length"])
        if size is None:
            size = 0
    except urllib.error.HTTPError:
        size = 0
    return float(size)


def create_rsslien(data, rss_template_path, rss_filename):
    rss_code = ""

    for emission_data in data:

        emission_data = emission_data["infos"]

        titre = emission_data["titre"]
        jj, mm, aa = (
            emission_data["date"]["jour"],
            emission_data["date"]["mois"],
            emission_data["date"]["annee"],
        )
        if "lien_ecouter" in emission_data:
            mp3link = emission_data["lien_mp3"]
        else:
            mp3link = ""

        # rss code
        rss_pdate = jj + "-" + mm + "-" + aa
        rss_pubdate = datetime.datetime.strptime(rss_pdate, "%d-%m-%Y")
        rss_line = "\t<item>"
        rss_line += """
            <title>{titre}</title>
            <description>
                Sur les épaules de Darwin - par : Jean-Claude Ameisen - réalisé par : Christophe IMBERT
            </description>
            <category>Science &amp; Medicine</category>
            <pubDate>{pubdate1}, {pubdate2} 19:00:00 +0100 </pubDate>
        """.format(
            titre=str(titre),
            pubdate1=rss_pubdate.strftime("%a"),
            pubdate2=rss_pubdate.strftime("%d %b %Y"),
        )

        # itune
        rss_line += """
            <itunes:author>Jean-Claude Ameisen</itunes:author>
            <itunes:explicit>no</itunes:explicit>
            <itunes:subtitle>
                Émission du {mm}.{jj}.{aa} {titre}
            </itunes:subtitle>
            <itunes:summary>Jean-Claude Ameisen - réalisé par : Christophe IMBERT</itunes:summary>
        """.format(
            mm=mm,
            jj=jj,
            aa=aa,
            titre=str(titre),
        )

        if mp3link:

            # TEST
            title = str2filename(titre)
            mp3link = "http://www.clementgrimal.fr/darwin/files/{aa}-{mm}-{jj}%20-%20{title}.mp3".format(
                aa=aa,
                mm=mm,
                jj=jj,
                title=title,
            )
            # ENDOF TEST

            rss_line += """
                <guid>{mp3link}</guid><enclosure length="{file_size}" url="{mp3link}" type="audio/mpeg"/>
            """.format(
                mp3link=str(mp3link),
                file_size=str(get_remote_file_size(mp3link)),
            )
        elif int(aa) < 2011 or (int(aa) == 2011 and int(mm) == 1):  # janvier 2011
            pascal_link = """
            http://prevost.pascal.free.fr/public/podcast/sur_les_epaules_de_darwin/Jean-Claude%20Ameisen%20-%20SUR%20LES%20EPAULES%20DE%20DARWIN%20{jj}.{mm}.{aa}.mp3
            """.format(
                mm=mm,
                jj=jj,
                aa=aa,
            )
            rss_line += """
                <guid>{pascal_link}</guid><enclosure length="0" url="{pascal_link}" type="audio/mpeg"/>
             """.format(
                pascal_link=str(pascal_link),
            )
        rss_line += "\t</item>\n"
        rss_code += rss_line
        print(titre)

    # rss_code
    rss_template_file = codecs.open(rss_template_path, "r", "utf-8")
    rss_template = rss_template_file.read()
    rss_template_file.close()

    rss_template = rss_template.replace("%rss_content", rss_code)

    rss_result_file = codecs.open(rss_filename, "w", "utf-8")
    rss_result_file.write(rss_template)
    rss_result_file.close()


#####################################################################

parser = argparse.ArgumentParser(
    description="Création d'un lien rss à partir d'une base de données JSON pour une émission de France Inter."
)

parser.add_argument(
    "-base",
    metavar="fichier JSON",
    help="Le fichier JSON qui contient la base de données.",
    default="./output/darwin_base.json",
)
parser.add_argument(
    "-rss_template",
    metavar="template",
    help="Le fichier de template du fichier rss.",
    default="./output/temp_public.rss",
)
parser.add_argument(
    "-rss",
    metavar="lien rss",
    help="Le fichier contenant le fichier rss créee.",
    default="./output/darwin.rss",
)
args = parser.parse_args()

json_file = args.base
rss_template_path = args.rss_template
rss_result_file = args.rss

#####################################################################

input_json = open(json_file, "r")
data = json.load(input_json)
input_json.close()

data = data["emissions"]

print("Création du lien rss\n")

create_rsslien(data, rss_template_path, rss_result_file)

print("\nlien rss créée : " + rss_result_file)
