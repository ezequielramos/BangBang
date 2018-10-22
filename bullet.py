import pygame
import config
from game_map import GameMap

class Bullet(object):

    def __init__(self, screen: pygame.Surface, game_map: GameMap, x, y, force, angle=45, direction='right'):
        self.x = x
        self.y = y
        self.collide = False
        self.verticalForce = force/2
        self.horizontalForce = force/2
        self.screen = screen
        self.radius = 4
        self.map_curve = game_map.map_curve
        self.direction = 1 if direction == 'right' else -1

    def update(self):

        self.verticalForce -= 1
        self.x += self.horizontalForce * self.direction
        self.y -= self.verticalForce

        if self.x > config.WIDTH + self.radius or self.x < 0 - self.radius:
            return False

        if self.y >= self.map_curve[int(self.x)]:
            self.collide = True
            return False

        return True

    def draw(self):
        pygame.draw.circle(self.screen, (0,100,0), [int(self.x), int(self.y)], 4)