import yaml
from pprint import pprint

CONFIGS = yaml.safe_load(open("./configs.yml"))

def get(path):
    attrs = path.split(".")

    node = CONFIGS

    for attr in attrs:
        if attr not in node:
            return None

        node = node[attr]

    return node
