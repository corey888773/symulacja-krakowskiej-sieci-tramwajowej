from collections import defaultdict
from simulation import Simulation
from models.tram_stop import TramStop
from models.node import Node
from models.edge import Edge
from enums.colors import Color
from enums.pygame_config import PyGameConfig

from typing import Final

import pygame
import json


# pygame.init()
# pgc = PyGameConfig()

# WINDOW = pygame.display.set_mode((pgc.WIDTH, pgc.HEIGHT))
# pygame.display.set_caption(pgc.WINDOW_TITLE)

def main() -> None:
    with open("../datapreprocessing/data/physical_network.json", "r", encoding="utf8") as f:
        network_model_physical = json.load(f)

    with open("../datapreprocessing/data/logical_network.json", "r", encoding="utf8") as f:
        network_model_logical = json.load(f)

    simulation = Simulation(network_model_logical, network_model_physical)
    simulation.run()

    # result: dict[int, list[list[tuple[int, int]]]] = {}
    # """
    # {
    #     route_id: [
    #         [
    #             (stop_id, time),
    #             ...
    #         ],
    #         ...
    #     ], 
    #     ...
    # }
    # """
    # for route_id, route in simulation.routes.items():
    #     result[route_id] = [[(route.stops[i], time) for i, time in enumerate(trip.time_table)] for trip in simulation.trips[route_id]]


    # #################################################### RESULT TO JSON ####################################################
    # result_copy = {}
    # for route_id, stops in result.items():
    #     result_copy[route_id] = [str(item) for stop in stops for item in stop] 
                
    # with open('./data/result.json', 'w', encoding='utf8') as f:
    #     json.dump(dict(result_copy), f, ensure_ascii=False, indent=4)
    # #################################################### RESULT TO JSON ####################################################

    # nodes_json_p = network_model_physical["nodes"]
    # nodes_json_l = network_model_logical["nodes"]
    # tram_stops = [TramStop(id=node["id"], x=node["x"], y=node["y"], stop_name=node["stop_name"]) for node in nodes_json_l if "stop_name" in node]
    # nodes = [Node(id=node["id"], x=node["x"], y=node["y"]) for node in nodes_json_p if "stop_name" not in node] 
    # all_nodes = [Node(id=node["id"], x=node["x"], y=node["y"]) for node in nodes_json_p]
    
    # edges = [Edge(id=edge["id"], length=edge["length"], max_speed=edge["max_speed"], nodes=[node for node in network_model_physical["edges"][i]["nodes"]]) for i, edge in enumerate(network_model_physical["edges"])]


    # # Normalize the coordinates of the nodes and tram stops
    # max_x = max(all_nodes, key=lambda node: node.x).x
    # max_y = max(all_nodes, key=lambda node: node.y).y
    # min_x = min(all_nodes, key=lambda node: node.x).x
    # min_y = min(nodes, key=lambda node: node.y).y

    # range_x = max_x - min_x
    # range_y = max_y - min_y

    # # for node in nodes:
    # #     node.x = ((node.x - min_x) / range_x) * (pgc.WIDTH - 50) + 25
    # #     node.y = pgc.HEIGHT - 80 - (((node.y - min_y) / range_y) * (pgc.HEIGHT - 130) + 25)

    # for tram_stop in tram_stops:
    #     tram_stop.x = ((tram_stop.x - min_x) / range_x) * (pgc.WIDTH - 50) + 25
    #     tram_stop.y = pgc.HEIGHT - 80 - (((tram_stop.y - min_y) / range_y) * (pgc.HEIGHT - 130) + 25)

    # max_x_a = max(all_nodes, key=lambda node: node.x).x
    # max_y_a = max(all_nodes, key=lambda node: node.y).y
    # min_x_a = min(all_nodes, key=lambda node: node.x).x
    # min_y_a = min(all_nodes, key=lambda node: node.y).y

    # range_x_a = max_x_a - min_x_a
    # range_y_a = max_y_a - min_y_a

    # for node in all_nodes:
    #     node.x = ((node.x - min_x_a) / range_x_a) * (pgc.WIDTH - 50) + 25
    #     node.y = pgc.HEIGHT - 80 - (((node.y - min_y_a) / range_y_a) * (pgc.HEIGHT - 130) + 25)

    # all_nodes_dict = {node.id: node for node in all_nodes}

    # #################################################### TRAM STOPS TO JSON ####################################################
    # tram_stops_copy = [str(tram_stop) for tram_stop in tram_stops]
    # with open('./data/tram_stops.json', 'w', encoding='utf8') as f:
    #     json.dump(tram_stops_copy, f, ensure_ascii=False, indent=4)
    # #################################################### TRAM STOPS TO JSON ####################################################

    # #################################################### NODES TO JSON ####################################################
    # nodes_copy = [str(node) for node in nodes]
    # with open('./data/nodes.json', 'w', encoding='utf8') as f:
    #     json.dump(nodes_copy, f, ensure_ascii=False, indent=4)
    # #################################################### NODES TO JSON ####################################################
    

    # # SLIDER
    # # slider_x = WIDTH - 0.96 * WIDTH
    # # slider_y = HEIGHT - 50
    # # slider_width = 0.9 * WIDTH
    # # slider_height = 20
    # # handle_width = 10
    # slider_x = pgc.SLIDER_X
    # slider_y = pgc.SLIDER_Y
    # slider_width = pgc.SLIDER_WIDTH
    # slider_height = pgc.SLIDER_HEIGHT
    # handle_width = pgc.HANDLE_WIDTH
    # handle_x = slider_x
    # dragging = False

    # # TIME
    # start_time = pgc.START_TIME  # 4:00 in minutes
    # end_time = pgc.END_TIME  # 23:30 in minutes
    # previous_time = None

    # # PLAY BUTTON
    # play_button_x = pgc.PLAY_BUTTON_X
    # play_button_y = pgc.PLAY_BUTTON_Y
    # play_button_width = pgc.PLAY_BUTTON_WIDTH
    # play_button_height = pgc.PLAY_BUTTON_HEIGHT

    # # SIMULATION
    # simulation_running = False
    # current_stops = defaultdict(list)

    # tram_image = pygame.image.load('./resources/Train.png')
    # tram_image = pygame.transform.scale(tram_image, (20, 20))


    # # BUTTONS
    # buttons = []
    # button_width = pgc.BUTTON_WIDTH
    # button_height = pgc.BUTTON_HEIGHT
    # button_spacing = pgc.BUTTON_SPACING
    # button_base_x = pgc.BUTTON_BASE_X
    # button_base_y = pgc.BUTTON_BASE_Y
    # cols = 8
    # for i in range(1, 45):
    #     col = (i - 1) % cols
    #     row = (i - 1) // cols
    #     x = button_base_x + col * (button_width + button_spacing)
    #     y = button_base_y + row * (button_height + button_spacing)
    #     buttons.append({'rect': pygame.Rect(x, y, button_width, button_height), 'route_id': i, 'text': str(i), 'clicked': False})

    # all_button_index = 45  # Assuming 'all' button is the 45th button
    # col = (all_button_index - 1) % cols
    # row = (all_button_index - 1) // cols
    # x = button_base_x + col * (button_width + button_spacing)
    # y = button_base_y + row * (button_height + button_spacing)
    # buttons.append({'rect': pygame.Rect(x, y, button_width + 10, button_height), 'route_id': None, 'text': 'all', 'clicked': True})

    # selected_route_ids = [None] # displaying all routes by default
    # clicked_tram_stop = None # the tram stop that the user clicked on
    # clicked_tram = None # the tram that the user clicked on
    # update_trams = False # whether to update the trams on the screen


    # lines_surface = pygame.Surface(WINDOW.get_size())
    # lines_surface.fill(Color.WHITE.value)
    # for edge in edges:
    #     for i, node_id in enumerate(edge.nodes):
    #         if i < len(edge.nodes) - 1:
    #             head_node = all_nodes_dict.get(node_id, None)
    #             tail_node = all_nodes_dict.get(edge.nodes[i + 1], None)
    #             if None not in [head_node, tail_node]:
    #                 pygame.draw.line(lines_surface, Color.BLACK.value, (head_node.x, head_node.y), (tail_node.x, tail_node.y), 3)

    # tram_stops_surface = pygame.Surface(WINDOW.get_size(), pygame.SRCALPHA)
    # for tram_stop in tram_stops:
    #     pygame.draw.circle(tram_stops_surface, Color.RED.value, (tram_stop.x, tram_stop.y), 4)


  
    # running = True
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False

    #         elif event.type == pygame.MOUSEBUTTONDOWN:
    #             if event.button == 1:
    #                 mouse_position = pygame.mouse.get_pos()
    #                 for tram_stop in tram_stops:
    #                     if ((mouse_position[0] - tram_stop.x) ** 2 + (mouse_position[1] - tram_stop.y) ** 2) ** 0.5 <= 4:
    #                         clicked_tram_stop = tram_stop
    #                         break
    #                     else:
    #                         clicked_tram_stop = None

    #                 if slider_x <= mouse_position[0] <= slider_x + slider_width and slider_y <= mouse_position[1] <= slider_y + slider_height:
    #                     dragging = True
    #                     handle_x = min(max(mouse_position[0], slider_x), slider_x + slider_width - handle_width)
    #                     update_trams = True
    #                     current_stops.clear()

    #                 if play_button_x <= mouse_position[0] <= play_button_x + play_button_width and play_button_y <= mouse_position[1] <= play_button_y + play_button_height:
    #                     if not simulation_running:
    #                         current_stops.clear()
    #                     simulation_running = not simulation_running 

    #                 for button in buttons:
    #                     if button['rect'].collidepoint(mouse_position):
    #                         if button['text'] != 'all':
    #                             # Unclick the 'all' button when any other button is clicked
    #                             all_button = next((b for b in buttons if b['text'] == 'all'), None)
    #                             if all_button:
    #                                 all_button['clicked'] = False
    #                                 if all_button['route_id'] in selected_route_ids:
    #                                     selected_route_ids.remove(all_button['route_id'])
    #                         else:
    #                             for other_button in buttons:
    #                                 if other_button['text'] != 'all':
    #                                     other_button['clicked'] = False
    #                                     if other_button['route_id'] in selected_route_ids:
    #                                         selected_route_ids.remove(other_button['route_id'])

    #                         if button['clicked']:
    #                             if button['route_id'] in selected_route_ids:
    #                                 selected_route_ids.remove(button['route_id'])
    #                         else:
    #                             if button['route_id'] not in selected_route_ids:
    #                                 selected_route_ids.append(button['route_id'])

    #                         update_trams = True
    #                         button['clicked'] = not button['clicked']

    #         elif event.type == pygame.MOUSEBUTTONUP:
    #             if event.button == 1:
    #                 dragging = False
    #                 update_trams = False

    #         elif event.type == pygame.MOUSEMOTION:
    #             mouse_position = pygame.mouse.get_pos()
    #             for tram_stop in tram_stops:
    #                 if ((mouse_position[0] - tram_stop.x) ** 2 + (mouse_position[1] - tram_stop.y) ** 2) ** 0.5 <= 4:
    #                     pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) 
    #                     break
    #             else:
    #                 if (slider_x <= mouse_position[0] <= slider_x + slider_width and slider_y <= mouse_position[1] <= slider_y + slider_height) or (play_button_x <= mouse_position[0] <= play_button_x + play_button_width and play_button_y <= mouse_position[1] <= play_button_y + play_button_height):
    #                     pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    #                 else:
    #                     for button in buttons:
    #                         if button['rect'].collidepoint(mouse_position):
    #                             pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    #                             break
    #                     else:
    #                         pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    #             if dragging and not simulation_running:
    #                 handle_x = min(max(event.pos[0], slider_x), slider_x + slider_width - handle_width)

    #     mouse_position = pygame.mouse.get_pos()

    #     # Display the tram stops and the lines
    #     WINDOW.fill(Color.WHITE.value)
    #     WINDOW.blit(lines_surface, (0, 0))
    #     WINDOW.blit(tram_stops_surface, (0, 0))

    #     # Calculate the current time
    #     ratio = (handle_x - slider_x) / (slider_width - handle_width)
    #     current_time = start_time + ratio * (end_time - start_time)

        

    #     if (simulation_running or update_trams) and current_time != previous_time:
    #         for route_id, stops in result.items():
    #             for i, trip in enumerate(result[route_id]):
    #                 for stop_id, time in trip:
    #                     if int(current_time) == time:
    #                         tram_stop = next((tram_stop for tram_stop in tram_stops if tram_stop.id == stop_id), None)

    #                         index_to_delete = next((idx for idx, (id, stop) in enumerate(current_stops[route_id]) if id == i), None)

    #                         if index_to_delete is not None:
    #                             del current_stops[route_id][index_to_delete]

    #                         current_stops[route_id].append((i, tram_stop))
    #                         # time_table = simulation.trips[route_id].time_table
    #                         #current_stops[route_id].append(Tram(id=i, current_stop=tram_stop, stops=stops, time_table=time_table))

    #                 # remove the last stop if the tram has reached its final destination
    #                 last_stop_id, last_stop_time = trip[-1]
    #                 if (int(current_time) == last_stop_time + 1):
    #                     index_to_delete = next((idx for idx, (id, stop) in enumerate(current_stops[route_id]) if id == i), None)
    #                     if index_to_delete is not None:
    #                         del current_stops[route_id][index_to_delete]
                
    #             previous_time = current_time

    #     for route_id, stops in current_stops.items():
    #         if route_id in selected_route_ids or None in selected_route_ids:
    #             for id, stop in stops:
    #                 WINDOW.blit(tram_image, (stop.x - 10, stop.y - 10))

    #     if current_time > end_time:
    #         current_time = start_time
    #         handle_x = slider_x

    #     hours = int(current_time // 60)
    #     minutes = int(current_time % 60)

    #     # Draw the slider
    #     pygame.draw.rect(WINDOW, (0, 0, 0), (slider_x, slider_y, slider_width, slider_height))
    #     pygame.draw.rect(WINDOW, (255, 0, 0), (handle_x, slider_y, handle_width, slider_height))

    #     # Draw the current time
    #     time_surface = pgc.FONT.render(f"{hours}:{minutes:02}", True, pgc.TEXT_COLOR, pgc.WIDGET_BACKGROUND_COLOR)
    #     WINDOW.blit(time_surface, (slider_x + slider_width + 10, slider_y))

    #     # Draw the play button
    #     pygame.draw.rect(WINDOW, Color.GRAY.value, (play_button_x, play_button_y, play_button_width, play_button_height))
    #     for button in buttons:
    #         button_color = Color.RED.value if button['clicked'] else Color.GRAY.value
    #         pygame.draw.rect(WINDOW, button_color, button['rect']) 
    #         text_surface = pgc.FONT.render(button['text'], True, Color.BLACK.value)
    #         text_rect = text_surface.get_rect(center=button['rect'].center)
    #         WINDOW.blit(text_surface, text_rect) 

    #     # Draw the play symbol (a triangle) inside the button
    #     if not simulation_running:
    #         pygame.draw.polygon(
    #             WINDOW, 
    #             Color.WHITE.value, 
    #             [(play_button_x + 10, play_button_y + 10), 
    #              (play_button_x + 10, play_button_y + play_button_height - 10), 
    #              (play_button_x + play_button_width - 10, play_button_y + play_button_height / 2)]
    #         )

    #     # Draw the pause symbol (two rectangles) inside the button
    #     else:
    #         pygame.draw.rect(
    #             WINDOW, 
    #             Color.WHITE.value, 
    #             (play_button_x + 10, play_button_y + 10, (play_button_width - 30) / 2, play_button_height - 20)
    #         )
    #         pygame.draw.rect(
    #             WINDOW, 
    #             Color.WHITE.value, 
    #             (play_button_x + play_button_width / 2 + 5, play_button_y + 10, (play_button_width - 30) / 2, play_button_height - 20)
    #         )

    #     if simulation_running and not dragging:
    #         handle_x += 1 / 60

    #     if clicked_tram_stop is not None:
    #         text_surface = pgc.FONT.render(clicked_tram_stop.stop_name, True, pgc.TEXT_COLOR, pgc.WIDGET_BACKGROUND_COLOR)
    #         WINDOW.blit(text_surface, (clicked_tram_stop.x, clicked_tram_stop.y))

    #     pygame.display.update()
    #     # pygame.display.flip()


    # #################################################### CURRENT STOPS TO JSON ####################################################
    # current_stops_copy = {}
    # for route_id, stops in current_stops.items():
    #     current_stops_copy[route_id] = [str(stop[0]) + " " + str(stop[1]) for stop in stops] 
                
    # with open('data/current_stops.json', 'w', encoding='utf8') as f:
    #     json.dump(dict(current_stops_copy), f, ensure_ascii=False, indent=4)
    # #################################################### CURRENT STOPS TO JSON ####################################################


    # pygame.quit()


if __name__ == '__main__':
    main()