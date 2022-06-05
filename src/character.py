from __future__ import annotations

from abc import ABC, abstractmethod
from time import time

from typing import Collection, TypeAlias, Union

import pygame

from .type_aliases import Sprite, Surface, ParticleGenerator, SingleSprite
from .support import flip_image, import_folder
from .enums import Speeds, Orientation, Collisions, PlayerState
from .bullets import Bullet

SurfaceVec: TypeAlias = Union[Collection[Surface], Collection[Collection[Surface]]]


class FunctionalityMixin(ABC):
    """
    Abstract base class to implement MIXIN functionality.
    """
    ...


class Shooter(FunctionalityMixin):
    """
    Shooter protocol.
    """
    def __init__(self):
        super().__init__()
        self.bullets: list[Bullet] = []
        self.last_shot = 0

    @property
    @abstractmethod
    def x(self) -> int:
        """
        :return: the x coordinate of the shooter
        """
        ...

    @property
    @abstractmethod
    def y(self) -> int:
        """
        :return: the y coordinate of the shooter
        """
        ...

    @property
    @abstractmethod
    def orientation(self) -> Orientation:
        """
        :return: the orientation of the shooter
        """
        ...

    @property
    @abstractmethod
    def display_surface(self) -> Surface:
        """
        :return: the surface to display the shooter
        """
        ...

    def shoot(self, bullet_image: Surface, speed: Speeds = Speeds.BULLET_SPEED) -> None:
        """
        Shoot a bullet.

        :param bullet_image: the image of the bullet
        :param speed: the speed of the bullet
        :return: None
        """
        if time() - self.last_shot > Speeds.SHOOT_DELAY.value:
            bullet = Bullet(self.x, self.y, bullet_image, self.orientation, speed.value)
            self.bullets.append(bullet)
            self.last_shot = time()

    def display_bullets(self) -> None:
        """
        Draw the bullets to the screen

        :return: None
        """
        for bullet in self.bullets:
            single_bullet = SingleSprite()
            single_bullet.add(bullet)
            single_bullet.update()
            single_bullet.draw(self.display_surface)


class Character(ABC, Sprite):
    """
    Abstract base class that defines a Character.
    """
    def __init__(
        self, x: int, y: int, image: Surface, surface: Surface, speed: Speeds, *args
    ):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed.value
        self._orientation = Orientation.RIGHT
        self.collisions: set[Collisions] = set()

        self._display_surface = surface

        self.direction = pygame.math.Vector2(0, 0)

    def hits(self, sprite: Sprite) -> bool:
        """
        Check if the character hits another sprite.

        :param sprite: the sprite to check
        :return: True if the character hits the sprite, False otherwise
        """
        return pygame.sprite.collide_rect(self, sprite)

    def handle_collisions(self) -> None:
        """
        Handle collisions with solid sprites and walls.

        :return: None
        """
        if {Collisions.BOTTOM, Collisions.RIGHT}.issubset(self.collisions):
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif {Collisions.BOTTOM, Collisions.LEFT}.issubset(self.collisions):
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif {Collisions.BOTTOM}.issubset(self.collisions):
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif {Collisions.TOP, Collisions.RIGHT}.issubset(self.collisions):
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif {Collisions.TOP, Collisions.LEFT}.issubset(self.collisions):
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif {Collisions.TOP}.issubset(self.collisions):
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    @abstractmethod
    def load_animations(self, *args, **kwargs) -> SurfaceVec:
        """
        Load the animations of the character.

        :param args: any positional arguments
        :param kwargs: any keyword arguments
        :return: the animations of the character
        """
        ...

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """
        Update the character.

        :param args: any positional arguments
        :param kwargs: any keyword arguments
        :return: None
        """
        ...

    def with_rect(self, width, height) -> Character:
        """
        Resize the character.

        :param width: the new width of the character
        :param height: the new height of the character
        :return: the resized character
        """
        self.rect.size = (width, height)
        return self


class Player(Character, Shooter):
    """
    Class that defines a Player.
    """
    def __init__(
        self,
        x: int,
        y: int,
        image: Surface,
        surface: Surface,
        create_jump_particles: ParticleGenerator,
        bullet_image: Surface,
    ):
        super().__init__(
            x,
            y,
            image,
            surface,
            Speeds.PLAYER_MOVEMENT,
        )

        # Frame counters
        self.frame_index: int = 0
        self.dust_frame_index: int = 0

        # Assets
        self.animations, self.dust_run_particles = self.load_animations(
            "src/graphics/character/",
            "src/graphics/character/dust_particles/run",
        )

        print(
            f"Enemy has {len(self.animations[PlayerState.IDLE]), len(self.dust_run_particles)} animations"
        )

        self.bullet_image: Surface = bullet_image

        # Animations
        self.create_jump_particles = create_jump_particles
        self.status = PlayerState.IDLE

        # Score
        self.score = 0

    # Movement-related properties
    @property
    def is_idle(self) -> bool:
        return self.status is PlayerState.IDLE

    @property
    def is_running(self) -> bool:
        return self.status is PlayerState.RUN

    @property
    def is_jumping(self) -> bool:
        return self.status is PlayerState.JUMP

    @property
    def is_falling(self) -> bool:
        return self.status is PlayerState.FALL

    # Protocol-derived properties
    @property
    def display_surface(self) -> Surface:
        return self._display_surface

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @property
    def x(self) -> int:
        return self.rect.x + self.rect.width // 2

    @property
    def y(self) -> int:
        return self.rect.y + self.rect.height // 2

    @orientation.setter
    def orientation(self, value: Orientation) -> None:
        self._orientation = value
        self.image = self.animations[self.status][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))

    # Asset loaders
    @staticmethod
    def load_walking_animations(path: str) -> Collection[Surface]:
        """
        Load the walking animations of the player.

        :param path: the path to the folder containing the animations
        :return: the walking animations of the player
        """
        return {
            state: list(import_folder(f"{path}/{state.name}")) for state in PlayerState
        }

    @staticmethod
    def load_dust_animations(path: str) -> Collection[Surface]:
        """
        Load the dust animations of the player.

        :param path: the path to the folder containing the animations
        :return: the dust animations of the player
        """
        return list(import_folder(path))

    def load_animations(
        self, walking_path: str, dust_path: str, *args, **kwargs
    ) -> SurfaceVec:
        return self.load_walking_animations(walking_path), self.load_dust_animations(
            dust_path
        )

    # Event loop handlers
    def handle_key_presses(self) -> None:
        """
        Event listener for key presses

        The player can move left and right, jump and shoot.

        :return: None
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.orientation = Orientation.RIGHT
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.orientation = Orientation.LEFT
        else:
            self.direction.x = 0

        if keys[pygame.K_UP] and Collisions.BOTTOM in self.collisions:
            self.jump()
            self.create_jump_particles(self.rect.midbottom)

        if keys[pygame.K_SPACE]:
            self.shoot(self.bullet_image)

    # Animations
    def animate(self) -> None:
        animation = self.animations[self.status]

        # loop over frame index
        self.frame_index += Speeds.PLAYER_ANIMATION.value
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]

        if self.orientation == Orientation.RIGHT:
            self.image = image
        else:
            flipped = flip_image(image)
            self.image = flipped

        self.handle_collisions()

    def update_status(self) -> None:
        """
        Update the player state

        :return: None
        """
        if self.direction.y < 0:
            self.status = PlayerState.JUMP
        elif self.direction.y > 1:
            self.status = PlayerState.FALL
        else:
            if self.direction.x != 0:
                self.status = PlayerState.RUN
            else:
                self.status = PlayerState.IDLE

    def apply_gravity(self) -> None:
        """
        Apply gravity to the player.

        :return: None
        """
        self.direction.y += Speeds.GRAVITY.value
        self.rect.y += self.direction.y

    def jump(self) -> None:
        self.direction.y = Speeds.PLAYER_JUMP.value

    def run_dust_animation(self) -> None:
        """
        Display dust particles

        :return: None
        """
        if self.is_running and Collisions.BOTTOM in self.collisions:
            self.dust_frame_index += Speeds.DUST_ANIMATION.value
            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.orientation == Orientation.RIGHT:
                pos = self.rect.bottomleft - pygame.math.Vector2(6, 10)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
                flipped_dust_particle = flip_image(dust_particle)
                self.display_surface.blit(flipped_dust_particle, pos)

    def update(self) -> None:
        self.handle_key_presses()
        self.update_status()
        self.animate()
        self.run_dust_animation()
        self.display_bullets()


class Enemy(Character):
    """
    Class representing an enemy.
    """
    def __init__(self, x: int, y: int, image: Surface, surface: Surface):
        super().__init__(x, y, image, surface, Speeds.ENEMY_MOVEMENT)

        self.frame_index: int = 0
        self.animations = self.load_animations("src/graphics/enemy")

        print(f"Enemy has {len(self.animations)} animations")

    def load_animations(self, path: str, *args, **kwargs) -> list[Surface]:
        return list(import_folder(f"{path}"))

    def animate(self) -> None:
        # loop over frame index
        self.frame_index += Speeds.ENEMY_ANIMATION.value
        if self.frame_index >= len(self.animations):
            self.frame_index = 0

        image = self.animations[int(self.frame_index)]

        if self._orientation == Orientation.RIGHT:
            self.image = image
        else:
            flipped = flip_image(image)
            self.image = flipped

        self.handle_collisions()

    def update(self, *args, **kwargs) -> None:
        self.animate()
