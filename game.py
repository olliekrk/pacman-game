import board
import characters
from ghosts import *
import pygame
import application


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
        application.game_over_menu.enable()

    def level_finished(self):
        # when all the dots are eaten
        self.level_number += 1
        self.killing_activated_time = None
        self.last_kill_time = None
        self.bonus_multiplier = 0
        application.level_completed_menu.enable()

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

    def __init__(self, game_screen, game_clock, tile_size):
        self.finished = False
        self.game_screen = game_screen
        self.game_clock = game_clock
        self.board = board.Board(tile_size, game_screen, board.ClassicLayout())
        self.status = GameStatus()
        self.menus = None

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
        self.information_panel = None

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
                self.information_panel.update_information_panel()

    # maintaining events like mouse/button clicks etc
    def events_loop(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                application.pause_game()
        #for key, value in self.menus:
            #value.mainloop(events)
        #application.get_pause_menu().mainloop(events)
        #application.get_game_over_menu().mainloop(events)
        #application.get_level_completed_menu().mainloop(events)
        self.menus.get('pause').mainloop(events)

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
        self.restart_characters_positions()
        self.dots_group = self.board.prepare_dots()
        self.big_dots_group = self.board.prepare_big_dots()

    def add_information_panel(self, panel):
        self.information_panel = panel

    def add_menus(self, menus):
        self.menus = menus





