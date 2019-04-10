import pygame
import game


class Board(object):
    TILES = pygame.image.load('./tileset/warTileset_64x64.png')
    TILE_X = 64  # the size of tile loaded from .png, in px
    TILES_IN_ROW = 6
    NO_TILES = 23

    def __init__(self, tile_size, game_screen, layout):
        self.tile_size = tile_size
        self.game_screen = game_screen
        self.board_layout = layout
        self.background = self.prepare_background()

    @staticmethod
    def get_tile(tile_number):
        tile_number %= Board.NO_TILES

        column = tile_number % Board.TILES_IN_ROW
        row = tile_number // Board.TILES_IN_ROW

        return Board.TILES.subsurface(column * Board.TILE_X, row * Board.TILE_X, Board.TILE_X, Board.TILE_X)

    @staticmethod
    def are_adjacent_tiles(tile1, tile2):
        if tile1[0] == tile2[0] and (tile1[1] + 1 == tile2[1] or tile1[1] - 1 == tile2[1]):
            return True
        elif tile1[1] == tile2[1] and (tile1[0] + 1 == tile2[0] or tile1[0] - 1 == tile2[0]):
            return True
        else:
            return False

    def get_tile_scaled(self, tile_number):
        return pygame.transform.scale(Board.get_tile(tile_number), (self.tile_size, self.tile_size))

    def prepare_background(self):
        background = pygame.Surface(self.game_screen.get_size())
        for (i, j) in self.board_layout.walls:
            background.blit(self.get_tile_scaled(6),
                            (i * self.tile_size, j * self.tile_size))
        return background

    def draw_onto_screen(self):
        self.game_screen.blit(self.background, (0, 0))


class BoardLayout(pygame.sprite.Sprite):  # not sure if Sprite is needed here
    def __init__(self, wall_coords, accessible_coords, ghost_house_coords, spawn_coords, tunnels_coords, size, *groups):
        super().__init__(*groups)
        self.walls = wall_coords
        self.accessible = accessible_coords
        self.ghost_house = ghost_house_coords
        self.spawn = spawn_coords
        self.tunnels = tunnels_coords
        self.layout_size = size


class ClassicLayout(BoardLayout):
    SIZE = (28, 31)  # only playable area size
    BOARD_MAP = ["XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                 "X            XX            X",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X                          X",
                 "X XXXX XX XXXXXXXX XX XXXX X",
                 "X XXXX XX XXXXXXXX XX XXXX X",
                 "X      XX    XX    XX      X",
                 "XXXXXX XXXXX XX XXXXX XXXXXX",
                 "     X XXXXX XX XXXXX X     ",
                 "     X XX          XX X     ",
                 "     X XX XXX  XXX XX X     ",
                 "XXXXXX XX X      X XX XXXXXX",
                 "          X      X          ",
                 "XXXXXX XX X      X XX XXXXXX",
                 "     X XX XXXXXXXX XX X     ",
                 "     X XX          XX X     ",
                 "     X XX XXXXXXXX XX X     ",
                 "XXXXXX XX XXXXXXXX XX XXXXXX",
                 "X            XX            X",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X   XX                XX   X",
                 "XXX XX XX XXXXXXXX XX XX XXX",
                 "XXX XX XX XXXXXXXX XX XX XXX",
                 "X      XX    XX    XX      X",
                 "X XXXXXXXXXX XX XXXXXXXXXX X",
                 "X XXXXXXXXXX XX XXXXXXXXXX X",
                 "X                          X",
                 "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"]

    def __init__(self, *groups):
        # each index correspond to one tile on playable area
        walls_indices = [(i, j)
                         for i in range(ClassicLayout.SIZE[0])
                         for j in range(ClassicLayout.SIZE[1])
                         if ClassicLayout.BOARD_MAP[j][i] == 'X']

        accessible_indices = [(i, j)
                              for i in range(ClassicLayout.SIZE[0])
                              for j in range(ClassicLayout.SIZE[1])
                              if (i, j) not in walls_indices]

        ghost_house_map = {
            game.GhostNames.inky: (11, 13),
            game.GhostNames.pinky: (12, 13),
            game.GhostNames.blinky: (15, 13),
            game.GhostNames.clyde: (16, 13)
        }

        super().__init__(walls_indices, accessible_indices, ghost_house_map, (1, 1), None, ClassicLayout.SIZE)
