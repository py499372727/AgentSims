import json


# Load a json file and return the json object.
def load_json_file(path):
    # Open json file.
    f = open(path)
    # Read json object from file.
    obj = json.load(f)
    # Close file.
    f.close()
    # Return json object.
    return obj


def get_json_value(obj, key, default):
    if key in obj:
        return obj[key]
    return default
