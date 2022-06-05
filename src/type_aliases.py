from __future__ import annotations

import pygame

from typing import TypeAlias, Callable, Generator, Union

from .enums import PlayerState

# A bunch of type aliases for mypy
Surface: TypeAlias = pygame.Surface
AnimationMap: TypeAlias = dict[PlayerState, list[Surface]]
Particles: TypeAlias = list[Surface]
SpriteGroup: TypeAlias = pygame.sprite.Group
SingleSprite: TypeAlias = pygame.sprite.GroupSingle
Sprite: TypeAlias = pygame.sprite.Sprite
SurfaceGenerator: TypeAlias = Generator[Surface, None, None]
LevelMatrix: TypeAlias = list[str]
Vec2: TypeAlias = pygame.math.Vector2
BareVec2: TypeAlias = tuple[int, int]
ParticleGenerator: TypeAlias = Callable[[Union[Vec2, BareVec2]], None]


# This is a workaround for mypy not being able to infer the type of pygame.sprite.Group
class PlayerGroup(SingleSprite):
    @property
    def sprite(self) -> "Player":
        return super().sprite  # type: ignore


# Re-export the names
__all__ = [
    Surface.__name__,
    ParticleGenerator.__name__,
    AnimationMap.__name__,
    Particles.__name__,
    SpriteGroup.__name__,
    SingleSprite.__name__,
    Sprite.__name__,
    SurfaceGenerator.__name__,
    PlayerGroup.__name__,
]
