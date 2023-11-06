import logging, math
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

    def fix_floating_islands(self):
        pass

    def graph_find_adjacents(self):
        for track in self.tracks:

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
                    logging.warning(f'Node {prev_node} already in adjacent nodes of {curr_node}')
            
                if next_node not in curr_node['adjacent_nodes']:
                    curr_node['adjacent_nodes'].append(next_node)
                else:
                    logging.warning(f'Node {next_node} already in adjacent nodes of {curr_node}')

            track_nodes[-1]['adjacent_nodes'].append(track_nodes[-2]) # last node is adjacent to second last node
            # outside of loop to avoid index out of range error

    def graph_find_successors(self):
        for track in self.tracks:

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
                    logging.warning(f'Node {next_node} already in accessible_nodes of {curr_node}')

    def track_remove_crossings(self):
        for joint in reversed(self.joints):
            if len(joint['adjacent_nodes']) != 4:
                continue

            if len(joint['accessible_nodes']) == 4:
                continue
            
            vectors = []
            for node in joint['adjacent_nodes']:
                vec = { 'x': node['x'] - joint['x'],
                        'y': node['y'] - joint['y'] }
                vec['mag'] = math.sqrt(vec['x'] ** 2 + vec['y'] ** 2) # magnitude of vector
                vectors.append(vec)

            paths = []
            for i in range(4):
                for j in range(i + 1, 4):
                    path_cos = (vectors[i]['x'] * vectors[j]['x'] + vectors[i]['y'] * vectors[j]['y']) / (vectors[i]['mag'] * vectors[j]['mag'])
                    path = { 'ix1': i,
                             'ix2': j,
                             'accessible': 0,
                             'cos': path_cos }
                    
                    if joint['adjacent_nodes'][i] in joint['accessible_nodes'] and joint['adjacent_nodes'][j] not in joint['accessible_nodes']:
                        path['accessible'] += i
                        paths.append(path)

                    elif joint['adjacent_nodes'][j] in joint['accessible_nodes'] and joint['adjacent_nodes'][i] not in joint['accessible_nodes']:
                        path['accessible'] += j
                        paths.append(path)
                        

            # find lowest cos path
            lowest = 0
            for i in range(1, len(paths)):
                if paths[i]['cos'] < paths[lowest]['cos']:
                    lowest = i
            
            path1 = paths[lowest]
            paths.pop(lowest)

            lowest = 0
            for i in range(1, len(paths)):
                if paths[i]['cos'] < paths[lowest]['cos']:
                    lowest = i

            path2 = paths[lowest]
            
            joint1 = {
                'id': 'xyz',
                'x': joint['x'],
                'y': joint['y'],
                'adjacent_nodes': [joint['adjacent_nodes'][path1['ix1']], joint['adjacent_nodes'][path1['ix2']]],
                'accessible_nodes': [joint['adjacent_nodes'][path1['accessible']]]
            }
            self.nodes[joint1['id']] = joint1

            joint2 = {
                'id': 'xyz',
                'x': joint['x'],
                'y': joint['y'],
                'adjacent_nodes': [joint['adjacent_nodes'][path2['ix1']], joint['adjacent_nodes'][path2['ix2']]],
                'accessible_nodes': [joint['adjacent_nodes'][path2['accessible']]]
            }
            self.nodes[joint2['id']] = joint2

            # update adjacent nodes and accessible nodes of modified nodes
            for adj in joint['adjacent_nodes']:

                for i in range(len(adj['accessible_nodes'])):
                    adj_to_adj = adj['accessible_nodes'][i]
                    
                    if adj not in joint1['adjacent_nodes'] and adj_to_adj == joint:
                        adj['accessible_nodes'][i] = joint1
                    elif adj not in joint2['adjacent_nodes'] and adj_to_adj == joint:
                        adj['accessible_nodes'][i] = joint2
                    
                for i in range(len(adj['adjacent_nodes'])):
                    adj_to_adj = adj['adjacent_nodes'][i]
                    
                    if adj not in joint1['adjacent_nodes'] and adj_to_adj == joint:
                        adj['adjacent_nodes'][i] = joint1
                    elif adj not in joint2['adjacent_nodes'] and adj_to_adj == joint:
                        adj['adjacent_nodes'][i] = joint2
            
            self.nodes.pop(joint['id'])
            self.joints.remove(joint)

    def track_generate_opposite_edges_to_bidirectional(self):
        pass