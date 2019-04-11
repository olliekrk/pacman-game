from enum import Enum

import pygame
from math import floor


class Directions(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class Character(pygame.sprite.DirtySprite):
    WALK_SPEED = 100
    DIRECTION_SWITCHER = {
        Directions.LEFT: (-1, 0),
        Directions.RIGHT: (1, 0),
        Directions.UP: (0, -1),
        Directions.DOWN: (0, 1)
    }

    def __init__(self, board, *groups):
        self.board = board
        # position_tile is a tile on which currently is the center of character
        self.position_tile = board.board_layout.spawn
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)
        self.direction = Directions.LEFT
        self.moving = False
        super().__init__(*groups)

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
        tile_switch = Character.DIRECTION_SWITCHER.get(new_direction)
        next_tile = self.position_tile[0] + tile_switch[0], self.position_tile[1] + tile_switch[1]
        next_tile_accessible = next_tile in self.board.board_layout.accessible
        if next_tile_accessible and self.safe_to_change_direction():
            self.moving = True
            self.direction = new_direction

    def move(self, dt):
        if not self.moving:
            return

        tile_switch = Character.DIRECTION_SWITCHER.get(self.direction)
        next_tile = self.position_tile[0] + tile_switch[0], self.position_tile[1] + tile_switch[1]
        next_tile_accessible = next_tile in self.board.board_layout.accessible

        if next_tile_accessible or self.safe_to_reach_center():
            self.position = \
                self.position[0] + (tile_switch[0] * Character.WALK_SPEED * dt), \
                self.position[1] + (tile_switch[1] * Character.WALK_SPEED * dt)
        else:
            self.moving = False

        self.position_tile = self.position[0] // self.board.tile_size, self.position[1] // self.board.tile_size


class Pacman(Character):
    def __init__(self, board, *groups):
        super().__init__(board, *groups)

    def draw(self, game_screen):
        # todo add pacman textures
        pygame.draw.rect(game_screen, RED,
                         pygame.Rect(self.position_tile[0] * self.board.tile_size,
                                     self.position_tile[1] * self.board.tile_size,
                                     self.board.tile_size,
                                     self.board.tile_size), 1)
        pygame.draw.circle(game_screen, YELLOW,
                           (round(self.position[0]), round(self.position[1])), 10)


class Ghost(Character):
    TILES_CHANGE_SPEED = 0.015

    def __init__(self, board, color, *groups):
        super().__init__(board, *groups)
        self.width = 24
        self.direction = Directions.UP
        self.moving = True
        self.current_texture = 0
        self.position_tile = board.board_layout.ghost_house.get(color)
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)

        texture_name = './sheets/DinoSprites - ' + color.name + '.png'
        self.texture = pygame.image.load(texture_name)
        self.idle_textures = [self.get_tile_scaled(i) for i in range(0, 4)]
        self.run_textures = [self.get_tile_scaled(i) for i in range(4, 11)]

    def get_tile(self, tile_number):
        tile_number %= self.width

        num_of_element = tile_number * self.width

        return self.texture.subsurface(num_of_element, 0, self.width, self.width)

    def get_tile_scaled(self, tile_number):
        return pygame.transform.scale(self.get_tile(tile_number), (self.board.tile_size * 2, self.board.tile_size * 2))

    def draw(self, game_screen):
        index = int((floor(pygame.time.get_ticks() * Ghost.TILES_CHANGE_SPEED) % 7))

        game_screen.blit(self.run_textures[index],
                         (self.position[0] - self.board.tile_size, self.position[1] - self.board.tile_size))
