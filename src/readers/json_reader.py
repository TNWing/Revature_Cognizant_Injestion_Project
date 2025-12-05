import pandas as pd
from pathlib import Path
from src import db_manager
from src import global_vars as globalvars

def read_json(conn, cur, source):
    file_path = globalvars.PARENT_DIR.__str__() + "\\" + source['path']
    schemas = source['schemas']
    if type(schemas) != list:
        schemas = [schemas]
    for s in schemas:
        for schema in s.values():

            rules = schema['rules']
            table_name = schema['target_table']

            rule_list = [db_manager.pk_constraint(schema['pk'])]
            if rules is not None:
                for r in rules:
                    rule_list.append(list(r.values())[0])
                    pass
            db_manager.create_table(cur, table_name, list(schema['attributes'].keys()),
                                    list(schema['attributes'].values()), rule_list)
            conn.commit()
    if Path(file_path).exists():
        if (file_path.endswith(".jsonl")):
            df = pd.read_json(file_path, lines=True)
        else:
            df = pd.read_json(file_path)
        db_manager.process_rows(conn, cur, schemas, df)
        conn.commit()
    return
