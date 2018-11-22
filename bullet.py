import pygame
import config
from game_map import GameMap
import math

class Bullet(object):

    def __init__(self, screen: pygame.Surface, game_map: GameMap, x, y, force, angle=45):
        self.x = x
        self.y = y
        self.collide = False
        radian_angle = angle / 180 * math.pi
        self.verticalForce = math.sin(radian_angle) * force
        self.horizontalForce = math.cos(radian_angle) * force
        self.screen = screen
        self.radius = 4
        self.map_curve = game_map.map_curve

    def update(self):

        self.verticalForce -= 1
        self.x += self.horizontalForce
        self.y -= self.verticalForce

        if self.x > config.WIDTH + self.radius or self.x < 0 - self.radius:
            return False

        if self.y >= self.map_curve[int(self.x)]:
            self.collide = True
            return False

        return True

    def draw(self):
        pygame.draw.circle(self.screen, (255,100,100), [int(self.x), int(self.y)], 4)
