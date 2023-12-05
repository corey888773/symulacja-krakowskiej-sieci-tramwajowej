from models.tram_stop import TramStop
from models.node import Node
from models.route import Route
from models.trip import Trip
from models.tram_stop import TramStop
from models.tram import Tram
from models.node import Node
from models.edge import Edge
from enums.colors import Color
from enums.pygame_config import PyGameConfig

from collections import defaultdict

import pygame
import json

class Simulation:
    def __init__(self, network_model_logical: dict, network_model_physical: dict) -> None:
        self.network_model_logical = network_model_logical
        self.network_model_physical = network_model_physical

        self.tram_stops_dict: dict[int, TramStop] = {}
        self.tram_stops_list: list[TramStop] = []

        self.nodes_dict: dict[int, Node] = {}
        self.nodes_list: list[Node] = []

        self.routes_dict: dict[int, Route] = {}
        self.routes_list: list[Route] = []

        self.trips_dict: dict[int, list[Trip]] = defaultdict(list)
        self.trips_list: list[Trip] = []

        self.edges_list: list[Edge] = []

        self.pgc = PyGameConfig()


        self.tram_stops_list = [
            TramStop(
                id=node["id"], 
                x=node["x"], 
                y=node["y"], 
                stop_name=node["stop_name"]
            ) 
            for node in self.network_model_logical["nodes"] if "stop_name" in node
        ]

        self.nodes_list = [
            Node(
                id=node["id"], 
                x=node["x"], 
                y=node["y"]
            ) 
            for node in self.network_model_physical["nodes"]
        ]

        self.edges_list = [
            Edge(
                id=edge["id"], 
                length=edge["length"], 
                max_speed=edge["max_speed"], 
                nodes=[node for node in self.network_model_physical["edges"][i]["nodes"]],
                head=self.network_model_physical["edges"][i]["nodes"][0],
                tail=self.network_model_physical["edges"][i]["nodes"][-1]
            ) 
            for i, edge in enumerate(self.network_model_physical["edges"])
        ]

        self.tram_stops_list = self.normalize_coords(self.tram_stops_list)
        self.tram_stops_dict = {tram_stop.id: tram_stop for tram_stop in self.tram_stops_list}

        self.nodes_list = self.normalize_coords(self.nodes_list)
        self.nodes_dict = {node.id: node for node in self.nodes_list}

        routes = self.network_model_logical["routes"]
        self.routes_list = [
            Route(
                id=route["id"],
                start=route["name"].split("-")[0],
                stop=route["name"].split("-")[1],
                stops=route["stops"]
            ) 
            for route in routes
        ]
        self.routes_dict = {route.id: route for route in self.routes_list}

        trips = self.network_model_logical["trips"]
        self.trips_list = [
            Trip(
                route_id=trip["route"],
                time_table=trip["time_table"]
            ) 
            for trip in trips
        ]
        for trip in self.trips_list:
            last_stop_time = trip.time_table[-1]
            trip.time_table.append(last_stop_time + 1)
            self.trips_dict[trip.route_id].append(trip)

        self._tram_stops_list_to_json()
        self._tram_stops_dict_to_json()
        self._nodes_list_to_json()
        self._nodes_dict_to_json()
        self._routes_list_to_json()
        self._routes_dict_to_json()
        self._trips_list_to_json()
        self._trips_dict_to_json()
        self._edges_list_to_json()


    def run(self) -> None:
        pygame.init()
        WINDOW = pygame.display.set_mode((self.pgc.WIDTH, self.pgc.HEIGHT))
        pygame.display.set_caption(self.pgc.WINDOW_TITLE)

        result: dict[int, list[list[tuple[int, int]]]] = {}
        """
        {
            route_id: [
                [
                    (stop_id, time),
                    ...
                ],
                ...
            ], 
            ...
        }
        """

        for route_id, route in self.routes_dict.items():
            result[route_id] = [[(route.stops[i], time) for i, time in enumerate(trip.time_table)] for trip in self.trips_dict[route_id]]

        self.result_to_json(result)

        # SLIDER
        slider_x = self.pgc.SLIDER_X
        slider_y = self.pgc.SLIDER_Y
        slider_width = self.pgc.SLIDER_WIDTH
        slider_height = self.pgc.SLIDER_HEIGHT
        handle_width = self.pgc.HANDLE_WIDTH
        handle_x = slider_x
        dragging = False

        # TIME
        start_time = self.pgc.START_TIME  # 4:00 in minutes
        end_time = self.pgc.END_TIME  # 23:30 in minutes
        previous_time = None

        # PLAY BUTTON
        play_button_x = self.pgc.PLAY_BUTTON_X
        play_button_y = self.pgc.PLAY_BUTTON_Y
        play_button_width = self.pgc.PLAY_BUTTON_WIDTH
        play_button_height = self.pgc.PLAY_BUTTON_HEIGHT

        # SIMULATION
        simulation_running = False
        current_stops = defaultdict(list)
        current_stops_trams = defaultdict(list)

        # TRAM
        tram_image = pygame.image.load(self.pgc.TRAM_IMAGE_PATH)
        tram_image = pygame.transform.scale(tram_image, self.pgc.TRAM_IMAGE_SIZE)

        # BUTTONS
        buttons = self.create_buttons()
        
        # DISPLAY LINES
        lines_surface = pygame.Surface(WINDOW.get_size(), pygame.SRCALPHA)
        self.display_lines(lines_surface)

        # DISPLAY TRAM STOPS
        tram_stops_surface = pygame.Surface(WINDOW.get_size(), pygame.SRCALPHA)
        self.display_tram_stops(tram_stops_surface)

        panel = pygame.Surface((300, 600)) 

        selected_route_ids = [None] # displaying all routes by default
        clicked_tram_stop = None # the tram stop that the user clicked on
        clicked_tram = None # the tram that the user clicked on
        update_trams = False # whether to update the trams on the screen

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_position = pygame.mouse.get_pos()

                        for route_id, stops in current_stops.items():
                            for id, stop in stops:
                                if ((mouse_position[0] - stop.x) ** 2 + (mouse_position[1] - stop.y) ** 2) ** 0.5 <= 20:
                                    tram = [tram for tram in current_stops_trams[route_id] if tram.id == id]
                                    clicked_tram = tram
                                    break
                                
                            if clicked_tram is not None:
                                break

                        for tram_stop in self.tram_stops_list:
                            if ((mouse_position[0] - tram_stop.x) ** 2 + (mouse_position[1] - tram_stop.y) ** 2) ** 0.5 <= 4:
                                clicked_tram_stop = tram_stop
                                break
                            else:
                                clicked_tram_stop = None

                        if slider_x <= mouse_position[0] <= slider_x + slider_width and slider_y <= mouse_position[1] <= slider_y + slider_height:
                            dragging = True
                            handle_x = min(max(mouse_position[0], slider_x), slider_x + slider_width - handle_width)
                            update_trams = True
                            current_stops.clear()

                        if play_button_x <= mouse_position[0] <= play_button_x + play_button_width and play_button_y <= mouse_position[1] <= play_button_y + play_button_height:
                            if not simulation_running:
                                current_stops.clear()
                            simulation_running = not simulation_running 

                        for button in buttons:
                            if button['rect'].collidepoint(mouse_position):
                                if button['text'] != 'all':
                                    # Unclick the 'all' button when any other button is clicked
                                    all_button = next((b for b in buttons if b['text'] == 'all'), None)
                                    if all_button:
                                        all_button['clicked'] = False
                                        if all_button['route_id'] in selected_route_ids:
                                            selected_route_ids.remove(all_button['route_id'])
                                else:
                                    for other_button in buttons:
                                        if other_button['text'] != 'all':
                                            other_button['clicked'] = False
                                            if other_button['route_id'] in selected_route_ids:
                                                selected_route_ids.remove(other_button['route_id'])

                                if button['clicked']:
                                    if button['route_id'] in selected_route_ids:
                                        selected_route_ids.remove(button['route_id'])
                                else:
                                    if button['route_id'] not in selected_route_ids:
                                        selected_route_ids.append(button['route_id'])

                                update_trams = True
                                button['clicked'] = not button['clicked']

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False
                        update_trams = False

                elif event.type == pygame.MOUSEMOTION:
                    mouse_position = pygame.mouse.get_pos()
                    for tram_stop in self.tram_stops_list:
                        if ((mouse_position[0] - tram_stop.x) ** 2 + (mouse_position[1] - tram_stop.y) ** 2) ** 0.5 <= 4:
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) 
                            break
                    else:
                        if (slider_x <= mouse_position[0] <= slider_x + slider_width and slider_y <= mouse_position[1] <= slider_y + slider_height) or (play_button_x <= mouse_position[0] <= play_button_x + play_button_width and play_button_y <= mouse_position[1] <= play_button_y + play_button_height):
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        else:
                            for button in buttons:
                                if button['rect'].collidepoint(mouse_position):
                                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                                    break
                            else:
                                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                    if dragging and not simulation_running:
                        handle_x = min(max(event.pos[0], slider_x), slider_x + slider_width - handle_width)

            mouse_position = pygame.mouse.get_pos()

            self.display_main_surfaces(WINDOW, lines_surface, tram_stops_surface)
            
            # Calculate the current time
            ratio = (handle_x - slider_x) / (slider_width - handle_width)
            current_time = start_time + ratio * (end_time - start_time)

            if (simulation_running or update_trams) and current_time != previous_time:
                # Go through all the routes
                for route_id in range(1, 45):

                    # Go through all the trips of the current route
                    for i, trip in enumerate(result[route_id]):

                        # Go through all the stops of the current trip
                        for stop_id, time in trip:
                            if int(current_time) == time:
                                tram_stop = self.tram_stops_dict[stop_id]

                                # Remove the tram from the previous stop
                                index_to_delete = next((idx for idx, (id, stop) in enumerate(current_stops[route_id]) if id == i), None)
                                if index_to_delete is not None:
                                    del current_stops[route_id][index_to_delete]

                                # Remove the tram from the previous stop
                                index_to_delete_tram = next((idx for idx, tram in enumerate(current_stops_trams[route_id]) if tram.id == i), None)
                                if index_to_delete_tram is not None:
                                    del current_stops_trams[route_id][index_to_delete_tram]

                                current_stops[route_id].append((i, tram_stop))
                                current_stops_trams[route_id].append(
                                    Tram(
                                        id=i, 
                                        current_stop=tram_stop, 
                                        stops=self.routes_dict[route_id].stops, 
                                        time_table=self.trips_dict[route_id][i].time_table
                                    )
                                )

                        # remove the last stop if the tram has reached its final destination
                        last_stop_id, last_stop_time = trip[-1]
                        if (int(current_time) == last_stop_time + 1):
                            index_to_delete = next((idx for idx, (id, stop) in enumerate(current_stops[route_id]) if id == i), None)
                            if index_to_delete is not None:
                                del current_stops[route_id][index_to_delete]
                                del current_stops_trams[route_id][index_to_delete]
                    
                    previous_time = current_time

            self.display_routes_with_color(WINDOW, selected_route_ids)
            self.display_trams(WINDOW, current_stops, selected_route_ids, tram_image)

            if current_time > end_time:
                current_time = start_time
                handle_x = slider_x

            hours = int(current_time // 60)
            minutes = int(current_time % 60)

            self.draw_slider(WINDOW, slider_x, slider_y, slider_width, slider_height, handle_x, handle_width)
            self.draw_current_time(WINDOW, slider_x, slider_y, slider_width, hours, minutes)
            self.draw_play_button(WINDOW, play_button_x, play_button_y, play_button_width, play_button_height)
            self.draw_buttons(WINDOW, buttons)

            # Draw the play symbol (a triangle) inside the button or the pause symbol (two rectangles)
            if not simulation_running:
                self.draw_symbol(WINDOW, "start", play_button_x, play_button_y, play_button_width, play_button_height)
            else:
                self.draw_symbol(WINDOW, "pause", play_button_x, play_button_y, play_button_width, play_button_height)

            if clicked_tram_stop is not None:
                self.show_tram_stop_name(WINDOW, clicked_tram_stop)

            if clicked_tram is not None:
                self.show_time_table(WINDOW, clicked_tram, panel)

            if simulation_running and not dragging:
                handle_x += 1 / 60

            pygame.display.update()
            # pygame.display.flip()

        self.current_stops_to_json(current_stops)
        self.current_stops_trams_to_json(current_stops_trams)

        pygame.quit()

    def normalize_coords(self, nodes_to_normalize: list[Node]) -> list[Node]:
        max_x = max(self.nodes_list, key=lambda node: node.x).x
        max_y = max(self.nodes_list, key=lambda node: node.y).y
        min_x = min(self.nodes_list, key=lambda node: node.x).x
        min_y = min(self.nodes_list, key=lambda node: node.y).y

        range_x = max_x - min_x
        range_y = max_y - min_y

        for node in nodes_to_normalize:
            node.x = ((node.x - min_x) / range_x) * (self.pgc.WIDTH - 50) + 25
            node.y = self.pgc.HEIGHT - 80 - (((node.y - min_y) / range_y) * (self.pgc.HEIGHT - 130) + 25)

        return nodes_to_normalize
    
    def display_lines(self, lines_surface: pygame.Surface) -> None:
        lines_surface.fill(Color.WHITE.value)
        for edge in self.edges_list:
            for i, node_id in enumerate(edge.nodes):
                if i < len(edge.nodes) - 1:
                    head_node = self.nodes_dict.get(node_id, None)
                    tail_node = self.nodes_dict.get(edge.nodes[i + 1], None)

                    if None not in [head_node, tail_node]:
                        pygame.draw.line(lines_surface, Color.BLACK.value, (head_node.x, head_node.y), (tail_node.x, tail_node.y), 3)

    def display_main_surfaces(self, WINDOW: pygame.Surface, lines_surface: pygame.Surface, tram_stops_surface: pygame.Surface) -> None:
        WINDOW.fill(Color.WHITE.value)
        WINDOW.blit(lines_surface, (0, 0))
        WINDOW.blit(tram_stops_surface, (0, 0))
    
    def display_tram_stops(self, tram_stops_surface: pygame.Surface) -> None:
        for tram_stop in self.tram_stops_list:
            pygame.draw.circle(tram_stops_surface, Color.RED.value, (tram_stop.x, tram_stop.y), 4)

    def display_routes_with_color(self, WINDOW: pygame.Surface, selected_route_ids: list[int]) -> None:
        for route_id in selected_route_ids:
            if route_id is None:
                continue
            for stop in self.routes_dict[route_id].stops:
                tram_stop = self.tram_stops_dict[stop]
                pygame.draw.circle(WINDOW, Color.GREEN.value, (tram_stop.x, tram_stop.y), 4)

    def display_trams(self, WINDOW: pygame.Surface, current_stops: dict, selected_route_ids: list[int], tram_image: pygame.Surface) -> None:
        for route_id, stops in current_stops.items():
            if route_id in selected_route_ids or None in selected_route_ids:
                for id, stop in stops:
                    WINDOW.blit(tram_image, (stop.x - 10, stop.y - 10))

    def show_tram_stop_name(self, WINDOW: pygame.Surface, tram_stop: TramStop) -> None:
        text_surface = self.pgc.FONT.render(tram_stop.stop_name, True, self.pgc.TEXT_COLOR, self.pgc.WIDGET_BACKGROUND_COLOR)
        WINDOW.blit(text_surface, (tram_stop.x, tram_stop.y))

    def show_time_table(self, WINDOW: pygame.Surface, tram: Tram, panel: pygame.Surface) -> None:
        lines = [f"Tram {tram[0].id} - {tram[0].current_stop.stop_name}"]

        for i, stop in enumerate(tram[0].stops):
            stop_name = self.tram_stops_dict[stop].stop_name
            hours, minutes = self._from_minutes_to_hours_and_minutes(tram[0].time_table[i])
            lines.append(f"{stop_name}: {hours}:{minutes:02}")

        panel.fill(self.pgc.WIDGET_BACKGROUND_COLOR)
        for i, line in enumerate(lines):
            text = self.pgc.FONT.render(line, True, self.pgc.TEXT_COLOR, self.pgc.WIDGET_BACKGROUND_COLOR)
            panel.blit(text, (10, 10 + i * 20))
        WINDOW.blit(panel, (10, 10))



    def draw_current_time(self, WINDOW: pygame.Surface, slider_x: int, slider_y: int, slider_width: int, hours: int, minutes: int) -> None:
        time_surface = self.pgc.FONT.render(f"{hours}:{minutes:02}", True, self.pgc.TEXT_COLOR, self.pgc.WIDGET_BACKGROUND_COLOR)
        WINDOW.blit(time_surface, (slider_x + slider_width + 10, slider_y))

    def draw_slider(self, WINDOW: pygame.Surface, slider_x: int, slider_y: int, slider_width: int, slider_height: int, handle_x: int, handle_width: int) -> None:
        pygame.draw.rect(WINDOW, (0, 0, 0), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(WINDOW, (255, 0, 0), (handle_x, slider_y, handle_width, slider_height))

    def create_buttons(self) -> list[dict]:
        buttons = []
        button_width = self.pgc.BUTTON_WIDTH
        button_height = self.pgc.BUTTON_HEIGHT
        button_spacing = self.pgc.BUTTON_SPACING
        button_base_x = self.pgc.BUTTON_BASE_X
        button_base_y = self.pgc.BUTTON_BASE_Y
        cols = 8
        for i in range(1, 46):
            col = (i - 1) % cols
            row = (i - 1) // cols
            x = button_base_x + col * (button_width + button_spacing)
            y = button_base_y + row * (button_height + button_spacing)

            if i == 45:
                buttons.append({'rect': pygame.Rect(x, y, button_width + 10, button_height), 'route_id': None, 'text': 'all', 'clicked': True})
            else:
                buttons.append({'rect': pygame.Rect(x, y, button_width, button_height), 'route_id': i, 'text': str(i), 'clicked': False})

        return buttons
    
    def draw_buttons(self, WINDOW: pygame.Surface, buttons: list[dict]) -> None:
        for button in buttons:
            button_color = Color.RED.value if button['clicked'] else Color.GRAY.value
            pygame.draw.rect(WINDOW, button_color, button['rect']) 
            text_surface = self.pgc.FONT.render(button['text'], True, Color.BLACK.value)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            WINDOW.blit(text_surface, text_rect) 

    def draw_play_button(self, WINDOW: pygame.Surface, button_x: int, button_y: int, button_width: int, button_height: int) -> None:
        pygame.draw.rect(WINDOW, Color.GRAY.value, (button_x, button_y, button_width, button_height))

    def draw_symbol(self, WINDOW: pygame.Surface, symbol: str, button_x: int, button_y: int, button_width: int, button_height: int) -> None:
        if symbol == "start":
            pygame.draw.polygon(
                WINDOW, 
                Color.WHITE.value, 
                [(button_x + 10, button_y + 10), 
                (button_x + 10, button_y + button_height - 10), 
                (button_x + button_width - 10, button_y + button_height / 2)]
            )

        elif symbol == "pause":
            pygame.draw.rect(
                    WINDOW, 
                    Color.WHITE.value, 
                    (button_x + 10, button_y + 10, (button_width - 30) / 2, button_height - 20)
                )
            pygame.draw.rect(
                WINDOW, 
                Color.WHITE.value, 
                (button_x + button_width / 2 + 5, button_y + 10, (button_width - 30) / 2, button_height - 20)
            )

    @staticmethod
    def result_to_json(result: dict) -> None:
        result_copy = {}
        for route_id, stops in result.items():
            result_copy[route_id] = [[str(item) for item in stop] for stop in stops] 
                    
        with open('./data/result.json', 'w', encoding='utf8') as f:
            json.dump(dict(result_copy), f, ensure_ascii=False, indent=4)

    @staticmethod
    def current_stops_to_json(current_stops: dict) -> None:
        current_stops_copy = {}
        for route_id, stops in current_stops.items():
            current_stops_copy[route_id] = [str(stop[0]) + " " + str(stop[1]) for stop in stops] 
                    
        with open(f'data/current_stops.json', 'w', encoding='utf8') as f:
            json.dump(dict(current_stops_copy), f, ensure_ascii=False, indent=4)

    @staticmethod
    def current_stops_trams_to_json(current_stops: dict) -> None:
        current_stops_copy = {}
        for route_id, stops in current_stops.items():
            current_stops_copy[route_id] = [str(stop) for stop in stops] 
                    
        with open(f'data/current_stops_trams.json', 'w', encoding='utf8') as f:
            json.dump(dict(current_stops_copy), f, ensure_ascii=False, indent=4)

    @staticmethod
    def _from_minutes_to_hours_and_minutes(minutes: int) -> tuple[int, int]:
        hours = minutes // 60
        minutes = minutes % 60
        return hours, minutes


    def _tram_stops_list_to_json(self) -> None:
        tram_stops_copy = [str(tram_stop) for tram_stop in self.tram_stops_list]
        with open('./data/tram_stops_list.json', 'w', encoding='utf8') as f:
            json.dump(tram_stops_copy, f, ensure_ascii=False, indent=4)

    def _tram_stops_dict_to_json(self) -> None:
        tram_stops_copy = {id: str(tram_stop) for id, tram_stop in self.tram_stops_dict.items()}
        with open('./data/tram_stops_dict.json', 'w', encoding='utf8') as f:
            json.dump(tram_stops_copy, f, ensure_ascii=False, indent=4)

    def _nodes_list_to_json(self) -> None:
        nodes_copy = [str(node) for node in self.nodes_list]
        with open('./data/nodes_list.json', 'w', encoding='utf8') as f:
            json.dump(nodes_copy, f, ensure_ascii=False, indent=4)

    def _nodes_dict_to_json(self) -> None:
        nodes_copy = {id: str(node) for id, node in self.nodes_dict.items()}
        with open('./data/nodes_dict.json', 'w', encoding='utf8') as f:
            json.dump(nodes_copy, f, ensure_ascii=False, indent=4)

    def _routes_list_to_json(self) -> None:
        routes_copy = [str(route) for route in self.routes_list]
        with open('./data/routes_list.json', 'w', encoding='utf8') as f:
            json.dump(routes_copy, f, ensure_ascii=False, indent=4)

    def _routes_dict_to_json(self) -> None:
        routes_copy = {id: str(route) for id, route in self.routes_dict.items()}
        with open('./data/routes_dict.json', 'w', encoding='utf8') as f:
            json.dump(routes_copy, f, ensure_ascii=False, indent=4)

    def _trips_list_to_json(self) -> None:
        trips_copy = [str(trip) for trip in self.trips_list]
        with open('./data/trips_list.json', 'w', encoding='utf8') as f:
            json.dump(trips_copy, f, ensure_ascii=False, indent=4)

    def _trips_dict_to_json(self) -> None:
        trips_copy = {id: [str(trip) for trip in trips] for id, trips in self.trips_dict.items()}
        with open('./data/trips_dict.json', 'w', encoding='utf8') as f:
            json.dump(trips_copy, f, ensure_ascii=False, indent=4)

    def _edges_list_to_json(self) -> None:
        edges_copy = [str(edge) for edge in self.edges_list]
        with open('./data/edges_list.json', 'w', encoding='utf8') as f:
            json.dump(edges_copy, f, ensure_ascii=False, indent=4)
