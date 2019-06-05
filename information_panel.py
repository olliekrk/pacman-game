import pygame
from time import sleep

COLOR_BLACK = (0, 0, 0)


class InformationPanel(object):

    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.life_texture = pygame.image.load('./sheets/life.png')
        self.life_size = 40
        self.life_texture = pygame.transform.scale(self.life_texture, (self.life_size, self.life_size))
        self.special_communique = ''
        self.is_special_communique_set = False

    def update_information_panel(self):
        points = self.font.render('SCORE:   ' + str(self.game.status.player_points), True, (255, 255, 255), None)
        level = self.font.render('LEVEL:   ' + str(self.game.status.level_number), True, (255, 255, 255), None)
        self.game.game_screen.fill(COLOR_BLACK, (0, 776, 700, 125))
        self.game.game_screen.blit(points, (0, 786))
        self.game.game_screen.blit(level, (0, 816))
        for i in range(0, self.game.status.player_lives):
            self.game.game_screen.blit(self.life_texture, (700 - self.life_size - (i * self.life_size), 776))
        if self.game.player.is_killing:
            ticks = pygame.time.get_ticks()
            killing_time = 5.0 - (ticks - self.game.status.killing_activated_time) / 1000.0
            time = self.font.render("KILLING TIME LEFT: %.2f s" % killing_time, True, (255, 255, 255), None)
            self.game.game_screen.blit(time, (0, 846))
        if self.is_special_communique_set:
            for i in range(0, 3):
                communique = self.font.render(self.special_communique + str(3 - i), True, (255, 255, 255), None)
                self.game.game_screen.fill(COLOR_BLACK, (0, 776, 700, 125))
                self.game.game_screen.blit(communique, (160, 820))
                pygame.display.flip()
                sleep(1)
            self.is_special_communique_set = False
            self.special_communique = ''
            self.game.first_after_pause = True
        pygame.display.flip()
