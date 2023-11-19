import logging
import utils as U
from physical_network import PhysicalNetwork, Track, Node
from logical_network import LogicalNetwork

def process_physical_network(trams_osm : dict, main_dir : str) -> PhysicalNetwork:
    pn = PhysicalNetwork()

    stop_temps = []
    temp_tracks = []

    for el in trams_osm['elements']:
        if el['type'] == 'node':
            x, y = U.translate_to_relative(el['lon'], el['lat'])

            node = Node(el['id'], x, y)
            pn.nodes[node.id] = node

            if U.contains_key(el, 'tags') and U.contains_key(el['tags'], 'railway'):
                if el['tags']['railway'] == 'tram_stop':
                    stop_temps.append(el)
            
        elif el['type'] == 'way':
            if U.contains_key(el, 'nodes'):
                pn.temp_tracks.append(el)

    # pn.fix_missing_stops(pn, stop_temps)

    for s in stop_temps:
        stop_node = pn.nodes.get(s.get('id'))
        stop_node.tags = s['tags']
        pn.stops.append(stop_node)

    # pn.fix_stop_names(pn)
    
    pn.fix_way_directions()
    pn.fix_max_speed()
    pn.fix_remove_banned_nodes()

    for stop_node in pn.stops:
        # this part is simple but looks complicated
        # it basically check if a list already exists and can be appended to, if not, it creates a new list 
        curr_ids = pn.stop_ids.get(stop_node.tags.get('name')) 

        if curr_ids == None: 
            pn.stop_ids[stop_node.tags['name']] = [stop_node.id] # if not, create new list of tags with name as a key { name : [id] }
        else:
            curr_ids.append(stop_node.id) # if yes, append id to the list
            pn.stop_ids[stop_node.tags['name']] = curr_ids # update the list


    for temp_track in pn.temp_tracks:
        track = Track.from_dict(temp_track, pn)
        pn.tracks.append(track)

    pn.graph_find_adjacents()
    pn.graph_find_successors()
    
    pn.fix_floating_islands()

    for node in pn.nodes.values():
         # if node has more than 2 adjacent nodes, this means it is a junction
        if len(node.adjacent_nodes) > 2:
            pn.joints.append(node)
            node.is_joint = True

    pn.track_remove_crossings()
    pn.track_generate_opposite_edges_to_bidirectional()

    pn.find_junctions()
    pn.generate_traffic_lights()
    pn.regenerate_tracks()

    pn.export_as_json(f'{main_dir}/data/physical_network.json')

    return pn


def process_logical_network(physical_network : PhysicalNetwork, schedule : dict, main_dir : str) -> LogicalNetwork:
    ln = LogicalNetwork(physical_network, schedule)

    #ln.remove_fake_route_stops()
    ln.validate_stop_names()
    ln.schedule_create_routes()
    ln.schedule_create_trips()
    ln.create_passanger_nodes()
    ln.set_passanger_nodes_properties()
    
    ln.export_as_json(f'{main_dir}/data/logical_network.json')

    return ln