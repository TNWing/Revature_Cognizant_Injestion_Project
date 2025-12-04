import yaml
from src import global_vars as globalvars
defaults = None
source_list = []
pythonObjs = []


def read_config():
    global defaults
    with open(globalvars.PARENT_DIR.__str__() + "\\config\\sources.yml", "r") as config:
        data = yaml.safe_load(config)
        defaults = data['defaults']
        sources = data['sources']
        for source in sources:
            source_list.append(source)
        """
        each source has the following
            -name
            -type
            -path
            -target_table
            -pk
            -schema
            -rules
        """
    return
