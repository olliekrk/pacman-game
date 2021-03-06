from math import sqrt

from characters import *


class GhostNames(Enum):
    inky = 1
    pinky = 2
    blinky = 3
    clyde = 4


class Ghost(Character):
    DIRECTION_CHANGE_TIME_GAP = 100

    def __init__(self, board, color, *groups):
        super().__init__(board, *groups)

        # general attributes
        self.character_width = self.character_height = self.board.tile_size * 2

        # movement-related features
        self.position_tile = board.board_layout.ghost_spawns.get(color)
        self.set_position_to_tile_center()
        self.speed = 100

        # textures related attributes
        texture_name = './sheets/DinoSprites - ' + color.name + '.png'
        self.texture = pygame.image.load(texture_name)
        self.texture_size = 24

        self.idle_length = 4
        self.idle_textures = [self.load_tile_scaled(self.texture, i) for i in range(0, 4)]
        self.kill_length = 7
        self.kill_textures = [self.load_tile_scaled(self.texture, i) for i in range(4, 11)]

        # textures used when ghosts are vulnerable
        self.run_texture = pygame.image.load('./sheets/DinoSprites - vulnerable.png')
        self.run_length = 7
        self.run_textures = [self.load_tile_scaled(self.run_texture, i) for i in range(10, 17)]

        # ghost behaviour attributes
        self.is_killing = True
        self.chase_tile = None  # target tile when ghost is killing
        self.scatter_tile = None  # target tile when ghost is running (not killing)

        # necessary to prohibit ghost from reversing direction while chasing
        self.direction_change_time = pygame.time.get_ticks()
        self.board = board

    @staticmethod
    def calculate_distance_to_tile(from_tile, to_tile):
        return sqrt(pow(from_tile[0] - to_tile[0], 2) + pow(from_tile[1] - to_tile[1], 2))

    def load_tile(self, texture, number_of_tile):
        number_of_tile %= self.texture_size
        tile_location_px = number_of_tile * self.texture_size
        return texture.subsurface(tile_location_px, 0, self.texture_size, self.texture_size)

    def update(self, dt, *args):
        if self.is_killing:
            self.update_chase_tile(args[0], args[1])
        else:
            self.chase_tile = self.scatter_tile

        self.update_direction()
        super().update(dt, *args)

    def reverse_direction(self):
        self.direction = Directions.opposite_direction(self.direction)
        self.direction_change_time = pygame.time.get_ticks()

    def update_direction(self):
        time = pygame.time.get_ticks()
        if time - self.direction_change_time < Ghost.DIRECTION_CHANGE_TIME_GAP:
            return

        if self.safe_to_change_direction():
            chosen_direction = self.direction
            chosen_distance = None

            direction_tiles = [(direction, (self.position_tile[0] + switch[0], self.position_tile[1] + switch[1]))
                               for (direction, switch) in Character.DIRECTION_SWITCH_MAP.items()]

            direction_distances = [(direction, Ghost.calculate_distance_to_tile(tile, self.chase_tile))
                                   for (direction, tile) in direction_tiles
                                   if direction != Directions.opposite_direction(self.direction)
                                   and tile in self.board.board_layout.accessible]

            # chose shortest distance & corresponding direction
            for (direction, distance) in direction_distances:
                if chosen_distance is None or chosen_distance > distance:
                    chosen_direction, chosen_distance = direction, distance

            # reverse direction on dead ends
            if chosen_distance is None and self.position_tile not in self.board.board_layout.ghost_path:
                self.reverse_direction()
            else:
                self.direction = chosen_direction

            self.direction_change_time = time

    @abc.abstractmethod
    def update_chase_tile(self, pacman, blinky):
        """Uses an unique algorithm to make decision about current direction"""


class Blinky(Ghost):
    def __init__(self, board, *groups):
        super().__init__(board, GhostNames.blinky, *groups)
        self.scatter_tile = (board.board_layout.layout_size[0] - 1, 0)

    def update_chase_tile(self, pacman, _):
        self.chase_tile = pacman.position_tile


class Pinky(Ghost):
    def __init__(self, board, *groups):
        super().__init__(board, GhostNames.pinky, *groups)
        self.scatter_tile = (0, 0)

    def update_chase_tile(self, pacman, _):
        switch_tuple = Character.DIRECTION_SWITCH_MAP.get(pacman.direction)
        self.chase_tile = pacman.position_tile[0] + 4 * switch_tuple[0], pacman.position_tile[1] + 4 * switch_tuple[1]


class Inky(Ghost):
    def __init__(self, board, *groups):
        super().__init__(board, GhostNames.inky, *groups)
        self.scatter_tile = ()
        self.scatter_tile = (board.board_layout.layout_size[0] - 1, board.board_layout.layout_size[1] - 1)

    def update_chase_tile(self, pacman, blinky):
        switch_tuple = Character.DIRECTION_SWITCH_MAP.get(pacman.direction)
        blinky_tile = pacman.position_tile[0] + 2 * switch_tuple[0], pacman.position_tile[1] + 2 * switch_tuple[1]
        blinky_vector = blinky_tile[0] - blinky.position_tile[0], blinky_tile[1] - blinky.position_tile[1]
        self.chase_tile = blinky.position_tile[0] + 2 * blinky_vector[0], blinky.position_tile[1] + 2 * blinky_vector[1]


class Clyde(Ghost):
    def __init__(self, board, *groups):
        super().__init__(board, GhostNames.clyde, *groups)
        self.scatter_tile = (0, board.board_layout.layout_size[1] - 1)

    def update_chase_tile(self, pacman, _):
        distance = Ghost.calculate_distance_to_tile(self.position_tile, pacman.position_tile)
        if distance < 8:
            self.chase_tile = self.scatter_tile
        else:
            self.chase_tile = pacman.position_tile
