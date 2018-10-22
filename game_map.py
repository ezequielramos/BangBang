import random
import pygame

import config 

stars = []

for _ in range(10):
    stars.append([random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT/5), 2, 2])

for _ in range(5):
    stars.append([random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT/5), 4, 4])

for _ in range(2):
    stars.append([random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT/5), 8, 8])

def reduceNoise(map_curve):
    for i in range(len(map_curve) - 1):
        map_curve[i] = (map_curve[i] + map_curve[i+1]) / 2

    map_curve[-1] = (map_curve[-1] + map_curve[0]) / 2

class GameMap(object):
    def __init__(self):
        self.map_curve = []

    def generate(self, width, height, reduce_noise=1000):
        for _ in range(width):
            self.map_curve.append(random.randint(50, height))

        for _ in range(reduce_noise):
            reduceNoise(self.map_curve)

        return self

    def printGround(self, screen: pygame.Surface):
        for i in range(config.WIDTH):
            pygame.draw.line(screen, (0,0,0), [i, self.map_curve[i]], [i,config.HEIGHT], 1)


    def printBackground(self, screen):
        #sky
        pygame.draw.rect(screen, (10,10,30),  [0,0,config.WIDTH, config.HEIGHT])
        pygame.draw.rect(screen, (10,30,50),  [0,config.HEIGHT/20, config.WIDTH, config.HEIGHT])
        pygame.draw.rect(screen, (10,50,70),  [0,config.HEIGHT/10, config.WIDTH, config.HEIGHT ])
        pygame.draw.rect(screen, (10,70,110), [0,config.HEIGHT/5, config.WIDTH, config.HEIGHT])
        pygame.draw.rect(screen, (10,100,150), [0,config.HEIGHT/2 - 100, config.WIDTH, config.HEIGHT])
        #moon
        pygame.draw.circle(screen, (255,255,255), [int(config.WIDTH/10), int(config.HEIGHT/2)], 50)
        #stars
        for star in stars:
            pygame.draw.rect(screen, (255,255,255), star)