import math

def contains_key(d : dict, key : str) -> bool:
    if key in d and d[key] != None:
        return True
    return False

def try_get(d : dict, key : str, default_value = None) -> any:
    if d != None and key in d and d[key] != None:
        return d[key]
    
    return default_value

def first_or_default(l : list, default_value = None) -> any:
    if l != None and len(l) > 0:
        return l[0]
    
    return default_value


LON0 = 19.937356 # in degrees
LAT0 = 50.061700 
EARTH_R = 6365828.0 # in meters

def translate_to_relative(lon : float, lat : float) -> tuple:
    rel_lon = lon - LON0 # in degrees
    rel_lat = lat - LAT0 

    rel_lat = rel_lat / 180.0 * math.pi # in radians
    rel_lon = rel_lon / 180.0 * math.pi

    y = EARTH_R * math.cos(rel_lat) * math.cos(rel_lon) # in meters
    x = EARTH_R * math.cos(lat / 180 * math.pi) * math.sin(rel_lon) 

    return x, y