import pandas as pd
from pathlib import Path
from src import db_manager
from src import global_vars as globalvars


def read_csv(conn, cur, source):
    file_path = globalvars.PARENT_DIR.__str__() + "\\" + source['path']
    schemas = source['schemas']
    print(type(schemas))
    if type(schemas) != list:
        schemas = [schemas]
    print(schemas)
    print(type(schemas))
    for s in schemas:
        print(s)
        print(s.keys())
        print(s.values())
        for schema in s.values():
            rules = schema['rules']
            table_name = schema['target_table']
            db_manager.create_table(cur, table_name, list(schema['attributes'].keys()), list(schema['attributes'].values()), rules,db_manager.pk_constraint(schema['pk']))
            conn.commit()
    if Path(file_path).exists():
        df = pd.read_csv(file_path, na_values=[""],
                         dtype={"STARTMARKETINGDATE": "Int64", "ENDMARKETINGDATE": "Int64"})
        #datetime.datetime.now()
        #move this below to db_maanger
        #db_manager.process_rows(conn,cur, schemas, df)

    return
    pass
