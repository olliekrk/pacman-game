import pygame


class Dot(pygame.sprite.DirtySprite):

    def __init__(self, x_tile, y_tile, tile_size, *groups):
        super().__init__(*groups)
        self.tile = (x_tile, y_tile)
        self.size = tile_size // 5

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 255, 0))
        self.rect = pygame.Rect((x_tile + 0.5) * tile_size - self.size / 2,
                                (y_tile + 0.5) * tile_size - self.size / 2,
                                self.size,
                                self.size)
        self.dirty = 1
        self.refresh = 0  # specifies how many times to perform complete refresh (force dirty=1)

    def update(self, alive_group, *args):
        # refresh without calculating distances
        if self.refresh > 0:
            self.refresh -= 1
            self.dirty = 1
            return

        too_close = False
        close_enough = False

        for sprite in alive_group.sprites():
            dist_x = sprite.position_tile[0] - self.tile[0]
            dist_y = sprite.position_tile[1] - self.tile[1]
            dist = max(abs(dist_x), abs(dist_y))

            if dist < 4:
                close_enough = True

            if dist < 1:
                too_close = True
                break

        if close_enough and not too_close:
            self.dirty = 1


class BigDot(Dot):
    def __init__(self, x_tile, y_tile, tile_size, *groups):
        super().__init__(x_tile, y_tile, tile_size, *groups)
        self.size = tile_size // 2
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 255, 0))
        self.rect = pygame.Rect((x_tile + 0.5) * tile_size - self.size / 2,
                                (y_tile + 0.5) * tile_size - self.size / 2,
                                self.size,
                                self.size)
