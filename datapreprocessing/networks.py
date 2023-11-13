import math, logging
import dict_utils as dutils
from physical_network import PhysicalNetwork

LON0 = 19.937356 # in degrees
LAT0 = 50.061700 
EARTH_R = 6365828.0 # in meters

def process_physical_network(trams_osm):
    pn = PhysicalNetwork()

    stop_temps = []
    for el in trams_osm['elements']:
        if el['type'] == 'node':
            rel_lon = el['lon'] - LON0 # in degrees
            rel_lat = el['lat'] - LAT0 

            rel_lat = rel_lat / 180.0 * math.pi # in radians
            rel_lon = rel_lon / 180.0 * math.pi

            y = EARTH_R * math.cos(rel_lat) * math.cos(rel_lon) # in meters
            x = EARTH_R * math.cos(el['lat'] / 180 * math.pi) * math.sin(rel_lon) 

            adjacent_nodes = []
            accesible_nodes = []

            pn.nodes[el['id']] = {
                'id': el['id'],
                'x': x,
                'y': y,
                'adjacent_nodes': adjacent_nodes,
                'accessible_nodes': accesible_nodes
            }

            if dutils.contains_key(el, 'tags') and dutils.contains_key(el['tags'], 'railway'):
                if el['tags']['railway'] == 'tram_stop':
                    stop_temps.append(el)
            
        elif el['type'] == 'way':
            if dutils.contains_key(el, 'nodes'):
                pn.tracks.append(el)

    # pn.fix_missing_stops(pn, stop_temps)

    for s in stop_temps:
        if tuple(s) not in pn.nodes:
            continue

        stop = pn.nodes[s]
        stop['tags'] = s['tags']
        pn.stops.append(stop)

    # pn.fix_stop_names(pn)
    pn.fix_way_directions()
    pn.fix_max_speed()
    pn.fix_remove_banned_nodes()

    for stop in pn.stops:
        # this part is simple but looks complicated
        # it basically check if a list already exists and can be appended to, if not, it creates a new list 
        sid_tags = pn.stop_ids.get('tags') # check if stop_ids has tags key
        curr_ids = sid_tags.get('name') # check if tags already has name key

        if curr_ids == None: 
            pn.stop_ids[s['tags']['name']] = [s['id']] # if not, create new list of tags with name as a key { name : [id] }
        else:
            curr_ids.append(s['id']) # if yes, append id to the list
            pn.stop_ids[s['tags']['name']] = curr_ids # update the list
        

    for track in pn.tracks:
        track['nodes'] = list(map(lambda id: pn.nodes.get(id), track['nodes']))

    pn.graph_find_adjacents()
    pn.graph_find_successors()
    
    pn.fix_floating_islands()

    for node in pn.nodes.values():
         # if node has more than 2 adjacent nodes, this means it is a junction
        if len(node['adjacent_nodes']) > 2:
            pn.joints.append(node)
            node['junction'] = None

    pn.track_remove_crossings()
    pn.track_generate_opposite_edges_to_bidirectional()

    pn.find_junctions()
    pn.generate_traffic_lights()
    pn.regenerate_tracks()

    pn.export_as_visualization('physical_network.json')