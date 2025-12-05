import math
import psycopg2
import datetime
import psycopg2.sql as sql




"""
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
"""
with the medical_medicine_dataset.jsonl, use the following info
"medicine_name"
"uses"
"side_effects"

and use that to make a separate table.

im pretty sure the medicine names in the jsonl file are the generic names
 so i can make a method where, given a proprietary name, i can find to see what side effects it has.

"""


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
'''
Monitoring 	Track load metrics (rows/sec, rejects/sec) and log to a dashboard.

'''
row_speed=[]
insert_speed=[]
rej_speed=[]
monitor_times=[]
row_cnt=0
insert_cnt=0
rej_cnt=0
current_time_stamp=None

def reset_monitor_vars():
    global row_speed, insert_speed, rej_speed, row_cnt, insert_cnt, rej_cnt, current_time_stamp,monitor_times
    row_speed = []
    insert_speed = []
    rej_speed = []
    monitor_times = []
    row_cnt = 0
    insert_cnt = 0
    rej_cnt = 0
    current_time_stamp = datetime.datetime.now()
#todo add a variant that runs regardless of the time difference to account foor the last set of inserts and whatnot
def monitor_func(force_monitor=False):
    global row_speed, insert_speed, rej_speed, row_cnt, insert_cnt, rej_cnt, current_time_stamp,monitor_times
    if (datetime.datetime.now() - current_time_stamp).total_seconds() >= 1 or force_monitor:

        row_speed.append(row_cnt)
        insert_speed.append(insert_cnt)
        rej_speed.append(rej_cnt)
        monitor_times.append((datetime.datetime.now() - current_time_stamp).total_seconds())
        current_time_stamp = datetime.datetime.now()
        row_cnt = 0
        insert_cnt = 0
        rej_cnt = 0
        pass

def monitor_output():
    global row_speed, insert_speed, rej_speed, monitor_times
    row_total=0
    ins_total=0
    rej_total=0
    row_time=0
    ins_time=0
    rej_time=0
    for (row,ins,rej,time) in zip(row_speed,insert_speed,rej_speed,monitor_times):
        if (rej!=0):
            rej_total += rej
            rej_time += time
        if (ins!=0):
            ins_total += ins
            ins_time += time
        row_total += row
        row_time +=time
    if (row_time!=0):
        print("Row Stats\nTotal:{}\nTime:{}\nAverage(per second):{}\n\n".format(row_total,row_time,row_total/row_time))
    else:
        print("No complete rows were inserted")
    if (ins_time!=0):
        print("Insert Stats\nTotal:{}\nTime:{}\nAverage(per second):{}\n\n".format(ins_total,ins_time,ins_total/ins_time))
    else:
        print("No inserted data")
    if (rej_time!=0):
        print("Reject Stats\nTotal:{}\nTime:{}\nAverage(per second):{}".format(rej_total,rej_time,rej_total/rej_time))
    else:
        print("No rejected data")


    pass

def process_rows(conn, cur, schemas, df):
    global row_cnt, current_time_stamp
    reset_monitor_vars()
    for row_dict in df.to_dict(orient="records"):
        process_row(conn, cur, schemas, row_dict)
        row_cnt +=1
        monitor_func()
        conn.commit()
    if (row_cnt!=0):
        monitor_func(True)
    monitor_output()
    pass

def process_row(conn, cur, schemas, data: dict):

    for entry in schemas:
        for schema in entry.values():
            name = schema['name']
            types = schema['attributes'].values()
            new_data = {}
            if ('attr_name_map' in schema.keys()):
                for attr in schema['attributes'].keys():
                    if (attr in schema['attr_name_map']):
                        new_data[attr] = (data.get(schema['attr_name_map'][attr]))
                    else:
                        new_data[attr] = data.get(attr)
                    pass
            else:
                for attr in schema['attributes'].keys():
                    new_data[attr] = data.get(attr)
                    pass

            func_name = str(name)
            if (func_name in ['drug_class', 'drug_units','drug_substance','drug_administration', 'drug_side_effects','drug_uses']):

                func_name = func_name.__add__('_helper')
            else:
                func_name = 'standard_helper'
            if (func_name in globals()):
                func = globals()[func_name]
                func(conn, cur, schema['target_table'], new_data, schema['pk'], types)
            """

            """

            # then just call the upsert

        pass
    pass


def standard_helper(conn, cur, table_name, data: dict, pk, types):
    upsert_into_table(conn, cur, table_name, list(data.values()), data.keys(), pk, types)
    pass

def drug_uses_helper(conn, cur, table_name, data: dict, pk, types):

    for use in data['use']:
        query_data = list()
        for n in data.keys():
            if n != 'use':
                query_data.append(data[n])
            else:
                query_data.append(use)
        upsert_into_table(conn, cur, table_name, query_data, data.keys(), pk, types)
    pass
def drug_side_effects_helper(conn, cur, table_name, data: dict, pk, types):
    for effect in data['side_effect']:
        query_data = list()
        for n in data.keys():
            if n != 'side_effect':
                query_data.append(data[n])
            else:
                query_data.append(effect)
        upsert_into_table(conn, cur, table_name, query_data, data.keys(), pk, types)




def drug_class_helper(conn, cur, table_name, data: dict, pk, types):
    pharm_classes=[""]
    if (type(data['PHARM_CLASS']) is float):
        if not math.isnan(data['PHARM_CLASS']):
            pharm_classes = data['PHARM_CLASS'].split(',')
    for pc in pharm_classes:
        query_data = list()
        for n in data.keys():
            if n != 'PHARM_CLASS':
                query_data.append(data[n])
            else:
                query_data.append(pc)

        upsert_into_table(conn, cur, table_name, query_data, data.keys(), pk, types)

    pass


#NOTE: strength and unit arent always the same size. need to rework this as a result
#figure out what to do since strength and unit can be blank
#i could discard rows for that, and use it as proof of rejection table working
#strength cnt >=unit cnt
'''
there must be 3 situations
1. strength cnt=unit cnt, single
2. strength cnt=unit cnt, multiple
3. strength cnt: multiple, unit cnt=1
'''
unit_counter=0
def drug_units_helper(conn, cur, table_name, data: dict, pk, types):
    global unit_counter
    strength = [None]
    units = [""]
    #print("UNITS   ",data['STRENGTH'],data['UNIT'])

    if (type(data['STRENGTH']) is float):
        if not math.isnan(data['STRENGTH']):
            strength = data['STRENGTH'].split(';')
            units = data['UNIT'].split(';')
        else:
            unit_counter += 1
    else:
        strength = data['STRENGTH'].split(';')
        units = data['UNIT'].split(';')

    if (strength.__sizeof__()==units.__sizeof__()):
        for s, u in zip(strength, units):
            query_data = list()

            for n in data.keys():
                if n not in ['STRENGTH', 'UNIT']:
                    query_data.append(data[n])
                elif n == 'STRENGTH':
                    if (s is None):
                        query_data.append(None)
                    else:
                        query_data.append(s.strip())
                else:
                    query_data.append(u.strip())
            upsert_into_table(conn, cur, table_name, query_data, data.keys(), pk, types)
    elif (strength.__sizeof__()>units.__sizeof__() and units.__sizeof__()==1):
        u = units[0]
        for s in strength:

            query_data = list()
            for n in data.keys():
                if n not in ['STRENGTH', 'UNIT']:
                    query_data.append(data[n])
                elif n == 'STRENGTH':
                    if (s is None):
                        query_data.append(None)
                    else:
                        query_data.append(s.strip())
                else:
                    query_data.append(u.strip())
            upsert_into_table(conn, cur, table_name, query_data, data.keys(), pk, types)


def drug_substance_helper(conn, cur, table_name, data: dict, pk, types):
    substances=[""]
    if (type(data['SUBSTANCENAME']) is float):
        if not math.isnan(data['SUBSTANCENAME']):
            substances=data['SUBSTANCENAME'].split(';')
    for substance in substances:
        query_data=list()
        for n in data.keys():
            if n not in ['SUBSTANCENAME']:
                query_data.append(data[n])
            else:
                query_data.append(substance.strip())
        upsert_into_table(conn, cur, table_name, query_data, data.keys(), pk, types)
    pass



def drug_administration_helper(conn, cur, table_name, data: dict, pk, types):
    routes=[""]
    if (type(data['ROUTENAME']) is float):
        if not math.isnan(data['ROUTENAME']):
            routes = data['ROUTENAME'].split(';')
    else:
        routes = data['ROUTENAME'].split(';')
    for route in routes:
        query_data = list()
        for n in data.keys():
            if n not in ['ROUTENAME']:
                query_data.append(data[n])
            else:
                query_data.append(route.strip())
        upsert_into_table(conn, cur, table_name, query_data, data.keys(), pk, types)
    pass


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


def upsert_into_table(conn,cur, table_name, data, schema, primary_key,types):
    global rejected_data, insert_cnt,rej_cnt
    data=preprocess_data(data,types)
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
        if (table_name == 'rejected_data'):
            # print(data)
            pass
        cur.execute(query, data)
        insert_cnt += 1
        #print("Success insert into table".__add__(table_name))

    except psycopg2.Error as e:
        #print("FAILED INSERT int table ".__add__(table_name))
        #print(data)
        #print(e)
        conn.rollback()

        if (table_name!='rejected_data'):
            rejected_data.append(Reject(table_name, data, datetime.datetime.now(), str(e)))
            rej_cnt+=1
    finally:
        monitor_func()
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
                d = None
        new_data.append(d)
    return new_data
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


def create_reject_table( cur):
    # have a pk that is auto assigned
    create_table(cur, 'rejected_data', ['col_id', 'table_name', 'data', 'time', 'reason'],
                 ['serial', 'str', 'str', 'datetime', 'str'], [pk_constraint(['col_id'])])


def put_in_reject_table(conn,cur):
    for data in rejected_data:
        data_list = [data.table, data.data, data.time, data.reason]
        upsert_into_table(conn, cur, 'rejected_data', data_list, ['table_name', 'data', 'time', 'reason'], ['col_id'],['str', 'str', 'datetime', 'str'])
    return

#conn,cur, table_name, data, schema, primary_key,types
def is_company_likely_to_make(cur, drug_table,drug_company,drug_class, company_col_name, drug_col_name, company_name, drug_name):
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
        name=sql.Identifier(drug_table),
        c_col=sql.Identifier(company_col_name),
        c_name=sql.Identifier(company_name),
        d_col=sql.Identifier(drug_col_name),
        d_name=sql.Identifier(drug_name),
    ))
    '''
    select classes from drug_table join drug_classes where prodid=given id(d1)
    select drug_ids from drug_company where companyname="" (d2)
    join d2 on drug_classes (d3), select pharm_classes, count(pharm_classes) group by pharm_classes
    count total # of drugs the company has produced, and calculate % of drugs that match at least 1 pharm class of the drug given in the params
        -do this by:
        (d4) count(prod_id) drug_company where company=""
    '''
    cur.execute(query)
    results=cur.fetchall()
    if not results:
        print("Company has not produced this drug yet.")
        query=sql.SQL('SELECT COUNT({p_col}) FROM {name} WHERE {c_col}={c_name}').format(
            p_col=sql.Identifier(""),
            name=sql.Identifier(drug_table),
            c_col=sql.Identifier(company_col_name),
            c_name=sql.Identifier(company_name)

        )
        '''
        take the previously joined table and join it with the drug_classes
        '''
    else:
        print("Company has produced this drug.")
        pass
    return


def get_side_effect_from_brand_name(conn,cur,brand_name):
    query=sql.SQL('SELECT NONPROPRIETARYNAME FROM drug_alias JOIN drug_table on drug_alias.PRODUCTID=drug_table.PRODUCTID WHERE PROPRIETARYNAME={name}').format(
        name=sql.Placeholder()
    )
    try:
        print(brand_name)
        cur.execute(query,brand_name)
        fetched_data=cur.fetchone()
        print(fetched_data)
        if (fetched_data is not None):
            generic_name=fetched_data[0]
            print(generic_name)
            query=sql.SQL('SELECT side_effect FROM drug_side_effects WHERE medicine_name={name}').format(
                name=sql.Placeholder()
            )
            try:
                cur.execute(query, generic_name)
                side_effects=cur.fetchall()
                if (side_effects is not None):
                    print("The drug has the following side effects:")
                    for side_effect in side_effects:
                        print(side_effect)
                else:
                    print("No known side effects")
            except Exception as e:
                pass
        else:
            print("No associated generic name")

    except Exception as e:
        print("ERR")
        print(e)
        print(query.as_string(cur))
        '''
        ERR
column "Strattera" does not exist
LINE 1: ...DUCTID=drug_table.PRODUCTID WHERE PROPRIETARYNAME="Strattera...
                                                             ^

SELECT NONPROPRIETARYNAME FROM drug_alias JOIN drug_table on drug_alias.PRODUCTID=drug_table.PRODUCTID WHERE PROPRIETARYNAME="Strattera"
        '''
        pass
    pass

def get_uses_from_brand_name(conn,cur,brand_name):
    pass

def get_medicine_for_condition(conn,cur,condition):
    pass