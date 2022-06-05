from enum import Enum, auto


class PlayerState(Enum):
    """
    Enum for the different states of the player.
    """
    IDLE = "idle"
    RUN = "run"
    JUMP = "jump"
    FALL = "fall"


class Speeds(Enum):
    """
    Enum to store the different speeds of the game.
    """
    PLAYER_ANIMATION = 0.15
    PARTICLE_ANIMATION = 0.5
    DUST_ANIMATION = 0.15
    PLAYER_MOVEMENT = 8
    PLAYER_JUMP = -16
    GRAVITY = 0.8
    SHOOT_DELAY = 0.18
    ENEMY_MOVEMENT = 3.5
    ENEMY_ANIMATION = 0.15
    BULLET_SPEED = 7


class Orientation(Enum):
    """
    Enum to store the different orientations of a character.
    """
    RIGHT = auto()
    LEFT = auto()


class Collisions(Enum):
    """
    Enum to store the different collision types.
    """
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


class AnimationType(Enum):
    """
    Enum to store the different types of animations.
    """
    JUMP = "jump"
    LAND = "land"


class CellType(Enum):
    """
    Enum to store the different types of cells.
    """
    EMPTY = " "
    WALL = "X"
    PLAYER = "P"
    ENEMY = "E"
    COIN = "C"
    DEATH_BOX = "D"
