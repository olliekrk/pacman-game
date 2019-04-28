import abc
from enum import Enum

import pygame


class Directions(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

    @staticmethod
    def opposite_direction(direction):
        if direction == Directions.LEFT:
            return Directions.RIGHT
        elif direction == Directions.RIGHT:
            return Directions.LEFT
        elif direction == Directions.UP:
            return Directions.DOWN
        elif direction == Directions.DOWN:
            return Directions.UP


class Character(pygame.sprite.DirtySprite):
    TILES_CHANGE_SPEED = 0.010
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
        self.direction = Directions.UP
        self.is_running = True
        self.speed = 130

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
                self.position[0] + (tile_switch[0] * self.speed * dt), \
                self.position[1] + (tile_switch[1] * self.speed * dt)
        else:
            self.is_running = False

        self.position_tile = self.position[0] // self.board.tile_size, self.position[1] // self.board.tile_size

    def update(self, dt, *args):
        self.dirty = 1  # it is always dirty
        self.set_rect()
        self.set_image()
        self.move(dt)

    @abc.abstractmethod
    def set_rect(self):
        """Sets up the area occupied by this character"""

    @abc.abstractmethod
    def set_image(self):
        """Method that sets 'image' field using character's textures"""


class Pacman(Character):
    def __init__(self, board, *groups):
        super().__init__(board, *groups)
        self.image = pygame.Surface((board.tile_size, board.tile_size))
        self.image.fill((0, 255, 0))

    def set_rect(self):
        self.rect = pygame.Rect(self.position[0] - self.character_width / 2,
                                self.position[1] - self.character_height / 2,
                                self.character_width,
                                self.character_height)

    # TODO: add Pacman textures
    def set_image(self):
        pass
