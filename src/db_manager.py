import enum

import psycopg2
import datetime
import psycopg2.sql as sql
from enum import Enum


class Conflict(Enum):
    APPEND = enum.auto()
    UPSERT = enum.auto()
    FAIL = enum.auto()


class DrugProduct:
    def __init__(self, prod_id, ndc, prod_type, generic, brand, substances, dea):
        self.id = prod_id
        self.ndc = ndc
        self.type = prod_type
        self.name_generic = generic
        self.name_brand = brand
        self.dosage = ""
        self.route = ""
        self.manufacture_start = ""
        self.manufacture_end = ""
        self.marketing = ""
        self.labeler = ""
        self.substances = substances.split(';')
        self.pharm_classes = ""
        self.dea = dea.split(",")
        return


dynamic_classes_from_config = {}

datatype_converter = {
    'str': 'VARCHAR',
    'str[]': 'VARCHAR[]',
    'int': 'INT',
    'int[]': 'INT[]',
    'datetime': 'TIMESTAMP',
    'date': 'DATE',
    'bool': 'BOOL',
    'float': 'FLOAT',
    'float[]': 'FLOAT[]'
}

rejected_data = {}


def commit(conn):
    conn.commit()


def close(conn):
    conn.close()


# https://www.psycopg.org/docs/sql.html#module-psycopg2.sql
def build_dynamic_class(name, attribute_names):
    attr = {}
    for n in attribute_names:
        attr[n] = None

    return type(name, (), attr)


def build_classes(class_name,class_schemas:dict):
    print("\n\n\nClass")
    print(class_name)
    print("\n\n\n")
    dynamic_classes_from_config[class_name] = build_dynamic_class(class_name, class_schemas.keys())
    print(vars(dynamic_classes_from_config[class_name]))
    print(dynamic_classes_from_config[class_name].__dict__)



def pk_constraint(pk):
    rule = 'PRIMARY KEY ('
    for x in range(len(pk)):
        rule = rule + pk[x]
        if x < len(pk) - 1:
            rule = rule + ','
    rule = rule + ")"
    return rule


def create_table(conn,cur, table_name, fields, data_types, constraints):
    attributes= [sql.SQL("{} {}").format(
                sql.SQL(c_name),
                sql.SQL(datatype_converter[c_type])
            )
            for c_name, c_type in zip(fields, data_types)]
    print(attributes)
    if (constraints is not None):
        attributes.extend(sql.SQL(c) for c in constraints)
    print(attributes)
    query = sql.SQL('CREATE TABLE IF NOT EXISTS {name} ({attr})').format(
        name=sql.Identifier(table_name),
        attr=sql.SQL(',').join(
            attributes
        )
    )
    #print(query.as_string(cur))
    cur.execute(query)
    return


def preprocess_data(data, types):
    new_data = []
    for d, t in zip(data, types):
        str_d = str(d)
        str_t = str(t)
        if hasattr(datetime, str_t):
            cast = getattr(datetime, str_t)
            try:
                if cast is datetime.date:
                    d = datetime.datetime.strptime(str_d, "%Y%m%d").date()
                else:
                    d = datetime.datetime.strptime(d, "%Y%m%d")
            except Exception:
                # print("invalid datetime value")
                d = None
        if str_t.__contains__("[]"):
            delim_ver = [d]
            if str_d.__contains__(";"):
                delim_ver = str_d.split(";")
            if t == 'int[]':
                delim_ver = list(map(int, delim_ver))
            elif t == 'bool[]':
                delim_ver = list(map(bool, delim_ver))
            elif t == 'float[]':
                delim_ver = list(map(float, delim_ver))
            new_data.append(delim_ver)
        else:
            new_data.append(d)
    return new_data


def upsert_into_table(cur, table_name, data, schema, primary_key):
    query = sql.SQL('INSERT INTO {name} ({fields})VALUES ({vals}) ON CONFLICT ({pk}) DO UPDATE SET {setter}').format(
        name=sql.Identifier(table_name),
        fields=sql.SQL(',').join(
            sql.SQL(n) for n in schema
        ),
        vals=sql.SQL(',').join(
            sql.Placeholder() * len(data)
            # sql.Placeholder
        ),
        pk=sql.SQL(',').join(
            sql.SQL(n) for n in primary_key
        ),
        setter=sql.SQL(',').join(
            sql.SQL('{} = EXCLUDED.{}').format(
                sql.SQL(n),
                sql.SQL(n)
            ) for n in schema
        )

    )
    try:
        cur.execute(query, data)
        pass
    except psycopg2.Error as e:
        print("Programming error")
        rejected_data[data] = e

        print(e)
    return


def get_from_table(table_name, str_query):
    query = table_name + str_query
    print(query)
    return


def drop_table(cur, table_name):
    query = sql.SQL('DROP TABLE {name}').format(
        name=sql.Identifier(table_name)
    )
    cur.execute(query)
    return
# create_table(cur, table_name, fields, data_types, constraints):

def create_reject_table(conn,cur):
    create_table(conn,cur, 'rejected_data', ['data', 'time', 'reason'], ['str', 'datetime', 'str'], None)
    print('reject table')

def put_in_reject_table(cur):

    for key, val in rejected_data.items():
        data=[key,datetime.datetime.now(),val]
        upsert_into_table(cur,'rejected_data',data,['data', 'time', 'reason'],None)
        query = sql.SQL('INSERT INTO TABLE rejected_data (data, time, reason) VALUES ({d},{t},{r})').format(
            d=sql.SQL(key),
            t=sql.SQL(datetime.datetime.now()),
            r=sql.SQL(val)
        )
        print(query.as_string(cur))
        cur.execute(query)
    return
