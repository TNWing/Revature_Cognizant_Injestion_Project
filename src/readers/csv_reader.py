import pandas as pd
from pathlib import Path
from src import db_manager
from src import globals as globals
def read_csv(conn, cur, source):
    file_path = globals.PARENT_DIR.__str__() + "\\" +source['path']
    schema = source['schema']
    rules = source['rules']
    table_name = source['target_table']
    rule_list = [db_manager.pk_constraint(source['pk'])]
    if rules is not None:
        for r in rules:
            rule_list.append(list(r.values())[0])
            pass
    db_manager.create_table(cur, table_name, list(schema.keys()), list(schema.values()), rule_list)
    db_manager.commit(conn)
    if Path(file_path).exists():
        df = pd.read_csv(file_path, na_values=[""], dtype={"STARTMARKETINGDATE": "Int64", "ENDMARKETINGDATE": "Int64"})
        # TODO: move the code below to a separate func to share btwn readers
        print("try build")
        print(source['name'])
        db_manager.build_classes(source['name'],schema)
        return
        for val in df.values:
            new_data = db_manager.preprocess_data(val, list(schema.values()))
            db_manager.upsert_into_table(cur, table_name, new_data, schema, source['pk'])
        db_manager.commit(conn)
    db_manager.close(conn)
    return
