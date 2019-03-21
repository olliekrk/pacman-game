import pygame

import board


class Game(object):
    MAX_LIFE = 3
    FPS_LIMIT = 90
    TICKS_PER_SEC = 1000

    def __init__(self, game_screen, game_clock, tile_size):
        self.board = board.Board(tile_size)
        self.game_screen = game_screen
        self.game_clock = game_clock
        self.finished = False

    def main_loop(self):
        self.draw_board()
        while not self.finished:
            dt = self.game_clock.tick(Game.FPS_LIMIT) / Game.TICKS_PER_SEC
            self.events_loop()
            self.draw_sprites(dt)

    def events_loop(self):
        # maintaining events like mouse/button clicks etc
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.finished = True

    def draw_board(self):
        self.board.draw_onto_screen(self.game_screen)
        pass

    def draw_sprites(self, dt):
        # drawing every alive character
        pass
