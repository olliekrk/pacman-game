import pygame
from board import Board
from enum import Enum


class Directions(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


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
