import abc
from enum import Enum

import pygame
from math import floor


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
    TELEPORT_TIME_GAP = 1000
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
        self.speed = 130

        # movement-related features
        self.position_tile = board.board_layout.spawn
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)
        self.direction = Directions.UP
        self.is_running = True

        # textures related attributes
        self.texture = None
        self.texture_size = None
        self.run_length = None
        self.idle_length = None
        self.idle_textures = None
        self.run_textures = None

        # dirty sprite features
        self.dirty = 1
        self.rect = None
        self.image = None

        # necessary to perform teleports
        self.last_teleport_time = pygame.time.get_ticks()

    def safe_to_change_direction(self):
        margin = self.board.tile_size / 15
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

    def tile_accessible(self, next_tile):
        regular_tile = next_tile in self.board.board_layout.accessible

        ghost_house_tile = self.position_tile in self.board.board_layout.ghost_path and next_tile in self.board.board_layout.ghost_path

        tunnel_tile = False
        for (start, end) in self.board.board_layout.tunnels:
            tunnel_tile = next_tile == start or next_tile == end

        return regular_tile or tunnel_tile or ghost_house_tile

    def change_direction(self, new_direction):
        tile_switch = Character.DIRECTION_SWITCH_MAP.get(new_direction)
        next_tile = self.position_tile[0] + tile_switch[0], self.position_tile[1] + tile_switch[1]
        if self.tile_accessible(next_tile) and self.safe_to_change_direction():
            self.is_running = True
            self.direction = new_direction

    def move(self, dt):

        # using tunnels on boards
        target_tile = self.board.teleport_available(self.position_tile)
        if target_tile is not None:
            self.teleport_character(target_tile)
            self.is_running = True

        if not self.is_running:
            return

        tile_switch = Character.DIRECTION_SWITCH_MAP.get(self.direction)
        next_tile = self.position_tile[0] + tile_switch[0], self.position_tile[1] + tile_switch[1]

        if self.tile_accessible(next_tile) or self.safe_to_reach_center():
            self.position = \
                self.position[0] + (tile_switch[0] * self.speed * dt), \
                self.position[1] + (tile_switch[1] * self.speed * dt)
            self.position_tile = self.position[0] // self.board.tile_size, self.position[1] // self.board.tile_size

        else:
            self.is_running = False

    def teleport_character(self, target_tile):
            time = pygame.time.get_ticks()
            if abs(time - self.last_teleport_time) > Character.TELEPORT_TIME_GAP:
                self.last_teleport_time = time
                self.position_tile = target_tile
                self.position = (target_tile[0] + 0.5) * self.board.tile_size, (target_tile[1] + 0.5) * self.board.tile_size

    def update(self, dt, *args):
        self.dirty = 1  # it is always dirty
        self.set_rect()
        self.set_image()
        self.move(dt)

    @abc.abstractmethod
    def load_tile(self, number_of_tile):
        """Loads the tile from given texture source"""

    def load_tile_scaled(self, tile_number):
        """Loads the tile from given texture source, respecting character's width and height"""
        return pygame.transform.scale(self.load_tile(tile_number), (self.character_width, self.character_height))

    def set_rect(self):
        """Sets up the area occupied by this character"""
        self.rect = pygame.Rect(self.position[0] - self.character_width / 2,
                                self.position[1] - self.character_height / 2,
                                self.character_width,
                                self.character_height)

    def set_image(self):
        """Method that sets 'image' field using character's textures"""
        if self.is_running:
            image_index = int(floor(pygame.time.get_ticks() * Character.TILES_CHANGE_SPEED) % self.run_length)
            self.image = self.run_textures[image_index]
        else:
            image_index = int(floor(pygame.time.get_ticks() * Character.TILES_CHANGE_SPEED) % self.idle_length)
            self.image = self.idle_textures[image_index]

        if self.direction in [Directions.LEFT, Directions.UP]:
            self.image = pygame.transform.flip(self.image, True, False)


class Pacman(Character):
    TEXTURES_ROW = TEXTURES_COLUMN = 10

    def __init__(self, board, *groups):
        super().__init__(board, *groups)

        # textures related attributes
        self.texture = pygame.image.load('./sheets/Dwarf Sprite Sheet.png')
        self.texture_size = 32
        self.run_length = 8
        self.idle_length = 5
        self.idle_textures = [self.load_tile_scaled(i) for i in range(0, 5)]
        self.run_textures = [self.load_tile_scaled(i) for i in range(10, 18)]

    def load_tile(self, number_of_tile):
        row = floor(number_of_tile / Pacman.TEXTURES_ROW)
        column = number_of_tile % Pacman.TEXTURES_COLUMN
        crop_left_px = column * self.texture_size
        crop_up_px = row * self.texture_size
        return self.texture.subsurface(crop_left_px, crop_up_px,
                                       self.texture_size, self.texture_size)
