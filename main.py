import pygame
import game_map

WIDTH = 1280
HEIGHT = 720

def main():

    fps = 30

    pygame.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen_w, screen_h = screen.get_size()

    map_curve = game_map.generate(WIDTH, HEIGHT)

    #icon = pygame.image.load("pygame-icon.png")
    #icon = icon.convert_alpha()
    #icon_w, icon_h = icon.get_size()

    font = pygame.font.Font("DejaVuSans.ttf", 24)
    #text = font.render('aaaa', True, (255, 255, 255, 255))
    #text_w, text_h = text.get_size()

    #sleeping = False

    # On startup, load state saved by APP_WILLENTERBACKGROUND, and the delete
    # that state.
    #x, y = load_state()
    #delete_state()

    while True:

        #socket.send('oi')
        #newText = socket.recv(1024)
        #text = font.render('aaaaaa', True, (255, 255, 255, 255))
        #text_w, text_h = text.get_size()

        screen.fill( (0,0,0) )

        #screen.blit(text, (screen_w / 2 - text_w / 2, screen_h / 2 - text_h / 2))

        for i in range(WIDTH):
            pygame.draw.line(screen, (255,255,255), [i, map_curve[i]], [i,HEIGHT], 1)
        
        pygame.display.flip()


        clock.tick(fps)

main()