import abc
import pygame
from math import floor
from enum import Enum


class Directions(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class Character(pygame.sprite.DirtySprite):
    WALK_SPEED = 100
    TILES_CHANGE_SPEED = 0.015
    DIRECTION_SWITCH_MAP = {
        Directions.LEFT: (-1, 0),
        Directions.RIGHT: (1, 0),
        Directions.UP: (0, -1),
        Directions.DOWN: (0, 1)
    }

    def __init__(self, board, *groups):
        super().__init__(*groups)

        # general attributes
        self.board = board
        self.character_width = board.tile_size
        self.character_height = board.tile_size

        # movement-related features
        self.position_tile = board.board_layout.spawn
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)
        self.direction = Directions.LEFT
        self.is_running = True

        # dirty sprite features
        self.dirty = 1
        self.rect = None
        self.image = None

    def safe_to_change_direction(self):
        margin = self.board.tile_size / 20
        center_x = (self.position_tile[0] + 0.5) * self.board.tile_size
        center_y = (self.position_tile[1] + 0.5) * self.board.tile_size
        return abs(center_x - self.position[0]) < margin and abs(center_y - self.position[1]) < margin

    def safe_to_reach_center(self):
        center_x = (self.position_tile[0] + 0.5) * self.board.tile_size
        center_y = (self.position_tile[1] + 0.5) * self.board.tile_size
        if self.direction == Directions.LEFT:
            return self.position[0] > center_x
        if self.direction == Directions.RIGHT:
            return self.position[0] < center_x
        if self.direction == Directions.UP:
            return self.position[1] > center_y
        if self.direction == Directions.DOWN:
            return self.position[1] < center_y

    def change_direction(self, new_direction):
        tile_switch = Character.DIRECTION_SWITCH_MAP.get(new_direction)
        next_tile = self.position_tile[0] + tile_switch[0], self.position_tile[1] + tile_switch[1]
        next_tile_accessible = next_tile in self.board.board_layout.accessible
        if next_tile_accessible and self.safe_to_change_direction():
            self.is_running = True
            self.direction = new_direction

    def move(self, dt):
        if not self.is_running:
            return

        tile_switch = Character.DIRECTION_SWITCH_MAP.get(self.direction)
        next_tile = self.position_tile[0] + tile_switch[0], self.position_tile[1] + tile_switch[1]
        next_tile_accessible = next_tile in self.board.board_layout.accessible

        if next_tile_accessible or self.safe_to_reach_center():
            self.position = \
                self.position[0] + (tile_switch[0] * Character.WALK_SPEED * dt), \
                self.position[1] + (tile_switch[1] * Character.WALK_SPEED * dt)
        else:
            self.is_running = False

        self.position_tile = self.position[0] // self.board.tile_size, self.position[1] // self.board.tile_size

    def update(self, *args):
        self.dirty = 1  # it is always dirty
        self.set_rect()
        self.set_image()

    def set_rect(self):
        self.rect = pygame.Rect(self.position[0] - self.character_width / 2,
                                self.position[1] - self.character_height / 2,
                                self.character_width,
                                self.character_height)

    @abc.abstractmethod
    def set_image(self):
        """Method that sets 'image' field using character's textures"""


class Pacman(Character):
    def __init__(self, board, *groups):
        super().__init__(board, *groups)
        self.image = pygame.Surface((board.tile_size, board.tile_size))
        self.image.fill(YELLOW)

    # TODO: add Pacman textures
    def set_image(self):
        pass

    def draw(self, game_screen):
        pygame.draw.rect(game_screen, RED,
                         pygame.Rect(self.position_tile[0] * self.board.tile_size,
                                     self.position_tile[1] * self.board.tile_size,
                                     self.board.tile_size,
                                     self.board.tile_size), 1)
        pygame.draw.circle(game_screen, YELLOW,
                           (round(self.position[0]), round(self.position[1])), 10)


class Ghost(Character):
    TEXTURE_SIZE = 24
    RUN_LENGTH = 7
    IDLE_LENGTH = 4

    def __init__(self, board, color, *groups):
        super().__init__(board, *groups)

        # general attributes
        self.color = color
        self.character_width = board.tile_size * 2
        self.character_height = board.tile_size * 2

        # movement-related features
        self.position_tile = board.board_layout.ghost_house.get(color)
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)

        # rendering related features
        texture_name = './sheets/DinoSprites - ' + color.name + '.png'
        self.texture = pygame.image.load(texture_name)
        self.idle_textures = [self.load_tile_scaled(i) for i in range(0, 4)]
        self.run_textures = [self.load_tile_scaled(i) for i in range(4, 11)]

    def load_tile(self, number_of_tile):
        number_of_tile %= Ghost.TEXTURE_SIZE
        tile_location_px = number_of_tile * Ghost.TEXTURE_SIZE
        return self.texture.subsurface(tile_location_px, 0, Ghost.TEXTURE_SIZE, Ghost.TEXTURE_SIZE)

    def load_tile_scaled(self, tile_number):
        return pygame.transform.scale(self.load_tile(tile_number), (self.character_width, self.character_height))

    def set_image(self):
        if self.is_running:
            image_index = int(floor(pygame.time.get_ticks() * Character.TILES_CHANGE_SPEED) % Ghost.RUN_LENGTH)
            self.image = self.run_textures[image_index]
        else:
            image_index = int(floor(pygame.time.get_ticks() * Character.TILES_CHANGE_SPEED) % Ghost.IDLE_LENGTH)
            self.image = self.idle_textures[image_index]

    # blue ghost "Inky" needs both pacman and Blinky position
    # TODO: set new target tile
    def update(self, dt, pacman_position, blinky_position, *args):
        super().update()

    def draw(self, game_screen):
        index = int((floor(pygame.time.get_ticks() * Character.TILES_CHANGE_SPEED) % 7))

        game_screen.blit(self.run_textures[index],
                         (self.position[0] - self.board.tile_size, self.position[1] - self.board.tile_size))
