import sys

TYPE = "NONE"

if len(sys.argv) >= 2:
    if sys.argv[1] == 'host':
        TYPE = 'HOST'
    elif sys.argv[1] == 'join':
        TYPE = 'JOIN'
    else:
        print('Invalid argument. You should use host or join for second argument.')
        sys.exit()

import pygame
import game_map
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import socket
import json
import time
import random

WIDTH = 1280
HEIGHT = 720

HOST = '127.0.0.1'
PORT = 5001

stars = []

class Bullet(object):

    def __init__(self, screen, map_curve, x, y, force, angle=45, direction='right'):
        self.x = x
        self.y = y
        self.collide = False
        self.verticalForce = force/2
        self.horizontalForce = force/2
        self.screen = screen
        self.radius = 4
        self.map_curve = map_curve
        self.direction = 1 if direction == 'right' else -1

    def update(self):

        self.verticalForce -= 1
        self.x += self.horizontalForce * self.direction
        self.y -= self.verticalForce

        if self.x > WIDTH + self.radius or self.x < 0 - self.radius:
            return False

        if self.y >= self.map_curve[int(self.x)]:
            self.collide = True
            return False

        return True

    def draw(self):
        pygame.draw.circle(self.screen, (0,100,0), [int(self.x), int(self.y)], 4)

for _ in range(10):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT/5), 2, 2])

for _ in range(5):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT/5), 4, 4])

for _ in range(2):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT/5), 8, 8])


def textOnMiddle(screen, text, font):
    text = font.render(text, True, (255, 255, 255))
    text_w, text_h = text.get_size()

    screen.blit(text, (WIDTH/2 - text_w/2, HEIGHT/2 - text_h/2))

def encodeDict(dict_var):
    return bytes(json.dumps(dict_var), 'utf-8')

def decodeDict(msg):
    return json.loads(msg.decode("utf-8"))

def printBackground(screen):
    #sky
    pygame.draw.rect(screen, (10,10,30),  [0,0,WIDTH, HEIGHT])
    pygame.draw.rect(screen, (10,30,50),  [0,HEIGHT/20, WIDTH, HEIGHT])
    pygame.draw.rect(screen, (10,50,70),  [0,HEIGHT/10, WIDTH, HEIGHT ])
    pygame.draw.rect(screen, (10,70,110), [0,HEIGHT/5, WIDTH, HEIGHT])
    pygame.draw.rect(screen, (10,100,150), [0,HEIGHT/2 - 100, WIDTH, HEIGHT])
    #moon
    pygame.draw.circle(screen, (255,255,255), [int(WIDTH/10), int(HEIGHT/2)], 50)
    #stars
    for star in stars:
        pygame.draw.rect(screen, (255,255,255), star)
    
def main():

    fps = 30
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.font.init()
    font = pygame.font.Font("DejaVuSans.ttf", 24)


    if TYPE == 'HOST':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')
        
        try:
            s.bind((HOST, PORT))
        except socket.error as msg:
            print(msg)
            print('Bind failed. Error Code. ')
            sys.exit()
            
        print('Socket bind complete')
        
        s.listen(10)
        print('Socket now listening')
        
        try:
            textOnMiddle(screen, 'Waiting for player to join...', font)
            pygame.display.flip()

            conn, _ = s.accept()
        except KeyboardInterrupt:
            print('Closing Server...')
            return s
    
        screen.fill( (0,0,0) )
        textOnMiddle(screen, 'Generating map...', font)
        pygame.display.flip()
        map_curve = game_map.generate(WIDTH, HEIGHT, 2500)
        msg = encodeDict(map_curve)
        conn.send(bytes(str(len(msg)), 'utf-8'))
        conn.recv(2)
        conn.send(msg)

    elif TYPE == 'JOIN':
        textOnMiddle(screen, 'Joining...', font)
        pygame.display.flip()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        msg_len = s.recv(64)
        s.send(b'ok')
        msg = s.recv(int(msg_len)*2)
        print(msg)
        map_curve = decodeDict(msg)
    else:
        textOnMiddle(screen, 'Generating map...', font)
        pygame.display.flip()
        map_curve = game_map.generate(WIDTH, HEIGHT, 2500)


    #icon = pygame.image.load("pygame-icon.png")
    #icon = icon.convert_alpha()
    #icon_w, icon_h = icon.get_size()

    shooting_force = -1

    bullets = []

    while True:

        msg = {}
        recv_msg = {}

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shooting_force = 0
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if TYPE == 'JOIN':
                        x = WIDTH - 100
                        direction = 'left'
                    else:
                        x = 100
                        direction = 'right'
                    bullets.append(Bullet(screen, map_curve, x, HEIGHT/4, shooting_force, 45, direction))
                    msg['shoot'] = {
                        'x': x,
                        'y': HEIGHT/4,
                        'shooting_force': shooting_force
                    }
                    shooting_force = -1

            if event.type == pygame.QUIT:
                conn.close()
                pygame.quit()

                print('Closing Server...')
                return s

        ping = time.time()
        if TYPE == 'HOST':
            conn.send(encodeDict(msg))
            recv_msg = conn.recv(1024)
            recv_msg = decodeDict(recv_msg)
        elif TYPE == 'JOIN':
            recv_msg = s.recv(1024)
            s.send(encodeDict(msg))
            recv_msg = decodeDict(recv_msg)

        if 'shoot' in recv_msg:
            if TYPE == 'JOIN':
                direction = 'right'
            else:
                direction = 'left'
            bullets.append(Bullet(screen, map_curve, recv_msg['shoot']['x'], recv_msg['shoot']['y'] , recv_msg['shoot']['shooting_force'], 45, direction))

        ping = time.time() - ping

        screen.fill( (0,0,0) )

        printBackground(screen)

        #socket.send('oi')
        #newText = socket.recv(1024)
        

        text = font.render('10uv >>', True, (255, 255, 255))
        fps_text = font.render(f'{round(clock.get_fps(),2)} fps', True, (255, 255, 255))
        ping_text = font.render(f'ping {int(ping * 1000)}ms', True, (255, 255, 255))
        text_w, text_h = fps_text.get_size()
        ping_text_w, _ = ping_text.get_size()


        screen.blit(text, (0, 0))
        screen.blit(fps_text, (WIDTH - text_w, 0))
        screen.blit(ping_text, (WIDTH - ping_text_w, text_h))

        for i in range(WIDTH):
            pygame.draw.line(screen, (0,0,0), [i, map_curve[i]], [i,HEIGHT], 1)
        

        if shooting_force != -1:
            if shooting_force < 50:
                shooting_force += 1
            
            pygame.draw.rect(screen, (255, 0, 0), [0, HEIGHT-(HEIGHT/20), WIDTH/50 * shooting_force, HEIGHT/20])

        for bullet in bullets[:]:
            if not bullet.update():
                if bullet.collide:
                    x = int(bullet.x)
                    for i in range(x-10, x+10):
                        map_curve[i] += 10
                bullets.remove(bullet)
                del bullet
            else:
                bullet.draw()

        pygame.display.flip()


        clock.tick(fps)

socket = main()
socket.close()