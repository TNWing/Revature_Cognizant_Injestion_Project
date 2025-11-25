import pandas as pd
from pathlib import Path
from src import db_manager
from src import globals as globals
from src import entity_converter

def read_csv(conn, cur, source):
    file_path = globals.PARENT_DIR.__str__() + "\\" + source['path']
    schemas = source['schemas']
    if (type(schemas) != list):
        schemas = [schemas]
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
            db_manager.create_table(cur, table_name, list(schema['attributes'].keys()),
                                    list(schema['attributes'].values()), rule_list)
            db_manager.commit(conn)
            if Path(file_path).exists():
                df = pd.read_csv(file_path, na_values=[""],
                                 dtype={"STARTMARKETINGDATE": "Int64", "ENDMARKETINGDATE": "Int64"})
                # TODO: move the code below to a separate func to share btwn readers
                db_manager.build_classes(schema['name'], schema['attributes'])
                cnt = 0
                '''
                as a note, not only do i have to deal with all of this
                but also the column names of the tables are different from the names in the csv/json now.
                so now i need to associate each data name to col name
                '''

                for index, row in df.iterrows():
                    cnt = cnt + 1
                    if (cnt > 2):
                        break
                    print("TEST TIME")
                    fields = []
                    types = []
                    vals = []
                    for key in schema['attributes'].keys():
                        print("HEYO")
                        keyName = key;
                        if ('attr_name_map' in schema):
                            if (key in schema['attr_name_map']):
                                keyName = schema['attr_name_map'][key]
                            pass
                        print(keyName)
                        print(row[keyName])
                        fields.append(key)
                        vals.append(row[keyName])
                        types.append(schema['attributes'][key])
                        new_data = db_manager.preprocess_data(vals, types)
                        print(new_data)

                        if ('data_type_map' in source and source['data_type_map'][keyName].__contains__("[]")):
                            # actually, issue here is that i dont have the other data besides the single column
                            # now, we need to do things differently
                            pass
                        else:
                            # do normal things
                            pass
                    print("BREAKER")
                    print(fields)
                    print(vals)
                    try:
                        pass
                        # db_manager.upsert_into_table(cur, table_name, new_data, list(schema['attributes'].keys()), schema['pk'])
                    except Exception as e:
                        conn.rollback()
                    db_manager.commit(conn)
    return


def readv2(conn, cur, source):

    print("Test")
    file_path = globals.PARENT_DIR.__str__() + "\\" + source['path']
    schemas = source['schemas']
    schema_list=[]

    if (type(schemas) != list):
        schemas = [schemas]
    #print(schemas)
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
            db_manager.create_table(cur, table_name, list(schema['attributes'].keys()),
                                    list(schema['attributes'].values()), rule_list)
            db_manager.commit(conn)
    if Path(file_path).exists():
        df = pd.read_csv(file_path, na_values=[""],
                         dtype={"STARTMARKETINGDATE": "Int64", "ENDMARKETINGDATE": "Int64"})
        cnt=0
        for row_dict in df.to_dict(orient="records"):
            cnt=cnt+1
            if (cnt>4):
                break
            print("NEW ROW")
            entity_converter.process_row(cur,schemas,row_dict,df.keys(),None)
    return
    for entry in schemas:
        for schema in entry.values():
            print(schema)
            attr_names=list(schema['attributes'].keys())
            name=schema['name']
            print(name)
            attr_names.append("links")
            print(attr_names)
            s=db_manager.build_dynamic_class(name,attr_names)
            links=[]
            if ('links' in schema):
                for A,B in schema['links'].items():
                    if (A==name):
                        links.append(B)
                        pass
                    elif(B==name):
                        links.append(A)
                        pass
            setattr(s,"links", links)
            schema_list.append(s)
            print(getattr(s,"links"))
            '''
            alternatively, create links using a general attribute list, listed under teh types section
            but that has an issue if there are multiple links
            Say, A,B,C
            A:B and A:C are links
            maybe i should just scrap this dynamic reading bc it tends to become way too complicated and dilutes the purpose of dynamic reading
            '''
    pass
