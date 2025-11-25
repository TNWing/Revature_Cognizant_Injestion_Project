import psycopg2
import psycopg2.sql as sql
'''
so process
i have the row of data
for each schema type, i process it into the corresponding table_format and then upsert it into the data
commit at the end of all the upserts for that row

'''
#process_row receives the list of schemas and the data present in a row
#should data just be the values or should it be the dict of vals
# should do what i need
#data_types should be the column names in the file
#schema dictates the names&types in the table (basically the schema in the source file)
#data represents the row of data
def process_row(cur,schemas,data:dict,data_types,links):
    for entry in schemas:
        print("NEW SET OF INSERTS")
        for schema in entry.values():
            print(schema)
            #print(data)
            #print(data_types)
            name=schema['name']
            new_data = {}
            #need to format the multi element values into a list
            if ('attr_name_map' in schema.keys()):
                for attr in schema['attributes'].keys():
                    if (attr in schema['attr_name_map']):
                        new_data[attr]=(data.get(schema['attr_name_map'][attr]))
                    else:
                        new_data[attr]=data.get(attr)
                    pass
            else:
                for attr in schema['attributes'].keys():
                    new_data[attr]=data.get(attr)
                    pass
            func_name=str(name)
            func_name=func_name.__add__('_helper')
            print(new_data)
            if (func_name in globals()):
                func=globals()[func_name]
                func(cur,schema['target_table'],new_data,schema['pk'])
            #new_data is unprocessed however, so there might be lists as elements
            """
            
            """

            #then just call the upsert

        pass
    pass
def drug_class_helper(cur,table_name,data:dict,pk):
    pharm_classes=data['PHARM_CLASS']
    print(pharm_classes)
    for pc in pharm_classes:
        #print(pc)
        query_data=list()
        query_data.append(pc)

        query_data.append(data[n] for n in data.keys() if not 'PHARM_CLASS')
        #print(query_data)
        upsert_into_table(cur,table_name,list(data.values()),data.keys(),pk)

    pass


def drug_administration_units_converter(data):
    new_data=[]
    return new_data




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
        #print(query.as_string(cur))
        cur.execute(query, data)#maximum recursion depth exceeded while getting the str of an object; reject table
        # You passed an object to psycopg2 that cannot be converted to a SQL literal, and psycopg2’s adapter is recursively trying to call __str__ or getquoted on it.
        #the thing below also adds to rejected_data which isnt ideal
    except psycopg2.Error as e:
        #print("FAILED INSERT ")
        #print(e)
        '''
        if (table_name!='rejected_data'):
            rejected_data.append(Reject(table_name, data, datetime.datetime.now(), str(e)))
            #print(query.as_string(cur))
            #print(e)

            raise
        '''

    return

