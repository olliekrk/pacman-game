import random

import board
import characters
from ghosts import *


class Game(object):
    MAX_LIFE = 3
    FPS_LIMIT = 90
    TICKS_PER_SEC = 1000.0

    def __init__(self, game_screen, game_clock, tile_size):
        self.ghosts_group = pygame.sprite.LayeredDirty()
        self.alive_group = pygame.sprite.LayeredDirty()

        self.finished = False
        self.game_screen = game_screen
        self.game_clock = game_clock
        self.board = board.Board(tile_size, game_screen, board.ClassicLayout())

        self.player = characters.Pacman(self.board, self.alive_group)
        self.monsters = {
            GhostNames.inky: Ghost(self.board, GhostNames.inky, self.alive_group, self.ghosts_group),
            GhostNames.pinky: Ghost(self.board, GhostNames.pinky, self.alive_group, self.ghosts_group),
            GhostNames.blinky: Blinky(self.board, self.alive_group, self.ghosts_group),
            GhostNames.clyde: Ghost(self.board, GhostNames.clyde, self.alive_group, self.ghosts_group)
        }

    def main_loop(self):
        self.alive_group.clear(self.game_screen, self.board.background)
        while not self.finished:
            dt = self.game_clock.tick(Game.FPS_LIMIT) / Game.TICKS_PER_SEC
            self.events_loop()
            self.update_pacman_direction()
            self.update_sprites(dt)

    # maintaining events like mouse/button clicks etc
    def events_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.finished = True

    def draw_board(self):
        self.board.draw_onto_screen()

    # updating and drawing every alive character
    def update_sprites(self, dt):
        self.alive_group.update(dt, self.player.position_tile, self.monsters.get(GhostNames.blinky).position_tile)
        dirty_rectangles = self.alive_group.draw(self.game_screen)
        pygame.display.update(dirty_rectangles)

    def update_pacman_direction(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_RIGHT]:
            self.player.change_direction(Directions.RIGHT)
        elif keys_pressed[pygame.K_LEFT]:
            self.player.change_direction(Directions.LEFT)
        elif keys_pressed[pygame.K_UP]:
            self.player.change_direction(Directions.UP)
        elif keys_pressed[pygame.K_DOWN]:
            self.player.change_direction(Directions.DOWN)

    # todo: implement ghosts movement algorithms
    def update_ghosts_position(self, dt):
        for key, value in self.monsters.items():
            if not value.is_running:
                new_direction = random.randint(0, 3)
                if new_direction == 0:
                    value.change_direction(Directions.LEFT)
                if new_direction == 1:
                    value.change_direction(Directions.RIGHT)
                if new_direction == 2:
                    value.change_direction(Directions.UP)
                if new_direction == 3:
                    value.change_direction(Directions.DOWN)
