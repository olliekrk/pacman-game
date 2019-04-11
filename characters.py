import pygame
from board import Board
from enum import Enum
from math import floor
import game


class Directions(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


values = [(0, 0), (1, 0), (-1, 0), (0, -1), (0, 1)]
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class Character(pygame.sprite.DirtySprite):
    WALK_SPEED = 80

    def __init__(self, board, *groups):
        self.board = board

        # position_tile is a tile on which currently is the center of character
        self.position_tile = board.board_layout.spawn
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)
        self.direction = Directions.LEFT
        self.moving = False
        super().__init__(*groups)

    def is_in_center(self):
        tile = self.position_tile
        center = (tile[0] + 0.5) * self.board.tile_size, (tile[1] + 0.5) * self.board.tile_size
        margin = 0.8
        return abs(center[0] - self.position[0]) < margin and abs(center[1] - self.position[1]) < margin

    def turn_left(self):
        next_tile = self.position_tile[0] - 1, self.position_tile[1]
        next_tile_accessible = next_tile in self.board.board_layout.accessible
        if next_tile_accessible and self.is_in_center():
            self.moving = True
            self.direction = Directions.LEFT

    def turn_right(self):
        next_tile = self.position_tile[0] + 1, self.position_tile[1]
        next_tile_accessible = next_tile in self.board.board_layout.accessible
        if next_tile_accessible and self.is_in_center():
            self.moving = True
            self.direction = Directions.RIGHT

    def turn_up(self):
        next_tile = self.position_tile[0], self.position_tile[1] - 1
        next_tile_accessible = next_tile in self.board.board_layout.accessible
        if next_tile_accessible and self.is_in_center():
            self.moving = True
            self.direction = Directions.UP

    def turn_down(self):
        next_tile = self.position_tile[0], self.position_tile[1] + 1
        next_tile_accessible = next_tile in self.board.board_layout.accessible
        if next_tile_accessible and self.is_in_center():
            self.moving = True
            self.direction = Directions.DOWN

    def move(self, dt):
        # todo make this code more consistent
        if self.moving:
            if self.direction == Directions.LEFT:
                next_tile = self.position_tile[0] - 1, self.position_tile[1]
                next_accessible = next_tile in self.board.board_layout.accessible
                center_safe = self.position[0] > (self.position_tile[0] + 0.5) * self.board.tile_size
                if next_accessible or center_safe:
                    self.position = self.position[0] - Character.WALK_SPEED * dt, self.position[1]
                else:
                    self.moving = False

            elif self.direction == Directions.RIGHT:
                next_tile = self.position_tile[0] + 1, self.position_tile[1]
                next_accessible = next_tile in self.board.board_layout.accessible
                center_safe = self.position[0] < (self.position_tile[0] + 0.5) * self.board.tile_size
                if next_accessible or center_safe:
                    self.position = self.position[0] + Character.WALK_SPEED * dt, self.position[1]
                else:
                    self.moving = False

            elif self.direction == Directions.UP:
                next_tile = self.position_tile[0], self.position_tile[1] - 1
                next_accessible = next_tile in self.board.board_layout.accessible
                center_safe = self.position[1] > (self.position_tile[1] + 0.5) * self.board.tile_size
                if next_accessible or center_safe:
                    self.position = self.position[0], self.position[1] - Character.WALK_SPEED * dt
                else:
                    self.moving = False

            elif self.direction == Directions.DOWN:
                next_tile = self.position_tile[0], self.position_tile[1] + 1
                next_accessible = next_tile in self.board.board_layout.accessible
                center_safe = self.position[1] < (self.position_tile[1] + 0.5) * self.board.tile_size
                if next_accessible or center_safe:
                    self.position = self.position[0], self.position[1] + Character.WALK_SPEED * dt
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
        self.current_texture = 0
        self.direction = Directions.UP
        self.moving = True
        self.position_tile = board.board_layout.ghost_house.get(color)
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)

        texture_name = './sheets/DinoSprites - ' + color.name + '.png'
        self.texture = pygame.image.load(texture_name)
        self.idle_textures = [self.get_tile_scaled(i) for i in range(0, 4)]
        self.run_textures = [self.get_tile_scaled(i) for i in range(5, 11)]

    def get_tile(self, tile_number):
        tile_number %= self.width;
        num_of_element = tile_number * self.width
        return self.texture.subsurface(num_of_element, 0, self.width, self.width)

    def get_tile_scaled(self, tile_number):
        return pygame.transform.scale(self.get_tile(tile_number), (self.board.tile_size * 2, self.board.tile_size * 2))

    def draw(self, game_screen):
        index = int((floor(pygame.time.get_ticks() * Ghost.TILES_CHANGE_SPEED) % 6))

        game_screen.blit(self.run_textures[index],
                         (self.position[0] - self.board.tile_size, self.position[1] - self.board.tile_size))
