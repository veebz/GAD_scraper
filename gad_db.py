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
    database = "google_assistant_directory.db"

    sql_create_categories_table = """CREATE TABLE IF NOT EXISTS categories (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        parent text
                                    );"""

    sql_create_actions_table = """CREATE TABLE IF NOT EXISTS actions (
                                        id integer PRIMARY KEY,
                                        name text UNIQUE NOT NULL, 
                                        company text,
                                        devices text,
                                        actions text,
                                        no_proposed_actions integer,
                                        ratings text,
                                        number_ratings integer,
                                        claim string
                                    );"""

    sql_create_action_category = """CREATE TABLE IF NOT EXISTS action_category (
                                    action_id integer,
                                    category_id integer,
                                    FOREIGN KEY (action_id) REFERENCES actions(id),
                                    FOREIGN KEY (category_id) REFERENCES categories(id)
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create categories table
        create_table(conn, sql_create_categories_table)

        # create actions table
        create_table(conn, sql_create_actions_table)

        # create action_category table
        create_table(conn, sql_create_action_category)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()



