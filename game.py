import board
import characters
from ghosts import *
import os
import pygame
import pygameMenu
from pygameMenu.locals import *

TITLE = "Pacman WIEiT Edition"
ICON_TITLE = "Pacman SE"

BOARD_SIZE = (28, 36)  # 28 x 36 tiles is the original size of board
TILE_SIZE = 18  # pixels
SCREEN_RESOLUTION = (TILE_SIZE * BOARD_SIZE[0], TILE_SIZE * BOARD_SIZE[1])

MENU_BACKGROUND_COLOR = (255, 255, 26)
COLOR_BACKGROUND = (107, 102, 97)
COLOR_BLACK = (0, 0, 0)
COLOR_SELECTED = (255, 153, 0)


class GameStatus(object):
    MAX_LIVES = 3
    DOT_POINTS = 10
    BIG_DOT_POINTS = 100
    GHOST_EATEN_POINTS = 200
    KILLING_DURATION = 5
    KILLING_BONUS_DURATION = 2

    def __init__(self):
        self.level_number = 1
        self.player_points = 0
        self.player_lives = GameStatus.MAX_LIVES
        self.killing_activated_time = None
        self.last_kill_time = None
        self.bonus_multiplier = 0

    def add_dot_points(self, dots_no, big_dots_no=0):
        self.player_points += (dots_no * GameStatus.DOT_POINTS) + (big_dots_no * GameStatus.BIG_DOT_POINTS)

    def add_ghost_kill_points(self, no_ghosts_killed):
        while no_ghosts_killed > 0:
            time = pygame.time.get_ticks()

            if self.last_kill_time is not None and \
                    abs(time - self.last_kill_time) / 1000 < GameStatus.KILLING_BONUS_DURATION:
                self.bonus_multiplier += 1
            else:
                self.bonus_multiplier = 1

            # add 0.5s (500 ms) to killing time
            self.killing_activated_time += 500
            self.last_kill_time = time
            no_ghosts_killed -= 1

            self.player_points += GameStatus.GHOST_EATEN_POINTS * self.bonus_multiplier

    def game_over(self):
        # when player has no lives left
        print("todo: GAME OVER SCREEN")
        pass

    def level_finished(self):
        # when all the dots are eaten
        print("todo: LEVEL FINISHED SCREEN")

        # advance to next level
        self.level_number += 1
        self.killing_activated_time = None
        self.last_kill_time = None


class Game(object):
    FPS_LIMIT = 90
    TICKS_PER_SEC = 1000.0

    def __init__(self, game_screen, game_clock, tile_size):
        self.finished = False
        self.game_screen = game_screen
        self.game_clock = game_clock
        self.board = board.Board(tile_size, game_screen, board.ClassicLayout())
        self.status = GameStatus()
        self.pause = False

        self.ghosts_group = pygame.sprite.LayeredDirty()
        self.alive_group = pygame.sprite.LayeredDirty()
        self.dots_group = self.board.prepare_dots()
        self.big_dots_group = self.board.prepare_big_dots()

        self.player = characters.Pacman(self.board, self.alive_group)
        self.monsters = {
            GhostNames.inky: Inky(self.board, self.alive_group, self.ghosts_group),
            GhostNames.pinky: Pinky(self.board, self.alive_group, self.ghosts_group),
            GhostNames.blinky: Blinky(self.board, self.alive_group, self.ghosts_group),
            GhostNames.clyde: Clyde(self.board, self.alive_group, self.ghosts_group)
        }

    # game loop
    def main_loop(self):
        self.alive_group.clear(self.game_screen, self.board.background)
        self.dots_group.clear(self.game_screen, self.board.background)
        while not self.finished:
            dt = self.game_clock.tick(Game.FPS_LIMIT) / Game.TICKS_PER_SEC
            self.events_loop()
            self.update_pacman_direction()
            self.update_sprites(dt)
            self.update_dots()

    # maintaining events like mouse/button clicks etc
    def events_loop(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.pause:
                    self.pause = False
                else:
                    self.pause = True
                    pause_game()
        pause_menu.mainloop(events)


    # updating and drawing every alive character and collectibles
    def update_sprites(self, dt):
        if self.pause:
            return

        # update alive characters (display)
        self.alive_group.update(dt, self.player, self.monsters.get(GhostNames.blinky))
        dirty_rectangles = self.alive_group.draw(self.game_screen)
        pygame.display.update(dirty_rectangles)

        # check for pacman killing status
        self.check_or_deactivate_pacman_killing()

        # check if pacman or ghosts are being eaten
        ghosts_colliding = pygame.sprite.spritecollide(self.player, self.ghosts_group, dokill=False)
        if len(ghosts_colliding) > 0:
            if self.player.is_killing:
                self.kill_ghosts(ghosts_colliding)
            else:
                self.kill_pacman()

    def update_dots(self):
        if self.pause:
            return

        # check for eaten small dots
        dots_eaten = pygame.sprite.spritecollide(self.player, self.dots_group, dokill=True)
        dots_no = len(dots_eaten)

        # check for eaten big dots
        big_dots_eaten = pygame.sprite.spritecollide(self.player, self.big_dots_group, dokill=True)
        big_dots_no = len(big_dots_eaten)

        if dots_no > 0 or big_dots_no > 0:
            self.status.add_dot_points(dots_no, big_dots_no)
        if big_dots_no > 0:
            self.activate_pacman_killing()

        # check if there are any dots left (whether level is unfinished)
        if not (self.dots_group or self.big_dots_group):
            self.status.level_finished()
            self.advance_to_next_level()

        self.draw_dots()

    def draw_dots(self):
        # update eaten dots (display)
        self.dots_group.update(self.alive_group)
        dirty_rectangles = self.dots_group.draw(self.game_screen)
        pygame.display.update(dirty_rectangles)

        self.big_dots_group.update(self.alive_group)
        dirty_rectangles = self.big_dots_group.draw(self.game_screen)
        pygame.display.update(dirty_rectangles)

    def update_pacman_direction(self):
        if self.pause:
            return

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_RIGHT]:
            self.player.change_direction(Directions.RIGHT)
        elif keys_pressed[pygame.K_LEFT]:
            self.player.change_direction(Directions.LEFT)
        elif keys_pressed[pygame.K_UP]:
            self.player.change_direction(Directions.UP)
        elif keys_pressed[pygame.K_DOWN]:
            self.player.change_direction(Directions.DOWN)

    def restart_characters_positions(self):
        # restart pacman
        self.player.position_tile = self.board.board_layout.spawn
        self.player.set_position_to_tile_center()
        self.player.is_running = False

        # restart ghosts
        for colour, ghost in self.monsters.items():
            ghost.position_tile = self.board.board_layout.ghost_spawns.get(colour)
            ghost.set_position_to_tile_center()
            ghost.direction = Directions.UP

        # refresh dots (draw)
        for dot in self.dots_group.sprites():
            dot.refresh = 2

    # pacman and ghosts collisions handling
    def kill_pacman(self):
        # handler for event when pacman is eaten by a ghost
        self.status.player_lives -= 1
        if self.status.player_lives == 0:
            self.status.game_over()
        else:
            self.restart_characters_positions()

    def kill_ghosts(self, ghosts_colliding):
        # handler for event when ghosts are eaten by pacman
        self.status.add_ghost_kill_points(len(ghosts_colliding))

        # return ghost to a spawn
        for killed_ghost in ghosts_colliding:
            for colour, ghost in self.monsters.items():
                if ghost == killed_ghost:
                    ghost.position_tile = self.board.board_layout.ghost_spawns.get(colour)
                    ghost.set_position_to_tile_center()
                    ghost.direction = Directions.UP

    def activate_pacman_killing(self):
        for monster in self.monsters.values():
            monster.is_killing = False
            monster.reverse_direction()

        self.player.is_killing = True
        self.status.killing_activated_time = pygame.time.get_ticks()

    def check_or_deactivate_pacman_killing(self):
        if self.player.is_killing:
            current_time = pygame.time.get_ticks()
            if self.status.killing_activated_time is not None and \
                    abs(current_time - self.status.killing_activated_time) / 1000 > GameStatus.KILLING_DURATION:
                self.player.is_killing = False
                for monster in self.monsters.values():
                    monster.is_killing = True

    # next level loading
    def advance_to_next_level(self):
        # start a new level, optionally: modify the difficulty
        self.restart_characters_positions()
        self.dots_group = self.board.prepare_dots()
        self.big_dots_group = self.board.prepare_big_dots()


def run_game():
    main_menu.disable()
    game.main_loop()


def pause_game():
    pause_menu.enable()


def resume_game():
    pause_menu.disable()
    game.pause = False
    pygame.display.flip()
    game.main_loop()


def main_background():
    game_screen.fill(COLOR_BACKGROUND)


def pause_background():
    return


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # displays the window in the center

    pygame.init()
    pygame.display.set_caption(TITLE, ICON_TITLE)

    game_screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    game_clock = pygame.time.Clock()
    game = Game(game_screen, game_clock, TILE_SIZE)

    # MAIN MENU
    main_menu = pygameMenu.Menu(game_screen,
                                bgfun=main_background,
                                color_selected=COLOR_SELECTED,
                                font=pygameMenu.fonts.FONT_BEBAS,
                                font_color=COLOR_BLACK,
                                font_size=30,
                                menu_alpha=100,
                                menu_color=MENU_BACKGROUND_COLOR,
                                menu_color_title=COLOR_SELECTED,
                                menu_height=int(SCREEN_RESOLUTION[1] * 0.6),
                                menu_width=int(SCREEN_RESOLUTION[0] * 0.6),
                                onclose=PYGAME_MENU_DISABLE_CLOSE,
                                option_shadow=False,
                                title='Main menu',
                                window_height=SCREEN_RESOLUTION[0],
                                window_width=SCREEN_RESOLUTION[1]
                                )
    main_menu.add_option('Play', run_game)
    main_menu.add_option('Quit', PYGAME_MENU_EXIT)

    # PAUSE MENU
    pause_menu = pygameMenu.Menu(game_screen,
                                bgfun=pause_background,
                                color_selected=COLOR_SELECTED,
                                font=pygameMenu.fonts.FONT_BEBAS,
                                font_color=COLOR_BLACK,
                                font_size=30,
                                menu_alpha=2,
                                menu_color=MENU_BACKGROUND_COLOR,
                                menu_color_title=COLOR_SELECTED,
                                menu_height=int(SCREEN_RESOLUTION[1] * 0.6),
                                menu_width=int(SCREEN_RESOLUTION[0] * 0.6),
                                onclose=PYGAME_MENU_DISABLE_CLOSE,
                                option_shadow=False,
                                title='Pause menu',
                                window_height=SCREEN_RESOLUTION[0],
                                window_width=SCREEN_RESOLUTION[1]
                                )
    pause_menu.add_option('Resume', resume_game)
    pause_menu.add_option('Quit', PYGAME_MENU_EXIT)
    pause_menu.disable()

    # Main loop
    while True:

        # Tick
        # game_clock.tick(60)

        events = pygame.event.get()

        # Main menu
        main_menu.mainloop(events)

        # Flip surface
        pygame.display.flip()
