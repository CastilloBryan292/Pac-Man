
import pygame
from pygame import mixer
from settings import *

pygame.init()


class Pellets:
    def __init__(self, pos):
        self.pix_pos = pos
        self.grid_pos = self.get_grid_pos()

        # Gameplay Mechanics
        self.eaten = False
        self.value = 10
        self.value_added = False
        
        
    def get_grid_pos(self):
        return ((self.pix_pos[0] - top_bottom_buffer + 20//2)// 20 + 1,
                (self.pix_pos[1] - top_bottom_buffer + 20//2)//20 + 1)

    def get_rect(self):
        return pygame.Rect(self.pix_pos[0], self.pix_pos[1], 20, 20)


    def draw_pellet(self, screen, pellet):
        return screen.blit(pellet, (self.pix_pos[0], self.pix_pos[1]))
        

    def pellet_type(self):
        return "pellet"


class Super_Pellets:
    def __init__(self, pos):
        self.pix_pos = pos
        self.grid_pos = self.get_grid_pos()

        # Gameplay Mechanics
        self.eaten = False
        self.value = 50
        self.value_added = False

        # Sound effects
        self.power_pellet_sound = mixer.Sound(path + "\ogg files\power_pellet_siren.ogg")
        self.power_pellet_sound.set_volume(0.3)

    def get_grid_pos(self):
        return ((self.pix_pos[0] - top_bottom_buffer + 20//2)// 20 + 1,
                (self.pix_pos[1] - top_bottom_buffer + 20//2)//20 + 1)


    def get_rect(self):
        return pygame.Rect(self.pix_pos[0], self.pix_pos[1], 20, 20)


    def draw_super_pellet(self, screen, super_pellet):
        return screen.blit(super_pellet, (self.pix_pos[0], self.pix_pos[1]))


    def pellet_type(self):
        return "super_pellet"
