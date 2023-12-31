from enum import Enum

class Color(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (192, 192, 192)
    DARK_GRAY = (64, 64, 64)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 128, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 0, 255)
    CYAN = (0, 255, 255)
    BROWN = (165, 42, 42)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    BRONZE = (205, 127, 50)
    LIGHT_BLUE = (173, 216, 230)
    LIGHT_GREEN = (144, 238, 144)
    LIGHT_RED = (255, 182, 193)
    LIGHT_YELLOW = (255, 255, 224)
    LIGHT_ORANGE = (255, 160, 122)
    LIGHT_PURPLE = (221, 160, 221)
    LIGHT_PINK = (255, 182, 193)
    LIGHT_CYAN = (224, 255, 255)
    LIGHT_BROWN = (222, 184, 135)
    LIGHT_GOLD = (250, 250, 210)
    LIGHT_GRAY_2 = (220, 220, 220)

print(list(Color)[0].value)