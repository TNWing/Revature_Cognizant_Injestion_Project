import pandas as pd
from pathlib import Path
from src import db_manager
from src import global_vars as globalvars
def read_csv(conn, cur, source):
    file_path = globalvars.PARENT_DIR.__str__() + "\\" +source['path']
    schemas=source['schemas']
    if (type(schemas)!=list):
        schemas=[schemas]
    '''
    the main  issue is that the csv file is read multiple times now. as such, it is slower than before
    
    '''
    for s in schemas:
        for schema in s.values():

            rules = schema['rules']
            table_name = schema['target_table']
            print("\n\n\n\n")
            print(table_name)


            rule_list = [db_manager.pk_constraint(schema['pk'])]
            if rules is not None:
                for r in rules:
                    rule_list.append(list(r.values())[0])
                    pass
            db_manager.create_table(cur, table_name, list(schema['attributes'].keys()), list(schema['attributes'].values()), rule_list)
            db_manager.commit(conn)
            if Path(file_path).exists():
                df = pd.read_csv(file_path, na_values=[""], dtype={"STARTMARKETINGDATE": "Int64", "ENDMARKETINGDATE": "Int64"})
                # TODO: move the code below to a separate func to share btwn readers
                db_manager.build_classes(schema['name'],schema['attributes'])
                cnt=0
                '''
                as a note, not only do i have to deal with all of this
                but also the column names of the tables are different from the names in the csv/json now.
                so now i need to associate each data name to col name
                '''

                for index, row in df.iterrows():
                    cnt=cnt+1
                    if (cnt>2):
                        break
                    print("TEST TIME")
                    fields=[]
                    types=[]
                    vals=[]
                    for key in schema['attributes'].keys():
                        print("HEYO")
                        keyName=key;
                        if ('attr_name_map' in schema):
                            if (key in schema['attr_name_map']):
                                keyName=schema['attr_name_map'][key]
                            pass
                        print(keyName)
                        print(row[keyName])
                        fields.append(key)
                        vals.append(row[keyName])
                        types.append(schema['attributes'][key])
                        new_data = db_manager.preprocess_data(vals,types)
                        print(new_data)

                        if ('data_type_map' in source and source['data_type_map'][keyName].__contains__("[]")):
                            #actually, issue here is that i dont have the other data besides the single column
                            #now, we need to do things differently
                            pass
                        else:
                            #do normal things
                            pass
                    print("BREAKER")
                    print(fields)
                    print(vals)
                    '''
                    The main issue is this
                    
                    Say i have 3 attributes: A,B,C
                    If A and C have multiple entries, how do i tell
                    If A and C are linked (ex: each C corresponds to a single A val)
                    or if they aren't (each C corresponds to each A)
                    I could do a link value in the config
                    -links
                        -A:C
                    and by default, assume not linked. if they are linked, use indexing to get corresponding value
                    Otherwise, do a loop thr all of c for each A
                    
                    ****NEW METHOD****
                    
                    
                    First, start by getting each schema and storing it in an array or dict or something.
                    the config file should contain a new piece of data: linked data 
                    Possibly include a bool saying whether or not a datatype from the csv/json has multiple entries
                    
                    Then, iterate through each row.
                    For each row, iterate through the array of schemas and use the schema to process the data
                    
                    if the bool from before is true, do this:
                        Figure out which values have multiple entries.
                         
                    '''
                    '''
                    and thats the issue, one vals entry has 2 elements, other one can have a diff amt like just 1
                    i could find the entry with the most elements, then loop thr it making a unique inesrt for each
                    but then that presents issues and lots of bloat
                    '''
                    '''
                    the issue here is how do i actually separate the data into each table
                    notably, if i want to separate str[] into separate rows, what do i do?
                    bc when i read it, i get smth like this
                    ['Antiarrhythmic [EPC],Cytochrome P450 2D6 Inhibitor [EPC],Cytochrome P450 2D6 Inhibitors [MoA]', '0002-1407_14757f9d-f641-4836-acf3-229265588d1d']
                    ['PHARM_CLASS', 'PRODUCTID']
                    
                    but if i have dynamic tables from the config
                    
                    okay, if i have a data_types row for all the data types present in the csv
                    i can then use that to determine how to proceed
                    '''
                cnt=0
                for val in df.values:
                    #print("DATA")
                    cnt=cnt+1
                    if (cnt>2):
                        break

                    #print(val)
                    #print(schema['attributes'])
                    #print("Pre")
                    #print(df.keys())
                    #print("P2")
                    #print(df.values)
                    #print(type(df.values))
                    #
                    '''


df = pd.DataFrame({'Name': ['Aman', 'Raj'], 'Age': [25, 32]})

# Iterating through the DataFrame
for index, row in df.iterrows():
    print(f"Index: {index}, Name: {row['Name']}, Age: {row['Age']}")
    '''
                    #print(new_data)
                    #print("POSt")
                    #print(schema['attributes'])
                    try:
                        pass
                        #db_manager.upsert_into_table(cur, table_name, new_data, list(schema['attributes'].keys()), schema['pk'])
                    except Exception as e:
                        conn.rollback()
                    db_manager.commit(conn)
    return
