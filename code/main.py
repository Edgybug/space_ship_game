import pygame
from random import randint
from os.path import join

#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
running = True

#plain surface
surf = pygame.Surface((100,200))
surf.fill("orange")
x = 100

#importing an image
player_surf = pygame.image.load(join('images', 'player.png')).convert_alpha()
star = pygame.image.load(join('images', 'star.png')).convert_alpha()
star_positions = [(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)) for i in range(20)] #create random star positions

       
while running:
    # event loop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #background
    display_surface.fill('darkgray')
   
    #display stars on the background
    for pos in star_positions:
        display_surface.blit(star, pos)

    #draw player
    display_surface.blit(player_surf,(x, 150))
    
    #update all elements from the while loop
    pygame.display.flip() 

pygame.quit()

