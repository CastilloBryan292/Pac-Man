
import pygame
from settings import *


pygame.init()


class Walls:
    def __init__(self, pos):
        self.pix_pos = pos
        self.wall = pygame.Rect(self.pix_pos[0], self.pix_pos[1], 20, 20)
        self.grid_pos = self.get_grid_pos()

    
    def get_grid_pos(self):
        return ((self.pix_pos[0] - top_bottom_buffer + 20//2)// 20 + 1,
                (self.pix_pos[1] - top_bottom_buffer + 20//2)//20 + 1)
