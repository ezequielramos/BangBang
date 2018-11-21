import config
import pygame

def drawShootForce(screen, shoot_force):    
    pygame.draw.rect(screen, (255, 0, 0), [0, config.HEIGHT-(config.HEIGHT/20), config.WIDTH/50 * shoot_force, config.HEIGHT/20])

def drawShootForceRuler(screen):
    pygame.draw.line(screen, (255,255,255), (0,config.HEIGHT-(config.HEIGHT/20)), (config.WIDTH, config.HEIGHT-(config.HEIGHT/20)), 3)

    for i in range(1,8):
        x_pos = i * config.WIDTH/8
        pygame.draw.line(screen, (255,255,255), (x_pos,config.HEIGHT), (x_pos, config.HEIGHT-(config.HEIGHT/40)), 3)

    for i in range(1,16):
        x_pos = i * config.WIDTH/16
        pygame.draw.line(screen, (255,255,255), (x_pos,config.HEIGHT), (x_pos, config.HEIGHT-(config.HEIGHT/80)), 1)