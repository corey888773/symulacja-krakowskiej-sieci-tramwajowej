import logging, math, re, json
import numpy as np
import utils as U
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

from .physical_network import PhysicalNetwork
from .common import Node, Track, Junction, Trip, Route, PassangerNode, PassangerEdge
from .schedule import Schedule, Line, Direction, Stop

REMOVED_STOPS = [
    'KrowodrzaGórkaP+R03'
]

class LogicalNetwork:
    def __init__(self, schedule : Schedule, physical_network : PhysicalNetwork):
        self.schedule = schedule
        self.physical_network = physical_network

        self.routes = []
        self.trips = []
        self.passanger_nodes = {} # stops and stations
        self.passanger_edges = {} # edges between stops and stations

        self.avaialbe_id = 0

    def remove_fake_route_stops(self):
        pass

    def validate_stop_names(self):
        for line in self.schedule.lines:
            for stop in line.direction1.stops:
                if stop.name in REMOVED_STOPS:
                    continue
                node_ids = self.physical_network.stop_ids.get(stop.name)
                if node_ids == None:
                    logging.error(f'stop {stop.name} not found')
                    continue

            for stop in line.direction2.stops:
                if stop.name in REMOVED_STOPS:
                    continue
                node_ids = self.physical_network.stop_ids.get(stop.name)
                if node_ids == None:
                    logging.error(f'stop {stop.name} not found')
                    continue

    END_STOPS = { 
        '1' : ['CichyKącik01', 'Wańkowicza02'],
        '3' : ['KrowodrzaGórkaP+R02', 'NowyBieżanówP+R'],
        '4' : ['BronowiceMałe', 'ZajezdniaNowaHuta02'],
        '5' : ['KrowodrzaGórkaP+R02', 'Wańkowicza02'],
        '8' : ['BronowiceMałe', 'BorekFałęcki'],
        '9' : ['NowyBieżanówP+R', 'Mistrzejowice'],
        '10' : ['KurdwanówP+R01', 'Pleszów'],
        '11' : ['CzerwoneMakiP+R', 'MałyPłaszówP+R'],
        '13' : ['Bronowice01', 'NowyBieżanówP+R'],
        '14' : ['Bronowice01', 'Mistrzejowice'],
        '16' : ['Bardosa02', 'Mistrzejowice'],
        '17' : ['DworzecTowarowy', 'CzerwoneMakiP+R'],
        '18' : ['PapierniPrądnickich02', 'CzerwoneMakiP+R'],
        '19' : ['KrowodrzaGórkaP+R02', 'BorekFałęcki'],
        '20' : ['CichyKącik01', 'MałyPłaszówP+R'],
        '21' : ['Os.Piastów01', 'Pleszów'],
        '22' : ['KopiecWandy', 'BorekFałęcki'],
        '24' : ['BronowiceMałe', 'KurdwanówP+R01'],
        '44' : ['DworzecTowarowy', 'KopiecWandy'],
        '49' : ['TAURONArenaKrakówWieczysta01', 'NowyBieżanówP+R'],
        '50' : ['BorekFałęcki', 'PapierniPrądnickich02'],
        '52' : ['Os.Piastów01', 'CzerwoneMakiP+R'],
    }

    def schedule_create_routes(self):
        for line in self.schedule.lines:
            dir1_start_name = line.direction1.stops[0].name
            dir1_end_name = self.END_STOPS.get(line.number)[0]

            dir2_start_name = line.direction2.stops[0].name
            dir2_end_name = self.END_STOPS.get(line.number)[1]

            logging.info(f'{line.number} {dir1_start_name}-{dir1_end_name} / {dir2_start_name}-{dir2_end_name}')

            dir1_start_id = int(np.squeeze(self.physical_network.stop_ids.get(dir1_start_name)[0]))
            dir1_end_id = int(np.squeeze(self.physical_network.stop_ids.get(dir1_end_name)[0]))

            dir2_start_id = int(np.squeeze(self.physical_network.stop_ids.get(dir2_start_name)[0]))
            dir2_end_id = int(np.squeeze(self.physical_network.stop_ids.get(dir2_end_name)[0]))

            if dir1_start_id == None or dir1_end_id == None or dir2_start_id == None or dir2_end_id == None:
                logging.error(f'line {line["number"]} has no start or end stop')
                continue
            
            route1 = self.process_route(line.direction1, dir1_start_id, dir1_end_id)
            route2 = self.process_route(line.direction2, dir2_start_id, dir2_end_id)

            route1.line = route2.line = int(line.number)

            if route1 != None:
                self.routes.append(route1)
            if route2 != None:
                self.routes.append(route2)


    def process_route(self, direction : Direction, start_node_id : int, end_node_id : int):
        route = Route(self.__get_next_available_id(), name=direction.name, schedule_route=direction)
        init_node = curr_stop = self.physical_network.nodes.get(start_node_id)
        
        route.nodes.append(init_node.id)
        route.stops.append(init_node.id)

        for idx in range(1, len(direction.stops)):
            next_stop = direction.stops[idx].name

            second_next_stop = self.physical_network.nodes.get(end_node_id).tags['name']
            if idx < len(direction.stops) - 1:
                second_next_stop = direction.stops[idx + 1].name
                

            next_stop_ids = self.physical_network.stop_ids.get(next_stop)
            target = [*next_stop_ids]
            path = []

            while target != []:
                # logging.info((curr_stop.id, target))
                dist1, path1 = self.physical_network.graph_find_path(curr_stop, target)
                intermediate_platform = self.physical_network.nodes.get(
                    U.first_or_default(path1, default_value=-1)
                )

                if intermediate_platform == None:
                    # logging.error(f'intermediate_platform is None, {curr_stop.id} to {target}')
                    break
            
                second_next_stop_ids = self.physical_network.stop_ids.get(second_next_stop)
                dist2, path2 = self.physical_network.graph_find_path(intermediate_platform, [*second_next_stop_ids])

                end_platform = self.physical_network.nodes.get(
                    U.first_or_default(path2, default_value=-1)
                )

                if end_platform == None:
                    # logging.error(f'end_platform is None, {second_next_stop_ids} to {intermediate_platform.id}')
                    break

                straight_line_distance = intermediate_platform.distance_to(end_platform)

                # logging.info((dist1, dist2, straight_line_distance))

                if dist2 <  2 * straight_line_distance:
                    path = path1
                    break
                else:
                    for i in range(len(target) - 1, -1, -1):
                        n = target[i]
                        if n == path1[0]:
                            target.pop(i)

            route.nodes.extend(path)
            path.append(curr_stop.id)
            curr_stop = self.physical_network.nodes.get(
                U.first_or_default(path, default_value=-1)
            )

            route.stops.append(curr_stop.id)

        if curr_stop.id != end_node_id and curr_stop.id not in route.nodes:
            route.nodes.append(end_node_id)

        if end_node_id not in route.nodes:
            route.stops.append(end_node_id)
        return route


    def update_route_lengths(self):
        for route in self.routes:
            route.length = self.__get_route_length(route)


    def __get_route_length(self, route : Route) -> float:
        length = 0
        for i in range(len(route.nodes) - 1):
            length += self.physical_network.nodes.get(route.nodes[i]).distance_to(
                self.physical_network.nodes.get(route.nodes[i + 1])
            )

        return length


    def __get_next_available_id(self):
        self.avaialbe_id += 1
        return self.avaialbe_id
        

    def schedule_create_trips(self):
        # TODO: additionally consider using calendar for weekends, holidays
        for route in self.routes:

            # firstly we want to combine all the schedules into one big schedule, 
            # each stop will have a list of times in minutes
            time_table = []
            for i in range(len(route.schedule_route.stops)):
                stop = route.schedule_route.stops[i]
                
                time_table.append([])
                for j in range(len(stop.schedule)):
                    hour = int(stop.schedule[j][0]) # Godzina
                    if hour == '' or hour == None:
                        continue

                    if hour < 2: # the schedule is weird and puts the 0 and 1 after 23 instead of at the beggining
                        hour += 24
                    
                    minutes = stop.schedule[j][1] # Minuty
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
                trip = Trip(route.id, route.name)

                last_stop_time = -1
                for j in range(stop_count):
                    k = 0

                    while k < len(time_table[j]):
                        if time_table[j][k] > last_stop_time and (last_stop_time == -1 or time_table[j][k] - last_stop_time < 8): # 8 is the max time between stops in minutes 
                            break
        
                        k += 1
                    
                    if k < len(time_table[j]):
                        trip.time_table.append(time_table[j][k])
                        last_stop_time = trip.time_table[j]

                        time_table[j][k] = -1 # mark as used 
                    else :
                        trip.time_table.append(-1)
                    
                    
                t = 0
                while trip.time_table[t] == -1:
                    t += 1
                
                trip.start = trip.time_table[t]
                trip.end = last_stop_time
                trip.duration = trip.end - trip.start

                if -1 in trip.time_table:
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
                
                # TODO: fix this
                # INFO - logical_network.py:379, message: Starowiślna 02 4
                # ERROR - logical_network.py:380, message: generation_sum != absorption_sum 24750 != 6375
                # INFO - logical_network.py:379, message: Starowiślna 02 5
                # ERROR - logical_network.py:380, message: generation_sum != absorption_sum 24750 != 6375
                # INFO - logical_network.py:379, message: Starowiślna 02 6
                # ERROR - logical_network.py:380, message: generation_sum != absorption_sum 24750 != 6375
                # INFO - logical_network.py:379, message: Starowiślna 02 7
                # ERROR - logical_network.py:380, message: generation_sum != absorption_sum 99000 != 25500
                # INFO - logical_network.py:379, message: Starowiślna 02 8
                # ERROR - logical_network.py:380, message: generation_sum != absorption_sum 99000 != 25500
                # INFO - logical_network.py:379, message: Starowiślna 02 16
                # ERROR - logical_network.py:380, message: generation_sum != absorption_sum 99000 != 25500
                # INFO - logical_network.py:379, message: Starowiślna 02 17
                # ERROR - logical_network.py:380, message: generation_sum != absorption_sum 99000 != 25500


    def create_passanger_nodes(self):
        for route in self.routes:
            for idx in range(len(route.stops) - 1):
                curr_stop_name = self.physical_network.nodes.get(route.stops[idx]).tags['name']
                next_stop_name = self.physical_network.nodes.get(route.stops[idx + 1]).tags['name']

                passanger_edge = self.passanger_edges.get(f"{curr_stop_name}_{next_stop_name}")
                if passanger_edge == None:
                    passanger_edge = PassangerEdge(next_stop_name, curr_stop_name)
                    self.passanger_edges[f"{curr_stop_name}_{next_stop_name}"] = passanger_edge

                passanger_edge.lines.append(route.id)
                
                if self.passanger_nodes.get(curr_stop_name) == None:
                    self.passanger_nodes[curr_stop_name] = self.create_passanger_node(curr_stop_name)

            if self.passanger_nodes.get(next_stop_name) == None:
                self.passanger_nodes[next_stop_name] = self.create_passanger_node(next_stop_name)
                    

    def create_passanger_node(self, name : str) -> PassangerNode:
        stops = self.physical_network.stop_ids.get(name)
        stop_nodes = [self.physical_network.nodes.get(id) for id in stops]

        if len(stops) > 1:
            logging.error(f'len(stops) > 1, {name}: {stops}')

            
        passanger_node = PassangerNode(
            name=name, 
            ids=stops,
            x=sum(node.x for node in stop_nodes) / len(stop_nodes),
            y=sum(node.y for node in stop_nodes) / len(stop_nodes)
        )

        return passanger_node


    def set_passanger_nodes_properties(self):
        residential = self.__generate_passanger_properties(
            generation_rate=[0, 100, 400, 120, 400, 100, 0],
			generation_time=[0, 4, 7, 9, 16, 18, 23],
			absorption_rate=[0, 25, 100, 120, 100, 100, 0],
			absorption_time=[0, 4, 7, 9, 16, 18, 23],
        )
        
        central = self.__generate_passanger_properties(
            generation_rate=[0, 25, 100, 120, 100, 100, 0],
			generation_time=[0, 4, 7, 9, 16, 18, 23],
			absorption_rate=[0, 100, 400, 120, 400, 100, 0],
			absorption_time=[0, 4, 7, 9, 16, 18, 23],
        )

        high_interest = self.__generate_passanger_properties(
            generation_rate=[0, 125, 500, 600, 500, 500, 0],
			generation_time=[0, 4, 7, 9, 16, 18, 23],
			absorption_rate=[0, 500, 2000, 600, 2000, 500, 0],
			absorption_time=[0, 4, 7, 9, 16, 18, 23],
        )

        for node in self.passanger_nodes.values():
            node.properties = residential

        city_center = self.__city_center_cords()
        for node in self.__get_passanger_nodes_inside_area(city_center):
            node.properties = central

        high_interest_nodes = self.__get_high_interest_nodes() # TODO: find high interest nodes
        for node in high_interest_nodes:
            node.properties = high_interest

        # Validation if passangers are generated and absorbed equally
        for h in range(24):
            generation_sum, absorption_sum = 0, 0
            for node in self.passanger_nodes.values():
                generation_sum += node.properties['generation_rate'][h]
                absorption_sum += node.properties['absorption_rate'][h]

            if generation_sum != absorption_sum:
                logging.error(f'{node.name} - {h}: generation_sum != absorption_sum {generation_sum} != {absorption_sum}')


    def __generate_passanger_properties(self, generation_rate : list, generation_time : list,
                                         absorption_rate : list, absorption_time : list) -> dict:
        properties = {
            'generation_rate': [],
            'generation_distribution': [],
            'absorption_rate': [],
            'expected_generated_count': []
        }

        j, rate_sum, rate = 0, 0, generation_rate[0]

        for h in range(24):
            if h >= generation_time[j + 1]:
                j += 1
                rate = generation_rate[j]

            rate_sum += rate
            properties['generation_rate'].append(rate)
            properties['generation_distribution'].append(rate_sum)

        properties['expected_generated_count'] = rate_sum

        j = 0
        for h in range(24):
            if h >= absorption_time[j + 1]:
                j += 1
                rate = absorption_rate[j]

            properties['absorption_rate'].append(rate)

        return properties


    def __get_passanger_nodes_inside_area(self, area : list) -> list:
        nodes_inside = []
        for node in self.passanger_nodes.values():
            point = Point(node.x, node.y)
            area = Polygon(area)
            if point.within(area):
                nodes_inside.append(node)


        #     x, y = area.exterior.xy
        #     plt.plot(x, y)
        # for node in self.physical_network.nodes.values():
        #     plt.plot(node.x, node.y, 'ro')
        # plt.show()

        return nodes_inside


    def __city_center_cords(self) -> list:
        border_stops = [
            "Reymana01", #
            "UniwersytetPedagogiczny02",
            "Biprostal02", #
            "Bratysławska01", #
            "CmentarzRakowicki01", #
            "Białucha01", #
            "Dąbie01", #
            "Klimeckiego01", #
            "PodgórzeSKA02", #
            "Łagiewniki05", #
            "Kobierzyńska01"
        ]
        cords = []

        for stop in border_stops:
            stop_id = self.physical_network.stop_ids.get(stop)
            if stop_id == None:
                logging.error(f'stop_id is None, {stop}')
                continue
            node = self.physical_network.nodes.get(stop_id[0])
            if node == None:
                logging.error(f'node is None, {stop}')
                continue
            
            cords.append((node.x, node.y))

        return cords

    def __get_high_interest_nodes(self) -> list:
        stops = [
            "TeatrSłowackiego01",
            "TeatrSłowackiego02",
            "TeatrBagatela01",
            "TeatrBagatela02",
            "PocztaGłówna01",
            "PocztaGłówna02",
            "RondoGrzegórzeckie01",
            "RondoGrzegórzeckie02",
            "RondoMogilskie01",
            "RondoMogilskie02",
            "RondoMatecznego01",
            "RondoMatecznego02",
            "Norymberska01",
            "Norymberska02",
            "CzerwoneMakiP+R01",
            "Politechnika01",
            "Politechnika02",
            "Politechnika03",
        ]

        high_interest_nodes = []
        for stop_name in stops:
            passanger_node = self.passanger_nodes.get(stop_name)
            if passanger_node == None:
                logging.error(f'passanger_node is None, {stop_name}')
                continue
            high_interest_nodes.append(passanger_node)

        return high_interest_nodes

    def cumulative_properties(self):
        temp_cumulative_generation_rate = {}
        temp_cumulative_absorption_rate = {}
        curr_route = None

        for trip in self.trips:
            if trip.route in [9, 13, 15, 27, 33, 39]:
                pass
            if curr_route == None or curr_route.id != trip.route:
                curr_route = self.routes[trip.route - 1]
                temp_cumulative_generation_rate = []
                temp_cumulative_absorption_rate = []

                for stop_id in curr_route.stops:
                    # node passanger node where stop is in .ids
                    node = self.passanger_nodes.get(self.physical_network.nodes.get(stop_id).tags['name'])
                    if node == None:
                        logging.error(f'node is None, {stop_id}')
                        continue

                    temp_cumulative_absorption_rate.append(node.properties['absorption_rate'])
                    temp_cumulative_generation_rate.append(node.properties['generation_rate']) 

            generation_left = [0] * len(trip.time_table)
            absorption_left = [0] * len(trip.time_table)

            for i in range(len(trip.time_table), 0, -1):
                curr_time = trip.time_table[i - 1]
                if curr_time == -1:
                    continue

                curr_hour = curr_time // 60
                
                for j in range(i, len(trip.time_table) - 1):
                    generation_left[i - 1] += temp_cumulative_generation_rate[j][curr_hour - 1]
                    absorption_left[i - 1] += temp_cumulative_absorption_rate[j][curr_hour - 1]

            trip.generation_left = generation_left
            trip.absorption_left = absorption_left
            
 
    def to_json(self) -> dict:
        export_network = {
            'nodes': [node.to_json() for node in self.physical_network.nodes.values() if node.is_special],
            'edges': [edge.to_json() for edge in self.physical_network.tracks],
            'junctions': [junction.to_json() for junction in self.physical_network.junctions],
            'routes': [route.to_json() for route in self.routes],
            'trips': [trip.to_json() for trip in self.trips],
            'passanger_nodes': [p_node.to_json() for p_node in self.passanger_nodes.values()],
            'passanger_edges': [p_edge.to_json() for p_edge in self.passanger_edges.values()],
            'passanger_count': sum(node.properties['expected_generated_count'] for node in self.passanger_nodes.values())
        }

        return export_network