from __future__ import annotations

from functools import cached_property

from typing import TypeVar

import pygame

from .type_aliases import Surface, Sprite

SpriteType = TypeVar("SpriteType", bound=Sprite)


class CustomSprite(Sprite):
    """
    Wrapper for pygame.sprite.Sprite
    """
    def with_rect(self, x: int, y: int) -> SpriteType:
        self.rect = self.image.get_rect(topleft=(x, y))
        return self

    def scaled(self, scale_x: float, scale_y: float) -> SpriteType:
        curr_width, curr_height = self.image.get_size()
        self.image = pygame.transform.scale(
            self.image, (curr_width * scale_x, curr_height * scale_y)
        )
        return self


class Square(CustomSprite):
    """
    Square class that represents a game tile.
    """
    def __init__(
        self,
        surface: Surface,
        collides: bool = True,
        collectable: bool = False,
        kills: bool = False,
    ) -> None:
        super().__init__()
        self.image = surface.convert_alpha()
        self.collides = collides
        self.collectable = collectable
        self.kills = kills

    def update(self, x_shift: float) -> None:
        self.rect.x += x_shift


class TileSheet:
    """
    Load a tileset from a file.
    """
    def __init__(self, filename: str, columns: int, rows: int) -> None:
        self.sheet = pygame.image.load(filename)

        print(self.sheet.get_rect())

        self.tile_width = self.sheet.get_rect().width // columns
        self.tile_height = self.sheet.get_rect().height // rows

    def tile_at(self, x: int, y: int, x_off: int = 0, y_off: int = 0) -> Surface:
        """
        Get the tile at the given coordinates.

        :param x: X coordinate
        :param y: Y coordinate
        :param x_off: X offset
        :param y_off: Y offset
        :return: The tile at the given coordinates
        """
        return self.sheet.subsurface(
            (
                (x * self.tile_width) + x_off,
                (y * self.tile_height) + y_off,
                self.tile_width,
                self.tile_height,
            )
        )

    @property
    def all_tiles(self):
        """
        Get all the tiles in the tileset.
        :return:
        """
        for y in range(self.tile_height):
            for x in range(self.tile_width):
                yield self.tile_at(x, y)


class MapTileSheet(TileSheet):
    """
    Get the tileset for the map.
    """
    @cached_property
    def square(self) -> Surface:
        return self.tile_at(1, 0)

    @cached_property
    def coin(self) -> Surface:
        return self.tile_at(7, 8, -8)


class BulletTileSheet(TileSheet):
    """
    Get the tileset for the bullets.
    """
    @cached_property
    def bullet(self) -> Surface:
        return self.tile_at(15, 15)

