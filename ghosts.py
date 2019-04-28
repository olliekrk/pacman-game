from math import floor, sqrt

from characters import *


class GhostNames(Enum):
    inky = 1
    pinky = 2
    blinky = 3
    clyde = 4


class Ghost(Character):
    DIRECTION_CHANGE_TIME_GAP = 100
    TEXTURE_SIZE = 24
    RUN_LENGTH = 7
    IDLE_LENGTH = 4

    def __init__(self, board, color, *groups):
        super().__init__(board, *groups)

        # general attributes
        self.color = color
        self.character_width = board.tile_size * 2
        self.character_height = board.tile_size * 2

        # movement-related features
        self.position_tile = board.board_layout.ghost_spawns.get(color)
        self.position = ((self.position_tile[0] + 0.5) * self.board.tile_size,
                         (self.position_tile[1] + 0.5) * self.board.tile_size)
        self.speed = 100

        # rendering related attributes
        texture_name = './sheets/DinoSprites - ' + color.name + '.png'
        self.texture = pygame.image.load(texture_name)
        self.idle_textures = [self.load_tile_scaled(i) for i in range(0, 4)]
        self.run_textures = [self.load_tile_scaled(i) for i in range(4, 11)]

        # ghost behaviour attributes
        self.is_chasing = True
        self.is_scattered = False
        self.chase_tile = None
        self.scatter_tile = None

        # necessary to prohibit ghost from reversing direction while chasing
        self.direction_change_time = pygame.time.get_ticks()

    @staticmethod
    def calculate_distance_to_tile(from_tile, to_tile):
        return sqrt(pow(from_tile[0] - to_tile[0], 2) + pow(from_tile[1] - to_tile[1], 2))

    def load_tile(self, number_of_tile):
        number_of_tile %= Ghost.TEXTURE_SIZE
        tile_location_px = number_of_tile * Ghost.TEXTURE_SIZE
        return self.texture.subsurface(tile_location_px, 0, Ghost.TEXTURE_SIZE, Ghost.TEXTURE_SIZE)

    def load_tile_scaled(self, tile_number):
        return pygame.transform.scale(self.load_tile(tile_number), (self.character_width, self.character_height))

    def set_rect(self):
        self.rect = pygame.Rect(self.position[0] - self.character_width / 2,
                                self.position[1] - self.character_height / 2,
                                self.character_width,
                                self.character_height)

    def set_image(self):
        if self.is_running:
            image_index = int(floor(pygame.time.get_ticks() * Character.TILES_CHANGE_SPEED) % Ghost.RUN_LENGTH)
            self.image = self.run_textures[image_index]
        else:
            image_index = int(floor(pygame.time.get_ticks() * Character.TILES_CHANGE_SPEED) % Ghost.IDLE_LENGTH)
            self.image = self.idle_textures[image_index]

        if self.direction in [Directions.LEFT, Directions.UP]:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, dt, *args):
        self.update_chase_tile(args[0], args[1])
        super().update(dt, *args)

    def reverse_direction(self):
        self.direction = Directions.opposite_direction(self.direction)

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

            self.direction_change_time = time
            self.direction = chosen_direction

    @abc.abstractmethod
    def update_chase_tile(self, pacman, blinky):
        """Uses an unique algorithm to make decision about current direction"""


class Blinky(Ghost):
    def __init__(self, board, *groups):
        super().__init__(board, GhostNames.blinky, *groups)
        self.scatter_tile = (board.board_layout.layout_size[0] - 1, 0)

    def update_chase_tile(self, pacman, _):
        self.chase_tile = pacman.position_tile
        self.update_direction()


class Pinky(Ghost):
    def __init__(self, board, *groups):
        super().__init__(board, GhostNames.pinky, *groups)
        self.scatter_tile = (0, 0)

    def update_chase_tile(self, pacman, _):
        switch_tuple = Character.DIRECTION_SWITCH_MAP.get(pacman.direction)
        self.chase_tile = pacman.position_tile[0] + 4 * switch_tuple[0], pacman.position_tile[1] + 4 * switch_tuple[1]
        self.update_direction()


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
        self.update_direction()


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
        self.update_direction()
