# This is a sample Python script.
from src import global_vars
from src import config
import pytest
from readers.json_reader import read_json
from readers.csv_reader import read_csv
import psycopg2
import os
from src import db_manager
from pathlib import Path
from dotenv import load_dotenv

global_vars.PARENT_DIR = Path(__file__).resolve().parent.parent


def read_from_source(conn, cur):
    for source in config.source_list:

        file_type = str.lower(source['type'])

        if file_type == 'csv':
            # read_csv(conn, cur, source)
            #read_csv(conn, cur, source)
            pass
        elif file_type == "json":
            read_json(conn, cur, source)
            pass
    return



if __name__ == '__main__':

    config.read_config()

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
    db_manager.put_in_reject_table(conn,cur)
    conn.commit()
    conn.close()

