import pygame
import board
import characters
from characters import Directions
from enum import Enum


class GhostNames(Enum):
    inky = 1
    pinky = 2
    blinky = 3
    clyde = 4


class Game(object):
    MAX_LIFE = 3
    FPS_LIMIT = 90
    TICKS_PER_SEC = 1000

    def __init__(self, game_screen, game_clock, tile_size):
        self.ghosts_group = pygame.sprite.LayeredDirty()
        self.alive_group = pygame.sprite.LayeredDirty()
        self.board = board.Board(tile_size, game_screen, board.ClassicLayout())
        self.game_screen = game_screen
        self.game_clock = game_clock
        self.finished = False
        self.player = characters.Pacman(self.board, self.alive_group)
        self.monsters = {
            GhostNames.inky: characters.Ghost(self.board, GhostNames.inky, self.alive_group, self.ghosts_group),
            GhostNames.pinky: characters.Ghost(self.board, GhostNames.pinky, self.alive_group, self.ghosts_group),
            GhostNames.blinky: characters.Ghost(self.board, GhostNames.blinky, self.alive_group, self.ghosts_group),
            GhostNames.clyde: characters.Ghost(self.board, GhostNames.clyde, self.alive_group, self.ghosts_group)
        }

    def main_loop(self):
        while not self.finished:
            dt = self.game_clock.tick(Game.FPS_LIMIT) / Game.TICKS_PER_SEC
            self.events_loop()
            self.update_pacman_position(dt)
            # self.update_ghosts_position(dt)
            self.draw_board()
            self.draw_sprites()
            pygame.display.flip()  # todo change flip to DirtySprites update

    def events_loop(self):
        # maintaining events like mouse/button clicks etc
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.finished = True

    def draw_board(self):
        self.board.draw_onto_screen()

    def draw_sprites(self):
        # drawing every alive character
        self.player.draw(self.game_screen)
        for ghost in self.monsters.values():
            ghost.draw(self.game_screen)

    def update_pacman_position(self, dt):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_RIGHT]:
            self.player.change_direction(Directions.RIGHT)
        elif keys_pressed[pygame.K_LEFT]:
            self.player.change_direction(Directions.LEFT)
        elif keys_pressed[pygame.K_UP]:
            self.player.change_direction(Directions.UP)
        elif keys_pressed[pygame.K_DOWN]:
            self.player.change_direction(Directions.DOWN)

        self.player.move(dt)
