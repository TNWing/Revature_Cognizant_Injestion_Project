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
  - schemas (the tables associated with this dataset)
    - schema:
      - name:
      - target_table
      - pk(list representing the columns used for the primary key): 
      - attributes
      - attr_name_map
      - rules:
        - attribute_name: attribute_constraint (sql code of the constraint)
        - first_name: 'CHECK (LENGTH(first_name)>0)'
  - data_types:
  - rules: