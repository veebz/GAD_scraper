#! python
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import urllib.request
import re
import os
import datetime


# Scraper für Google Assistant Directory

def save_html(url, filename):
    browser = webdriver.Firefox()
    browser.get(url)
    browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    time.sleep(3)
    browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    time.sleep(3)
    browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    time.sleep(3)
    browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    time.sleep(3)
    browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    time.sleep(3)
    with open(filename, "w") as f:
        sourcecode = browser.page_source
        f.write(sourcecode)
    browser.close()


def save_from_list(urllist, filenamelist):
    for url in urllist:
        for filename in filenamelist:
            return filename
        save_html(url, filename)


def open_from_directory(filename):
    with open(filename, 'r') as f:
        html_string = f.read()
        return html_string


def create_filename(string, *oberkategorie):
    filename = re.sub("[^A-Za-z0-9]+", "", string)
    filename = filename.lower()
    if not oberkategorie:
        filename += "-category.html"
    else:
        filename += "-"
        filename += oberkategorie[0]
        filename += "-subcategory.html"
    return filename


def create_filenames_from_list(stringlist, type):
    newstringlist = []
    for string in stringlist:
        newstringlist.append(create_filename(string, type))
    return newstringlist


def make_url(urlanhang):
    url = "https://assistant.google.com/"
    url += urlanhang
    return url

# noch nicht fertig
# def scrape_oberkategorien():
    # neuen Ordner mit Timestamp erstellen
    # dt_date = datetime.datetime.now()
    # zeitstempel = dt_date.strftime(%d-%m-%Y-%I-%M)
    # path = "/gad_scrape_"
    # path += zeitstempel
    # os.mkdir(path)

# noch nicht fertig
# def scrape_unterkategorien():
    # dir = 'path/to/Pics2'
    # if not os.path.isdir(dir): os.makedirs(dir)


# Scrape auf Startseite starten
save_html("https://assistant.google.com/explore", "start.html")
start = open_from_directory("start.html")
soup_start = BeautifulSoup(start, "html.parser")

for a in soup_start.find_all("a", "hSRGPd", href=True, jslog=True)[1:19]:
    label = a['aria-label']
    global label_oberkategorie
    label_oberkategorie = re.sub("[^A-Za-z0-9]+", "", label)
    label_oberkategorie = label_oberkategorie.lower()
    url = make_url(a['href'])
    filename = create_filename(label)

    # htmls für Oberkategorien speichern
    save_html(url, filename)

    # htmls für Oberkategorien öffnen und soup erstellen
    sourcecode_oberkategorie = open_from_directory(filename)
    soup_oberkategorie = "global"
    soup_oberkategorie = BeautifulSoup(sourcecode_oberkategorie, "html.parser")

    # htmls nach Unterkategorien durchsuchen und die entsprechenden Seiten speichern
    for a in soup_oberkategorie.find_all("div", "dLQiFb"):
        label_unterkategorie = a['data-title']
        filename_unterkategorie = create_filename(label_unterkategorie, label_oberkategorie)
        url = make_url(a['data-link'])
        save_html(url, filename_unterkategorie)


        # htmls nach Actions durchsuchen und Daten ablegen
        sourcecode_unterkategorie = open_from_directory(filename_unterkategorie)
        soup_unterkategorie = BeautifulSoup(sourcecode_unterkategorie, "html.parser")

        for a in soup_unterkategorie.find_all("div", "FdWgBb nhLye"):
        action_name = a.contents
        print(action_name)


