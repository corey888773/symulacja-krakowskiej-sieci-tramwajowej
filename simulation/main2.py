from simulation import Simulation
from models.tram_stop import TramStop
from models.node import Node
from enums.colors import Color

from typing import Final

import pygame
import json


pygame.init()

# Constants
WIDTH: Final[int] = 1200
HEIGHT: Final[int] = 1000
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation")

FONT = pygame.font.Font(None, 24)
TEXT_COLOR = Color.BLACK.value
BACKGROUND_COLOR = (220, 220, 220)

def main() -> None:
    with open("../datapreprocessing/data/physical_network.json", "r", encoding="utf8") as f:
        file_p = json.load(f)

    with open("../datapreprocessing/data/logical_network.json", "r", encoding="utf8") as f:
        file_l = json.load(f)

    simulation = Simulation(file_l)

    result: dict[int, list[list[tuple[int, int]]]] = {}
    for route_id, route in simulation.routes.items():
        result[route_id] = [[(route.stops[i], time) for i, time in enumerate(trip.time_table)] for trip in simulation.trips[route_id]]


    nodes_json_p = file_p["nodes"]
    nodes_json_l = file_l["nodes"]
    tram_stops = [TramStop(id=node["id"], x=node["x"], y=node["y"], stop_name=node["stop_name"]) for node in nodes_json_l if "stop_name" in node]
    nodes = [Node(id=node["id"], x=node["x"], y=node["y"]) for node in nodes_json_p if "stop_name" not in node]    

    max_x = max(nodes, key=lambda node: node.x).x
    max_y = max(nodes, key=lambda node: node.y).y
    min_x = min(nodes, key=lambda node: node.x).x
    min_y = min(nodes, key=lambda node: node.y).y

    range_x = max_x - min_x
    range_y = max_y - min_y

    for node in nodes:
        node.x = ((node.x - min_x) / range_x) * (WIDTH - 50) + 25
        node.y = HEIGHT - (((node.y - min_y) / range_y) * (HEIGHT - 50) + 25)

    for tram_stop in tram_stops:
        tram_stop.x = ((tram_stop.x - min_x) / range_x) * (WIDTH - 50) + 25
        tram_stop.y = HEIGHT - (((tram_stop.y - min_y) / range_y) * (HEIGHT - 50) + 25)
    

    # SLIDER
    slider_x = WIDTH - 400
    slider_y = HEIGHT - 50
    slider_width = 350
    slider_height = 20
    handle_width = 10
    handle_x = slider_x
    dragging = False

    # TIME
    start_time = 4 * 60  # 4:00 in minutes
    end_time = 23.5 * 60  # 23:30 in minutes

    # PLAY BUTTON
    play_button_x = WIDTH - 400
    play_button_y = HEIGHT - 110
    play_button_width = 50
    play_button_height = 50

    # SIMULATION
    simulation_running = False

    
    clicked_tram_stop = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_position = pygame.mouse.get_pos()
                    for tram_stop in tram_stops:
                        if ((mouse_position[0] - tram_stop.x) ** 2 + (mouse_position[1] - tram_stop.y) ** 2) ** 0.5 <= 4:
                            clicked_tram_stop = tram_stop
                            break
                        else:
                            clicked_tram_stop = None

                    if slider_x <= mouse_position[0] <= slider_x + slider_width and slider_y <= mouse_position[1] <= slider_y + slider_height:
                        dragging = True
                        handle_x = min(max(mouse_position[0], slider_x), slider_x + slider_width - handle_width)

                    if play_button_x <= mouse_position[0] <= play_button_x + play_button_width and play_button_y <= mouse_position[1] <= play_button_y + play_button_height:
                        simulation_running = not simulation_running 

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                mouse_position = pygame.mouse.get_pos()
                for tram_stop in tram_stops:
                    if ((mouse_position[0] - tram_stop.x) ** 2 + (mouse_position[1] - tram_stop.y) ** 2) ** 0.5 <= 4:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) 
                        break
                else:
                    if (slider_x <= mouse_position[0] <= slider_x + slider_width and slider_y <= mouse_position[1] <= slider_y + slider_height) or (play_button_x <= mouse_position[0] <= play_button_x + play_button_width and play_button_y <= mouse_position[1] <= play_button_y + play_button_height):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if dragging and not simulation_running:
                    handle_x = min(max(event.pos[0], slider_x), slider_x + slider_width - handle_width)

        mouse_position = pygame.mouse.get_pos()

        WINDOW.fill(Color.WHITE.value)

        for node in nodes:
            pygame.draw.circle(WINDOW, (0, 0, 0), (node.x, node.y), 3)

        for tram_stop in tram_stops:
            pygame.draw.circle(WINDOW, (255, 0, 0), (tram_stop.x, tram_stop.y), 4)

        # Calculate the current time
        ratio = (handle_x - slider_x) / (slider_width - handle_width)
        current_time = start_time + ratio * (end_time - start_time)

        current_stops = {route_id: None for route_id in result}

        for route_id, route in result.items():
            for trip in route:
                for stop_id, time in trip:
                    if time == current_time:
                        # Update the current stop for this route
                        current_stops[route_id] = next((stop for stop in tram_stops if stop.id == stop_id), None)

            tram_stop = current_stops[route_id]
            if tram_stop is not None:
                pygame.draw.circle(WINDOW, (0, 255, 0), (tram_stop.x, tram_stop.y), 10)

        if current_time > end_time:
            current_time = start_time
            handle_x = slider_x

        hours = int(current_time // 60)
        minutes = int(current_time % 60)

        # Draw the slider
        pygame.draw.rect(WINDOW, (0, 0, 0), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(WINDOW, (255, 0, 0), (handle_x, slider_y, handle_width, slider_height))

        # Draw the current time
        time_surface = FONT.render(f"{hours}:{minutes:02}", True, TEXT_COLOR, BACKGROUND_COLOR)
        WINDOW.blit(time_surface, (slider_x + slider_width + 10, slider_y))

        # Draw the play button
        pygame.draw.rect(WINDOW, (128, 128, 128), (play_button_x, play_button_y, play_button_width, play_button_height))

        # Draw the play symbol (a triangle) inside the button
        if not simulation_running:
            pygame.draw.polygon(
                WINDOW, 
                (255, 255, 255), 
                [(play_button_x + 10, play_button_y + 10), 
                 (play_button_x + 10, play_button_y + play_button_height - 10), 
                 (play_button_x + play_button_width - 10, play_button_y + play_button_height / 2)]
            )

        # Draw the pause symbol (two rectangles) inside the button
        else:
            pygame.draw.rect(
                WINDOW, 
                (255, 255, 255), 
                (play_button_x + 10, play_button_y + 10, (play_button_width - 30) / 2, play_button_height - 20)
            )
            pygame.draw.rect(
                WINDOW, 
                (255, 255, 255), 
                (play_button_x + play_button_width / 2 + 5, play_button_y + 10, (play_button_width - 30) / 2, play_button_height - 20)
            )

        if simulation_running and not dragging:
            handle_x += 1 / 60

        if clicked_tram_stop is not None:
            text_surface = FONT.render(clicked_tram_stop.stop_name, True, TEXT_COLOR, BACKGROUND_COLOR)
            WINDOW.blit(text_surface, (clicked_tram_stop.x, clicked_tram_stop.y))

        # pygame.display.update()
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()