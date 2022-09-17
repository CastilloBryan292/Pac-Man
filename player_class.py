
import pygame
from settings import *
from pygame import mixer

vec = pygame.math.Vector2


class Player:

    def __init__(self, app, pos):

        # Position and movement
        self.app = app
        self.grid_pos = pos
        self.pix_pos = self.get_pix_pos()
        self.lives = 2
        self.direction = left
        self.stored_direction = None
        self.last_location = self.get_pix_pos()
        
        # Player Sprite
        self.sprites = [pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-0.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-1.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-2.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-3.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-4.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-5.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-6.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-7.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-8.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-9.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-10.png"),
                        pygame.image.load(path + "\png files\pac_man_animations\pixil-frame-11.png")]
                        
        self.curr_index = 0
        self.replay_animation = -1
        self.animation_played = False
        self.sprite_length = len(self.sprites)
        
        self.curr_sprite = self.sprites[self.curr_index]
        self.rect = self.curr_sprite.get_rect()


        # Death Sprites
        self.death_sprites = self.get_death_sprites()
        self.death_sprites_length = len(self.death_sprites)
        self.died = False
        self.death_animation_finished = False
        

        # Sound effects
        self.waka = mixer.Sound(path + "\ogg files\waka_waka.ogg")
        self.waka.set_volume(0.8)
        self.extra_life = mixer.Sound(path + "\ogg files\extra_life.ogg")
        self.death_sound = mixer.Sound(path + "\ogg files\death_sound.ogg")
        
        
########################### Update ########################
        
    def update(self):
        self.off_screen_handler()

        self.pix_pos += self.direction
        
        if self.time_to_move():
            if self.stored_direction:
                self.direction = self.stored_direction


        # Pac-Man sprite
        self.rect.center = (int(self.pix_pos.x), int(self.pix_pos.y))

        if not self.direction == still:
            self.play_animation()

        
        # Grid position in reference to pix pos
        # X
        self.grid_pos[0] = (self.pix_pos[0] - top_bottom_buffer \
        + self.app.cell_width//2)//self.app.cell_width + 1
        # Y
        self.grid_pos[1] = (self.pix_pos[1] - top_bottom_buffer \
        + self.app.cell_height//2)//self.app.cell_height + 1
        

    def get_pix_pos(self):
        return vec((self.grid_pos.x * self.app.cell_width) \
        + top_bottom_buffer//2 + self.app.cell_width//2,
        (self.grid_pos.y * self.app.cell_height) + \
        top_bottom_buffer//2 + self.app.cell_height//2)
    

############################## Movement ##################################    

    def move(self, direction):
        self.stored_direction = direction


    def time_to_move(self):
        # Checks if Pac-Man is in center of cell 
        if int(self.pix_pos.x + top_bottom_buffer//2) % self.app.cell_width == 0:
            self.last_location = self.get_pix_pos()
            
            # If so and direction is the way he is moving
            if self.direction == right or self.direction == left or self.direction == still:
                return True

        if int(self.pix_pos.y + top_bottom_buffer//2) % self.app.cell_width == 0:
            self.last_location = self.get_pix_pos()
            
            if self.direction == up or self.direction == down or self.direction == still:
                return True
            

    def off_screen_handler(self):   
        if self.pix_pos[0] < 35:
            self.pix_pos[0] = 575

        if self.pix_pos[0] > 575:
            self.pix_pos[0] = 35
        
        if self.pix_pos[1] < 35:
            self.pix_pos[1] = 635

        if self.pix_pos[1] > 635:
            self.pix_pos[1] = 35


######################### Helper Functions ##############################

    def player_reset(self):
        # Movement and position
        self.grid_pos = vec(13, 24)
        self.pix_pos = self.get_pix_pos()
        self.stored_direction = None
        self.direction = left

        # Gameplay
        self.lives = 2

        # Animation
        self.curr_index = 0
        self.replay_animation = -1
        self.animation_played = False
        self.curr_sprite = self.sprites[self.curr_index]

        # Death Animation
        self.died = False
        self.death_animation_finished = False


    def death_reset(self):
        # Movement and position
        self.grid_pos = vec(13, 24)
        self.pix_pos = self.get_pix_pos()
        self.stored_direction = None
        self.direction = left
        
        # Gameplay
        self.lives -= 1

        # Animation
        self.curr_index = 0
        self.replay_animation = -1
        self.animation_played = False
        self.curr_sprite = self.sprites[self.curr_index]

        
    def level_reset(self, grd_pos):
        # Movement and position
        self.grid_pos = grd_pos
        self.pix_pos = self.get_pix_pos()
        self.stored_direction = None
        self.direction = left

        # Animation
        self.curr_index = 0
        self.replay_animation = -1
        self.animation_played = False
        self.curr_sprite = self.sprites[self.curr_index]

        # Death Animation
        self.died = False
        self.death_animation_finished = False

       
    def draw(self):
            
        #Pac-Man circle
        """pygame.draw.circle(self.app.screen , yellow,
        (int(self.pix_pos.x), int(self.pix_pos.y)), self.app.cell_width//2 -2) # self.app.cell_width//2 -2"""
        
        # Pac-Man test tracker
        pygame.draw.rect(self.app.screen, red, \
        (self.grid_pos[0] * self.app.cell_width + top_bottom_buffer//2, \
        self.grid_pos[1] * self.app.cell_height + top_bottom_buffer//2, \
        self.app.cell_width, self.app.cell_height), 1)
        
    
########################## Animation #######################################

    def play_animation(self):
        if self.curr_index + 1 == self.sprite_length:
            self.curr_index = 0
            self.animation_played = True

        elif self.replay_animation - 1 < self.sprite_length * -1:
            self.replay_animation = -1
            self.animation_played = False

        if not self.animation_played:
            self.curr_index += 1
            self.curr_sprite = self.sprites[self.curr_index]
            
            if self.direction == right:
                self.curr_sprite = pygame.transform.rotate(self.curr_sprite, 180)
            if self.direction == up:
                self.curr_sprite = pygame.transform.rotate(self.curr_sprite, 270)
            if self.direction == down:
                self.curr_sprite = pygame.transform.rotate(self.curr_sprite, 90)

        else:
            self.curr_sprite = self.sprites[self.replay_animation]
            self.replay_animation -= 1

            if self.direction == right:
                self.curr_sprite = pygame.transform.rotate(self.curr_sprite, 180)
            if self.direction == up:
                self.curr_sprite = pygame.transform.rotate(self.curr_sprite, 270)
            if self.direction == down:
                self.curr_sprite = pygame.transform.rotate(self.curr_sprite, 90)
    

    def get_death_sprites(self):
        return [pygame.image.load(path + "\png files\death_animations\pixil-frame-0.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-1.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-2.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-3.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-4.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-5.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-6.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-7.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-8.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-9.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-10.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-11.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-12.png"),
                pygame.image.load(path + "\png files\death_animations\pixil-frame-13.png")]


        











    

                

        
