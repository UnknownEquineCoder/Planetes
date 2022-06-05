from __future__ import annotations

import pygame
import requests

from .tiles import Square, MapTileSheet, BulletTileSheet
from .character import Enemy
from .settings import tile_size, screen_width
from .player import Player
from .particles import ParticleEffect
from .enums import *
from .character import Character
from .settings import db
from .save import Save
from .type_aliases import (
    PlayerGroup,
    SingleSprite,
    Surface,
    LevelMatrix,
    BareVec2,
    Vec2,
    SpriteGroup,
)

map_tiles = MapTileSheet("src/graphics/tiles/tileset.png", 20, 12)
bullet_tiles = BulletTileSheet("src/graphics/tiles/bullets2.png", 32, 24)


class GameOver(Exception):
    pass


class Level:
    """
    Class representing a level.
    """
    def __init__(self, level_data: LevelMatrix, surface: Surface) -> None:
        # level setup
        self.level_data = level_data
        self.display_surface = surface
        self.enemies: list[SingleSprite] = []
        self.tiles, self.player = self.spawn_sprites(level_data)
        self.world_shift = 0
        self.current_x = 0
        self.landed = False

        # dust
        self.dust_sprite = SingleSprite()
        # self.player_on_ground = False

    async def save(self):
        """
        Save the current level progression to the database and to the API.
        :return:
        """
        self.update_db()
        await self.save_to_api()

    def create_jump_particles(self, pos: BareVec2) -> None:
        """
        Create particles when the player jumps.

        :param pos: The position of the player.
        :return: None
        """
        player: Player = self.player.sprite
        if player.orientation == Orientation.RIGHT:
            pos -= Vec2(10, 5)
        else:
            pos += Vec2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, AnimationType.JUMP)
        self.dust_sprite.add(jump_particle_sprite)

    @property
    def player_landed(self) -> bool:
        player: Player = self.player.sprite

        return Collisions.BOTTOM in player.collisions

    def create_landing_dust(self) -> None:
        """
        Create particles when the player lands.
        :return: None
        """
        player: Player = self.player.sprite
        if (
            self.player_landed
            and
            # Collisions.BOTTOM in player.collisions and
            not self.dust_sprite.sprites()
        ):
            if player.orientation == Orientation.RIGHT:
                offset = Vec2(10, 15)
            else:
                offset = Vec2(-10, 15)
            fall_dust_particle = ParticleEffect(
                player.rect.midbottom - offset, AnimationType.LAND
            )
            self.dust_sprite.add(fall_dust_particle)

    def spawn_sprites(
        self,
        layout: LevelMatrix,
    ) -> tuple[SpriteGroup, PlayerGroup]:
        """
        Create the sprites for the player, coins, tiles and enemies.

        :param layout: The level layout.
        :return: A tuple containing the sprites for the player, coins, tiles and enemies.
        """
        tiles = pygame.sprite.Group()
        player_sprite: Player | None = None

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                # Match the cell type
                match CellType(cell):
                    case CellType.WALL:
                        tiles.add(Square(map_tiles.square).scaled(4, 4).with_rect(x, y))
                    case CellType.PLAYER:
                        player_sprite = Player(
                            x,
                            y,
                            pygame.image.load("src/graphics/character/idle/1.png"),
                            self.display_surface,
                            self.create_jump_particles,
                            bullet_tiles.bullet,
                        )
                    case CellType.COIN:
                        tiles.add(
                            Square(map_tiles.coin, collides=False, collectable=True)
                            .scaled(2, 2)
                            .with_rect(x + 16, y + 16)
                        )
                    case CellType.DEATH_BOX:
                        tiles.add(
                            Square(Surface((64, 64), pygame.SRCALPHA), kills=True)
                            .scaled(4, 4)
                            .with_rect(x, y)
                        )
                    case CellType.ENEMY:
                        # TODO: FIX
                        group = SingleSprite()
                        group.add(
                            Enemy(
                                x,
                                y - 64,
                                pygame.image.load("src/graphics/enemy/enemy_0.png"),
                                self.display_surface,
                            )
                        )
                        self.enemies.append(group)

                        tiles.add(
                            Square(Surface((64, 64), pygame.SRCALPHA))
                            .scaled(4, 4)
                            .with_rect(x, y)
                        )
                    case _:
                        pass

        # if no player is present, raise an error
        if not player_sprite:
            raise ValueError("No player found")

        player = PlayerGroup(player_sprite)

        return tiles, player

    def display_enemies(self) -> None:
        """
        Display the enemies on the screen.

        :return: None
        """
        for enemy in self.enemies:
            enemy.draw(self.display_surface)
            enemy.update()

    def handle_horizontal_movement(self) -> None:
        """
        Check if camer has to move horizontally and move it.

        :return: None
        """
        player: Player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = Speeds.PLAYER_MOVEMENT.value * 2
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -Speeds.PLAYER_MOVEMENT.value * 2
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self, character: Character) -> None:
        """
        Handle character collisions

        :param character: The character to check collisions for.
        :return: None
        """
        character.rect.x += character.direction.x * character.speed

        for sprite in self.tiles.sprites():

            if type(character) is Enemy:
                # enemies change orientation when they hit a wall
                if (
                    character.direction.x > 0
                    and sprite.rect.left < character.rect.right < sprite.rect.right
                ):
                    character.direction.x *= -1
                    character.speed = Speeds.ENEMY_MOVEMENT.value

            # If the character collides with a wall, stop moving
            if hasattr(sprite, "collides") and sprite.collides:
                if sprite.rect.colliderect(character.rect):
                    # If the character touches a death box, kill it
                    if hasattr(sprite, "kills") and sprite.kills:
                        if character is self.player:
                            character.kill()
                            print("Player was killed")
                    else:
                        if character.direction.x < 0:
                            character.rect.left = sprite.rect.right
                            character.collisions.add(Collisions.LEFT)
                            self.current_x = sprite.rect.left

                        elif character.direction.x > 0:
                            character.rect.right = sprite.rect.left
                            character.collisions.add(Collisions.RIGHT)
                            self.current_x = sprite.rect.right

        # If the character collides with a coin, collect it
        if (Collisions.LEFT in character.collisions) and (
            character.rect.left < self.current_x or character.direction.x >= 0
        ):
            character.collisions.remove(Collisions.LEFT)
        if (Collisions.RIGHT in character.collisions) and (
            character.rect.right > self.current_x or character.direction.x <= 0
        ):
            character.collisions.remove(Collisions.RIGHT)

    def vertical_movement_collision(self) -> None:
        """
        Handle character collisions

        :return: None
        """
        player: Player = self.player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if hasattr(sprite, "collides") and sprite.collides:
                if sprite.rect.colliderect(player.rect):
                    if hasattr(sprite, "kills") and sprite.kills:
                        player.kill()
                        raise GameOver(" < GAME OVER > ")
                    else:
                        if player.direction.y > 0:
                            player.rect.bottom = sprite.rect.top
                            player.direction.y = 0
                            player.collisions.add(Collisions.BOTTOM)
                        elif player.direction.y < 0:
                            player.rect.top = sprite.rect.bottom
                            player.direction.y = 0
                            player.collisions.add(Collisions.TOP)
            if hasattr(sprite, "collectable") and sprite.collectable:
                if sprite.rect.colliderect(player.rect):
                    sprite.kill()
                    player.score += 1

        if (Collisions.BOTTOM in player.collisions) and (
            player.direction.y < 0 or player.direction.y > 1
        ):
            player.collisions.remove(Collisions.BOTTOM)
        if Collisions.TOP in player.collisions and player.direction.y > 0.1:
            player.collisions.remove(Collisions.TOP)

    def update_db(self) -> None:
        """
        Get the current save and save it to the database
        :return: None
        """
        db.set(self.get_save.name, self.get_save.to_json())
        print("Saved to database")

    async def save_to_api(self) -> None:
        """
        Get the current save and save it to the API

        :return: None
        """
        # WARNING: This function takes some time, should be rewritten to be more efficient
        request = requests.post(
            url="http://localhost:8000/save", json=self.get_save.to_json()
        )
        print(request.status_code)

        if request.status_code == 200:
            print("Saved")
        else:
            print("Error")

    @property
    def get_save(self) -> Save:
        """
        Current save

        :return: The current save object
        """
        return Save(
            name="Player 1",
            score=self.player.sprite.score,
            level=0,
            map=self.level_data,
            created_at="today",
        )

    async def run(self) -> None:
        """
        Run the level

        :return: None
        """
        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # level tiles
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.handle_horizontal_movement()

        # player
        self.player.update()
        self.horizontal_movement_collision(self.player.sprite)

        for enemy in self.enemies:
            self.horizontal_movement_collision(enemy.sprite)

        # self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        self.player.draw(self.display_surface)

        self.display_enemies()

        keys = pygame.key.get_pressed()

        # Press QUIT to exit the game
        if keys[pygame.K_ESCAPE]:
            raise GameOver(" < GAME OVER > ")
        # Press S to save
        if keys[pygame.K_s]:
            await self.save()
