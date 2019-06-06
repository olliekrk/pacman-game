import random

import pygame

import collectibles
import game
from maze_generator import MazeGenerator


class Board(object):
    TILES = pygame.image.load('./tileset/warTileset_64x64.png')
    TILE_X = 64  # the size of tile loaded from .png, in px
    TILES_IN_ROW = 6
    NO_TILES = 23

    # indices of tiles used for drawing background
    BACKGROUND_TILE = 0
    GHOST_HOUSE_TILE = 4

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
            background.blit(self.get_tile_scaled(Board.BACKGROUND_TILE), (i * self.tile_size, j * self.tile_size))

        for (i, j) in self.board_layout.ghost_house:
            ghost_house_tile = self.get_tile_scaled(Board.GHOST_HOUSE_TILE)
            ghost_house_tile.set_alpha(10)
            background.blit(ghost_house_tile, (i * self.tile_size, j * self.tile_size))

        return background

    def prepare_dots(self):
        dots_group = pygame.sprite.LayeredDirty()
        for (x, y) in self.board_layout.accessible:
            collectibles.Dot(x, y, self.tile_size, dots_group)
        return dots_group

    def prepare_big_dots(self):
        big_dots_group = pygame.sprite.LayeredDirty()
        for (x, y) in self.board_layout.big_dots_indices:
            collectibles.BigDot(x, y, self.tile_size, big_dots_group)
        return big_dots_group

    def teleport_available(self, position_tile):
        for (start_tile, end_tile) in self.board_layout.tunnels:
            if position_tile == start_tile:
                return end_tile
        return None


class BoardLayout:
    def __init__(self, wall_indices, accessible_indices,
                 ghost_spawn_map, ghost_house_indices, ghost_path_indices,
                 spawn_index, tunnel_indices, big_dots_indices, size):
        self.layout_size = size
        self.walls = wall_indices
        self.accessible = accessible_indices
        self.big_dots_indices = big_dots_indices

        self.ghost_spawns = ghost_spawn_map
        self.ghost_house = ghost_house_indices
        self.ghost_path = ghost_path_indices

        self.spawn = spawn_index
        self.tunnels = tunnel_indices


class ClassicLayout(BoardLayout):
    SIZE = (28, 31)  # only playable area size
    BOARD_MAP = ["XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                 "XO           XX           OX",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X XXXX XXXXX XX XXXXX XXXX X",
                 "X                          X",
                 "X XXXX XX XXXXXXXX XX XXXX X",
                 "X XXXX XX XXXXXXXX XX XXXX X",
                 "X      XX    XX    XX      X",
                 "XXXXXX XXXXX XX XXXXX XXXXXX",
                 "/////X XXXXX XX XXXXX X/////",
                 "/////X XX          XX X/////",
                 "/////X XX XXXGGXXX XX X/////",
                 "XXXXXX XX XggGGggX XX XXXXXX",
                 "          XggGGggX          ",
                 "XXXXXX XX XggGGggX XX XXXXXX",
                 "/////X XX XXXXXXXX XX X/////",
                 "/////X XX          XX X/////",
                 "/////X XX XXXXXXXX XX X/////",
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
                 "XO                        OX",
                 "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"]

    def __init__(self):
        # each index correspond to one tile on playable area
        walls_indices = [(i, j)
                         for i in range(ClassicLayout.SIZE[0])
                         for j in range(ClassicLayout.SIZE[1])
                         if ClassicLayout.BOARD_MAP[j][i] == 'X']

        ghost_house_indices = [(i, j)
                               for i in range(ClassicLayout.SIZE[0])
                               for j in range(ClassicLayout.SIZE[1])
                               if ClassicLayout.BOARD_MAP[j][i] in ['g', 'G']]

        ghost_path_indices = [(i, j)
                              for i in range(ClassicLayout.SIZE[0])
                              for j in range(ClassicLayout.SIZE[1])
                              if ClassicLayout.BOARD_MAP[j][i] == 'G']

        big_dots_indices = [(i, j)
                            for i in range(ClassicLayout.SIZE[0])
                            for j in range(ClassicLayout.SIZE[1])
                            if ClassicLayout.BOARD_MAP[j][i] == 'O']

        accessible_indices = [(i, j)
                              for i in range(ClassicLayout.SIZE[0])
                              for j in range(ClassicLayout.SIZE[1])
                              if ClassicLayout.BOARD_MAP[j][i] == ' ']

        accessible_indices += big_dots_indices

        ghost_spawn_map = {
            game.GhostNames.inky: (13, 14),
            game.GhostNames.pinky: (14, 14),
            game.GhostNames.blinky: (13, 15),
            game.GhostNames.clyde: (14, 15)
        }

        spawn_index = (14, 23)

        tunnel_indices = [((-1, 14), (28, 14)),
                          ((28, 14), (-1, 14))]

        super().__init__(walls_indices, accessible_indices,
                         ghost_spawn_map, ghost_house_indices, ghost_path_indices,
                         spawn_index, tunnel_indices, big_dots_indices,
                         ClassicLayout.SIZE)


class GeneratedLayout(BoardLayout):
    SIZE = (28, 31)

    def __init__(self, type):
        generator = MazeGenerator()
        if type == 'prim':
            generator.prepare_prim_model()
        elif type == 'wall':
            generator.prepare_wall_model()

        self.model = generator.maze_model

        walls = [(i, j) for i in range(self.SIZE[0]) for j in range(self.SIZE[1]) if self.model[j][i] == 1]

        ghost_house = []

        ghost_path = []

        accessible = [(i, j) for i in range(self.SIZE[0]) for j in range(self.SIZE[1]) if self.model[j][i] == 0]

        big_dots = [accessible[random.randint(0, len(accessible)-1)] for i in range(4)]

        possible_ghost_spawn = [accessible[random.randint(0, len(accessible) - 1)] for i in range(4)]
        ghost_spawn = {
            game.GhostNames.inky: possible_ghost_spawn[0],
            game.GhostNames.pinky: possible_ghost_spawn[1],
            game.GhostNames.blinky: possible_ghost_spawn[2],
            game.GhostNames.clyde: possible_ghost_spawn[3]
        }

        possible_spawn = [x for x in accessible if x not in possible_ghost_spawn]
        spawn = possible_spawn[random.randint(0, len(possible_spawn) - 1)]

        tunnel = []

        super().__init__(walls, accessible, ghost_spawn, ghost_house, ghost_path, spawn, tunnel, big_dots, self.SIZE)
