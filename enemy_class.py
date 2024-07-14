
import pygame
import math, random
from pygame import mixer
from settings import *

pygame.init()

class Enemy:
    def __init__(self, start_pos, ghost_type, wall_pos_list = [185, 275], intersection_list = [275, 275]):
        # Position
        self.pix_pos = start_pos
        self.grid_pos = self.get_grid_pos()

        # Initializers
        self.ghost = ghost_type
        self.state = self.get_initial_state()
        self.time_to_leave = True if self.ghost == "blinky" else False
        self.reached_center = False
         
        # Initial directions and their opposite counter parts
        self.direction = self.get_initial_direction() 
        self.string_direction = self.convert_vec_to_direction(self.direction)
        self.opposite_dict = {
                "left" : "right",
                "right" : "left",
                "up" : "down",
                "down" : "up" 
            }

        # All ghost initial target is the ghost house center
        # Gets updated based off Players pixel position
        # and type of ghost
        self.target = [305, 335]


        # Boundaries and places where the ghosts can move
        self.walls_pos = wall_pos_list
        self.intersections = intersection_list


        # Only for frightened State
        self.has_flipped = False
        self.start_blinking = False
        self.blinked = False
        self.blink_counter = 0
        self.blink_interval = 12
        
        # Only for idle state
        self.player_xcoord = 294

            
        # Sprite
        self.sprites = self.get_sprites()

        self.curr_index = 0
        self.curr_sprite = self.sprites[self.curr_index]
        self.rect = self.sprites[0].get_rect()
        self.hitbox = self.rect.inflate(-15,-15)
        self.move_counter = 0
        self.move_interval = 20
        self.walked = False
        
        # Sound effects
        self.eaten_sound = mixer.Sound(path + "\ogg files\ghost_eaten.ogg")
        self.ghost_sound = mixer.Sound(path + "\ogg files\ghost_noises.ogg")
        self.ghost_sound.set_volume(0.3)
        self.pellet_siren_playing = False



########################### Update #############################
        
    def update(self, player_pix_pos, player_direction = left, blinky_pix_pos = [305, 275]):
        self.off_screen_handler()

        # Update Target and Player x-coord 
        self.set_target(player_pix_pos, player_direction, blinky_pix_pos)
        self.player_xcoord = player_pix_pos[0]

        
        # Enemy Sprite
        self.rect.center = (int(self.pix_pos.x), int(self.pix_pos.y))
        self.hitbox.center = self.rect.center
        self.play_animation()

        
        if self.state == "frightened":
            # As soon as enemy enters frightened mode he will head in the opposite direction
            if not self.has_flipped:
                self.flip_direction()
                self.has_flipped = True
                
        
        self.pix_pos += self.direction 
        self.grid_pos = self.get_grid_pos()


        if self.state == "idle":
            self.idle()
            return

            
        if self.time_to_move():
            if self.state == "frightened":
                self.direction = self.frightened_move()
                self.string_direction = self.convert_vec_to_direction(self.direction)

            else:
                self.direction = self.calculate_best_move()
                self.string_direction = self.convert_vec_to_direction(self.direction)


        if self.state == "eaten":
            if self.pix_pos == self.target:
                self.direction = down
                self.state = "idle"

                        

    def set_target(self, player_pix_pos, player_direction, blinky_pix_pos):

        if self.state == "idle":
            return
        if self.state == "chase":
            self.set_chase_target(player_pix_pos, player_direction, blinky_pix_pos)
        elif self.state == "scatter":
            self.set_scatter_target()
        elif self.state == "eaten":
            self.set_eaten_target()
        else:
            self.set_chase_target(player_pix_pos, player_direction, blinky_pix_pos)

        
############################## Get #################################

    def get_scatter_target(self):
        if self.ghost == "blinky":
            return [575, 15]

        if self.ghost == "pinky":
            return [35, 15]

        if self.ghost == "inky":
            return [575, 655]

        elif self.ghost == "clyde":
            return [35, 655]

    
    def get_ghost(self):
        # Returns if ghost is blinky, pinky, inky or clyde
        return self.ghost


    def get_initial_state(self):
        if self.ghost == "blinky":
            return "chase"

        else:
            return "idle"


    def get_initial_direction(self):
        if self.ghost == "blinky":
            return left

        elif self.ghost == "pinky":
            return down

        else:
            return up


    def get_sprites(self):
        # Determines what sprites to use based off of what ghost it is
        # Ex. if ghost is blinky it will load blinky's sprites

        sprite_list = [ pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_1.PNG"),
                        pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_2.PNG"),
                        pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_3.PNG"),
                        pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_4.PNG"),
                        pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_5.PNG"),
                        pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_6.PNG"),
                        pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_7.PNG"),
                        pygame.image.load(path + fr"\png files\{self.ghost}_animations\{self.ghost}_8.PNG"),
                        pygame.image.load(path + "\png files\Frightened_animations\Frightened_1.PNG"),
                        pygame.image.load(path + "\png files\Frightened_animations\Frightened_2.PNG"),
                        pygame.image.load(path + "\png files\Frightened_animations\Frightened_3.PNG"),
                        pygame.image.load(path + "\png files\Frightened_animations\Frightened_4.PNG"),
                        pygame.image.load(path + "\png files\eaten_animations\eaten_1.PNG"), 
                        pygame.image.load(path + "\png files\eaten_animations\eaten_2.PNG"), 
                        pygame.image.load(path + "\png files\eaten_animations\eaten_3.PNG"), 
                        pygame.image.load(path + "\png files\eaten_animations\eaten_4.PNG")]

        return sprite_list
    

    def get_grid_pos(self):
        return ((self.pix_pos[0] - top_bottom_buffer + 20//2)// 20 + 1,
                (self.pix_pos[1] - top_bottom_buffer + 20//2)//20 + 1)


############################# Helper ###############################

    def enemy_reset(self, start_pos):
        # Position
        self.pix_pos = start_pos
        self.grid_pos = self.get_grid_pos()

        # Movement
        self.state = self.get_initial_state()
        self.direction = self.get_initial_direction()
        self.string_direction = self.convert_vec_to_direction(self.direction)
        self.time_to_leave = True if self.ghost == "blinky" else False
        self.reached_center = False

        # Target
        self.target = [305, 335]

        # Boundaries and areas where enemy is allowed to move
        self.walls_pos.clear()
        self.intersections.clear()

        # Frightened mode flip
        self.has_flipped = False

        # Animation
        self.curr_index = 0
        self.curr_sprite = self.sprites[self.curr_index]

        # Sound effects
        self.pellet_siren_playing = False
        
    
    def death_reset(self, start_pos):
        # Position
        self.pix_pos = start_pos
        self.grid_pos = self.get_grid_pos()

        # Movement
        self.state = self.get_initial_state()
        self.direction = self.get_initial_direction()
        self.string_direction = self.convert_vec_to_direction(self.direction)
        self.time_to_leave = True if self.ghost == "blinky" else False
        self.reached_center = False

        # Target
        self.target = [305, 335]

        # Frightened mode flip
        self.has_flipped = False

        # Animation
        self.curr_index = 0
        self.curr_sprite = self.sprites[self.curr_index]

        # Sound effects
        self.pellet_siren_playing = False        

    
    # Should only be called once per level
    # per ghost in the App class under
    # generate walls function
    def set_walls_pos(self, wall_pos_list):
        self.walls_pos = wall_pos_list
        

    # Should only be called once per level
    # per ghost in the App class under
    # generate pellets function
    def set_intersections(self, intersect_list):
        self.intersections = intersect_list


    def set_enemy_state(self, state):
        self.state = state
        
            
    def draw(self, screen):
        # Tester in place of sprite

        if self.state == "frightened":
            pygame.draw.circle(screen , blue,
            (int(self.pix_pos.x), int(self.pix_pos.y)), 20//2 -2)

        else:
            if self.ghost == "blinky":
                pygame.draw.circle(screen , red,
                (int(self.pix_pos.x), int(self.pix_pos.y)), 20//2 -2)
            elif self.ghost == "pinky":
                pygame.draw.circle(screen , pink,
                (int(self.pix_pos.x), int(self.pix_pos.y)), 20//2 -2)
            elif self.ghost == "inky":
                pygame.draw.circle(screen , cyan,
                (int(self.pix_pos.x), int(self.pix_pos.y)), 20//2 -2)
            elif self.ghost == "clyde":
                pygame.draw.circle(screen , orange,
                (int(self.pix_pos.x), int(self.pix_pos.y)), 20//2 -2)
        

    def convert_vec_to_direction(self, vec):
        if vec == left:
            return "left"

        elif vec == right:
            return "right"
            
        elif vec == up:
            return "up"
        
        elif vec == down:
            return "down"


    def convert_direction_to_vec(self, direction):
        if direction == "left":
            return left
        elif direction == "right":
            return right
        elif direction == "up":
            return up
        elif direction == "down":
            return down
        
        
    def flip_direction(self):
        self.direction = self.convert_direction_to_vec(self.opposite_dict[self.convert_vec_to_direction(self.direction)])
        self.string_direction = self.convert_vec_to_direction(self.direction)

        
    
########################## Movement ################################

    def time_to_move(self):
        # If ghost is in center of cell (this if statement checks for x position)
        # then he might be at a intersection
        # This also prevents him from coming off grid boundaries
        if int(self.pix_pos[0] + top_bottom_buffer//2) % 20 == 0:
            
            # Prevents from returning True if ghost is moving up since ghost will
            # always be at the center of the cell on the x coord while moving up
            if self.direction == right or self.direction == left:

                # This is also a good time to play the ghost sound effects
                if self.ghost == "blinky" and not self.pellet_siren_playing:
                    self.ghost_sound.play()
  
                # If ghost is at an intersection then he is allowed to move/change directions
                if (self.pix_pos[0]-10, self.pix_pos[1]-10) in self.intersections:
                    return True


        if int(self.pix_pos[1] + top_bottom_buffer//2) % 20 == 0:
            if self.direction == up or self.direction == down:
                
                if self.ghost == "blinky" and not self.pellet_siren_playing:
                    self.ghost_sound.play()
                    
                if (self.pix_pos[0]-10, self.pix_pos[1]-10) in self.intersections:
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


######################### Gamplay Functions ########################

    def find_available_tiles(self):
        available_spaces = []
        
        # Finds available spaces as well as sorts them in priority order
        # in case two tiles have the same distance from player

        #print(self.pix_pos)

        # Up
        if (int(self.pix_pos[0] - 10), int(self.pix_pos[1] - 30)) not in self.walls_pos:
            #                    direction       x                  y 
            available_spaces.append((up, int(self.pix_pos[0] - 10), int(self.pix_pos[1] - 30)))
            #print("U:ADDED")
            
        # Down
        if (int(self.pix_pos[0] - 10), int(self.pix_pos[1] + 10)) not in self.walls_pos:
            available_spaces.append((down, int(self.pix_pos[0] - 10), int(self.pix_pos[1] + 10)))
            #print("D:ADDED")
            
        # Left
        if (int(self.pix_pos[0] - 30), int(self.pix_pos[1] - 10)) not in self.walls_pos:
            available_spaces.append((left, int(self.pix_pos[0] - 30), int(self.pix_pos[1] - 10)))
            #print("L:ADDED")
            
        # Right
        if (int(self.pix_pos[0] + 10), int(self.pix_pos[1] - 10)) not in self.walls_pos:
            available_spaces.append((right, int(self.pix_pos[0] + 10), int(self.pix_pos[1] - 10)))
            #print("R:ADDED")

        return available_spaces


    def calculate_best_move(self):
        available_spaces = self.find_available_tiles()
        distances_list = []
        available_directions = []

        # Calculates all available spaces distance from their target
        for space in available_spaces:

            # This if statement prevents the ghost from turning 180 degrees
            # of the direction he was initially heading
            # So if he was moving left he now can't go right
            # only up, down, and left if they are available
            
            if self.convert_vec_to_direction(space[0]) != self.opposite_dict[self.string_direction]:
                distance = math.sqrt(((space[1] - self.target[0])**2) + ((space[2] - self.target[1])**2))
                distances_list.append(distance)
                available_directions.append(space[0])
                

        # Finds the available path with the shortest distance to the target
        # A.K.A the optimal path
        
        smallest_distance = min(distances_list)
        
        # Returns what direction the optimal path is in
        # A.K.A the direction the ghost should move

        return available_directions[distances_list.index(smallest_distance)]


    def frightened_move(self):
        # When enemies are in frightened mode instead of finding
        # an optimal path, they just choose random directions
        # these choices should still follow regular enemy rules such as
        # not being able to turn 180 degrees
        
        available_spaces = self.find_available_tiles()
        available_directions = [direction[0] for direction in available_spaces if self.convert_vec_to_direction(direction[0]) != self.opposite_dict[self.string_direction]]

        return random.choice(available_directions)


    def set_scatter_target(self):
        self.target = self.get_scatter_target()

    
    def set_eaten_target(self):
        self.target = [305, 275]

    
    def set_chase_target(self, player_pix_pos, player_direction, blinky_pix_pos):
        # Updates target based on ghost type

        ######### BLINKY #########
        # Blinky targets player's exact location
        
        if self.ghost == "blinky":
            self.target = player_pix_pos
        

        ######### PINKY ###########
        # Pinky targets 4 tiles infront of player
        
        elif self.ghost == "pinky":

            # 4 tiles infront of player depends on what direction he is facing
            # Checks and updates accordingly
            if player_direction == left:
                self.target = [player_pix_pos[0] - 80, player_pix_pos[1]]
            elif player_direction == right:
                self.target = [player_pix_pos[0] + 80, player_pix_pos[1]]
            elif player_direction == up:
                self.target = [player_pix_pos[0], player_pix_pos[1] - 80]
            elif player_direction == down:
                self.target = [player_pix_pos[0], player_pix_pos[1] + 80]


        ######### INKY #############
        # Inky's target can be found by targeting two tiles infront of the player
        # Then finding the position of blinky and his distance from those new tiles,
        # drawing a line connecting them, then flipping it around by 180 degrees.
        # The tile at the end of that flipped line is inky's target
        
        elif self.ghost == "inky":
            # Finds the tile two tiles infront of player
            if player_direction == left:
                two_infront = [player_pix_pos[0] - 40, player_pix_pos[1]]
            elif player_direction == right:
                two_infront = [player_pix_pos[0] + 40, player_pix_pos[1]]
            elif player_direction == up:
                two_infront = [player_pix_pos[0], player_pix_pos[1] - 40]
            elif player_direction == down:
                two_infront = [player_pix_pos[0], player_pix_pos[1] + 40]
            else:
                two_infront = player_pix_pos
                
            
            # Finds the distance between blinky and the new tiles
            blinky_infront_diff = [blinky_pix_pos[0] - two_infront[0], blinky_pix_pos[1] - two_infront[1]]

            # Subtracts that from the two infront position to emulate flipping
            # a line around by 180 degrees
            # Ex. Blinky_pos = [5, 6], Two_tiles_infront = [4, 4],
            # 5 - 4 = 1, 6 - 4 = 2
            # 4 - 1 = 3, 4 - 2 = 2
            # So inkys target will be [3, 2] 
            
            self.target = [two_infront[0] - blinky_infront_diff[0], two_infront[1] - blinky_infront_diff[1]]
        

        ######## CLYDE #############
        # Clyde targets player's exact location if he is at least 8 blocks away
        # If he is any closer he will target his scatter target
        
        elif self.ghost == "clyde":
            clyde_player_distance = math.sqrt(((self.pix_pos[0] - player_pix_pos[0])**2) + ((self.pix_pos[1] - player_pix_pos[1])**2))

            if clyde_player_distance >= 160:
                self.target = player_pix_pos

            else:
                self.target = self.get_scatter_target()

    def idle(self):
        
        if self.time_to_leave:
            if self.pix_pos == vec(305, 335):
                self.reached_center = True
                self.direction = up
                self.string_direction = self.convert_vec_to_direction(self.direction)

            elif self.pix_pos == vec(305, 275):
                if self.player_xcoord <= 295:
                    self.direction = left
                else:
                    self.direction = right
                    
                self.string_direction = self.convert_vec_to_direction(self.direction)
                self.state = "chase"

            elif not self.reached_center:
                if self.pix_pos[1] <= 315:
                    self.direction = down
                    self.string_direction = self.convert_vec_to_direction(self.direction)

                if self.pix_pos[1] >= 355:
                    self.direction = up
                    self.string_direction = self.convert_vec_to_direction(self.direction)
                    
                if self.ghost == "inky":
                    if self.pix_pos == vec(275, 335):
                        self.direction = right

                elif self.ghost == "clyde":
                    if self.pix_pos == vec(335, 335):   
                        self.direction = left

        else:
            if self.pix_pos[1] <= 315:
                self.direction = down
                self.string_direction = self.convert_vec_to_direction(self.direction)

            if self.pix_pos[1] >= 355:
                self.direction = up
                self.string_direction = self.convert_vec_to_direction(self.direction)
                

############################## Animation ###############################    

    def play_animation(self):

        # Moves enemies feet
        self.move_counter += 1
        if self.move_counter >= self.move_interval:
                self.move_counter = 0
                self.walked = not self.walked

        if self.state == "chase" or self.state == "scatter" or self.state == "idle":
            
            if self.direction == left:
                self.curr_index = 0 if self.walked else 1    

            elif self.direction == right:
                self.curr_index = 2 if self.walked else 3

            elif self.direction == up:
                self.curr_index = 4 if self.walked else 5

            elif self.direction == down:
                self.curr_index = 6 if self.walked else 7
                
        elif self.state == "frightened":
            if not self.start_blinking:
                self.curr_index = 8 if self.walked else 9
            else:
                self.blink_counter += 1
                if self.blink_counter >= self.blink_interval:
                    self.blink_counter = 0
                    self.blinked = not self.blinked

                if self.blinked:
                    self.curr_index = 8 if self.walked else 9
                else:
                    self.curr_index = 10 if self.walked else 11

        elif self.state == "eaten":
            
            if self.direction == left:
                self.curr_index = 12

            elif self.direction == right:
                self.curr_index = 13

            elif self.direction == up:
                self.curr_index = 14
    
            elif self.direction == down:
                self.curr_index = 15

        
        self.curr_sprite = self.sprites[self.curr_index]             












   
