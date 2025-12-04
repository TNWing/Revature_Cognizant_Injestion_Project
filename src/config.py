import yaml
import enum
from enum import Enum
from src import global_vars as globalvars
defaults = None
source_list = []
class Conflict(Enum):
    APPEND = enum.auto()
    UPSERT = enum.auto()
    FAIL = enum.auto()

class CommitType(Enum):
    INSERT = enum.auto()
    ROW = enum.auto()
commit_type=CommitType.ROW
conflict_method=Conflict.UPSERT


def read_config():
    global defaults
    with open(globalvars.PARENT_DIR.__str__() + "\\config\\sources.yml", "r") as config:
        data = yaml.safe_load(config)
        defaults = data['defaults']
        sources = data['sources']
        commit_type = defaults['commit_freq_type']#TODO: look up how to properly do this
        for source in sources:
            source_list.append(source)
    return
