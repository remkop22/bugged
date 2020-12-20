

def without(kwargs_dict, keys):
    result = {}
    for key, val in kwargs_dict.items():
        if key not in keys:
            result[key] = val
    return result

