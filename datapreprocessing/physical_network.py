import logging, math, sys, json

class PhysicalNetwork:
    def __init__(self):
        self.nodes = {}
        self.stops = []
        self.stop_ids = {}
        self.tracks = []
        self.joints = []
        self.junctions = []


    def fix_missing_stops(self):
        pass


    def fix_way_directions(self):
        logging.info(f'Fixing way directions')

        for track in self.tracks:
            if 'oneway' not in track['tags']:
                track['tags']['oneway'] = 'no'


    def fix_max_speed(self):
        logging.info(f'Fixing max speed')

        for track in self.tracks:
            if 'maxspeed' not in track['tags']:
                track['tags']['maxspeed'] = '50'

            track['tags']['maxspeed'] = int(track['tags']['maxspeed'])


    def fix_remove_banned_nodes(self):
        logging.info(f'Removing banned nodes')

        banned_nodes = [2431249451, 1578667749, 1578667767, 2375524704, 2756848363] # those are nodes near the tram depot (Łagiewniki and Nowa Huta) that are not used in the network

        for b_node_id in banned_nodes:
            self.__remove_node(b_node_id)
    

    def __remove_node(self, node_id):
        for track in reversed(self.tracks):
            if node_id in track['nodes']:
                self.tracks.remove(track)

        del self.nodes[node_id]


    def fix_floating_islands(self):
        logging.info(f'Fixing floating islands')

        pass


    def graph_find_adjacents(self):
        logging.info(f'Finding adjacent nodes tracks {len(self.tracks)}')

        for idx, track in enumerate(self.tracks):
            track_nodes = track.get('nodes', None)
            if track_nodes == None or len(track_nodes) < 2:
                # if track has no nodes or less than 2 nodes then it is not a valid track
                logging.warning(f'Track {track} has no nodes or less than 2 nodes')
                continue

            track_nodes[0]['adjacent_nodes'].append(track_nodes[1]) # first node is adjacent to second node 
            # outside of loop to avoid index out of range error
            
            for i in range (1, len(track_nodes) - 1):
                prev_node = track_nodes[i - 1]
                curr_node = track_nodes[i]
                next_node = track_nodes[i + 1]

                if prev_node not in curr_node['adjacent_nodes']:
                    curr_node['adjacent_nodes'].append(prev_node)
                else:
                    logging.warning(f'Node already in adjacent nodes of current node {idx}')
            
                if next_node not in curr_node['adjacent_nodes']:
                    curr_node['adjacent_nodes'].append(next_node)
                else:
                    logging.warning(f'Node already in adjacent nodes of current node {idx}')

                
            track_nodes[-1]['adjacent_nodes'].append(track_nodes[-2]) # last node is adjacent to second last node
            # outside of loop to avoid index out of range error


    def graph_find_successors(self):
        logging.info(f'Finding successor nodes tracks {len(self.tracks)}')

        for idx, track in enumerate(self.tracks):

            track_nodes = track.get('nodes', None)
            if track_nodes == None or len(track_nodes) < 2:
                # if track has no nodes or less than 2 nodes then it is not a valid track
                logging.warning(f'Track {track} has no nodes or less than 2 nodes')
                continue

            for i in range(len(track_nodes) - 1):
                curr_node = track_nodes[i]
                next_node = track_nodes[i + 1]

                if next_node not in curr_node['accessible_nodes']:
                    curr_node['accessible_nodes'].append(next_node)
                else:
                    logging.warning(f'Node already in accessible nodes of current node {idx}')


    def graph_manual_successor_nodes_adjustment(self):
        pass


    def track_remove_crossings(self):
        logging.info(f'Removing crossings')

        # we need to find junctions for each joint node 
        # we do this by finding the closest junction to each joint node
        # than we split the track between the joint node and the junction into 2 tracks
        for idx in range (len(self.joints) - 1, -1, -1):
            joint = self.joints[idx]

            if len(joint['adjacent_nodes']) != 4: 
                # if joint has 4 adjacent nodes then we cannot split the track
                continue

            if len(joint['accessible_nodes']) == 4: 
                # if joint has 4 accessible nodes then from this joint we can go to any other joint and we cannot split the track
                continue
            
            vectors = [] # list of vectors from joint to adjacent nodes
            for node in joint['adjacent_nodes']: # for each adjacent node
                vec = { 'x': node['x'] - joint['x'],
                        'y': node['y'] - joint['y'] }
                vec['dist'] = math.sqrt(vec['x'] ** 2 + vec['y'] ** 2) # distance from joint to adjacent node
                vectors.append(vec)

            # this loop creates a list of paths between adjacent nodes
            # it also calculates the cosine of the angle between the vectors
            # the cosine is used to determine which paths are the most opposite to each other
            # the most opposite paths are the ones that are most likely to be the crossing paths
            paths = []
            for i in range(4):
                for j in range(i + 1, 4):
                    path_cos = (vectors[i]['x'] * vectors[j]['x'] + vectors[i]['y'] * vectors[j]['y']) / (vectors[i]['dist'] * vectors[j]['dist'])
                    path = { 'ix1': i, # index of first adjacent node
                             'ix2': j, # index of second adjacent node
                             'accessible': 0, 
                             'cos': path_cos }
                    
                    if joint['adjacent_nodes'][i] in joint['accessible_nodes'] and joint['adjacent_nodes'][j] not in joint['accessible_nodes']:
                        path['accessible'] += i
                        paths.append(path)

                    elif joint['adjacent_nodes'][j] in joint['accessible_nodes'] and joint['adjacent_nodes'][i] not in joint['accessible_nodes']:
                        path['accessible'] += j
                        paths.append(path)
                        
            # find first lowest cosine which is the most opposite path
            lowest = self.__find_lowest_cos(paths)
            path1 = paths[lowest]
            paths.pop(lowest)

            # find second lowest cosine which is the second most opposite path
            lowest = self.__find_lowest_cos(paths)
            path2 = paths[lowest]
            
            # now we have the two most opposite paths
            # we can create two new joints and remove the old joint
            # the two new joints will have the same coordinates as the old joint
            joint1 = {
                'id': self.__find_available_node_id(),
                'x': joint['x'],
                'y': joint['y'],
                'adjacent_nodes': [joint['adjacent_nodes'][path1['ix1']], joint['adjacent_nodes'][path1['ix2']]],
                'accessible_nodes': [joint['adjacent_nodes'][path1['accessible']]]
            }
            self.nodes[joint1['id']] = joint1

            joint2 = {
                'id': self.__find_available_node_id(),
                'x': joint['x'],
                'y': joint['y'],
                'adjacent_nodes': [joint['adjacent_nodes'][path2['ix1']], joint['adjacent_nodes'][path2['ix2']]],
                'accessible_nodes': [joint['adjacent_nodes'][path2['accessible']]]
            }
            self.nodes[joint2['id']] = joint2

            # update adjacent nodes and accessible nodes of modified nodes
            for adj in joint['adjacent_nodes']:

                for i in range(len(adj['accessible_nodes'])):
                    # adj_to_adj = adjacent node to adjacent node
                    adj_to_adj = adj['accessible_nodes'][i]
                    
                    if adj not in joint1['adjacent_nodes'] and adj_to_adj == joint:
                        adj['accessible_nodes'][i] = joint1
                    elif adj not in joint2['adjacent_nodes'] and adj_to_adj == joint:
                        adj['accessible_nodes'][i] = joint2
                    
                for i in range(len(adj['adjacent_nodes'])):
                    # adj_to_adj = adjacent node to adjacent node
                    adj_to_adj = adj['adjacent_nodes'][i]
                    
                    if adj not in joint1['adjacent_nodes'] and adj_to_adj == joint:
                        adj['adjacent_nodes'][i] = joint1
                    elif adj not in joint2['adjacent_nodes'] and adj_to_adj == joint:
                        adj['adjacent_nodes'][i] = joint2

            self.nodes.pop(joint['id'])
            self.joints.remove(joint)


    def __find_lowest_cos(self, paths):
        lowest = 0
        for i in range(1, len(paths)):
            if paths[i]['cos'] < paths[lowest]['cos']:
                lowest = i

        return lowest
    

    def __find_available_node_id(self) -> int:
        self.id = 0
        while self.id in self.nodes:
            self.id += 1

        # logging.info(f'Found available node id: {self.id}')
        return self.id


    # below nodes has been removed from the the OSM data because they were caused by the rebulding of the tram depot 
    def track_generate_opposite_edges_to_bidirectional(self):
        logging.info(f'Generating opposite edges to bidirectional tracks')

        bidirectional_tracks = []
        # bidirectional_tracks.append({
        #     'nodes': [213578409, *self.graph_find_path(self.nodes.get(213578409), [1770978496])[1].reverse()],
        #     'in1': 4556178684,
        #     'out1': 1770978500,
        #     'in2': 1770978502,
        #     'out2': 4556178678
        # })

        # bidirectional_tracks.append({
        #     'nodes': [1770978486, *self.graph_find_path(self.nodes.get(1770978486), [213578407])[1].reverse()],
        #     'in1': 4556178680,
        #     'out1': 1770978488,
        #     'in2': 1770978489,
        #     'out2': 4556178677
        # })

        for b_track in bidirectional_tracks:
            b_track['nodes'] = [self.nodes.get(el['id']) for el in b_track['nodes']]
            b_track['in1'] = self.nodes.get(b_track['in1'])
            b_track['out1'] = self.nodes.get(b_track['out1'])
            b_track['in2'] = self.nodes.get(b_track['in2'])
            b_track['out2'] = self.nodes.get(b_track['out2'])

            b_track['in1']['accessible_nodes'] = [b_track['nodes'][0]]
            for i in range(len(b_track['nodes']) - 1):
                curr_node = b_track['nodes'][i]
                next_node = b_track['nodes'][i + 1]
                curr_node['accessible_nodes'] = [next_node]
            b_track['nodes'][-1]['accessible_nodes'] = [b_track['out1']]

            opposisite_edge = []
            for i in range(len(b_track['nodes'])):
                curr_node = b_track['nodes'][i]
                opposite_node = {
                    'id': self.__find_available_node_id(),
                    'x': curr_node['x'],
                    'y': curr_node['y'],
                    'adjacent_nodes': [curr_node['adjacent_nodes']],
                    'accessible_nodes': []
                }
                self.nodes[opposite_node['id']] = opposite_node
                opposisite_edge.append(opposite_node)
            opposisite_edge = opposisite_edge.reverse()
                
            b_track['in2']['accessible_nodes'] = [opposisite_edge[0]]
            for i in range(len(opposisite_edge) - 1):
                curr_node = opposisite_edge[i]
                next_node = opposisite_edge[i + 1]
                curr_node['accessible_nodes'] = [next_node]
            opposisite_edge[-1]['accessible_nodes'] = [b_track['out2']]


    def graph_find_path(self, start : dict, targets : list, limit=sys.maxsize) -> tuple[int, list]:
        # variation of Dijkstra's algorithm for finding shortest path
        # to understand this algorithm, reach the following article:
        # https://eduinf.waw.pl/inf/alg/001_search/0138.php

        distance = {}
        previous = {}
        queue = []
        path = []

        if start == None:
            return sys.maxsize, path

        distance[start['id']] = 0
        for acs in start['accessible_nodes']:
            dst = self.__distance_between_nodes(start, acs)

            distance[acs['id']] = dst
            previous[acs['id']] = start
            queue.append((dst, acs))

       
        found, found_dst, found_node = False, limit, None
        while len(queue) > 0:
            dst, node = queue.pop(0)
            if dst > limit:
                break

            if node['id'] in targets:
                if not found:
                    found = True
                    found_node = node
                    found_dst = dst
                else:
                    if dst >= found_dst:
                        continue
                    found_dst = dst
                    found_node = node
            if dst > found_dst:
                break

            for acs in node['accessible_nodes']:
                acs_dst = distance.get(acs['id'], None)

                if acs_dst == None:
                    new_dst = dst + self.__distance_between_nodes(node, acs)

                    queue.append((new_dst, acs))
                    distance[acs['id']] = new_dst
                    previous[acs['id']] = node

        if not found:
            return sys.maxsize, path
        
        node = found_node
        while node != start:
            path.append(node['id'])
            node = previous[node['id']]

        return found_dst, path


    def __distance_between_nodes(self, n1, n2):
        return math.sqrt((n1['x'] - n2['x']) ** 2 + (n1['y'] - n2['y']) ** 2)
    
    def find_junctions(self):
        logging.info(f'Finding junctions')

        for joint in self.joints:
            if joint['junction'] != None:
                continue

            junction = {
                'joints': [joint],
                'traffic_lights': [],
                'exits': []
            }

            joint['junction'] = junction
            self.__group_nearby_joints(joint, junction)

            self.junctions.append(junction)


    def __group_nearby_joints(self, node : dict, junction : dict):
        searching_distance = 120

        for joint in self.joints:
            if joint['junction'] != None:
                continue

            if self.__distance_between_nodes(node, joint) < searching_distance:
                joint['junction'] = junction
                junction['joints'].append(joint)
                self.__group_nearby_joints(joint, junction)


    def generate_traffic_lights(self):
        logging.info(f'Generating traffic lights')

        for junction in self.junctions:
            for joint in junction['joints']:
                if len(joint['accessible_nodes']) > 1:
                    junction['traffic_lights'].append(joint)
                elif len(joint['adjacent_nodes']) > 2:
                    junction['exits'].append(joint)

            traffic_lights_ids = [tl['id'] for tl in junction['traffic_lights'] if 'id' in tl]

            for joint in junction['traffic_lights']: # remove pointless traffic lights
                dst, path = self.graph_find_path(joint, traffic_lights_ids, 60) 
                if dst < sys.maxsize:
                    junction['traffic_lights'] = [tl for tl in junction['traffic_lights'] if tl['id'] != path[0]]

            exits_ids = [ex['id'] for ex in junction['exits'] if 'id' in ex]

            for joint in junction['exits']: # remove pointless exits
                dst, path = self.graph_find_path(joint, exits_ids, 60) 
                if dst < sys.maxsize:
                    junction['exits'] = [ex for ex in junction['exits'] if ex['id'] != joint['id']]

            self.__update_junction(junction)


    def __update_junction(self, junction):
        for traffic_light in junction['traffic_lights']:
            traffic_light['traffic_light'] = True
        
        for exit in junction['exits']:
            exit['exit'] = True


    def regenerate_tracks(self):
        logging.info(f'Regenerating tracks')

        special_nodes = []

        for [id, node] in self.nodes.items():
            if 'special' not in node:
                node['special'] = False

            if len(node['adjacent_nodes']) != 2 \
                    or len(node['accessible_nodes']) != 1 \
                    or 'tags' in node \
                    or 'traffic_light' in node \
                    or node.get('exit') == True\
                    or node.get('special') == True:
                node['special'] = True
                special_nodes.append(node)

        new_tracks, id = [], 0 

        logging.warning(f'len(special_nodes): {len(special_nodes)}')
        for first_node in special_nodes:
            # logging.warning(f'first_node: {len(first_node["accessible_nodes"])}')
            for idx, second_node in enumerate(first_node['accessible_nodes']):
                track = {
                    'id' : id,
                    'nodes': [first_node, second_node],
                    'tags': {
                        'maxspeed': 50,
                    }
                }

                curr_node = second_node
                while node['special'] == False and len(curr_node['accessible_nodes']) > 0:
                    curr_node = curr_node['accessible_nodes'][0]

                    if curr_node in track['nodes']:
                        # logging.warning(f'curr_node: {curr_node["id"]} is already in track')
                        break
                    track['nodes'].append(curr_node)


                length, prev_node = 0, track['nodes'][0]
                for i in range(1, len(track['nodes'])):
                    curr_node = track['nodes'][i]
                    length += self.__distance_between_nodes(prev_node, curr_node)
                    prev_node = curr_node
                track['length'] = length

                new_tracks.append(track)
                id += 1

        self.tracks = new_tracks


    def export_as_visualization(self, filename):
        network_visualization_model = {
            'nodes': [],
            'edges': []
        }

        for id, node in self.nodes.items():
            export_node = {
                'id': id,
                'x': node['x'],
                'y': node['y'],
            }

            if 'tags' in node:
                export_node['stop_name'] = node['tags']['name']

            if 'traffic_light' in node:
                export_node['traffic_light'] = node['traffic_light']

            network_visualization_model['nodes'].append(export_node)

        for track in self.tracks:
            head = track['nodes'][-1]
            tail = track['nodes'][0]

            export_edge = {
                'id': track['id'],
                'nodes': [node['id'] for node in track['nodes']],
                'length': track['length'],
                'maxspeed': track['tags']['maxspeed'],
            }

            network_visualization_model['edges'].append(export_edge)

        with open(filename, 'w') as f:
            json.dump(network_visualization_model, f, indent=2)