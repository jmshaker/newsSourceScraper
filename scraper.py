import requests
import re
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

db_connect = create_engine('sqlite:///test.db')

biases = ["left", "leftcenter", "center", "right-center", "right", "pro-science", "conspiracy"]

baseAddress = "https://mediabiasfactcheck.com/"

def biasCheck_linkScraper():

    all_source_links = []

    for bias in biases:

        address = baseAddress + bias + "/"

        source_code = requests.get(address)

        plaintext = source_code.text

        soup = BeautifulSoup(plaintext)

        sourceLinks = []

        z = soup.find("div", attrs={'class':'entry clearfix'})

        for link in z.find_all('a'):

            sourceLinks.append((link.get('href')))

        x = [link for link in sourceLinks if ('?share' not in link) & ('addtoany' not in link) & ('#print' not in link) & ('whatsapp' not in link)]

        all_source_links.append(x)

    biasCheck_biasScraper(all_source_links)


def biasCheck_biasScraper(all_source_links):

    all_source_biases = []

    for i in range(0,biases.__len__()):

        sourceLinks = []

        for link in all_source_links[i]:

            source_code = requests.get(link)

            plaintext = source_code.text

            soup = BeautifulSoup(plaintext)

            try:
                q = soup.find(string=re.compile("Source:"))
            except:
                try:
                    q = soup.find_all(string=re.compile("Sources:"))
                except:
                    try:
                        q = soup.find_all(string=re.compile("Notes:"))[1]
                    except:
                        q = None

            if (q != None):

                w = q.find_parent("p")

                for link in w.find_all('a'):

                    u = link.get('href')

                    if ('http://' in u):
                        u = u.replace('http://', '')

                    if ('https://' in u):
                        u = u.replace('https://','')

                    if ('www.' in u):
                        u = u.replace('www.','')

                    sourceLinks.append((u))

        i = i + 1

        all_source_biases.append(sourceLinks)

    biasCheck_addLinksDB(all_source_biases)


def biasCheck_addLinksDB(all_source_biases):

    #all_source_biases = []

    for i in range(0,biases.__len__()):

        sourceLinks = []

        for link in all_source_biases[i]:

            conn = db_connect.connect()

            query = conn.execute("select * from biaslinks where ? LIKE '%' || ADDRESS || '%'", (link))

            result = {'biasLinks': [i[1] for i in query.cursor.fetchall()]}

            #if ((result.get('biaslinks').__len__()) == 0):

            query = conn.execute("insert into BIASLINKS (ADDRESS, BIAS) values (\"%s\", \"%s\");" %(link, biases[i]))

        #all_source_biases.append(sourceLinks)

        i = i + 1


biasCheck_linkScraper()