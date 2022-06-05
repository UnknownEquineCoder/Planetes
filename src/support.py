from os import walk

import pygame
from .type_aliases import SurfaceGenerator


def import_folder(path: str) -> SurfaceGenerator:
    """
    Imports a folder and yields all the images in it.

    :param path: Path to the folder
    :return: Generator of images
    """
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            yield image_surf


def flip_image(image: pygame.Surface) -> pygame.Surface:
    """
    Flips a pygame image.

    :param image:
    :return:
    """
    return pygame.transform.flip(image, True, False)


def load_tiles(filename: str, columns: int, rows: int) -> SurfaceGenerator:
    """
    Loads a tileset from a file.

    :param filename: Path to the tileset file
    :param columns: Number of columns in the tileset
    :param rows: Number of rows in the tileset
    :return: Generator of images
    """
    sheet = pygame.image.load(filename).convert_alpha()
    sheet_rect = sheet.get_rect()

    tile_width = sheet_rect.width // columns
    tile_height = sheet_rect.height // rows

    for j in range(rows):
        for i in range(columns):
            yield sheet.subsurface(
                (i * tile_width, j * tile_height, tile_width, tile_height)
            )
