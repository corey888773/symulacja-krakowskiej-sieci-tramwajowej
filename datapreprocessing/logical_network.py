import logging, math, re
import numpy as np
from physical_network import PhysicalNetwork
import utils as U

class LogicalNetwork:
    def __init__(self, schedule : dict, physical_network : PhysicalNetwork):
        self.schedule = schedule
        self.physical_network = physical_network

        self.routes = []
        self.trips = []
        self.passanger_nodes = [] # stops and stations
        self.passanger_edges = [] # edges between stops and stations

        self.avaialbe_id = 0

    def remove_fake_route_stops(self):
        pass

    def validate_stop_names(self):
        for line in self.schedule['lines']:
            for stop in line['direction1'].get('stops'):
                node_ids = self.physical_network.stop_ids.get(stop['name'])
                if node_ids == None:
                    logging.error(f'stop {stop["name"]}, {node_ids}, {type(stop["name"])}')
                    continue

            for stop in line['direction2'].get('stops'):
                node_ids = self.physical_network.stop_ids.get(stop['name'])
                if node_ids == None:
                    logging.error(f'stop {stop["name"]}, {node_ids}, {type(stop["name"])}')
                    continue
            
            # TODO EXAMINE THIS NODES, BECAUSE THEY CAUSE PROBLEMS ALSO IN PROCESS_ROUTE
            # ERROR - logical_network.py:22, message: stop Plac Bohaterów Getta 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Krowodrza Górka P+R 03 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Bohaterów Getta 01 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Centralny im. R.Reagana 01 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Urzędnicza 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Centralny im. R.Reagana 03 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Krowodrza Górka P+R 03 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Urzędnicza 02 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Centralny im. R.Reagana 01 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Centralny im. R.Reagana 04 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Urzędnicza 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Urzędnicza 02 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Centralny im. R.Reagana 04 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Centralny im. R.Reagana 02 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Bohaterów Getta 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Bohaterów Getta 01 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Stary Kleparz 03 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Bohaterów Getta 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Krowodrza Górka P+R 03 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Bohaterów Getta 01 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Centralny im. R.Reagana 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Centralny im. R.Reagana 03 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Centralny im. R.Reagana 03 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Centralny im. R.Reagana 01 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Bohaterów Getta 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Urzędnicza 02 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Bohaterów Getta 01 , None, <class 'str'>
            # ERROR - logical_network.py:22, message: stop Plac Centralny im. R.Reagana 01 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Stary Kleparz 03 , None, <class 'str'>
            # ERROR - logical_network.py:28, message: stop Plac Centralny im. R.Reagana 03 , None, <class 'str'>

    def schedule_create_routes(self):
        line_info = []
        route_starting_from_stop = []

        for line in self.schedule['lines']:
            start_name = line['direction1']['stops'][0]['name']
            end_name = line['direction2']['stops'][-1]['name']

            start_id = int(np.squeeze(self.physical_network.stop_ids.get(start_name)[0])) #TODO: temp workaround wit [0]
            end_id = int(np.squeeze(self.physical_network.stop_ids.get(end_name)[0]))

            if start_id == None or end_id == None:
                logging.error(f'line {line["number"]} has no start or end stop')
                continue

            line_data = {
                "number": line['number'],
                "direction1": {
                    "name": line['direction1']['name'],
                    "start_id": start_id,
                    "start_name": start_name,
                    "end_id": end_id,
                    "end_name": end_name,
                },
                "direction2": {
                    "name": line['direction2']['name'],
                    "start_id": end_id,
                    "start_name": end_name,
                    "end_id": start_id,
                    "end_name": start_name,
                }
            }
            route_starting_from_stop.append(line_data)

            route1 = self.process_route(line['direction1'], start_id, end_id)
            route2 = self.process_route(line['direction2'], end_id, start_id)

            if route1 != None:
                self.routes.append(route1)
            if route2 != None:
                self.routes.append(route2)


    def process_route(self, direction : dict, start_node_id : int, end_node_id : int):
        route = {
            'id': self.__get_next_available_id(),
            'name': direction['name'],
            'nodes': [],
            'stops': [],
            'schedule_route': direction
            }

        init_node = curr_stop = self.physical_network.nodes.get(start_node_id)
        
        route['nodes'].append(init_node['id'])
        route['stops'].append(init_node['id'])


        for idx in range(1, len(direction['stops'])):
            next_stop = direction['stops'][idx]['name']

            second_next_stop = self.physical_network.nodes.get(end_node_id)['tags']['name']
            if idx < len(direction['stops']) - 1:
                second_next_stop = direction['stops'][idx + 1]['name']
                

            next_stop_ids = self.physical_network.stop_ids.get(next_stop)
            if next_stop_ids == None:
                logging.error(f'next_stop_ids is None, {next_stop}')
                continue

            target = [*next_stop_ids]
            path = []

            while target != []:
                # logging.info((curr_stop['id'], target))
                dist1, path1 = self.physical_network.graph_find_path(curr_stop, target)
                intermediate_platform = self.physical_network.nodes.get(
                    U.first_or_default(path1, default_value=-1)
                )

                if intermediate_platform == None:
                    logging.error(f'intermediate_platform is None, {curr_stop["id"]} to {target}')
                    break
            
                second_next_stop_ids = self.physical_network.stop_ids.get(second_next_stop)
                if second_next_stop_ids == None:
                    logging.error(f'second_next_stop_ids is None, {second_next_stop}')
                    break

                dist2, path2 = self.physical_network.graph_find_path(intermediate_platform, [*second_next_stop_ids])

                end_platform = self.physical_network.nodes.get(
                    U.first_or_default(path2, default_value=-1)
                )

                if end_platform == None:
                    logging.error(f'end_platform is None, {second_next_stop_ids} to {intermediate_platform["id"]}')
                    break

                straight_line_distance = \
                math.sqrt(
                    (intermediate_platform['x'] - end_platform['x']) ** 2 + (intermediate_platform['y'] - end_platform['y']) ** 2
                )

                # logging.info((dist1, dist2, straight_line_distance))

                if dist2 <  2 * straight_line_distance:
                    # logging.info(len(path1))
                    path = path1
                    break
                else:
                    for i in range(len(target) - 1, -1, -1):
                        n = target[i]
                        if n == path1[0]:
                            target.pop(i)

            
            if len(path) == 0:
                continue

            route['nodes'].extend(path)
            path.append(curr_stop)
            curr_stop = self.physical_network.nodes.get(
                U.first_or_default(path, default_value=-1)
            )

            route['stops'].append(curr_stop['id'])

        route['stops'].append(end_node_id)
        return route


    def __get_next_available_id(self):
        self.avaialbe_id += 1
        return self.avaialbe_id
        

    def schedule_create_trips(self):
        # TODO: additionally consider using calendar for weekends, holidays
        for route in self.routes:
        
            # firstly we want to combine all the schedules into one big schedule, 
            # each stop will have a list of times in minutes
            time_table = []
            for i in range(len(route['schedule_route']['stops'])):
                stop = route['schedule_route']['stops'][i]
                
                time_table.append([])
                for j in range(len(stop['schedule'])):
                    hour = int(stop['schedule'][j][0]) # Godzina
                    if hour == '' or hour == None:
                        continue

                    if hour < 2: # the schedule is weird and puts the 0 and 1 after 23 instead of at the beggining
                        hour += 24
                    
                    minutes = stop['schedule'][j][1] # Minuty
                    if minutes == '' or minutes == None:
                        continue

                    minutes = minutes.split(' ')
                    for m in minutes:
                        m = m.strip()
                        # only numbers
                        if re.match(r'^\d+$', m) == None:
                            continue

                        if m == '' or m == None:
                            continue
                                
                        minutes = int(m)
                        time_table[i].append(hour * 60 + minutes)

            # then for  each specific drive from Start to End we want to find a time for each stop 
            # and make sure that every trip has the same number of stops and we use every time from
            # the big schedule
            trip_count = len(time_table[0])
            for row in time_table:
                if len(row) > trip_count:
                    trip_count = len(row) # how many unique trips during a day are for this route 

            stop_count = len(time_table) # how many stops are on this route

            for i in range(trip_count):
                trip = {
                    'route' : route['id'],
                    'route_name' : route['name'],
                    'time_table' : [],
                    'start': 0,
                    'end': 0,
                    'duration': 0
                }

                last_stop_time = -1
                for j in range(stop_count):
                    k = 0

                    while k < len(time_table[j]):
                        if time_table[j][k] > last_stop_time and (last_stop_time == -1 or time_table[j][k] - last_stop_time < 8): # 8 is the max time between stops in minutes 
                            break
        
                        k += 1
                    
                    if k < len(time_table[j]):
                        trip['time_table'].append(time_table[j][k])
                        last_stop_time = trip['time_table'][j]

                        time_table[j][k] = -1 # mark as used 
                    else :
                        trip['time_table'].append(-1)
                    
                    
                t = 0
                while trip['time_table'][t] == -1:
                    t += 1
                
                trip['start'] = trip['time_table'][t]
                trip['end'] = trip['time_table'][t]
                trip['duration'] = trip['end'] - trip['start']

                if -1 in trip['time_table']:
                    continue

                self.trips.append(trip)
            

            # Validation if all times in temp time_table are used
            error = False
            for stop_time_table in time_table:
                for hour in stop_time_table:
                    if hour != -1:
                        error = True

            if error == True:
                logging.error(f'invalid trip {route} \n\n\n')

