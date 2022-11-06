import json


def load_conf():
    file_path = 'configure.json'

    with open(file_path) as f:
        load_conf = json.load(f)

    return load_conf