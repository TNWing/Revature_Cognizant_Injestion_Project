# This is a sample Python script.
from src import globals
from src import config
import pytest
from readers.csv_reader import read_csv
from readers.json_reader import read_json
import psycopg2
import os
from src import db_manager
from pathlib import Path
from dotenv import load_dotenv

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
"""
the config file contains the sources of the data, the schema of the data, and the rules for the data
this means that to establish the format of a table entry, need to load from the config to dict
"""
globals.PARENT_DIR=Path(__file__).resolve().parent.parent

def read_from_source(conn, cur):
    for source in config.source_list:

        file_type = str.lower(source['type'])

        if (file_type == 'csv') :#and source['path'] != 'data/customers.csv'
            read_csv(conn, cur, source)
        elif file_type == "json":
            read_json(conn, cur, source)
            pass
    print("CHECK CLASSES")
    for d_class,class_data in db_manager.dynamic_classes_from_config.items():
        print(d_class)
        print(dir(class_data))
    return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(globals.PARENT_DIR)
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
    db_manager.create_reject_table(cur)
    read_from_source(conn, cur)

    # db_manager.insertIntoTable(conn,cur,"test",{'apple':'red','grape':'purple'},None)
    conn.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
