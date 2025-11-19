Python project that reads data from various sources
and uploads it to a local PostgresSQL database.

One of the main focuses of this project was to delve into dynamic
class creation via the type() method.
As such, this project serves as a "master" controller,
being able to dynamically define tables using the config file.

Data Sources are defined as such in the config
  - name(generic name for the data): 
  - type(the way data is stored): 
  - path(path to data file):
  - target_table(table name): 
  - pk(list representing the columns used for the primary key): 
  - schema(format for the entries of the table):
    - attribute_name: attribute_type
  - rules:
    - attribute_name: attribute_constraint (sql code of the constraint)
    - first_name: 'CHECK (LENGTH(first_name)>0)'
  - clean(determine what column data to standardize, and what standardize method to use):
    - attribute_name: {method}