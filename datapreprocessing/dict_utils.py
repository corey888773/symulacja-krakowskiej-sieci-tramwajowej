def contains_key(d : dict, key : str) -> bool:
    if key in d and d[key] != None:
        return True
    return False

def try_get(d : dict, key : str, default_value = None) -> any:
    if d != None and key in d and d[key] != None:
        return d[key]
    
    return default_value