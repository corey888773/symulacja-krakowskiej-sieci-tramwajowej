from enum import Enum
from .colors import Color

import pygame

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

    # Time settings
    START_TIME = 4 * 60  # 4:00 in minutes
    END_TIME = 23.5 * 60  # 23:30 in minutes

    # Play button settings
    PLAY_BUTTON_X = WIDTH * 0.02
    PLAY_BUTTON_Y = HEIGHT * 0.89
    PLAY_BUTTON_WIDTH = WIDTH * 0.04167
    PLAY_BUTTON_HEIGHT = HEIGHT * 0.05

    # Button settings
    BUTTON_WIDTH = WIDTH * 0.01667
    BUTTON_HEIGHT = HEIGHT * 0.02
    BUTTON_SPACING = WIDTH * 0.00833
    BUTTON_COLS = 8
    BUTTON_BASE_X = WIDTH * 0.7
    BUTTON_BASE_Y = HEIGHT * 0.43

    # Tram image settings
    TRAM_IMAGE_PATH = './resources/Train.png'
    TRAM_IMAGE_PATHS = ['./resources/l1.png', './resources/l2.png', './resources/l3.png', './resources/l4.png', './resources/l5.png', './resources/l6.png', './resources/l7.png', './resources/l8.png', './resources/l9.png', './resources/l10.png']
    TRAM_IMAGE_SIZE = (20, 20)  # This might not need scaling

    # Node and tram stop scaling factors
    NODE_SCALE_FACTOR_X = WIDTH * 0.95833
    NODE_SCALE_FACTOR_Y = HEIGHT * 0.87
    NODE_TRANSLATION_X = WIDTH * 0.02083
    NODE_TRANSLATION_Y = HEIGHT * 0.025
    NODE_OFFSET_Y = HEIGHT * 0.08

    # Widget settings
    WIDGET_BACKGROUND_COLOR = Color.LIGHT_GRAY_2.value