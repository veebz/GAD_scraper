#! python
from bs4 import BeautifulSoup
from selenium import webdriver
from gad_db import *
import time
import urllib.request
import re
import os
import datetime

# Scraper for the Google Assistant Directory (Web version)

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

def db_create_action(conn, action):
    """ Create a new action into the actions table
        if it does not already exist.
        The action parameter contains a list with
        the input values
    :param conn:
    :param action:
    :return: id of new action in the table
    """
    sql = ''' INSERT OR IGNORE INTO actions(name, devices) VALUES(?,?) '''
    print(action)
    cur = conn.cursor()
    cur.execute(sql, action)
    return cur.lastrowid


def db_create_category(conn, category):
    """ Create a new category into the categories table.
    :param conn:
    :param category:
    :return: id of new category in the table
    """
    sql = ''' INSERT INTO categories(name,parent) VALUES(?,?) '''
    print(category)
    cur = conn.cursor()
    cur.execute(sql, category)
    conn.commit()
    return cur.lastrowid

def db_create_action_category_relation(conn, actioncategory):
    """ Create a new action-category-relationship into
        the action_category table. The parameter actioncategory
        is a list containing action_id and category_id.
    :param conn:
    :param actioncategory:
    :return: id of new action-category-relationship in the table
    """
    sql = ''' INSERT INTO action_category(action_id,category_id) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, actioncategory)
    conn.commit()
    return cur.lastrowid

def save_html(url, filename):
    """ Saves the url to filename into a new folder named according to the
        timestamp of the current scrape. In order to load all contents
        a browser is simulated in which the user scrolls down to the bottom
        of the website.
    :param url:
    :param filename:
    """
    browser = webdriver.Firefox()
    browser.get(url)
    # browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    # time.sleep(3)
    #browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    #time.sleep(3)
    #browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    #time.sleep(3)
    #browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    #time.sleep(3)
    #browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    #time.sleep(3)
    file_in_directory = os.path.join(scrape_directory, filename)
    with open(file_in_directory, "w+") as f:
        sourcecode = browser.page_source
        f.write(sourcecode)
    browser.close()
    print("saved successfully " + filename)

def open_from_directory(filename):
    """ Opens a file from the folder in which save_html() saves files.
    :param db_file: database file
    :return: Connection object or None
    """
    file_in_directory = os.path.join(scrape_directory, filename)
    with open(file_in_directory, 'r') as f:
        html_string = f.read()
        return html_string

def create_filename(string_filename, *string_topcategory):
    """ Deletes all special characters and lowers capital letters from a string
        and makes a html filename out of it.
        If topcategory is set, the filename will include "-subcategory", if not
        it will just say "-category)
    :param string_filename:
    :return:
    """
    filename = re.sub("[^A-Za-z0-9]+", "", str(string_filename))
    filename = filename.lower()

    if not string_topcategory:
        filename += "-category.html"
    else:
        if string_topcategory == 'service':
            filename += "-service.html"
        else:
            topcategory = re.sub("[^A-Za-z0-9]+", "", str(string_topcategory))
            topcategory = topcategory.lower()
            filename += "-"
            filename += topcategory
            filename += "-subcategory.html"
        return filename
    return filename

def make_url(url_piece):
    """ makes a full url out of the suburls found in
        Google's sourcecode
    :param url_piece:
    :return: full_url
    """
    full_url = "https://assistant.google.com/"
    full_url += url_piece
    return full_url

# Initialize global variables
global scrape_directory
global name_oberkategorie
global name_unterkategorie
global soup_oberkategorie
global index

# Create timestamp for scrape
dt_date = datetime.datetime.now()
zeitstempel = dt_date.strftime('%d-%m-%Y-%I-%M')

# Create a new directory for the html_files
scrape_directory = ''.join(['./', zeitstempel, '/'])
dirname = os.path.dirname(scrape_directory)
if not os.path.exists(dirname):
    os.mkdir(dirname)

# Set a sqlite database in the directory (always create a new db with gad_db.py before scraping)
database = "google_assistant_directory.db"

# Create a database connection
conn = create_connection(database)

if conn is not None:
    with conn:

        # Save the Google Assistant Directory start page
        save_html("https://assistant.google.com/explore", "start.html")
        start = open_from_directory("start.html")
        soup_start = BeautifulSoup(start, "html.parser")

        # Browse the start page for categories and extract their names
        for a in soup_start.find_all("a", "hSRGPd", href=True, jslog=True)[1:19]:
            name_oberkategorie = a['aria-label']
            name_oberkategorie = "".join(name_oberkategorie)
            # name_oberkategorie = name_oberkategorie[0:len(name_oberkategorie)]
            url = make_url(a['href'])
            filename = create_filename(name_oberkategorie)

            # Save the categories to the database
            category = (name_oberkategorie, 'no parent')
            category_id = db_create_category(conn, category)

            # Save the html site belonging to each category
            save_html(url, filename)

            # Open the new html files
            sourcecode_oberkategorie = open_from_directory(filename)
            soup_oberkategorie = BeautifulSoup(sourcecode_oberkategorie, "html.parser")

            # Browse for subcategories
            for b in soup_oberkategorie.find_all("div", "dLQiFb"):

                # Save the html site belonging to each subcategory
                name_unterkategorie = b['data-title']
                name_unterkategorie = "".join(name_unterkategorie)
                filename_unterkategorie = create_filename(name_unterkategorie, name_oberkategorie)
                url = make_url(b['data-link'])

                # Save the subcategories to the database
                category = (name_unterkategorie, name_oberkategorie)
                category_id = db_create_category(conn, category)

                # Save the html site belonging to each subcategory
                save_html(url, filename_unterkategorie)

                # Open the new html files
                sourcecode_unterkategorie = open_from_directory(filename_unterkategorie)
                soup_unterkategorie = BeautifulSoup(sourcecode_unterkategorie, "html.parser")

                # Browse for actions
                index_c = 0

                # search for all links pointing to actions (those including the string "/services/")
                for c in soup_unterkategorie.find_all("a", href = re.compile(r'services/')):

                    # search for all action titles and convert to labels and filenames
                    div_tags = c.find_all("div", "FdWgBb")
                    action_name = div_tags[index_c].contents
                    action_name = action_name[index_c]
                    action_filename = create_filename(action_name, 'service')
                    print(action_filename)
                    url = make_url(a['href'])

                    # Save the html site belonging to each action
                    save_html(url, action_filename)

                    # Open the new html files
                    sourcecode_actions = open_from_directory(action_filename)
                    soup_actions = BeautifulSoup(sourcecode_actions, "html.parser")

                    index_x = 0
                    for x in soup_actions.find_all("div", "VTLJT"):
                        # extract company name
                        # company_tags = x.find_all("div", "lUcxUb CbqDob")
                        # company = company_tags[1]
                        #print(company)

                        # extract devices and make string
                        #devices_tags = x.find_all("div", "rkJR4e CdFZQ")
                        #devices = devices_tags
                        #devices = ", ".join(devices)
                        #print(devices)

                        ## extract actions
                        #for f in soup_actions.find_all("span", "bCHKrf"):
                        #    invocations = f.contents
                        #    invocations = ", ".join(invocations)
                        #    print(invocations)
                        #
                        ## extract rating
                        #for g in soup_actions.find_all("div", "NRNQAb"):
                        #    rating = g[0].contents
                        #    print(rating)

                        # Save the actions to the database
                        print('hier')
                        action = (action_name, 'service')
                        action_id = db_create_action(conn, action)

                        # Save the category-action relationship
                        action_category = (action_id, category_id)
                        category_action_id = db_create_action_category_relation(conn, action_category)


                index_c = index + 1

    conn.close()

else:
        print("Error! cannot create the database connection.")
