import os

from pprint import pprint

import yaml

config_path = "./example_configs.yml" if 'TEST' in os.environ else "./configs.yml"

CONFIGS = yaml.safe_load(open(config_path))

def get(path):
    attrs = path.split(".")

    node = CONFIGS

    for attr in attrs:
        if attr not in node:
            return None

        node = node[attr]

    return node
