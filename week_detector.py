import datetime
import requests

from bs4 import BeautifulSoup
import re




# https://stackoverflow.com/a/1058693/11678858
# for all DIRECT children
#children = soup.find("div", { "id" : "inhalt1" }).find("table", recursive=False).findAll("tr",recursive=False)

#print(pdf_liste)

def available_documents():

    nickname= 'tn'
    password = 'EgAbmZ-06'

    payload = {'nickname': nickname, 'pass': password}
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    r = requests.post("https://us.ibb.com/umschueler/pass/loginlogout.php", data=payload , headers=headers)

    #--------------------
    # 0 .  WEBSITE PARSEN
    #--------------------

    soup = BeautifulSoup(r.text, 'html.parser')
    vertretungen = soup.find('div', class_='aktuell1') # class
    pdf_liste = soup.find('div', id='inhalt1')  # id

    year = str(datetime.datetime.now().year)

    klasse = "US_IT_2020_Sommer_FIAE_B_"
    splitstring = klasse + year + "_abKW"
    #US_IT_2020_Sommer_FIAE_B_2021_abKW
    #US_IT_2020_Sommer_FIAE_B_2021_abKW

    available_documents = []
    for x in soup.findAll('a'):
        if x.parent.name == 'td':
            entry = x["href"]
            prefix , pdf = entry.split("./daten/") # US_IT_2020_Sommer_FIAE_B_2021_abKW19.pdf
            #print(pdf)

            try :
                p1 , woche = pdf.split(splitstring) # US_IT_2020_Sommer_FIAE_B_2021_abKW18.pdf
                w1 , w2 = woche.split(".pdf")
                if w1 != "":
                    available_documents.append(w1)

            except:
                pass
    return available_documents



print("verfügbare Dokumente für WOchen : " , available_documents())




def weeknr():
    weeknr= datetime.datetime.now().isocalendar()[1]
    docs = available_documents()
    if str(weeknr) in docs:
        print("avilable")
        return str(weeknr)

        #print(entry)

#print(children)
#--------------------
# 0 .  CREATE PDF ENTRRIES LIST
#--------------------


