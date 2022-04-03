from enum import Enum


def sort_dictionary_by_key(dict_to_sort):
    # TODO -> Add Docstring
    # TODO -> Add Typing
    return {key:dict_to_sort[key] for key in sorted(dict_to_sort.keys())}

class VarTypes(Enum):
    PROPORTION = "proportion"
    CONTINUOUS = "continuous"
