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


WIDTH = 1280
HEIGHT = 720

PORT = 5006

def textOnMiddle(screen, text, font):
    text = font.render(text, True, (255, 255, 255))
    text_w, text_h = text.get_size()

    screen.blit(text, (WIDTH/2 - text_w/2, HEIGHT/2 - text_h/2))

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
            s.bind(('127.0.0.1', PORT))
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

            conn, addr = s.accept()
        except KeyboardInterrupt:
            print('Closing Server...')
            return s
    
        screen.fill( (0,0,0) )
        textOnMiddle(screen, 'Generating map...', font)
        pygame.display.flip()
        map_curve = game_map.generate(WIDTH, HEIGHT, 2500)
        msg = bytes(json.dumps(map_curve), 'utf-8')
        conn.send(bytes(str(len(msg)), 'utf-8'))
        conn.recv(2)
        conn.send(msg)
        #return s

    elif TYPE == 'JOIN':
        textOnMiddle(screen, 'Joining...', font)
        pygame.display.flip()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', PORT))
        msg_len = s.recv(64)
        s.send(b'ok')
        msg = s.recv(int(msg_len))
        msg = msg.decode("utf-8")
        print(msg)
        map_curve = json.loads(msg)
        # return s
    #screen.blit(fps_text, (WIDTH - text_w, 0))


    #icon = pygame.image.load("pygame-icon.png")
    #icon = icon.convert_alpha()
    #icon_w, icon_h = icon.get_size()

    #text = font.render('aaaa', True, (255, 255, 255, 255))
    #text_w, text_h = text.get_size()

    #sleeping = False

    # On startup, load state saved by APP_WILLENTERBACKGROUND, and the delete
    # that state.
    #x, y = load_state()
    #delete_state()


    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                conn.close()
                pygame.quit()

                print('Closing Server...')
                return s


        #socket.send('oi')
        #newText = socket.recv(1024)
        

        text = font.render('10uv >>', True, (255, 255, 255))
        fps_text = font.render(f'{round(clock.get_fps(),2)} fps', True, (255, 255, 255))
        
        text_w, _ = fps_text.get_size()

        screen.fill( (0,0,0) )

        screen.blit(text, (0, 0))
        screen.blit(fps_text, (WIDTH - text_w, 0))

        for i in range(WIDTH):
            pygame.draw.line(screen, (255,255,255), [i, map_curve[i]], [i,HEIGHT], 1)
        
        pygame.display.flip()


        clock.tick(fps)

socket = main()
socket.close()