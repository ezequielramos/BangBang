import pygame

class Cannon(pygame.sprite.Group):
    def __init__(self, screen: pygame.Surface, map_curve, x, color):
        super(pygame.sprite.Group, self).__init__()

        self.rotating = 0
        self.map_curve = map_curve
        y = map_curve[int(x)] - 13

        self.base = pygame.sprite.Sprite()
        
        self.base.image = pygame.Surface([30, 10])
        self.base.image.set_colorkey([0,0,0])
        self.base.image.fill(color)  
        
        self.image = self.base.image.copy()
        self.image.set_colorkey([0,0,0])
        
        self.base.rect = self.base.image.get_rect()

        self.base.rect.center = (x , y)  

        self.rot = 0
        self.rot_speed = 2

        self.add(self.base)

    def update(self):
        if self.rotating != 0:
            self.rotate()

    def rotate(self):
        old_center = self.base.rect.center
        self.rot = (self.rot + (self.rot_speed * self.rotating) ) % 360
        self.image = pygame.transform.rotate(self.base.image, self.rot)  
        rect = self.image.get_rect()
        rect.center = old_center
        self.base.rect = rect

    def draw(self, screen):
        center = self.base.rect.center
        screen.blit(self.image , self.base.rect)

        brown = (100,50,30)
        pygame.draw.rect(screen, brown, [center[0]-5,center[1],10,15])
        pygame.draw.circle(screen, brown, center, 5)
