Python project that reads data from various sources
and uploads it to a local PostgresSQL database.

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
    - Attribute_Name : INLINE Rule (NOT NULL, UNIQUE, etc)
    - None : End of attribute rule (Foreign key, check, etc)

Features
- Supports reading from csv and json files
- Stores db credentials in local env file for extra security
- Logs info regarding processing speed of inserts
- Some basic built in queries to retrieve data
- Partitioned tables to improve efficiency