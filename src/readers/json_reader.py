import pandas as pd
from pathlib import Path
from src import db_manager


def read_json(conn, cur, source):
    file_path = source['path']
    schema = source['schema']
    rules = source['rules']
    table_name = source['target_table']
    rule_list = [db_manager.pk_constraint(source['pk'])]
    if rules is not None:
        for r in rules:
            rule_list.append(list(r.values())[0])
            pass
    db_manager.create_table(conn, cur, table_name, list(schema.keys()), list(schema.values()), rule_list)
    db_manager.commit(conn)
    if Path(file_path).exists():
        # TODO see if this read works
        df = pd.read_json(file_path, na_values=[""], dtype={"STARTMARKETINGDATE": "Int64", "ENDMARKETINGDATE": "Int64"})
        for val in df.values:
            new_data = db_manager.preprocess_data(val, list(schema.values()))
            db_manager.upsert_into_table(cur, table_name, new_data, schema, source['pk'])
        db_manager.commit(conn)
    db_manager.close(conn)
    return
