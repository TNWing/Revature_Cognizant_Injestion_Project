# This is a sample Python script.
import config
import pytest
from readers.csv_reader import read_csv
from readers.json_reader import read_json
import psycopg2
import os
from dotenv import load_dotenv

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
"""
the config file contains the sources of the data, the schema of the data, and the rules for the data
this means that to establish the format of a table entry, need to load from the config to dict
"""


def read_from_source(conn, cur):
    for source in config.source_list:

        file_type = str.lower(source['type'])

        if (file_type == 'csv') and source['path'] != 'data/customers.csv':
            read_csv(conn, cur, source)
        elif file_type == "json":
            read_json(conn, cur, source)
            pass
    return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    config.read_config()
    print(config.defaults)
    '''
    conn=psycopg2.connect(
        dbname="",
        user="",
        password="",
        host=config.defaults['db_url']
    )
    '''

    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cur = conn.cursor()
    read_from_source(conn, cur)
    # db_manager.insertIntoTable(conn,cur,"test",{'apple':'red','grape':'purple'},None)
    conn.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
