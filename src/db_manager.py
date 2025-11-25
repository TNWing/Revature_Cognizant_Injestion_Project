import enum

import psycopg2
import datetime
import psycopg2.sql as sql
from enum import Enum

"""
if i wanted to associate a file with multiple schemas, and then parse the data to form multiple tables based on schemas
ideas on how to do that
*** In source, define schema as such
schemas:
    -schema:{
        -pk:[]
        -target_table:""
        -attributes:{}
        -rules:{}
    }
For each schema, form a table based on the data provided
this requires changes to the readers rather than db_manager i think
"""
"""
for drug data, this is the data in csv
      PRODUCTID: str
      PRODUCTNDC : str
      PRODUCTTYPENAME: str
      PROPRIETARYNAME: str
      PROPRIETARYNAMESUFFIX : str
      NONPROPRIETARYNAME : str
      DOSAGEFORMNAME: str
      ROUTENAME : str[]
      STARTMARKETINGDATE : date
      ENDMARKETINGDATE : date
      MARKETINGCATEGORYNAME: str
      APPLICATIONNUMBER : str
      LABELERNAME : str
      SUBSTANCENAME : str[]
      ACTIVE_NUMERATOR_STRENGTH : float[]
      ACTIVE_INGRED_UNIT : str[]
      PHARM_CLASSES : str[]
      DEASCHEDULE : str
      
    Notes:
    strength and unit are the same size (eg: if there are 2 strength levels of the drug, there are 2 corresponding units for each strenegth level
      
  drug_classes
  -drug_id, referencing drug_table
  -pharm class
  primary key is drug_id + class
  
  drug_substances
  id,substance (pk_
  
  drug_administration_method
  id,dosage,route (pk)
  
  drug_administration_units
  id,strength,unit
  
  drug_table:
    -id, ndc, type, proprietary name, deaschedule
    -id is the primary key
    
  drug_alias:
    -generic name, drug_id
    -id, generic is the primary key, with id being a foreign key to drug_table
    notably, multiple drugs can have different ids and proprietary names but the same generic name
    
  company_drug table
    -company name, drug id, marketing date (two columns for start and end), marketing category, application #
    -application # serves as the primary key
    drug id foreign key references drug_table
"""

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
    'float[]': 'FLOAT[]',
    'serial': 'SERIAL'
}


class Reject:
    def __init__(self, table_name, data, time, reason):
        self.table = table_name
        self.data = data
        self.time = time
        self.reason = reason


rejected_data = []
# make this a list instead
'''
such that each entry in list is a reject_data class
'''


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


def build_classes(class_name, class_schemas: dict):
    #print("\n\n\nClass")
    #print(class_name)
    #print("\n\n\n")
    dynamic_classes_from_config[class_name] = build_dynamic_class(class_name, class_schemas.keys())
    #print(vars(dynamic_classes_from_config[class_name]))
    #print(dynamic_classes_from_config[class_name].__dict__)


def pk_constraint(pk):
    rule = 'PRIMARY KEY ('
    for x in range(len(pk)):
        rule = rule + pk[x]
        if x < len(pk) - 1:
            rule = rule + ','
    rule = rule + ")"
    return rule


def create_table(cur, table_name, fields, data_types, constraints):

    attributes = [sql.SQL("{} {}").format(
        sql.SQL(c_name),
        sql.SQL(datatype_converter[c_type])
    )
        for c_name, c_type in zip(fields, data_types)]
    if (constraints is not None):
        attributes.extend(sql.SQL(c) for c in constraints)
    query = sql.SQL('CREATE TABLE IF NOT EXISTS {name} ({attr})').format(
        name=sql.Identifier(table_name),
        attr=sql.SQL(',').join(
            attributes
        )
    )
    try:
        cur.execute(query)
    except Exception as e:
        print(e)
        pass


def preprocess_data(data, types):
    #print(data)
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
def preprocess_datav3(fields,val):
    pass
def preprocess_datav2(df, attributes):
    #print(data)
    new_data = []

    for name,type in attributes.items():
        d=df.get(name)
        str_d=str(d)
        str_t=str(type)
        if hasattr(datetime, str_t):
            cast = getattr(datetime, str_t)
            try:
                if cast is datetime.date:
                    d = datetime.datetime.strptime(str_d, "%Y%m%d").date()
                else:
                    d = datetime.datetime.strptime(d, "%Y%m%d")
            except Exception:
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
    pass
    '''
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
    '''


def upsert_into_table(cur, table_name, data, schema, primary_key):
    query = sql.SQL('INSERT INTO {name} ({fields})VALUES ({vals}) ON CONFLICT ({pk}) DO UPDATE SET {setter}').format(
        name=sql.Identifier(table_name),
        fields=sql.SQL(',').join(
            sql.SQL(n) for n in schema
        ),
        vals=sql.SQL(',').join(
            sql.Placeholder() * len(data)
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
        if (table_name=='rejected_data'):
            #current transaction is aborted, commands ignored until end of transaction block is the reason the reject insert fails
            #print(query.as_string(cur))

            #print(data)
            pass
        cur.execute(query, data)#maximum recursion depth exceeded while getting the str of an object; reject table
        # You passed an object to psycopg2 that cannot be converted to a SQL literal, and psycopg2’s adapter is recursively trying to call __str__ or getquoted on it.
        #the thing below also adds to rejected_data which isnt ideal
    except psycopg2.Error as e:

        if (table_name!='rejected_data'):
            rejected_data.append(Reject(table_name, data, datetime.datetime.now(), str(e)))
            #print(query.as_string(cur))
            #print(e)

            raise

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

def create_reject_table( cur):
    # have a pk that is auto assigned
    create_table(cur, 'rejected_data', ['col_id', 'table_name', 'data', 'time', 'reason'],
                 ['serial', 'str', 'str', 'datetime', 'str'], [pk_constraint(['col_id'])])


def put_in_reject_table(cur):
    print("Reject table time")
    for data in rejected_data:
        print("OUR REASON")
        print(data.reason)
        data_list = [data.table, data.data, data.time, data.reason]
        upsert_into_table(cur, 'rejected_data', data_list, ['table_name', 'data', 'time', 'reason'], ['col_id'])
    return


def is_company_likely_to_make(cur,table_name, company_col_name,drug_col_name,company_name,drug_name):
    """
    Process:
    -see if company is already making drug_name (generic)
    -if not, get pharm classes of drug
    -get number of drugs company has made of that pharm class
    -based on that, make a rough guess on likelyhood on making said drug

        query = sql.SQL('CREATE TABLE IF NOT EXISTS {name} ({attr})').format(
        name=sql.Identifier(table_name),
        attr=sql.SQL(',').join(
            attributes
        )
    )
    """
    query=(sql.SQL('SELECT * FROM {name} WHERE {c_col} = {c_name} AND {d_col} = {d_name}')
           .format(
        name=sql.Identifier(table_name),
        c_col=sql.Identifier(company_col_name),
        c_name=sql.Identifier(company_name),
        d_col=sql.Identifier(drug_col_name),
        d_name=sql.Identifier(drug_name),
    ))
    cur.execute(query)
    results=cur.fetchall()
    if not results:
        print("Company has not produced this drug yet.")
        query=sql.SQL('SELECT COUNT({p_col}) FROM {name} WHERE {c_col}={c_name}').format(
            p_col=sql.Identifier(""),
            name=sql.Identifier(table_name),
            c_col=sql.Identifier(company_col_name),
            c_name=sql.Identifier(company_name)
        )
    else:
        print("Company has produced this drug.")
        pass
    return
