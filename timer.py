
import pygame
from settings import *


pygame.init()


class Timer:

    def __init__(self):
        # Main Timer
        # 20100
        self.counter = 20100
        self.enemy_leave_timer = self.counter//100 - 1
        self.text = str(self.counter//100)
        self.font = pygame.font.Font(arcade, 30)

        # Timer for enemy state
        # Initial state is chase
        self.index = 0
        self.enemy_state_list = ["chase", "scatter"]
        self.enemy_state = self.enemy_state_list[self.index]

        # Chase/ Scatter timer
        self.chase_scatter_timer = self.counter//100 - 21
        self.exited_scatter_state = False
        self.scatter_break_count = 0

        # Frightened Timer
        self.frightened_timer = self.counter//100
        self.frightened_timer_set = False
        self.blink_timer = self.frightened_timer
        self.start_blinking = False
        
        
    def run_timer(self):
        if self.counter//100 > 0:
            self.counter -= 1
            self.text = str(self.counter//100)
        else:
            self.text = "TIME'S UP"
                

    def times_up(self):
        return self.text == "TIME'S UP"
    

######################### Helper ###############################

    def timer_reset(self):
        # Main timer reset
        self.counter = 20100
        self.enemy_leave_timer = self.counter//100 - 1
        self.text = str(self.counter//100)

        # Enemy state reset
        self.index = 0
        self.enemy_state = self.enemy_state_list[self.index]

        # Chase/Scatter Timer Reset
        self.chase_scatter_timer = self.counter//100 - 21
        self.exited_scatter_state = False
        self.scatter_break_count = 0

        # Frightened Timer Reset
        self.frightened_timer = self.counter//100 
        self.frightened_timer_set = False


    def update_enemy_leave_timer(self):
        self.enemy_leave_timer = self.counter//100
        

    def get_enemy_leave_time(self, ghost):
        if ghost == "pinky":
            return self.enemy_leave_timer - 3

        elif ghost == "inky":
            return self.enemy_leave_timer - 5

        elif ghost == "clyde":
            return self.enemy_leave_timer - 7

        else:
            return 200
    

    def times_up_delay(self):
        event = pygame.USEREVENT 
        pygame.time.set_timer(event, 1000)
        
        delay = 2
        while delay > 0:
            for e in pygame.event.get():
                if e.type == pygame.USEREVENT:
                    delay -= 1


##################### Enemy Functions ########################
    
    def enemy_state_timer(self):
        # Chase state last for 20 seconds
        # Scatter state last for 7
        # Frightened mode lasts for 5 seconds

        # Checks if the enemy state needs to be updated to either chase or scatter
        if self.counter//100 == self.chase_scatter_timer:
            if self.index >= 1:
                self.index = 0

            else:
                self.index += 1
            

            if self.exited_scatter_state:
                self.chase_scatter_timer = self.counter//100 - 20
                self.exited_scatter_state = False

            else:
                self.chase_scatter_timer = self.counter//100 - 7
                self.exited_scatter_state = True
                self.scatter_break_count += 1


        if self.enemy_state == "frightened":

            # Sets frightened mode to last for 5 seconds
            # Makes chase_scatter_timer to accomadate for this
            # Also sets timer for enemies to blink for player warning
            if not self.frightened_timer_set:
                self.frightened_timer = self.counter//100 - 6
                self.chase_scatter_timer -= 6
                self.frightened_timer_set = True
                self.blink_timer = self.frightened_timer + 2


            # Give player warning 
            if self.counter//100 ==  self.blink_timer:
                self.start_blinking = True
                

            # Checks if 5 seconds has passed
            # If it has, then enemies go back to the state (either chase or scatter)
            # they were in before they entered frightened mode
            if self.counter//100 == self.frightened_timer:
                self.enemy_state = self.enemy_state_list[self.index]
                self.frightened_timer_set = False
                self.start_blinking = False


            # Handles bug when all 4 enemies would get eaten then
            # the counter would go below frightened_timer
            # and the ghost would stay in frightened forever
            elif self.counter//100 < self.frightened_timer:
                self.enemy_state = self.enemy_state_list[self.index]
                self.frightened_timer_set = False
                
            
            # If not enemy stays in frightened mode
            else:
                self.enemy_state = "frightened"

            
            return self.enemy_state

        
        # After 4 scatter breaks the ghost will chase indefinitely        
        if self.scatter_break_count == 4:
            self.enemy_state = "chase"
            return self.enemy_state    

             
        self.enemy_state = self.enemy_state_list[self.index]                

        return self.enemy_state 







