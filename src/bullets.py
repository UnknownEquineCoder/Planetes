import pygame
from .enums import Orientation
from .tiles import CustomSprite
from .type_aliases import Sprite, Surface


class Bullet(CustomSprite):
    """
    Class that represents a bullet.
    """
    def __init__(
        self,
        x: int,
        y: int,
        image: Surface,
        orientation: Orientation,
        speed: int = 10,
    ):
        super().__init__()
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.spawn = {"x": x, "y": y}
        self.orientation = orientation
        self.speed = speed
        self.is_alive = True

    def update(self, *_, **__) -> None:
        """
        Compute the state for each frame.

        :param _: ignore *args
        :param __: ignore **kwargs
        :return: None
        """
        if self.orientation == Orientation.LEFT:
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed
        if abs(self.rect.x - self.spawn["x"]) > 550:
            self.kill()
            self.is_alive = False

    def hits(self, sprite: Sprite) -> bool:
        """
        Check if the bullet hits an enemy.

        :param sprite: the sprite to check
        :return: True if the bullet hits the sprite, False otherwise
        """
        return pygame.sprite.collide_rect(self, sprite)
