import os
import pygame
import game
from information_panel import InformationPanel
from game_menus import GameMenus

TITLE = "Pacman WIEiT Edition"
ICON_TITLE = "Pacman SE"

BOARD_SIZE = (28, 36)  # 28 x 36 tiles is the original size of board
TILE_SIZE = 25  # pixels
SCREEN_RESOLUTION = (TILE_SIZE * BOARD_SIZE[0], TILE_SIZE * BOARD_SIZE[1])


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # displays the window in the center

    pygame.init()
    pygame.display.set_caption(TITLE, ICON_TITLE)
    game_screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    game_clock = pygame.time.Clock()

    game = game.Game(game_screen, game_clock, TILE_SIZE)
    information_panel = InformationPanel(game)
    game.add_information_panel(information_panel)

    menus = GameMenus(game)
    game.add_menus(menus)

    # Main loop
    while True:
        events = pygame.event.get()
        menus.main_menu.mainloop(events)
        pygame.display.flip()
