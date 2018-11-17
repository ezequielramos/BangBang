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
# import game_map
import socket
import json
import time
import random
from pygame.locals import KEYDOWN, KEYUP, K_SPACE, QUIT, K_UP, K_DOWN #pylint: disable=E0611

import config
from bullet import Bullet
from cannon import Cannon
from game_map import GameMap

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5001

if TYPE == 'JOIN':
    if len(sys.argv) >= 3:
        HOST = sys.argv[2]

def textOnMiddle(screen, text, font):
    text = font.render(text, True, (255, 255, 255))
    text_w, text_h = text.get_size()

    screen.blit(text, (config.WIDTH/2 - text_w/2, config.HEIGHT/2 - text_h/2))

def encodeDict(dict_var):
    return bytes(json.dumps(dict_var), 'utf-8')

def decodeDict(msg):
    return json.loads(msg.decode("utf-8"))

def main():

    fps = 30
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))

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
        print('Hosting on: '+HOST+':'+str(PORT))
        
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
        game_map = GameMap().generate(config.WIDTH, config.HEIGHT, 2500)
        msg = encodeDict(game_map.map_curve)
        conn.send(bytes(str(len(msg)), 'utf-8'))
        conn.recv(2)
        conn.send(msg)
        conn.recv(2)

    elif TYPE == 'JOIN':
        textOnMiddle(screen, 'Joining...', font)
        pygame.display.flip()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print('Can\'t connect to host.')
            return 
        
        msg_len = s.recv(64)
        s.send(b'ok')
        msg = b''
        while len(msg) < int(msg_len):
            msg += s.recv(int(msg_len))
            print(len(msg), msg_len)

        game_map = GameMap()
        game_map.map_curve = decodeDict(msg)
        s.send(b'ok')
    else:
        textOnMiddle(screen, 'Generating map...', font)
        pygame.display.flip()
        game_map = GameMap().generate(config.WIDTH, config.HEIGHT, 2500)


    #icon = pygame.image.load("pygame-icon.png")
    #icon = icon.convert_alpha()
    #icon_w, icon_h = icon.get_size()

    shooting_force = -1

    bullets = []

    cannon1 = Cannon(screen, game_map, 100, (0,255,0))
    cannon2 = Cannon(screen, game_map, config.WIDTH-100, (255,0,0))

    while True:

        msg = {
            "cannon": {}
        }
        recv_msg = {}

        for event in pygame.event.get():

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    shooting_force = 0

                if event.key == K_UP:
                    if TYPE == 'JOIN':
                        cannon2.rotating = -1
                        msg['cannon']['rotation'] = -1
                    else:
                        cannon1.rotating = 1
                        msg['cannon']['rotation'] = 1

                if event.key == K_DOWN:
                    if TYPE == 'JOIN':
                        cannon2.rotating = 1
                        msg['cannon']['rotation'] = 1
                    else:
                        cannon1.rotating = -1
                        msg['cannon']['rotation'] = -1
            
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    if TYPE == 'JOIN':
                        x = config.WIDTH - 100
                        direction = 'left'
                        center = cannon2.base.rect.center
                    else:
                        x = 100
                        direction = 'right'
                        center = cannon1.base.rect.center

                    bullets.append(Bullet(screen, game_map, center[0], center[1], shooting_force, 45, direction))
                    msg['shoot'] = {
                        'x': center[0],
                        'y': center[1],
                        'shooting_force': shooting_force
                    }
                    shooting_force = -1
                
                if event.key == K_UP or event.key == K_DOWN:
                    if TYPE == 'JOIN':
                        cannon2.rotating = 0
                    else:
                        cannon1.rotating = 0

                    msg['cannon']['rotation'] = 0

            if event.type == QUIT:
                pygame.font.quit()
                pygame.display.quit()

                if TYPE == 'HOST':
                    conn.close()

                if TYPE == 'JOIN' or TYPE == 'HOST': 
                    print('Closing Server...')
                    return s
                
                return

        ping = time.time()
        if TYPE == 'HOST':
            try:
                conn.send(encodeDict(msg))
                recv_msg = conn.recv(1024)
                recv_msg = decodeDict(recv_msg)
            except ConnectionResetError:
                print('Connection closed by client')
                conn.close()
                return s
            except json.decoder.JSONDecodeError:
                print('Connection closed by client')
                conn.close()
                return s

        elif TYPE == 'JOIN':
            try:
                recv_msg = s.recv(1024)
                s.send(encodeDict(msg))
                recv_msg = decodeDict(recv_msg)
            except json.decoder.JSONDecodeError:
                print('Connection closed by host')
                return s
            except ConnectionResetError:
                print('Connection closed by host')
                return s


        if 'shoot' in recv_msg:
            if TYPE == 'JOIN':
                direction = 'right'
            else:
                direction = 'left'
            bullets.append(Bullet(screen, game_map, recv_msg['shoot']['x'], recv_msg['shoot']['y'] , recv_msg['shoot']['shooting_force'], 45, direction))

        if 'cannon' in recv_msg:
            if 'rotation' in recv_msg['cannon']:
                rotation = recv_msg['cannon']['rotation']
                if TYPE == 'JOIN':
                    cannon1.rotating = rotation
                if TYPE == 'HOST':
                    cannon2.rotating = rotation

        ping = time.time() - ping

        screen.fill( (0,0,0) )

        game_map.printBackground(screen)

        text = font.render('10uv >>', True, (255, 255, 255))
        fps_text = font.render( str(round(clock.get_fps(),2)) + ' fps', True, (255, 255, 255))
        ping_text = font.render('ping ' + str(int(ping * 1000)) + 'ms', True, (255, 255, 255))
        text_w, text_h = fps_text.get_size()
        ping_text_w, _ = ping_text.get_size()


        screen.blit(text, (0, 0))
        screen.blit(fps_text, (config.WIDTH - text_w, 0))
        screen.blit(ping_text, (config.WIDTH - ping_text_w, text_h))

        game_map.printGround(screen)


        #TODO: draw force rect
        if shooting_force != -1:
            if shooting_force < 50:
                shooting_force += 1
            
            pygame.draw.rect(screen, (255, 0, 0), [0, config.HEIGHT-(config.HEIGHT/20), config.WIDTH/50 * shooting_force, config.HEIGHT/20])

        #TODO: draw force ruler 
        pygame.draw.line(screen, (255,255,255), (0,config.HEIGHT-(config.HEIGHT/20)), (config.WIDTH, config.HEIGHT-(config.HEIGHT/20)), 3)

        for i in range(1,8):
            x_pos = i * config.WIDTH/8
            pygame.draw.line(screen, (255,255,255), (x_pos,config.HEIGHT), (x_pos, config.HEIGHT-(config.HEIGHT/40)), 3)

        for i in range(1,16):
            x_pos = i * config.WIDTH/16
            pygame.draw.line(screen, (255,255,255), (x_pos,config.HEIGHT), (x_pos, config.HEIGHT-(config.HEIGHT/80)), 1)

        for bullet in bullets[:]:
            if not bullet.update():
                if bullet.collide:
                    x = int(bullet.x)
                    for i in range(x-10, x+10): #TODO: send this to game map
                        if i >= 0 and i < len(game_map.map_curve):
                            game_map.map_curve[i] += 10
                bullets.remove(bullet)
                del bullet
            else:
                bullet.draw()

        cannon1.update()
        cannon1.draw(screen)
        cannon2.update()
        cannon2.draw(screen)

        pygame.display.flip()


        clock.tick(fps)

socket = main()

if socket:
    socket.close()
