import logging, math, sys
import dict_utils as dutil

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
        for track in self.tracks:
            if 'oneway' not in track['tags']:
                track['tags']['oneway'] = 'no'

    def fix_max_speed(self):
        for track in self.tracks:
            if 'maxspeed' not in track['tags']:
                track['tags']['maxspeed'] = '50'

            track['tags']['maxspeed'] = int(track['tags']['maxspeed'])

    def fix_remove_banned_nodes(self):
        banned_nodes = [2431249451, 1578667749, 1578667767, 2375524704] 
        banned_nodes.extend([2756848363])
        for b_node_id in banned_nodes:
            self.__remove_node(b_node_id)
    
    def __remove_node(self, node_id):
        for track in reversed(self.tracks):
            if node_id in track['nodes']:
                self.tracks.remove(track)

        del self.nodes[node_id]

    def fix_floating_islands(self):
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

        return self.id

    def track_generate_opposite_edges_to_bidirectional(self):
        pass 

    def __graph_find_path(self, start, targets, limit=sys.maxsize) -> tuple[int, list]:
        # variation of Dijkstra's algorithm for finding shortest path
        # to understand this algorithm, reach the following article:
        # https://eduinf.waw.pl/inf/alg/001_search/0138.php

        distance = {}
        previous = {}
        queue = []

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

        path = []
        if not found:
            return sys.maxsize, path
        
        node = found_node
        while node != start:
            path.append(node)
            node = previous[node['id']]

        return found_dst, path

    def __distance_between_nodes(self, n1, n2):
        return math.sqrt((n1['x'] - n2['x']) ** 2 + (n1['y'] - n2['y']) ** 2)
    
    def find_junctions(self):
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
        for junction in self.junctions:
            for joint in junction['joints']:
                if len(joint['accessible_nodes']) > 1:
                    junction['traffic_lights'].append(joint)
                elif len(joint['adjacent_nodes']) > 2:
                    junction['exits'].append(joint)

            traffic_lights_ids = [tl['id'] for tl in junction['traffic_lights'] if 'id' in tl]

            for joint in junction['traffic_lights']: # remove pointless traffic lights
                dst, path = self.__graph_find_path(joint, traffic_lights_ids, 60) 
                if dst < sys.maxsize:
                    junction['traffic_lights'] = [tl for tl in junction['traffic_lights'] if tl['id'] != path[0]]

            exits_ids = [ex['id'] for ex in junction['exits'] if 'id' in ex]

            for joint in junction['exits']: # remove pointless exits
                dst, path = self.__graph_find_path(joint, exits_ids, 60) 
                if dst < sys.maxsize:
                    junction['exits'] = [ex for ex in junction['exits'] if ex['id'] != joint['id']]

            self.__update_junction(junction)

    def __update_junction(self, junction):
        for traffic_light in junction['traffic_lights']:
            traffic_light['traffic_light'] = True
        
        for exit in junction['exits']:
            exit['exit'] = True