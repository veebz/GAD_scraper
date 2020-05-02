#! python
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import geckodriver_autoinstaller
from gad_db import *
import time
import urllib.request
import re
import os
import datetime
from retrying import retry
from pprint import pprint

geckodriver_autoinstaller.install()

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
    sql = ''' INSERT OR IGNORE INTO actions(name, company, devices, actions, no_proposed_actions, ratings, number_ratings, claim) VALUES(?,?,?,?,?,?,?,?) '''
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
    sql = ''' INSERT OR IGNORE INTO categories(name,parent) VALUES(?,?) '''
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
    sql = ''' INSERT OR IGNORE INTO action_category(action_id,category_id) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, actioncategory)
    conn.commit()
    return cur.lastrowid

@retry
def save_html(url, filename):
    """ Saves the url to filename into a new folder named according to the
        timestamp of the current scrape. In order to load all contents
        a browser is simulated in which the user scrolls down to the bottom
        of the website.
    :param url:
    :param filename:
    """
    browser = webdriver.Firefox(options=options)
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
    browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    time.sleep(3)
    browser.execute_script("document.querySelector('.y3IDJd').scrollTop=10000000")
    time.sleep(3)
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

def create_filename(string_filename, string_topcategory=False, string_subcategory = False, string_type = False):
    """ Deletes all special characters and lowers capital letters from a string
        and makes a html filename out of it.
        If topcategory is set, the filename will include "-subcategory", if not
        it will just say "-category)
    :param string_filename:
    :return:
    """
    filename = re.sub("[^A-Za-z0-9]+", "", str(string_filename))
    filename = filename.lower()

    if string_topcategory == False:
        filename += "-category.html"
    else:
        if string_type == 'service':
            topcategory = re.sub("[^A-Za-z0-9]+", "", str(string_topcategory))
            topcategory = topcategory.lower()
            subcategory = re.sub("[^A-Za-z0-9]+", "", str(string_subcategory))
            subcategory = subcategory.lower()
            filename += "-"
            filename += topcategory
            filename += "-"
            filename += subcategory
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
global name_topcategory
global name_subcategory
global soup_topcategory
global index

options = Options()
options.headless = True

# Create timestamp for scrape
dt_date = datetime.datetime.now()
timestamp = dt_date.strftime('%d-%m-%Y-%I-%M')

# Create a new directory for the html_files
scrape_directory = ''.join(['./', timestamp, '/'])
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
            name_topcategory = a['aria-label']
            name_topcategory = "".join(name_topcategory)
            url = make_url(a['href'])
            filename = create_filename(name_topcategory)

            # Save the categories to the database
            category = (name_topcategory, 'no parent')
            category_id = db_create_category(conn, category)

            # Save the html site belonging to each category
            save_html(url, filename)

            # Open the new html files
            sourcecode_topcategory = open_from_directory(filename)
            soup_topcategory = BeautifulSoup(sourcecode_topcategory, "html.parser")

            # Browse for subcategories
            for b in soup_topcategory.find_all("div", "dLQiFb"):

                # Save the html site belonging to each subcategory
                name_subcategory = b['data-title']
                name_subcategory = "".join(name_subcategory)
                filename_subcategory = create_filename(name_subcategory, name_topcategory)
                url = make_url(b['data-link'])
                print(url)

                # Save the subcategories to the database
                category = (name_subcategory, name_topcategory)
                category_id = db_create_category(conn, category)

                # Save the html site belonging to each subcategory
                save_html(url, filename_subcategory)

                # Browse for actions on "View All" pages
                # Open the new html files
                sourcecode_subcategory = open_from_directory(filename_subcategory)
                soup_subcategory = BeautifulSoup(sourcecode_subcategory, "html.parser")

                # search for all links pointing to actions (those including the string "/services/")
                for c in soup_subcategory.find_all("a", href=re.compile(r'services/')):

                    # search for all action titles and convert to labels and filenames
                    div_tags = c.find_all("div", "FdWgBb")
                    name_service = div_tags[0].contents
                    name_service = name_service[0]
                    filename_service = create_filename(name_service, name_topcategory, name_subcategory, 'service')

                    print(filename_service)
                    url = make_url(c['href'])
                    print("service url: " + url)

                    # Save the html site belonging to each action
                    save_html(url, filename_service)

                    # Open the new html files
                    sourcecode_service = open_from_directory(filename_service)
                    soup_service = BeautifulSoup(sourcecode_service, "html.parser")

                    x = soup_service.find("div", "VTLJT")

                    # extract company name
                    company_tags = x.find_all("div", "lUcxUb CbqDob")
                    company = company_tags[0].contents
                    company = "".join(company)
                    print("company: " + company)

                    # extract devices and make string
                    devices_tags = x.find_all("div", "rkJR4e CdFZQ")
                    deviceslist = ""
                    for i in devices_tags[1:len(devices_tags)]:
                        devices = str(i.contents)
                        deviceslist += devices
                    print("devices: " + deviceslist)

                    # extract actions
                    action_tags = x.find_all("span", "bCHKrf")
                    actionlist = ""
                    for a in action_tags:
                        action = str(a.contents)
                        actionlist += action
                    print("actions: " + actionlist)
                    no_actions = len(action_tags)
                    print(no_actions, type(no_actions))

                    # extract rating and number of ratings if available
                    rating_tag = x.find("div", "NRNQAb")
                    if rating_tag is not None:
                        rating_int = int(re.sub('[^0-9]','', ''.join(rating_tag.contents)))
                    else:
                        rating_int = int()

                    number_of_user_ratings = x.find("div", "rriIab")
                    if number_of_user_ratings is not None:
                        number_of_user_ratings = ''.join(number_of_user_ratings.contents)
                        number_of_user_ratings_int = int(re.sub('[^0-9]','', number_of_user_ratings))
                    else:
                        number_of_user_ratings = int()

                    # check if there is a "Claim this page" button
                    claim = x.find("span", "VfPpkd-vQzf8d")
                    if claim is not None:
                        claim = "true"
                    else:
                        claim = "false"

                    # Save the services to the database
                    db_action = (name_service, company, deviceslist, actionlist, no_actions, rating_int, number_of_user_ratings_int, claim)
                    action_id = db_create_action(conn, db_action)

                    # Save the category-action relationship
                    action_category = (action_id, category_id)
                    category_action_id = db_create_action_category_relation(conn, action_category)

                # Browse for proposed actions for each intent displayed in category overview

                for d in b.find_all("a", href = re.compile(r'services/')):

                     # Save the name of each action displayed in the overview
                     for e in d.find_all("div", "FdWgBb"):

                         # overview_actions_tags = b.find_all("div", "FdWgBb")
                         # name_service_overview = overview_actions_tags[0].contents
                         name_service_overview = e.contents
                         name_service_overview = name_service_overview[0]
                         filename_service_overview = create_filename(name_service_overview, name_topcategory, name_subcategory, 'service')
                         print(filename_service_overview)
                         url_overview = make_url(d['href'])
                         print("service url_overview: " + url_overview)

                         # Save the html site belonging to each action
                         save_html(url_overview, filename_service_overview)

                         # Open the new html files
                         sourcecode_service_overview = open_from_directory(filename_service_overview)
                         soup_service_overview = BeautifulSoup(sourcecode_service_overview, "html.parser")

                         #index_x = 0
                         x = soup_service_overview.find("div", "VTLJT")

                         # extract company name
                         company_tags = x.find_all("div", "lUcxUb CbqDob")
                         company = company_tags[0].contents
                         company = "".join(company)
                         print("company: " + company)

                         # extract devices and make string
                         devices_tags = x.find_all("div", "rkJR4e CdFZQ")
                         deviceslist = ""
                         for i in devices_tags[1:len(devices_tags)]:
                             devices = str(i.contents)
                             deviceslist += devices
                         print("devices: " + deviceslist)

                         # extract actions
                         action_tags = x.find_all("span", "bCHKrf")
                         actionlist = ""
                         for a in action_tags:
                             action = str(a.contents)
                             actionlist += action
                         print("actions: " + actionlist)
                         no_actions = len(action_tags)

                         # extract actions
                         action_tags = x.find_all("span", "bCHKrf")
                         actionlist = ""
                         for a in action_tags:
                             action = str(a.contents)
                             actionlist += action
                         print("actions: " + actionlist)
                         no_actions = len(action_tags)
                         print(no_actions, type(no_actions))

                         # extract rating and number of ratings if available
                         rating_tag = x.find("div", "NRNQAb")
                         if rating_tag is not None:
                             rating_int = int(re.sub('[^0-9]', '', ''.join(rating_tag.contents)))
                         else:
                             rating_int = int()

                         number_of_user_ratings = x.find("div", "rriIab")
                         if number_of_user_ratings is not None:
                             number_of_user_ratings = ''.join(number_of_user_ratings.contents)
                             number_of_user_ratings_int = int(re.sub('[^0-9]', '', number_of_user_ratings))
                         else:
                             number_of_user_ratings = int()

                         # check if there is a "Claim this page" button
                         claim = x.find("span", "VfPpkd-vQzf8d")
                         if claim is not None:
                             claim = "true"
                         else:
                             claim = "false"


                         # Save the services from the overview to the database
                         db_action = (name_service_overview, company, deviceslist, actionlist, no_actions, rating_int, number_of_user_ratings_int, claim)
                         action_id = db_create_action(conn, db_action)

                         # Save the category-action relationship
                         action_category = (action_id, category_id)
                         category_action_id = db_create_action_category_relation(conn, action_category)

    conn.close()

else:
        print("Error! cannot create the database connection.")
