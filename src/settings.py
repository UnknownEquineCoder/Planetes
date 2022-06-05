import pygame
from .start import setup

from .save import Save

# Global resources
db = setup()
level_map = Save.from_json(db.get("current")).map
clock = pygame.time.Clock()

tile_size = 64
screen_width = 1200
screen_height = len(level_map) * tile_size
