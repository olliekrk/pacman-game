import os
from time import sleep

import pygameMenu
from pygameMenu.locals import *

import board
import characters
from ghosts import *

TITLE = "Pacman WIEiT Edition"
ICON_TITLE = "Pacman SE"

BOARD_SIZE = (28, 36)  # 28 x 36 tiles is the original size of board
TILE_SIZE = 25  # pixels
SCREEN_RESOLUTION = (TILE_SIZE * BOARD_SIZE[0], TILE_SIZE * BOARD_SIZE[1])

MENU_BACKGROUND_COLOR = (255, 255, 26)
COLOR_GREY = (107, 102, 97)
COLOR_BLACK = (0, 0, 0)
COLOR_SELECTED = (255, 153, 0)

game = None


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
        game_over_menu.enable()

    def level_finished(self):
        # when all the dots are eaten
        self.level_number += 1
        self.killing_activated_time = None
        self.last_kill_time = None
        self.bonus_multiplier = 0
        level_completed_menu.enable()

    def reset(self):
        self.level_number = 1
        self.player_points = 0
        self.player_lives = GameStatus.MAX_LIVES
        self.killing_activated_time = None
        self.last_kill_time = None
        self.bonus_multiplier = 0


class Game(object):
    FPS_LIMIT = 90
    TICKS_PER_SEC = 1000.0

    def __init__(self, game_screen, game_clock, tile_size, layout='classic'):
        self.finished = False
        self.game_screen = game_screen
        self.game_clock = game_clock
        if layout == 'classic':
            self.board = board.Board(tile_size, game_screen, board.ClassicLayout())
        else:
            self.board = board.Board(tile_size, game_screen, board.GeneratedLayout(layout))

        self.status = GameStatus()

        # pause properties
        self.pause = False
        self.first_after_pause = True
        self.last_dt = 0
        self.pause_start_ticks = 0
        self.pause_end_ticks = 0

        # information panel properties
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.life_texture = pygame.image.load('./sheets/life.png')
        self.life_size = 40
        self.life_texture = pygame.transform.scale(self.life_texture, (self.life_size, self.life_size))
        self.special_communique = ''
        self.is_special_communique_set = False

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
            self.events_loop()
            if not self.pause:
                dt = self.game_clock.tick(Game.FPS_LIMIT) / Game.TICKS_PER_SEC
                if self.first_after_pause:
                    dt = self.last_dt
                    self.first_after_pause = False
                    self.refresh_game_screen()
                self.last_dt = dt
                self.update_pacman_direction()
                self.update_sprites(dt)
                self.update_dots()
                self.update_information_panel()

    # maintaining events like mouse/button clicks etc
    @staticmethod
    def events_loop():
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_game()
        pause_menu.mainloop(events)
        game_over_menu.mainloop(events)
        level_completed_menu.mainloop(events)

    def refresh_game_screen(self):
        self.game_screen.blit(self.board.background, (0, 0))
        for dot in self.dots_group:
            dot.dirty = 1
        for big_dot in self.big_dots_group:
            big_dot.dirty = 1

    # updating and drawing every alive character and collectibles
    def update_sprites(self, dt):
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
                for ghost in ghosts_colliding:
                    if self.player.is_colliding(ghost):
                        self.kill_pacman()
                        return

    def update_dots(self):
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
            self.pause = True
            self.advance_to_next_level()
            self.status.level_finished()

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
        self.player.direction = Directions.UP
        self.player.is_killing = False

        # restart ghosts
        for colour, ghost in self.monsters.items():
            ghost.position_tile = self.board.board_layout.ghost_spawns.get(colour)
            ghost.set_position_to_tile_center()
            ghost.direction = Directions.UP
            ghost.is_killing = True

        # refresh dots (draw)
        for dot in self.dots_group.sprites():
            dot.refresh = 2

    # pacman and ghosts collisions handling
    def kill_pacman(self):
        # handler for event when pacman is eaten by a ghost
        self.status.player_lives -= 1
        if self.status.player_lives == 0:
            self.pause = True
            self.status.game_over()
        else:
            self.restart_characters_positions()
            self.special_communique = 'You have been killed. Continue in '
            self.is_special_communique_set = True

    def kill_ghosts(self, ghosts_colliding):
        # handler for event when ghosts are eaten by pacman
        for ghost in ghosts_colliding:
            if not self.player.is_colliding(ghost):
                ghosts_colliding.remove(ghost)

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
        self.player.speed += Pacman.SPEED_BONUS
        self.status.killing_activated_time = pygame.time.get_ticks()
        self.pause_start_ticks = 0
        self.pause_end_ticks = 0

    def check_or_deactivate_pacman_killing(self):
        if self.player.is_killing:
            current_time = pygame.time.get_ticks()
            if self.status.killing_activated_time is not None and \
                    abs(current_time - self.pause_end_ticks + self.pause_start_ticks -
                        self.status.killing_activated_time) / 1000 > GameStatus.KILLING_DURATION:
                self.player.is_killing = False
                self.player.speed -= Pacman.SPEED_BONUS
                for monster in self.monsters.values():
                    monster.is_killing = True

    # next level loading
    def advance_to_next_level(self):
        # start a new level, optionally: modify the difficulty
        self.player.speed = Character.BASE_SPEED
        self.restart_characters_positions()
        self.dots_group = self.board.prepare_dots()
        self.big_dots_group = self.board.prepare_big_dots()

    def update_information_panel(self):
        points = self.font.render('SCORE:   ' + str(self.status.player_points), True, (255, 255, 255), None)
        level = self.font.render('LEVEL:   ' + str(self.status.level_number), True, (255, 255, 255), None)
        self.game_screen.fill(COLOR_BLACK, (0, 776, 700, 125))
        self.game_screen.blit(points, (0, 786))
        self.game_screen.blit(level, (0, 816))
        for i in range(0, self.status.player_lives):
            self.game_screen.blit(self.life_texture, (700 - self.life_size - (i * self.life_size), 776))
        if self.player.is_killing:
            ticks = pygame.time.get_ticks()
            killing_time = 5.0 - (ticks - self.status.killing_activated_time) / 1000.0
            time = self.font.render("KILLING TIME LEFT: %.2f s" % killing_time, True, (255, 255, 255), None)
            self.game_screen.blit(time, (0, 846))
        if self.is_special_communique_set:
            for i in range(0, 3):
                communique = self.font.render(self.special_communique + str(3 - i), True, (255, 255, 255), None)
                self.game_screen.fill(COLOR_BLACK, (0, 776, 700, 125))
                self.game_screen.blit(communique, (160, 820))
                pygame.display.flip()
                sleep(1)
            self.is_special_communique_set = False
            self.special_communique = ''
            self.first_after_pause = True
        pygame.display.flip()


def run_game():
    main_menu.disable()
    game.main_loop()


def run_random_game():
    global game
    game = Game(game_screen, game_clock, TILE_SIZE, 'prim')
    game.main_loop()
    main_menu.disable()


def run_wall_game():
    global game
    game = Game(game_screen, game_clock, TILE_SIZE, 'wall')
    game.main_loop()
    main_menu.disable()


def new_game():
    game_over_menu.disable()
    pause_menu.disable()
    game.advance_to_next_level()
    game.pause = False
    game.first_after_pause = True
    game.status.reset()
    game.main_loop()


def next_level():
    level_completed_menu.disable()
    game.advance_to_next_level()
    game.pause = False
    game.first_after_pause = True
    game.main_loop()


def pause_game():
    game.pause = True
    game.pause_start_ticks = pygame.time.get_ticks()
    pause_menu.enable()


def resume_game():
    pause_menu.disable()
    game.pause = False
    game.pause_end_ticks = pygame.time.get_ticks()
    game.first_after_pause = True
    game.main_loop()


def main_background():
    game_screen.fill(COLOR_BLACK)
    pygame.draw.rect(game_screen, COLOR_GREY, (0, 83, SCREEN_RESOLUTION[0], 10))
    pygame.draw.rect(game_screen, COLOR_GREY, (0, 850, SCREEN_RESOLUTION[0], 10))
    for i in range(6):
        pygame.draw.rect(game_screen, MENU_BACKGROUND_COLOR, (300 + (i * 80), 50, 10, 10))
    for i in range(14):
        pygame.draw.rect(game_screen, MENU_BACKGROUND_COLOR, (10 + (i * 80), 817, 10, 10))
    game_screen.blit(ghost2_texture, (20, 13))
    game_screen.blit(ghost1_texture, (100, 13))
    game_screen.blit(pacman_texture, (200, 8))
    game_screen.blit(ghost3_texture, (550, 13))
    game_screen.blit(ghost4_texture, (350, 780))


def empty_function():
    return


def create_menu(title, bgfun, alpha):
    return pygameMenu.Menu(game_screen, bgfun=bgfun, color_selected=COLOR_SELECTED, font=pygameMenu.fonts.FONT_BEBAS,
                           font_color=COLOR_BLACK, font_size=60, menu_alpha=alpha, menu_color=MENU_BACKGROUND_COLOR,
                           menu_color_title=COLOR_SELECTED, menu_height=int(SCREEN_RESOLUTION[1] * 0.6),
                           menu_width=int(SCREEN_RESOLUTION[0] * 0.6), onclose=PYGAME_MENU_DISABLE_CLOSE,
                           option_shadow=False, title=title, window_height=SCREEN_RESOLUTION[1],
                           window_width=SCREEN_RESOLUTION[0], draw_select=False)


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # displays the window in the center

    pygame.init()
    pygame.display.set_caption(TITLE, ICON_TITLE)

    game_screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    game_clock = pygame.time.Clock()
    game = Game(game_screen, game_clock, TILE_SIZE)

    # MAIN SCREEN BACKGROUND TEXTURES
    pacman_texture = game.player.load_tile(game.player.texture, 10)
    pacman_texture = pygame.transform.scale(pacman_texture, (80, 80))
    ghost1_texture = game.monsters.get(GhostNames.blinky).load_tile(game.monsters.get(GhostNames.blinky).texture, 9)
    ghost1_texture = pygame.transform.scale(ghost1_texture, (80, 80))
    ghost2_texture = game.monsters.get(GhostNames.inky).load_tile(game.monsters.get(GhostNames.inky).texture, 16)
    ghost2_texture = pygame.transform.scale(ghost2_texture, (80, 80))
    ghost3_texture = game.monsters.get(GhostNames.pinky).load_tile(game.monsters.get(GhostNames.pinky).texture, 8)
    ghost3_texture = pygame.transform.scale(ghost3_texture, (80, 80))
    ghost3_texture = pygame.transform.flip(ghost3_texture, True, False)
    ghost4_texture = game.monsters.get(GhostNames.clyde).load_tile(game.monsters.get(GhostNames.clyde).texture, 6)
    ghost4_texture = pygame.transform.scale(ghost4_texture, (80, 80))
    ghost4_texture = pygame.transform.flip(ghost4_texture, True, False)

    # MAIN MENU
    main_menu = create_menu('Pacman', main_background, 100)
    main_menu.add_option('Classic', run_game)
    main_menu.add_option('Random maze', run_random_game)
    main_menu.add_option('Cross maze', run_wall_game)
    main_menu.add_option('Quit', PYGAME_MENU_EXIT)

    # PAUSE MENU
    pause_menu = create_menu('Pause', empty_function, 2)
    pause_menu.add_option('Resume', resume_game)
    pause_menu.add_option('Restart', new_game)
    pause_menu.add_option('Quit', PYGAME_MENU_EXIT)
    pause_menu.disable()

    # GAME OVER MENU
    game_over_menu = create_menu('Game over', empty_function, 2)
    game_over_menu.add_option('New Game', new_game)
    game_over_menu.add_option('Quit', PYGAME_MENU_EXIT)
    game_over_menu.disable()

    # LEVEL COMPLETED MENU
    level_completed_menu = create_menu('Level completed', main_background, 100)
    level_completed_menu.add_option('Next Level', next_level)
    level_completed_menu.add_option('Quit', PYGAME_MENU_EXIT)
    level_completed_menu.disable()

    # Main loop
    while True:
        events = pygame.event.get()
        main_menu.mainloop(events)
        pygame.display.flip()
