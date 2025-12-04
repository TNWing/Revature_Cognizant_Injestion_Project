import pandas as pd
from pathlib import Path
from src import db_manager
from src import global_vars as globalvars


def read_csv(conn, cur, source):
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
        df = pd.read_csv(file_path, na_values=[""],
                         dtype={"STARTMARKETINGDATE": "Int64", "ENDMARKETINGDATE": "Int64"})
        for row_dict in df.to_dict(orient="records"):
            db_manager.process_row(conn,cur, schemas, row_dict)
            conn.commit()
        print("UNIT CT    ",db_manager.unit_counter)
    return
    pass
