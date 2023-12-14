from enum import Enum
from .colors import Color

import pygame, os

curr_dir = os.path.dirname(os.path.abspath(__file__))

#TODO where should i put these?
pygame.init()

class PyGameConfig():
    # Window settings
    WIDTH = 1200
    HEIGHT = 900
    WINDOW_TITLE = "Tram Simulation"

    # Text settings
    FONT_SIZE = int(HEIGHT * 0.032)
    FONT = pygame.font.Font(None, 24)
    FONT_SMALL = pygame.font.Font(None, 18)
    TEXT_COLOR = Color.BLACK.value
    
    # Slider settings
    SLIDER_X = WIDTH * 0.02
    SLIDER_Y = HEIGHT * 0.95
    SLIDER_WIDTH = WIDTH * 0.93
    SLIDER_HEIGHT = HEIGHT * 0.02
    HANDLE_WIDTH = WIDTH * 0.00833
    TIME_PROPORTION = 60

    # Time settings
    START_TIME = 4 * 60  # 4:00 in minutes
    END_TIME = 23.5 * 60  # 23:30 in minutes

    # Play button settings
    PLAY_BUTTON_X = WIDTH * 0.02
    PLAY_BUTTON_Y = HEIGHT * 0.89
    PLAY_BUTTON_WIDTH = WIDTH * 0.04167
    PLAY_BUTTON_HEIGHT = HEIGHT * 0.05

    # 2x time button settings
    DOUBLE_TIME_BUTTON_X = WIDTH * 0.07
    DOUBLE_TIME_BUTTON_Y = HEIGHT * 0.89
    DOUBLE_TIME_BUTTON_WIDTH = WIDTH * 0.04167
    DOUBLE_TIME_BUTTON_HEIGHT = HEIGHT * 0.05

    # 4x time button settings
    QUADRUPLE_TIME_BUTTON_X = WIDTH * 0.12
    QUADRUPLE_TIME_BUTTON_Y = HEIGHT * 0.89
    QUADRUPLE_TIME_BUTTON_WIDTH = WIDTH * 0.04167
    QUADRUPLE_TIME_BUTTON_HEIGHT = HEIGHT * 0.05

    # 1/2 time button settings
    HALF_TIME_BUTTON_X = WIDTH * 0.17
    HALF_TIME_BUTTON_Y = HEIGHT * 0.89
    HALF_TIME_BUTTON_WIDTH = WIDTH * 0.04167
    HALF_TIME_BUTTON_HEIGHT = HEIGHT * 0.05

    # Button settings
    BUTTON_WIDTH = WIDTH * 0.01667
    BUTTON_HEIGHT = HEIGHT * 0.02
    BUTTON_SPACING = WIDTH * 0.00833
    BUTTON_COLS = 8
    BUTTON_BASE_X = WIDTH * 0.7
    BUTTON_BASE_Y = HEIGHT * 0.43

    # Tram image settings
    TRAM_IMAGE_PATH = f'{curr_dir}/../resources/Train.png'
    TRAM_IMAGE_PATHS = [f'{curr_dir}/../resources/l1.png', f'{curr_dir}/../resources/l2.png', f'{curr_dir}/../resources/l3.png', f'{curr_dir}/../resources/l4.png', f'{curr_dir}/../resources/l5.png', f'{curr_dir}/../resources/l6.png', f'{curr_dir}/../resources/l7.png', f'{curr_dir}/../resources/l8.png', f'{curr_dir}/../resources/l9.png', f'{curr_dir}/../resources/l10.png', f'{curr_dir}/../resources/g5.png', f'{curr_dir}/../resources/g4.png', f'{curr_dir}/../resources/g3.png', f'{curr_dir}/../resources/g2.png', f'{curr_dir}/../resources/g1.png']
    TRAM_IMAGE_SIZE = (18, 18)  # This might not need scaling

    # Node and tram stop scaling factors
    NODE_SCALE_FACTOR_X = WIDTH * 0.95833
    NODE_SCALE_FACTOR_Y = HEIGHT * 0.87
    NODE_TRANSLATION_X = WIDTH * 0.02083
    NODE_TRANSLATION_Y = HEIGHT * 0.025
    NODE_OFFSET_Y = HEIGHT * 0.08

    # Widget settings
    WIDGET_BACKGROUND_COLOR = Color.LIGHT_GRAY_2.value