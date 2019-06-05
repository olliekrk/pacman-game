import pygame
import pygameMenu
from pygameMenu.locals import *
from ghosts import GhostNames

MENU_BACKGROUND_COLOR = (255, 255, 26)
COLOR_GREY = (107, 102, 97)
COLOR_BLACK = (0, 0, 0)
COLOR_SELECTED = (255, 153, 0)
BOARD_SIZE = (28, 36)  # 28 x 36 tiles is the original size of board
TILE_SIZE = 25  # pixels
SCREEN_RESOLUTION = (TILE_SIZE * BOARD_SIZE[0], TILE_SIZE * BOARD_SIZE[1])


class GameMenus(object):

    def __init__(self, game):
        # BACKGROUND TEXTURES
        self.game = game
        self.game_screen = self.game.game_screen
        self.pacman_texture = game.player.load_tile(game.player.texture, 10)
        self.pacman_texture = pygame.transform.scale(self.pacman_texture, (80, 80))
        self.ghost1_texture = game.monsters.get(GhostNames.blinky).load_tile(game.monsters.get(GhostNames.blinky).texture, 9)
        self.ghost1_texture = pygame.transform.scale(self.ghost1_texture, (80, 80))
        self.ghost2_texture = game.monsters.get(GhostNames.inky).load_tile(game.monsters.get(GhostNames.inky).texture, 16)
        self.ghost2_texture = pygame.transform.scale(self.ghost2_texture, (80, 80))
        self.ghost3_texture = game.monsters.get(GhostNames.pinky).load_tile(game.monsters.get(GhostNames.pinky).texture, 8)
        self.ghost3_texture = pygame.transform.scale(self.ghost3_texture, (80, 80))
        self.ghost3_texture = pygame.transform.flip(self.ghost3_texture, True, False)
        self.ghost4_texture = game.monsters.get(GhostNames.clyde).load_tile(game.monsters.get(GhostNames.clyde).texture, 6)
        self.ghost4_texture = pygame.transform.scale(self.ghost4_texture, (80, 80))
        self.ghost4_texture = pygame.transform.flip(self.ghost4_texture, True, False)

        # MAIN MENU
        self.main_menu = self.create_menu('Pacman', self.main_background, 100)
        self.main_menu.add_option('Play', self.run_game)
        self.main_menu.add_option('Quit', PYGAME_MENU_EXIT)

        # PAUSE MENU
        self.pause_menu = self.create_menu('Pause', self.empty_function, 2)
        self.pause_menu.add_option('Resume', self.resume_game)
        self.pause_menu.add_option('Quit', PYGAME_MENU_EXIT)
        self.pause_menu.disable()

        # GAME OVER MENU
        self.game_over_menu = self.create_menu('Game over', self.empty_function, 2)
        self.game_over_menu.add_option('New Game', self.new_game)
        self.game_over_menu.add_option('Quit', PYGAME_MENU_EXIT)
        self.game_over_menu.disable()

        # LEVEL COMPLETED MENU
        self.level_completed_menu = self.create_menu('Level completed', self.main_background, 100)
        self.level_completed_menu.add_option('Next LeveL', self.next_level)
        self.level_completed_menu.add_option('Quit', PYGAME_MENU_EXIT)
        self.level_completed_menu.disable()

    def run_game(self):
        self.main_menu.disable()
        self.game.main_loop()

    def new_game(self):
        self.game_over_menu.disable()
        self.game.advance_to_next_level()
        self.game.pause = False
        self.game.first_after_pause = True
        self.game.status.reset()
        self.game.main_loop()

    def next_level(self):
        self.level_completed_menu.disable()
        self.game.advance_to_next_level()
        self.game.pause = False
        self.game.first_after_pause = True
        self.game.main_loop()

    def pause_game(self):
        self.game.pause = True
        self.game.pause_start_ticks = pygame.time.get_ticks()
        self.pause_menu.enable()

    def resume_game(self):
        self.pause_menu.disable()
        self.game.pause = False
        self.game.pause_end_ticks = pygame.time.get_ticks()
        self.game.first_after_pause = True
        self.game.main_loop()

    def main_background(self):
        self.game_screen.fill(COLOR_BLACK)
        pygame.draw.rect(self.game_screen, COLOR_GREY, (0, 83, SCREEN_RESOLUTION[0], 10))
        pygame.draw.rect(self.game_screen, COLOR_GREY, (0, 850, SCREEN_RESOLUTION[0], 10))
        for i in range(6):
            pygame.draw.rect(self.game_screen, MENU_BACKGROUND_COLOR, (300 + (i * 80), 50, 10, 10))
        for i in range(14):
            pygame.draw.rect(self.game_screen, MENU_BACKGROUND_COLOR, (10 + (i * 80), 817, 10, 10))
        self.game_screen.blit(self.ghost2_texture, (20, 13))
        self.game_screen.blit(self.ghost1_texture, (100, 13))
        self.game_screen.blit(self.pacman_texture, (200, 8))
        self.game_screen.blit(self.ghost3_texture, (550, 13))
        self.game_screen.blit(self.ghost4_texture, (350, 780))

    def empty_function(self):
        return

    def create_menu(self, title, bgfun, alpha):
        return pygameMenu.Menu(surface=self.game_screen, bgfun=bgfun, color_selected=COLOR_SELECTED,
                               font=pygameMenu.fonts.FONT_BEBAS,
                               font_color=COLOR_BLACK, font_size=40, menu_alpha=alpha,
                               menu_color=MENU_BACKGROUND_COLOR,
                               menu_color_title=COLOR_SELECTED, menu_height=int(SCREEN_RESOLUTION[1] * 0.6),
                               menu_width=int(SCREEN_RESOLUTION[0] * 0.6), onclose=PYGAME_MENU_DISABLE_CLOSE,
                               option_shadow=False, title=title, window_height=SCREEN_RESOLUTION[1],
                               window_width=SCREEN_RESOLUTION[0], draw_select=False)
