'''
so process
i have the row of data
for each schema type, i process it into the corresponding table_format and then upsert it into the data
commit at the end of all the upserts for that row

'''
#process_row receives the list of schemas and the data present in a row
#should data just be the values or should it be the dict of vals
# should do what i need
#data_types should be the column names in the file
#schema dictates the names&types in the table (basically the schema in the source file)
#data represents the row of data
def process_row(schemas,data:dict,data_types,links):
    for entry in schemas:
        print("NEW SET OF INSERTS")
        for schema in entry.values():
            print(schema)
            #print(data)
            #print(data_types)

            new_data = {}
            if ('attr_name_map' in schema.keys()):
                for attr in schema['attributes'].keys():
                    if (attr in schema['attr_name_map']):
                        new_data[attr]=(data.get(schema['attr_name_map'][attr]))
                    else:
                        new_data[attr]=data.get(attr)
                    pass
            else:
                for attr in schema['attributes'].keys():
                    new_data[attr]=data.get(attr)
                    pass
            #new_data is unprocessed however, so there might be lists as elements
            """
            
            """
            print(new_data)
            #then just call the upsert

        pass
    pass
def drug_class_helper(data:dict):

    pass


def drug_administration_units_converter(data):
    new_data=[]
    return new_data