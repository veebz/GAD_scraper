import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    database = "pythonsqlite.db"

    sql_create_categories_table = """ CREATE TABLE IF NOT EXISTS categories (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        parent text,
                                        timestamp_scrape text
                                    ); """

#    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS actions-categories (
#                                    id integer PRIMARY KEY,
#                                    name text NOT NULL,
#                                    priority integer,
#                                    status_id integer NOT NULL,
#                                    project_id integer NOT NULL,
#                                    begin_date text NOT NULL,
#                                    end_date text NOT NULL,
#                                    FOREIGN KEY (project_id) REFERENCES projects (id)
#                                );"""

    sql_create_actions_table = """CREATE TABLE IF NOT EXISTS actions (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    priority integer,
                                    company text NOT NULL,
                                    description text NOT NULL,
                                    devices text,
                                    actions text,
                                    rating integer,
                                    ranking_view_all integer,
                                    ranking_category integer,
                                    ranking_startseite integer,
                                    timestamp_scrape text NOT NULL,
                                    category_id integer NOT NULL,
                                    FOREIGN KEY (category_id) REFERENCES categories (id)
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_categories_table)

        # create tasks table
        create_table(conn, sql_create_actions_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()


    ## actions: id, title, company, description, details, available devices, proposed actions, rating, ranking in view all, ranking in kategorie?, ranking auf startseite
    ## categories: id, title, parent
    ## action-category: id