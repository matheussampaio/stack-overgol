from pprint import pprint

import yaml

default_config_path = "./defaults.yml"
config_path = "./configs.yml"

DEFAULT_CONFIGS = yaml.safe_load(open(default_config_path))
CONFIGS = yaml.safe_load(open(config_path))

def _get(path, configs):
    attrs = path.split(".")

    node = configs

    for attr in attrs:
        if attr not in node:
            return (False, None)

        node = node[attr]

    return (True, node)

def get(path):
    hasVariable, variable = _get(path, CONFIGS)

    if hasVariable:
        return variable

    _, default_variable = _get(path, DEFAULT_CONFIGS)

    return default_variable
