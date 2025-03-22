import pygame
from random import randint, uniform
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2 , WINDOW_HEIGHT/2))
        self.direction = pygame.math.Vector2()
        self.speed = 300
      
        # cooldown section
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400 #milseconds

        #mask used for collisions
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks() #get time since the game has started
            if current_time - self.laser_shoot_time >= self.cooldown_duration: 
                self.can_shoot = True

    def update(self, dt):

        #BASIC MOVEMENT
        keys = pygame.key.get_pressed()
    
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]) # if right 1-0 = 1 going +1, if left 0 - 1 = -1 going -1
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]) # same as above

        #fix diagonal speed  by normalizing the vector, normalize only if there is a value for player direction.
        self.direction = self.direction.normalize() if self.direction else self.direction

        #standart for updating player position with a vector and speed and ajusting with delta time
        self.rect.center += self.direction * self.speed * dt 

        #capture only 1 fire event with "just_pressed"
        recent_keys = pygame.key.get_just_pressed() 
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks() #get the time of the shoot
            laser_sound.play()
            laser_sound.set_volume(0.2)
        self.laser_timer()      

class Star(pygame.sprite.Sprite):
    def __init__(self, *groups, surface):
        super().__init__(*groups)
        self.image = surface
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, *groups):
        super().__init__(*groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks() #initiate timer on create
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)  
        self.speed = randint(400,500)

        self.rotation = 0
        self.rotation_speed = randint(40,80)
        

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        
        if pygame.time.get_ticks() - self.start_time >= self.lifetime: #kill meteor after 2 seconds
            self.kill()

        #continuous rotations of the Asteroids
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center) 

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, *groups):
        super().__init__(*groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions(): 
    global running
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            explosion_sound.set_volume(0.2)
def display_score():
    current_time = int(pygame.time.get_ticks() / 100)
    text_surf = font.render(str(current_time), True, (255,255,255))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    #add rect arround the text and allign it with inflate and move
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10) 

#general setup
pygame.mixer.pre_init()
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock()

#import
surf = pygame.image.load(join('images', 'star.png')).convert_alpha() 
meteor = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images','explosion', f'{i}.png')).convert_alpha() for i in range(21)] #load explosion images

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.2)
game_music.play()

#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sprites, surface=surf)
player = Player(all_sprites)

#custom events -> meteor
meteor_event = pygame.event.custom_type() #custom timer that triggers every X seconds based on event
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick() / 1000 # delta time in seconds

    # event loop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor,(x,y), (all_sprites, meteor_sprites))
    all_sprites.update(dt)
    collisions()
    
    #background
    display_surface.fill('#3a2e3f')
    display_score()
    all_sprites.draw(display_surface)
   
    pygame.display.flip() 

pygame.quit()

