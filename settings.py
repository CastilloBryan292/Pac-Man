
import os
from pygame.math import Vector2 as vec

# File path
path = os.getcwd()

# screen settings
# 610, 670
width, height = 610, 670
fps = 60
top_bottom_buffer = 50
maze_width , maze_height = width - top_bottom_buffer, height - top_bottom_buffer
maze_start_text = (265, 382)

# player settings
player_starting_pos = vec(13, 24)


# controls
left = vec(-1, 0)
right = vec(1, 0)
up = vec(0, -1)
down = vec(0, 1)
still = vec(0,0)


# start screen
start_text = (140, 250)
start_exit_text = (205, 280)


# pause screen
pause_center = (215,200)
continue_text = (115, 250)
quit_text = (205, 280)


# game over screen
game_over_center = (190, 200)
play_again_text = (110, 250)
game_over_quit = (205, 280)


# color settings
black = (0, 0, 0)
grey = (107, 107, 107)
white = (255, 255, 255)
yellow = (255,255,0)
red = (208, 22, 22)
pink = (255, 192, 203)
cyan = (0 , 255, 255)
orange = (255, 140, 0)
blue = (0, 0, 255)
player_color = (255,211,67)


# fonts
classic = "ARCADECLASSIC.ttf"
pac_font = "PAC-FONT.ttf"
arcade = "ARCADE.ttf"
