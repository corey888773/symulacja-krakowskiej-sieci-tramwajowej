from models.tram_stop import TramStop
from models.node import Node
from models.route import Route
from models.trip import Trip

from collections import defaultdict

import json

class Simulation:
    def __init__(self, network_model: dict) -> None:
        self.network_model = network_model

        # self.events: list[Event] = []
        # self.removed_events: list[Event] = []

        # self.trams: list[Tram] = []
        # self.removed_trams: list[Tram] = []

        self.tram_stops: dict[int, Node] = {}
        self.routes: dict[int, Route] = {}
        self.trips: dict[int, list[Trip]] = defaultdict(list)

        nodes = network_model["nodes"]
        for node in nodes:
            node_id = node["id"]

            if "stop_name" in node:
                self.tram_stops[node_id] = TramStop(node_id, node["x"], node["y"], node["stop_name"]) 

        routes = network_model["routes"]
        for route in routes:
            route_id = route["id"]
            start, stop = route["name"].split("-")
            route_stops = route["stops"]

            self.routes[route_id] = Route(route_id, start, stop, route_stops)

        trips = network_model["trips"]
        for trip in trips:
            route_id = trip["route"]
            time_table = trip["time_table"]
            time_table.append(time_table[-1] + 1)

            self.trips[route_id].append(Trip(route_id, time_table))

    def run(self) -> None:
        pass
        
        # for k, v in self.tram_stops.items():
        #     print(k, v)

        # for k, v in self.routes.items():
        #     print(k, v)
        #     break

        # for k, v in self.trips.items():
        #     print(k, [str(trip) for trip in v])
        #     break

# with open("../datapreprocessing/data/logical_network.json", "r", encoding="utf8") as f:
#     file_l = json.load(f)
# s = Simulation(file_l);
# s.run()

