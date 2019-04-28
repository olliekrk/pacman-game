import pygame

import collectibles
import game


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
        self.collectibles = self.prepare_collectibles()

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

    def prepare_collectibles(self):
        collectible_group = pygame.sprite.LayeredDirty()
        for (x, y) in self.board_layout.accessible:
            collectibles.Collectible(x, y, self.tile_size, collectible_group)
        return collectible_group


class BoardLayout:
    def __init__(self, wall_indices, accessible_indices,
                 ghost_spawn_map, ghost_house_indices, ghost_path_indices,
                 spawn_index, tunnel_indices, size):
        self.layout_size = size
        self.walls = wall_indices
        self.accessible = accessible_indices

        self.ghost_spawns = ghost_spawn_map
        self.ghost_house = ghost_house_indices
        self.ghost_path = ghost_path_indices

        self.spawn = spawn_index
        self.tunnels = tunnel_indices


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
                 "X                          X",
                 "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"]

    def __init__(self):
        # each index correspond to one tile on playable area
        walls_indices = [(i, j)
                         for i in range(ClassicLayout.SIZE[0])
                         for j in range(ClassicLayout.SIZE[1])
                         if ClassicLayout.BOARD_MAP[j][i] == 'X']

        accessible_indices = [(i, j)
                              for i in range(ClassicLayout.SIZE[0])
                              for j in range(ClassicLayout.SIZE[1])
                              if ClassicLayout.BOARD_MAP[j][i] == ' ']

        ghost_house_indices = [(i, j)
                               for i in range(ClassicLayout.SIZE[0])
                               for j in range(ClassicLayout.SIZE[1])
                               if ClassicLayout.BOARD_MAP[j][i] in ['g', 'G']]

        ghost_path_indices = [(i, j)
                              for i in range(ClassicLayout.SIZE[0])
                              for j in range(ClassicLayout.SIZE[1])
                              if ClassicLayout.BOARD_MAP[j][i] == 'G']

        ghost_spawn_map = {
            game.GhostNames.inky: (13, 14),
            game.GhostNames.pinky: (14, 14),
            game.GhostNames.blinky: (13, 15),
            game.GhostNames.clyde: (14, 15)
        }

        spawn_index = (14, 23)

        super().__init__(walls_indices, accessible_indices,
                         ghost_spawn_map, ghost_house_indices, ghost_path_indices,
                         spawn_index, None, ClassicLayout.SIZE)
