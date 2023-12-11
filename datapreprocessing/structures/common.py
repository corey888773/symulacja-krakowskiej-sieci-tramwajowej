import math

class Junction:
    def __init__(self):
        self.joints = []
        self.traffic_lights = []
        self.exits = []

    def to_json(self) -> dict:
        return {
            'traffic_lights': [traffic_light.id for traffic_light in self.traffic_lights],
            'exits': [exit.id for exit in self.exits],
        }


class Track:
    def __init__(self):
        self.id = None
        self.nodes = []
        self.tags = {}
        self.length = None

    def from_dict(d : dict, pn):
        track = Track()
        track.id = d['id']
        track.nodes = [pn.nodes[id] for id in d['nodes']]
        track.tags = d['tags']
        return track

    def to_json(self, detailed : bool=False) -> dict:
        export_track = {
                'id': self.id,
                'length': self.length,
                'max_speed': self.tags['maxspeed'],
            }

        if detailed:
            export_track['nodes'] = [node.id for node in self.nodes]
            return export_track

        export_track['head'] = self.nodes[0].id
        export_track['tail'] = self.nodes[-1].id
        return export_track


class Node:
    def __init__(self, id : int, x : float, y : float):
        self.id = id
        self.x = x
        self.y = y
        self.adjacent_nodes = []
        self.accessible_nodes = []
        self.tags = {}

        self.is_traffic_light = False
        self.is_exit = False
        self.is_special = False
        self.is_junction = False

        self.junction = None

    def distance_to(self, other) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def add_tags(self, tags : dict):
        self.tags = tags

        if 'name' in tags:
            self.tags['name'] = tags['name'].strip().replace(' ', '')

    def to_json(self) -> dict:
        export_node = {
                'id': self.id,
                'x': self.x,
                'y': self.y,
            }

        if self.tags != {}:
                export_node['stop_name'] = self.tags['name']

        if self.is_traffic_light:
                export_node['traffic_light'] = True

        if self.is_exit:
                export_node['exit'] = True

        return export_node


class PassangerNode:
    def __init__(self, ids : int, name : str, x : float, y : float):
        self.name = name
        self.ids = ids
        self.x = x
        self.y = y
        self.properties = {}

    def to_json(self):
        return {
            'name': self.name,
            'ids': self.ids,
            'generation_rate': self.properties['generation_rate'],
            'absorption_rate': self.properties['absorption_rate'],
            'expected_generated_count': self.properties['expected_generated_count'],
        }


class PassangerEdge:
    def __init__(self, head : str, tail : str):
        self.head = head
        self.tail = tail
        self.lines = []

    def to_json(self) -> dict:
        return {
            'head': self.head,
            'tail': self.tail,
            'lines': self.lines
        }


class Route:
    def __init__(self, id : int, name : str, schedule_route : dict):
        self.id = id
        self.name = name
        self.schedule_route = schedule_route
        self.nodes = []
        self.stops = []

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'stops': self.stops,
        }


class Trip:
    def __init__(self, route : int, route_name : str):
        self.route = route
        self.route_name = route_name
        self.time_table = []
        self.generation_left = []
        self.absorption_left = []
        self.start = 0
        self.end = 0
        self.duration = 0

    def to_json(self) -> dict:
        return {
            'route': self.route,
            'time_table': self.time_table,
            'generation_left': self.generation_left,
            'absorption_left': self.absorption_left,
        }