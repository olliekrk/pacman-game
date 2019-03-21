import pygame


class Board(object):
    TILES = pygame.image.load('./tileset/warTileset_64x64.png')
    NO_TILES = 23
    TILES_IN_ROW = 6
    TILE_X = 64  # the size of tile loaded from .png, in px

    def __init__(self, tile_size):
        self.tile_size = tile_size

    @staticmethod
    def get_tile(tile_number):
        tile_number %= Board.NO_TILES

        column = tile_number % 6
        row = tile_number // 6

        return Board.TILES.subsurface(column * Board.TILE_X, row * Board.TILE_X, Board.TILE_X, Board.TILE_X)

    def get_tile_scaled(self, tile_number):
        return pygame.transform.scale(Board.get_tile(tile_number), (self.tile_size, self.tile_size))

    def draw_onto_screen(self, game_screen):
        # todo: add correct way of printing the whole board
        game_screen.blit(self.get_tile_scaled(3), (100, 0))
        game_screen.blit(self.get_tile_scaled(13), (0, 100))
        game_screen.blit(self.get_tile_scaled(23), (200, 0))
        game_screen.blit(self.get_tile_scaled(33), (0, 200))
        pygame.display.flip()
