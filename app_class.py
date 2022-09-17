
from pygame import *
import sys
from player_class import *
from settings import *
from timer import *
from walls_class import *
from pellets_class import * 
from enemy_class import *


pygame.init()
vec = pygame.math.Vector2

class App:

    def __init__(self):
        # Initializers
        self.screen = pygame.display.set_mode((width, height))
        self.running = True
        self.state = "start"
        self.clock = pygame.time.Clock()
        self.start_delayed_played = False
        self.playing_state_loaded = False
        self.level = 1
        

        ###### Files #####

        # Music
        mixer.music.load(path + "\ogg files\Pac-man-theme-remix.ogg")
        mixer.music.play(-1)

        # Chimes
        self.pause_chime = mixer.Sound(path + "\ogg files\pause_chime.ogg")
        self.game_over_chime = mixer.Sound(path + "\ogg files\game_over_chime.ogg")
        self.win_chime = mixer.Sound(path + "\ogg files\pac_man_intermission.ogg")
        self.maze_chime = mixer.Sound(path + "\ogg files\maze_chime.ogg")
        self.game_over_chime_played = False
        self.win_chime_played = False
        self.maze_chime_played = False
        
        # Images
        self.bg_img = pygame.image.load(path + f"\png files\maze_background{self.level}.png")
        self.start_logo = pygame.image.load(path + "\png files\pacman_start_screen.png")
        self.win_logo = pygame.image.load(path + "\png files\pacman_win_screen.png")
        self.pellet = pygame.image.load(path + "\png files\pellet.png")
        self.super_pellet = pygame.image.load(path + "\png files\super_pellet.png")
        self.lives_image = pygame.image.load(path + "\png files\pacman_standard.png")

        ####################
        
        # Maze cells
        self.cell_width = maze_width //28
        self.cell_height = maze_height // 30

        # Imports
        self.player = Player(self, player_starting_pos)
        self.timer = Timer()

        # Enemies
        self.blinky = Enemy(vec(305, 275), "blinky")
        self.pinky = Enemy(vec(305, 335), "pinky")
        self.inky = Enemy(vec(275, 335), "inky")
        self.clyde = Enemy(vec(335, 335), "clyde")
        self.enemy_list = [self.blinky, self.pinky, self.inky, self.clyde]

        # Maze
        self.score = 0
        self.last_score = 0
        self.final_level = 6
        self.walls_list = []
        self.pellets_list = []
        self.walls_pix_pos = []
        self.intersections_list = []
        self.pellet_count = 0
        self.pellets_counted = False
        self.generated_walls = False
        self.generated_pellets = False
        self.maze = self.get_mazes() 
        
        # TEST
        
        

############################# Core ##############################

    def run(self):
        while self.running:
            if self.state == "start":
                self.start_events()
                self.start_draw()
            elif self.state == "playing":
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == "game over":
                self.game_over_events()
                self.game_over_draw()
            elif self.state == "win":
                self.win_events()
                self.win_draw()
            else:
                self.running = False
        
            self.clock.tick(fps)
            
        pygame.quit()
        sys.exit()


############################ Start Functions ########################### 

    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = "playing"
                mixer.music.pause()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.running = False


    def start_draw(self):
        
        if not self.start_delayed_played:
            self.start_delayed_played = True
            pygame.time.delay(820)
        
        self.screen.fill(black)
        self.draw_start_screen()
        pygame.display.update()
        

########################### Playing Functions ###########################
                
    def playing_events(self):
        if not self.generated_walls:
            self.generate_walls(self.maze[self.level])
            self.generated_walls = True

        self.collision_detection()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(left)
                if event.key == pygame.K_RIGHT:
                    self.player.move(right)
                if event.key == pygame.K_UP:
                    self.player.move(up)
                if event.key == pygame.K_DOWN:
                    self.player.move(down)
                if event.key == pygame.K_SPACE:
                    self.pause_chime.play()
                    self.pause()


    def playing_update(self):
        self.game_over_checker()

        # State/Level Update
        if self.pellet_count == 0 and self.pellets_counted:
            self.level += 1
            self.timer.times_up_delay()
            
            if self.level == self.final_level:
                self.state = "win"
                return
            
            else:
                self.screen.fill(black)
                pygame.display.update()
                pygame.time.delay(400)
                self.level_reset(vec(13, 24), vec(305, 275), vec(305, 335), vec(275, 335), vec(335, 335))

            

        # Player Update
        self.player.update()
        
        
        # Enemy Update
        for enemy in self.enemy_list:
            if enemy.state == "idle":
                if self.timer.get_enemy_leave_time(enemy.ghost) == self.timer.counter//100:
                    enemy.time_to_leave = True
            
            elif not enemy.state == "eaten" and not enemy.state == "idle":
                enemy.set_enemy_state(self.timer.enemy_state_timer())
            
            enemy.update(self.player.pix_pos, self.player.direction, self.blinky.pix_pos)


        if not self.timer.enemy_state_timer() == "frightened":
                self.blinky.pellet_siren_playing = False


    def playing_draw(self):
        if self.state == "start":
            self.screen.fill(black)
            pygame.display.update()
            return
        
        if self.level == self.final_level:
            return


        # Background
        self.screen.fill(black)
        self.load_background()

        # Generate
        self.generate_pellets(self.maze[self.level])


        # Displays
        #self.player.group.draw(self.screen)
        self.draw_timer()
        self.draw_score()
        self.draw_lives()


        # Helper
        #self.draw_grid()
        #self.player.draw()
        #print(self.intersections_list)
        
        
        #### Draw Key Elements

        if not self.player.died:
            # Player
            self.screen.blit(self.player.curr_sprite, self.player.rect)


            # Enemies
            for enemy in self.enemy_list:
                self.screen.blit(enemy.curr_sprite, enemy.rect)
                
        else:
            curr_index = 0

            while not self.player.death_animation_finished:
                self.screen.fill(black)
                self.load_background()
                self.generate_pellets(self.maze[self.level])
                self.draw_timer()
                self.draw_score()
                self.draw_lives()
                self.screen.blit(self.player.death_sprites[curr_index], self.player.rect)
                pygame.display.update()

                if curr_index + 1 == self.player.death_sprites_length:
                    curr_index = 0
                    self.player.death_animation_finished = True
                    pygame.time.delay(200)

                else:
                    curr_index += 1
                    pygame.time.delay(75)
            
            self.player.died = False
            self.player.death_animation_finished = False
            pygame.time.delay(400)
            
            
        if not self.maze_chime_played:
            self.maze_chime_played = True
            self.maze_chime.play()
            self.screen.blit(pygame.font.Font(classic, 25).render("READY!", True, yellow), maze_start_text)
            pygame.display.update()
            pygame.time.delay(4500)

       
        # Update
        self.playing_state_loaded = True
        pygame.display.update()


    def pause(self):
        mixer.music.load(path + "\ogg files\pause_music.ogg")
        mixer.music.play(-1)
        paused = True

        while paused:    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = False
                        mixer.music.pause()
                        self.pause_chime.play()

                    elif event.key == pygame.K_q:
                        paused = False
                        self.reset()
            
            self.screen.fill(black)
            self.draw_pause()
            pygame.display.update()
            self.clock.tick(5)
                    

########################## Game Over Functions ##########################

    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.reset()
                if event.key == pygame.K_SPACE:
                    self.reset("playing")
    


    def game_over_draw(self):
        if self.state == "start":
            self.game_over_chime.stop()
            self.screen.fill(black)
            pygame.display.update()
            return

        if self.state == "playing":
            self.game_over_chime.stop()
            return       

        if not self.game_over_chime_played:
            self.game_over_chime.play()
            self.game_over_chime_played = True
            
        self.screen.fill(black)
        self.draw_game_over()
        pygame.display.update()


############################## Win Functions ###################################
    
    def win_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.reset()
                if event.key == pygame.K_SPACE:
                    self.reset("playing")

    def win_draw(self):
        if self.state == "start":
            self.win_chime.stop()
            self.screen.fill(black)
            pygame.display.update()
            return

        if self.state == "playing":
            self.win_chime.stop()
            return

        if not self.win_chime_played:
            self.win_chime.play()
            self.win_chime_played = True

        self.draw_win()
        pygame.display.update()



############################ Draw Functions ###########################

    def draw_timer(self):
        self.screen.blit(self.timer.font.render("Time: " + self.timer.text, True, white), (25, 5))

    def draw_pause(self):
        self.screen.blit(pygame.font.Font(classic, 50).render("PAUSED", True, white), pause_center)
        self.screen.blit(pygame.font.Font(classic, 25).render("Press  the  spacebar  to  continue", True, white), continue_text)
        self.screen.blit(pygame.font.Font(classic, 25).render("Press  Q  to  quit", True, white), quit_text)
        
    def draw_game_over(self):
        self.screen.blit(pygame.font.Font(classic, 50).render("GAME OVER!", True, red), game_over_center)
        self.screen.blit(pygame.font.Font(classic, 25).render("Press  the  spacebar  to  play again", True, white), play_again_text)
        self.screen.blit(pygame.font.Font(classic, 25).render("Press  Q  to  quit", True, white), game_over_quit)


    def draw_start_screen(self):
        self.screen.blit(self.start_logo, (0, 0))
        

    def draw_score(self):
        self.screen.blit(pygame.font.Font(arcade, 30).render("Score: " + str(self.score), True, white), (250, 5))


    def draw_lives(self):
        x = 500

        for i in range(1, self.player.lives+1):
            self.screen.blit(self.lives_image, (x, 5))
            x += 20


    def draw_win(self):
        self.screen.blit(self.win_logo, (0,0))
        

        
############################## Helper Functions #############################

    def reset(self, state = "start"):
        
        # Player Reset
        self.player.player_reset()

        # Enemy reset
        self.blinky.enemy_reset(vec(305, 275))
        self.pinky.enemy_reset(vec(305, 335))
        self.inky.enemy_reset(vec(275, 335))
        self.clyde.enemy_reset(vec(335, 335))

        # Timer Reset
        self.timer.timer_reset()
        
        # State Reset
        self.start_delayed_played = False
        self.playing_state_loaded = False
        self.state = state

        # Maze Reset
        self.score = 0
        self.last_score = 0
        self.pellet_count = 0
        self.pellets_list.clear()
        self.walls_list.clear()
        self.walls_pix_pos.clear()
        self.intersections_list.clear()
        self.generated_walls = False
        self.generated_pellets = False
        self.pellets_counted = False

        # Level
        self.level = 1
        self.bg_img = pygame.image.load(path + f"\png files\maze_background{self.level}.png")

        # Start Music Reset         
        if self.state == "start":
            mixer.music.load(path + "\ogg files\Pac-man-theme-remix.ogg")
            mixer.music.play(-1)

        # Chimes
        self.game_over_chime_played = False
        self.maze_chime_played = False
        self.win_chime_played = False

    
    def death_reset(self):

        # Player Reset
        self.player.death_reset()

        # Enemy 
        self.blinky.death_reset(vec(305, 275))
        self.pinky.death_reset(vec(305, 335))
        self.inky.death_reset(vec(275, 335))
        self.clyde.death_reset(vec(335, 335))

        # Timer
        self.timer.update_enemy_leave_timer()


    def level_reset(self, plyr_pos, blky_pos, pnky_pos, inky_pos, clyd_pos):
        # Player Reset
        self.player.level_reset(plyr_pos)

        # Enemy reset
        self.blinky.enemy_reset(blky_pos)
        self.pinky.enemy_reset(pnky_pos)
        self.inky.enemy_reset(inky_pos)
        self.clyde.enemy_reset(clyd_pos)

        # Timer Reset
        self.timer.timer_reset()
        
        # State Reset
        self.playing_state_loaded = False

        # Maze
        self.pellet_count = 0
        self.pellets_list.clear()
        self.walls_list.clear()
        self.walls_pix_pos.clear()
        self.intersections_list.clear()
        self.generated_walls = False
        self.generated_pellets = False
        self.pellets_counted = False
        self.maze_chime_played = False

        # Level
        self.bg_img = pygame.image.load(path + f"\png files\maze_background{self.level}.png")

        
    def draw_grid(self):
        for x in range(width// self.cell_width):
            pygame.draw.line(self.bg_img, grey, (x * self.cell_width, 0), \
                            (x * self.cell_width, height))
        for y in range(height// self.cell_height):
            pygame.draw.line(self.bg_img, grey, (0, y * self.cell_height),  # (0, y * self.cell_height)
                            (width, y * self.cell_height)) # (width, y * self.cell_height)
            
    
############################### Load Functions ###############################
            
    def load_background(self):
        self.screen.blit(self.bg_img, (width//2 - maze_width//2, height//2 - maze_height//2))

        
############################# Gameplay Functions ##########################

    def game_over_checker(self):
         
        if self.timer.times_up():
            self.timer.times_up_delay()
            self.state = "game over"
        else:
             self.timer.run_timer()

        if self.player.lives <= 0:
            self.state = "game over"

            
        
    def collision_detection(self):

        # Wall Collision
        for wal in self.walls_list:
            if self.player.rect.colliderect(wal):                
                self.player.pix_pos = self.player.last_location
                self.player.direction = still
                self.player.stored_direction = still
                break


        # Enemy Collision
        for enemy in self.enemy_list:
            if self.player.rect.colliderect(enemy.hitbox):
                if self.playing_state_loaded:
                    if enemy.state == "chase" or enemy.state == "scatter":
                        self.player.died = True
                        self.death_reset()
                        self.player.death_sound.play()
                        break
                
                    if enemy.state == "frightened":
                        enemy.eaten_sound.play()
                        enemy.state = "eaten"
                        pygame.time.delay(400)
                        self.score += 200


        # Pellet and Super Pellet Collision
        # Pellet count and Score updater
        for pel in self.pellets_list:
            
            # Checks if player has collided with a pellet
            if self.player.grid_pos == pel.grid_pos:
                
                # Checks if a pellet has been eaten
                if not pel.value_added:
                    pel.eaten = True
                    self.pellet_count -= 1 
                    self.player.waka.play()
                    self.score += pel.value
                    pel.value_added = True

                    # Checks if a new life needs to be added
                    if self.score >= self.last_score + 2000:
                        if self.player.lives < 3:
                            self.player.lives += 1
                            self.player.extra_life.play()
                            
                        self.last_score = self.score

                    # Checks if the eaten pellet was a super pellet
                    if pel.pellet_type() == "super_pellet":
                        self.timer.enemy_state = "frightened"
                        pel.power_pellet_sound.play()
                        self.blinky.pellet_siren_playing = True
                        
                        for enemy in self.enemy_list:
                            if not enemy.state == "eaten" and not enemy.state == "idle":
                                enemy.has_flipped = False
                                enemy.set_enemy_state("frightened")
                


    def generate_walls(self, maze):
        
        # test coords - (125, 425)
        x = 25
        y = 25
        
        for line in maze:
            for char in line:
                if char == "W":
                    curr_wall = Walls((x, y))
                    self.walls_list.append(curr_wall.wall)
                    self.walls_pix_pos.append((x, y))
                    #print((x,y))


                    # Uncomment this to make invisible walls visible and call in playing_draw   
                    #pygame.draw.rect(self.screen, white, curr_wall.wall)

                if x + 20 <= 575: 
                    x += 20
                else:
                    x = 25

            if y + 20 <= 635:
                y += 20

            else:
                y = 25

        for enemy in self.enemy_list:
            enemy.set_walls_pos(self.walls_pix_pos)


    def generate_pellets(self, maze):

        # Initial State
        # Generates and figures out how many pellets there are
        if not self.generated_pellets:
            x = 25
            y = 25
            
            for line in maze:
                for char in line:
                    if char == "P":
                        curr_pell = Pellets((x, y))
                        curr_pell.draw_pellet(self.screen, self.pellet)
                        self.pellets_list.append(curr_pell)
                        self.pellet_count += 1

                    elif char == "S":
                        curr_sup = Super_Pellets((x, y))
                        curr_sup.draw_super_pellet(self.screen, self.super_pellet)
                        self.pellets_list.append(curr_sup)
                        self.pellet_count += 1

                    if char == "I":
                        curr_pell = Pellets((x, y))
                        curr_pell.draw_pellet(self.screen, self.pellet)
                        self.pellets_list.append(curr_pell)
                        self.pellet_count += 1
                        self.intersections_list.append((x,y))

                    elif char == "i":
                        self.intersections_list.append((x,y))

                    
                    if x + 20 <= 575: 
                        x += 20
                    else:
                        x = 25

                if y + 20 <= 635:
                    y += 20

                else:
                    y = 25

            self.generated_pellets = True
            self.pellets_counted = True

            for enemy in self.enemy_list:
                enemy.set_intersections(self.intersections_list)

    
        # Playing State
        else:
            for pell in self.pellets_list:
                if not pell.eaten:
                    if pell.pellet_type() == "pellet":
                        pell.draw_pellet(self.screen, self.pellet)

                    else:
                        pell.draw_super_pellet(self.screen, self.super_pellet)


     
##################################### MAZES ####################################

    def get_mazes(self):
        return {
            1:
            [
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                "WIPPPIPPPPPPIWWIPPPPPPIPPPIW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WIPPPIPPIPPPIPPIPPPIPPIPPPIW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WIPPPIWWIPPPIWWIPPPIWWIPPPIW",
                "WWWWWPWWWWWW WW WWWWWWPWWWWW",
                "    WPWWWWWW WW WWWWWWPW    ",
                "    WPWWi   i  i   iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW W        W WWPWWWWW",
                "     I  iW        Wi  I     ",
                "WWWWWPWW W        W WWPWWWWW",
                "    WPWW WWWWWWWWWW WWPW    ",
                "    WPWWi          iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW WWWWWWWWWW WWPWWWWW",
                "WIPPPIPPIPPPIWWIPPPIPPIPPPIW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WIIWWIPPIPPPI  IPPPIPPIWWIIW",
                "WWPWWPWWPWWWWWWWWWWPWWPWWPWW",
                "WWPWWPWWPWWWWWWWWWWPWWPWWPWW",
                "WIIPPIWWIPPPIWWIPPPIWWIPPIIW",
                "WPWWWWWWWWWWPWWPWWWWWWWWWWPW",
                "WIPPPPPPPPPPIPPIPPPPPPPPPPIW",
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW"
            ],

            2:
            [
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                "WIPPPIPPPPPPIWWIPPPPPPIPPPIW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WIPPPIPPIPPPIPPIPPPIPPIPPPIW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WIPPPIWWIPPPIWWIPPPIWWIPPPIW",
                "WWWWWPWWWWWW WW WWWWWWPWWWWW",
                "    WPWWWWWW WW WWWWWWPW    ",
                "    WPWWi   i  i   iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW W        W WWPWWWWW",
                "     I  iW        Wi  I     ",
                "WWWWWPWW W        W WWPWWWWW",
                "    WPWW WWWWWWWWWW WWPW    ",
                "    WPWWi          iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW WWWWWWWWWW WWPWWWWW",
                "WIPPPIPPIPPPIWWIPPPIPPIPPPIW",
                "WPWWWPWWPWWWPWWPWWWPWWPWWWPW",
                "WSWWWPWWPWWWPWWPWWWPWWPWWWSW",
                "WIIWWIPPIPPPI  IPPPIPPIWWIIW",
                "WWPWWPWWPWWWWWWWWWWPWWPWWPWW",
                "WWPWWPWWPWWWWWWWWWWPWWPWWPWW",
                "WIIPPIWWIPPPIWWIPPPIWWIPPIIW",
                "WPWWWWWWWWWWPWWPWWWWWWWWWWPW",
                "WIPPPPPPPPPPIPPIPPPPPPPPPPIW",
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW"
            ],

            3:
            [
                "WWWWWWWWWWWWWWWWWWWWWW WWWWW",
                "WIPPPIPPPPPPIWWIPPPPPPIPPPIW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                " IPPPIPPIPPPIPPIPPPIPPIPPPI ",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                " IPPPIWWIPPPIWWIPPPIWWIPPPI ",
                "WWWWWPWWWWWW WW WWWWWWPWWWWW",
                "    WPWWWWWW WW WWWWWWPW    ",
                "    WPWWi   i  i   iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW W        W WWPWWWWW",
                "     I  iW        Wi  I     ",
                "WWWWWPWW W        W WWPWWWWW",
                "    WPWW WWWWWWWWWW WWPW    ",
                "    WPWWi          iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW WWWWWWWWWW WWPWWWWW",
                " IPPPIPPIPPPIWWIPPPIPPIPPPI ",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WIIWWIPPIPPPI  IPPPIPPIWWIIW",
                "WWPWWPWWPWWWWWWWWWWPWWPWWPWW",
                "WWPWWPWWPWWWWWWWWWWPWWPWWPWW",
                " IIPPIWWIPPPIWWIPPPIWWIPPII ",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WIPPPIPPPPPPIPPIPPPPPPIPPPIW",
                "WWWWWWWWWWWWWWWWWWWWWW WWWWW"
            ],
                        
            4:
            [
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                "WIPPPIPPPPPPIPPIPPPPPPIPPPIW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WIPPPIPPIPPPIPPIPPPIPPIPPPIW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WIPPPIPPIPPPIPPIPPPIPPIPPPIW",
                "WWWWWPWWWWWW WW WWWWWWPWWWWW",
                "    WPWWWWWW WW WWWWWWPW    ",
                "    WIPPi   i  i   iPPIW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW W        W WWPWWWWW",
                "WWWWWI  iW        Wi  IWWWWW",
                "WWWWWPWW W        W WWPWWWWW",
                "    WPWW WWWWWWWWWW WWPW    ",
                "    WPWWi          iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW WWWWWWWWWW WWPWWWWW",
                "WIPPPIPPIPPPIPPIPPPIPPIPPPIW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WPWWWIPPIPPPI  IPPPIPPIWWWPW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WPWWWPWWPWWWWWWWWWWPWWPWWWPW",
                "WIPPPIWWIPPPIWWIPPPIWWIPPPIW",
                "WPWWWPWWPWWWPWWPWWWPWWPWWWPW",
                "WIPPPIPPIPPPIPPIPPPIPPIPPPIW",
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW"
            ],
            
            5:
            [
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                "PPPPPIPPPPPPIPPIPPPPPPIPPPPP",
                "WWWWWPWWWWWWPWWPWWWWWWPWWWWW",
                "W   WPWWWWWWPWWPWWWWWWPW    ",
                "W   WPWWWWWWPWWPWWWWWWPW    ",
                "WWWWWPWWWWWWPWWPWWWWWWPWWWWW",
                "WIPPPIPPIPPPIPPIPPPIPPIPPPIW",
                "WPWWWWWWPWWWPWWPWWWPWWWWWWPW",
                "WSWWWWWWPWWWPWWPWWWPWWWWWWSW",
                "WIPPPIWWIPPPIPPIPPPIWWIPPPIW",
                "WWWWWPWWPWWWPWWPWWWPWWPWWWWW",
                "    WPWWPWWWPWWPWWWPWWPW    ",
                "    WPWWi   i  i   iWWPW    ",
                "    WPWW WWWWWWWWWW WWPW    ",
                "WWWWWPWW W        W WWPWWWWW",
                "WIPPPIPPiW        WiPPIPPPIW",
                "WPWWWPWW W        W WWPWWWPW",
                "WIPPPIWW WWWWWWWWWW WWIPPPIW",
                "WPWWWPWWi   i  i   iWWPWWWPW",
                "WIPPPIWWPWWWPWWPWWWPWWIPPPIW",
                "WPWWWPWWPWWWPWWPWWWPWWPWWWPW",
                "WIPPPIPPIPPPIWWIPPPIPPIPPPIW",
                "WPWWWPWWWWWWPWWPWWWWWWPWWWPW",
                "WSWWWPWWWWWWPWWPWWWWWWPWWWSW",
                "WIIWWIPPIWWWI  IWWWIPPIWWIIW",
                "WWPWWPWWIPPPIWWIPPPIWWPWWPWW",
                " WPWWPWWPWWWPWWPWWWPWWPWWPW ",
                " WIPPIWWIPPPIWWIPPPIWWIPPIW ",
                "WWPWWPWWPWWWPWWPWWWPWWPWWPWW",
                "PPIPPIPPIPPPIPPIPPPIPPIPPIPP",
                "WWWWWWWWWWWWWWWWWWWWWWWWWWWW"
            ]
        }
        

        
