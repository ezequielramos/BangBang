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
import hud

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

def hostOptions(screen, font):
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

    return s, game_map, conn

def joinOptions(screen, font):
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

    return s, game_map

def getInputEvents(screen, cannon1, cannon2, bullets, game_map, shooting_force, msg):

    quitGame = False

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
                    center = cannon2.base.rect.center
                    rot = cannon2.rot
                else:
                    center = cannon1.base.rect.center
                    rot = cannon1.rot

                bullets.append(Bullet(screen, game_map, center[0], center[1], shooting_force, rot))
                msg['shoot'] = {
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
            quitGame = True

    return shooting_force, quitGame

def main():

    fps = 30
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))

    pygame.font.init()
    font = pygame.font.Font("DejaVuSans.ttf", 24)

    if TYPE == 'HOST':
        s, game_map, conn = hostOptions(screen, font)
    elif TYPE == 'JOIN':
        s, game_map = joinOptions(screen, font)
    else:
        textOnMiddle(screen, 'Generating map...', font)
        pygame.display.flip()
        game_map = GameMap().generate(config.WIDTH, config.HEIGHT, 2500)


    #icon = pygame.image.load("pygame-icon.png")
    #icon = icon.convert_alpha()
    #icon_w, icon_h = icon.get_size()

    shooting_force = -1

    bullets = []

    cannon1 = Cannon(screen, game_map, 100, (0,255,0), 0)
    cannon2 = Cannon(screen, game_map, config.WIDTH-100, (255,0,0), 180)

    gameEnded = False

    while True:


        msg = {
            "cannon": {}
        }
        recv_msg = {}

        shooting_force, quitGame = getInputEvents(screen, cannon1, cannon2, bullets, game_map, shooting_force, msg)

        if quitGame:
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
                rot = cannon1.rot
                center = cannon1.base.rect.center
            else:
                rot = cannon2.rot
                center = cannon2.base.rect.center

            bullets.append(Bullet(screen, game_map, center[0], center[1] , recv_msg['shoot']['shooting_force'], rot))

        if 'cannon' in recv_msg:
            if 'rotation' in recv_msg['cannon']:
                rotation = recv_msg['cannon']['rotation']
                if TYPE == 'JOIN':
                    cannon1.rotating = rotation
                if TYPE == 'HOST':
                    cannon2.rotating = rotation

        ping = time.time() - ping

        #reset drawing
        screen.fill( (0,0,0) )

        #draw background
        game_map.printBackground(screen)

        #draw top info
        text = font.render('10uv >>', True, (255, 255, 255))
        fps_text = font.render( str(round(clock.get_fps(),2)) + ' fps', True, (255, 255, 255))
        ping_text = font.render('ping ' + str(int(ping * 1000)) + 'ms', True, (255, 255, 255))
        text_w, text_h = fps_text.get_size()
        ping_text_w, _ = ping_text.get_size()
        screen.blit(text, (0, 0))
        screen.blit(fps_text, (config.WIDTH - text_w, 0))
        screen.blit(ping_text, (config.WIDTH - ping_text_w, text_h))

        #draw map ground
        game_map.printGround(screen)

        #draw shoot bar
        if shooting_force != -1:
            if shooting_force < 50:
                shooting_force += 1
        
            hud.drawShootForce(screen, shooting_force)

        #draw shoot bar ruler
        hud.drawShootForceRuler(screen)

        #update and draw bullets
        for bullet in bullets[:]:
            if not bullet.update():
                if bullet.collide:
                    x = int(bullet.x)
                    collision_range = range(x-100, x+100)
                    for i in collision_range: #TODO: send this to game map
                        if len(game_map.map_curve) > i >= 0:
                            game_map.map_curve[i] += 10

                    if not cannon1.isAlive(collision_range):
                        winnerText = font.render('Cannon 2 won.', True, (255, 255, 255))
                        gameEnded = True
                        break
                    if not cannon2.isAlive(collision_range):
                        winnerText = font.render('Cannon 1 won.', True, (255, 255, 255))
                        gameEnded = True
                        break


                bullets.remove(bullet)
                del bullet
            else:
                bullet.draw()

        #update and draw cannons
        cannon1.update()
        cannon1.draw(screen)
        cannon2.update()
        cannon2.draw(screen)

        if gameEnded:
            while len(bullets) > 0:
                bullets.pop()
            winnerText_w, winnerText_h = winnerText.get_size()
            screen.blit(winnerText, (config.WIDTH/2 - winnerText_w/2, config.HEIGHT/2 - winnerText_h/2))

        #end drawing
        pygame.display.flip()

        clock.tick(fps)

socket = main()

if socket:
    socket.close()
