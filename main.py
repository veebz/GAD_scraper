#! python
from bs4 import BeautifulSoup
from selenium import webdriver
from gad_db import *
import time
import urllib.request
import re
import os
import datetime


# Scraper für Google Assistant Directory

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


#def db_create_action(conn, action):
#    """
#    Create a new project into the projects table
#    :param conn:
#    :param project:
#    :return: project id
#    """
#    sql = ''' INSERT INTO projects(name,begin_date,end_date)
#              VALUES(?,?,?) '''
#    cur = conn.cursor()
#    cur.execute(sql, action)
#    return cur.lastrowid


def db_create_category(conn, category):
    """
    Create a new task
    :param conn:
    :param category:
    :return:
    """
    sql = ''' INSERT INTO categories(name,parent,timestamp_scrape) VALUES(?,?,?) '''
    print(category)
    cur = conn.cursor()
    cur.execute(sql, category)
    conn.commit()
    return cur.lastrowid

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

def make_label(label):
    final = re.sub("[^A-Za-z0-9]+", "", label)
    final = final.lower()
    return final


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
database = "pythonsqlite.db"
dt_date = datetime.datetime.now()
zeitstempel = dt_date.strftime('%d-%m-%Y-%I-%M')
print("zeitstempel: " + zeitstempel)
# create a database connection
conn = create_connection(database)
if conn is not None:
    with conn:
        save_html("https://assistant.google.com/explore", "start.html")
        start = open_from_directory("start.html")
        soup_start = BeautifulSoup(start, "html.parser")

        for a in soup_start.find_all("a", "hSRGPd", href=True, jslog=True)[1:19]:
            name_oberkategorie = a['aria-label']
            global label_oberkategorie
            label_oberkategorie = make_label(a['aria-label'])
            url = make_url(a['href'])
            filename = create_filename(label_oberkategorie)

            # Kategorien in Datenbank ablegen
            category = (name_oberkategorie, 'no parent', zeitstempel)
            category_id = db_create_category(conn, category)

            # htmls für Oberkategorien speichern
            save_html(url, filename)

            # htmls für Oberkategorien öffnen und soup erstellen
            sourcecode_oberkategorie = open_from_directory(filename)
            global soup_oberkategorie
            soup_oberkategorie = BeautifulSoup(sourcecode_oberkategorie, "html.parser")

            for a in soup_oberkategorie.find_all("div", "dLQiFb"):
                # htmls nach Unterkategorien durchsuchen und die entsprechenden Seiten speichern
                global label_unterkategorie
                label_unterkategorie = make_label(a['data-title'])
                filename_unterkategorie = create_filename(label_unterkategorie, label_oberkategorie)
                url = make_url(a['data-link'])
                save_html(url, filename_unterkategorie)

                # Unterkategorien in Datenbank ablegen
                category = (label_oberkategorie, label_unterkategorie, zeitstempel)
                category_id = db_create_category(conn, category)

                # htmls nach Actions durchsuchen und Daten ablegen
                sourcecode_unterkategorie = open_from_directory(filename_unterkategorie)
                soup_unterkategorie = BeautifulSoup(sourcecode_unterkategorie, "html.parser")

        #        for a in soup_unterkategorie.find_all("a", href = re.compile('^services .*')):
        #            for b in soup_unterkategorie.find_all("div", "FdWgBb"):
        #                label = "".join(str(item) for item in b.contents)
        #                action_name = re.sub("[^A-Za-z0-9]+", "", label)
        #                action_name = action_name.lower()
        #                filename_actions = create_filename(action_name, label_unterkategorie)
        #                print("filename: " + filename_actions)
        #                url = make_url(a['href'])
        #                print("url: " + url)
        #                save_html(url, filename_actions)
    conn.close()
else:
        print("Error! cannot create the database connection.")
