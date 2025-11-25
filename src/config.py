import yaml
from src import globals
defaults = None
source_list = []
pythonObjs = []


def read_config():
    global defaults
    with open(globals.PARENT_DIR.__str__() + "\\config\\sourcesv2.yml", "r") as config:
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
