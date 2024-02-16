
from platform import python_branch
import random
from xml.etree.ElementPath import prepare_descendant
from numpy import angle
import pygame
import math 
import os
import time
import sys
from math import acos, degrees

# Constants for the game window size
WIDTH, HEIGHT = 256*2, 196*2
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 21*2, 21*2
x,y = WIDTH/2, HEIGHT/2

# Game settings
FPS = 60  # Frames per second
Jetpower = 0.1  # Power of the jet or thruster
maxspeed = 100 / FPS  # Maximum speed
mass = 50  # Mass of the spaceship
accx, accy = 0, 0  # Initial acceleration
speedx, speedy = 0, 0  # Initial velocity
pygame.init()  # Initialize all imported pygame modules



# GRAPHICS
# Loading graphics and scaling images to appropriate sizes

bg = pygame.transform.scale(pygame.image.load(r'graphics\bg.png'), (256*2, 196*2))
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
ROCKET = pygame.transform.scale(pygame.image.load(r'graphics\spaceship.png'), (21*2,21*2))
RIFFLE = pygame.transform.scale(pygame.image.load(r'graphics\spaceshooter.png'), (41*2,41*2))
PLAY = pygame.transform.scale(pygame.image.load(r'graphics\playbutton.png'), (45*2,33*2))  
LEADBOARD = pygame.transform.scale(pygame.image.load(r'graphics\leadboard.png'), (47*2,34*2))
EXIT = pygame.transform.scale(pygame.image.load(r'graphics\exitbutton.png'), (47*2,34*2))
HEALTH = pygame.transform.scale(pygame.image.load(r'graphics\lifecounter.png'), (12*2,17*2))
BONUSHEALTH = pygame.transform.scale(pygame.image.load(r'graphics\life.png'), (7*2,12*2))
BULLET = pygame.transform.scale(pygame.image.load(r'graphics\bulletcounter.png'), (11*2,17*2))
BONUSBULLET = pygame.transform.scale(pygame.image.load(r'graphics\bullet.png'), (7*2,11*2))
BULLETSHOOT = pygame.transform.scale(pygame.image.load(r'graphics\bulletingame.png'), (3*2,5*2))
MENU = pygame.transform.scale(pygame.image.load(r'graphics\mainmenu.png'), (19*2,21*2))
RESET = pygame.transform.scale(pygame.image.load(r'graphics\resetbutton.png'), (19*2,21*2))
ENEMY = pygame.transform.scale(pygame.image.load(r'graphics\enemy.png'), (21*2,21*2))

# SOUND
# Initialize the mixer module and load sound files
pygame.mixer.music.load("sounds/gamesong.wav")
pygame.mixer.music.set_volume(0.01)
pygame.mixer.music.play(loops=-1)

explosion_bullet_sound = pygame.mixer.Sound("sounds/explosionbullet.wav")
click_sound = pygame.mixer.Sound("sounds/click.wav")
explosion_sound = pygame.mixer.Sound("sounds/explosionbullet.wav")
heal_sound = pygame.mixer.Sound("sounds/heal.wav")
pickup_sound = pygame.mixer.Sound("sounds/pickupBullet.wav")
lasershoot_sound = pygame.mixer.Sound("sounds/laserShoot.wav")
hit_hurt_sound = pygame.mixer.Sound("sounds/hitHurt.wav")
click_sound.set_volume(0.1)
explosion_bullet_sound.set_volume(0.4)
lasershoot_sound.set_volume(0.2)
pickup_sound.set_volume(0.3)
heal_sound.set_volume(0.2)
explosion_sound.set_volume(0.5)
hit_hurt_sound.set_volume(0.3)

# CLASSES

# Define Button class for creating interactive buttons
class Button():
    # Constructor for Button class
    def __init__(self, x, y, image, scale):
        self.originalimage = image
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image,(int(self.height * scale), int(self.height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False
    
    # Draw the button on the screen and check for interaction
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):

            self.image = pygame.transform.scale(self.originalimage,(int(self.width * 1.05), int(self.height * 1.05)))
            
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                click_sound.play()
                self.clicked = True
                action = True
        else:
            self.image = pygame.transform.scale(self.originalimage,(int(self.width * 1), int(self.height * 1)))
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        WIN.blit(self.image, (self.rect.x, self.rect.y))      
        return action
class Bonushealth():
    def __init__(self, x, y, rect):
        self.clicked = False
        self.x = x
        self.y = y
        self.rect = rect
        self.angle = 0
    def update(self):
        self.angle += 0.2
        if self.angle == 360:
            self.angle = 0
        rotation = pygame.transform.rotate(BONUSHEALTH, self.angle)
        new_rect = rotation.get_rect(center = BONUSHEALTH.get_rect(center = (self.x + 7, self.y + 12)).center)
        self.rect.update((self.x, self.y), (7*2, 12*2))
        return [rotation, new_rect]
# Define the Bonushealth class for creating bonus health pickups
class Bonusbullet():
    def __init__(self, x, y, rect):
        self.clicked = False
        self.x = x
        self.y = y
        self.rect = rect
        self.angle = 0
    def update(self):
        self.angle += 0.2
        if self.angle == 360:
            self.angle = 0
        rotation = pygame.transform.rotate(BONUSBULLET, self.angle)
        new_rect = rotation.get_rect(center = BONUSBULLET.get_rect(center = (self.x + 7, self.y + 11)).center)
        self.rect.update((self.x, self.y), (7*2, 12*2))
        return [rotation, new_rect]

# Define the Bullet class to represent bullets shot by the player
class Bullet():
    def __init__(self, rect, parent):
        super().__init__()
        self.parent = parent
        self.angle = rotate_riffle(parent)[2]
        if rotate_riffle(parent)[3] == 1:
            self.x = parent.x + SPACESHIP_WIDTH/2 - math.sin(math.radians(abs(rotate_riffle(parent)[2])))*39
            self.y = parent.y + SPACESHIP_WIDTH/2 - math.cos(math.radians(abs(rotate_riffle(parent)[2])))*39
        elif rotate_riffle(parent)[3] == 2:
            self.x = parent.x + SPACESHIP_WIDTH/2 + math.sin(math.radians(rotate_riffle(parent)[2]))*39
            self.y = parent.y + SPACESHIP_WIDTH/2 - math.cos(math.radians(rotate_riffle(parent)[2]))*39
        elif rotate_riffle(parent)[3] == 3:
            self.x = parent.x + SPACESHIP_WIDTH/2 + math.sin(math.radians(rotate_riffle(parent)[2]))*39
            self.y = parent.y + SPACESHIP_WIDTH/2 - math.cos(math.radians(rotate_riffle(parent)[2]))*39
        elif rotate_riffle(parent)[3] == 4:
            self.x = parent.x + SPACESHIP_WIDTH/2 - math.sin(math.radians(abs(rotate_riffle(parent)[2])))*39
            self.y = parent.y + SPACESHIP_WIDTH/2 - math.cos(math.radians(abs(rotate_riffle(parent)[2])))*39
        self.image = pygame.Surface((5,2))
        self.image.fill((0,40,255))
        self.Rect = rect
    def update(self):
        self.x += 2
        
        rotate_riffle(self.parent)[2]
        if self.angle <= 0 and self.angle >= -90:
            self.x -= math.sin(math.radians(abs(self.angle)))*10
            self.y -= math.cos(math.radians(abs(self.angle)))*10
        if self.angle > 0 and self.angle <= 90:
            self.x +=  math.sin(math.radians(abs(self.angle)))*10
            self.y -= math.cos(math.radians(abs(self.angle)))*10
        if self.angle < -90 and self.angle >= -180:
            self.x -=  math.sin(math.radians(abs(self.angle)))*10
            self.y -= math.cos(math.radians(abs(self.angle)))*10
        if self.angle < -180 and self.angle >= -270:
            self.x -= math.sin(math.radians(abs(self.angle)))*10
            self.y -= math.cos(math.radians(abs(self.angle)))*10
        self.Rect.update((self.x, self.y), (6, 10))

# Define the Enemy class for creating enemy ships
class Enemy():
    def __init__(self, x, y, jetforce, mass, Rect, health, target):
        self.x = x
        self.y = y
        self.jetforce = jetforce
        self.mass = mass
        self.inteligence = 0
        self.velocityx = 0
        self.velocityy = 0
        self.accelerationx = 0
        self.accelerationy = 0
        self.Rect = Rect
        self.health = health
        self.target = target
    def slowingforce(self, slowpower = 0.05, gravityforce = 9.81):
        if(self.velocityx > 0):
            self.accelerationx -= (self.mass * gravityforce * slowpower)/self.mass
        if(self.velocityy > 0):
            self.accelerationy -= (self.mass * gravityforce * slowpower)/self.mass
        if(self.velocityx < 0):
            self.accelerationx += (self.mass * gravityforce * slowpower)/self.mass
        if(self.velocityy < 0):
            self.accelerationy += (self.mass * gravityforce * slowpower)/self.mass
            
        return (self.mass * gravityforce * slowpower)/self.mass
    def dead(self):
        WIN.blit(BONUSHEALTH, (self.x, self.y))

    def movejetforce(self):
        if self.rotatetowardplayer()[3] == 1:
            if self.rotatetowardplayer()[2] < 0 and self.rotatetowardplayer()[2] > -30:
                self.accelerationx = -self.jetforce/self.mass * 0.9659
                self.accelerationy = -self.jetforce/self.mass * 0.2588
            elif self.rotatetowardplayer()[2] < -30 and self.rotatetowardplayer()[2] > -60:
                self.accelerationx = -self.jetforce/self.mass * 0.707
                self.accelerationy = -self.jetforce/self.mass * 0.707
            elif self.rotatetowardplayer()[2] < -60 and self.rotatetowardplayer()[2] > -90:
                self.accelerationx = -self.jetforce/self.mass * 0.2588
                self.accelerationy = -self.jetforce/self.mass * 0.9659
        if self.rotatetowardplayer()[3] == 2:
            if self.rotatetowardplayer()[2] > 0 and self.rotatetowardplayer()[2] < 30:
                self.accelerationx = self.jetforce/self.mass * 0.2588
                self.accelerationy = -self.jetforce/self.mass * 0.9659
            elif self.rotatetowardplayer()[2] > 30 and self.rotatetowardplayer()[2] < 60:
                self.accelerationx = self.jetforce/self.mass * 0.707
                self.accelerationy = -self.jetforce/self.mass * 0.707
            elif self.rotatetowardplayer()[2] > 60 and self.rotatetowardplayer()[2] < 90:
                self.accelerationx = self.jetforce/self.mass * 0.9659
                self.accelerationy = -self.jetforce/self.mass * 0.2588
        if self.rotatetowardplayer()[3] == 3:
            if self.rotatetowardplayer()[2] < -90 and self.rotatetowardplayer()[2] > -120:
                self.accelerationx = -self.jetforce/self.mass * 0.2588
                self.accelerationy = self.jetforce/self.mass * 0.9659
            elif self.rotatetowardplayer()[2] < -120 and self.rotatetowardplayer()[2] > -150:
                self.accelerationx = -self.jetforce/self.mass * 0.707
                self.accelerationy = self.jetforce/self.mass * 0.707
            elif self.rotatetowardplayer()[2] < -150 and self.rotatetowardplayer()[2] > -180:
                self.accelerationx = -self.jetforce/self.mass * 0.9659
                self.accelerationy = self.jetforce/self.mass * 0.2588
        if self.rotatetowardplayer()[3] == 4:
            if self.rotatetowardplayer()[2] < -180 and self.rotatetowardplayer()[2] > -210:
                self.accelerationx = self.jetforce/self.mass * 0.2588
                self.accelerationy = self.jetforce/self.mass * 0.9659   
            elif self.rotatetowardplayer()[2] < -210 and self.rotatetowardplayer()[2] > -210:
                self.accelerationx = self.jetforce/self.mass * 0.707
                self.accelerationy = self.jetforce/self.mass * 0.707
            elif self.rotatetowardplayer()[2] < -240 and self.rotatetowardplayer()[2] > -270:
                self.accelerationx = self.jetforce/self.mass * 0.9659
                self.accelerationy = self.jetforce/self.mass * 0.2588
                
    def move(self, borderx, bordery):
        if((self.x < 0 or self.x > borderx) == True):       
            self.accelerationx = -self.accelerationx/2
            self.velocityx = -self.velocityx/2
            self.x += self.velocityx
            self.y += self.velocityy
        if((self.y < 0 or self.y > bordery) == True):       
            self.accelerationy = -self.accelerationy/2
            self.velocityy = -self.velocityy/2
            self.x += self.velocityx
            self.y += self.velocityy*4
        else:
            self.x += self.velocityx
            self.y += self.velocityy
        self.Rect.update((self.x, self.y), (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
    def rotatetowardplayer(self):
        x = self.target.x + SPACESHIP_WIDTH/2
        y = self.target.y + SPACESHIP_WIDTH/2
        x2 = self.x + SPACESHIP_WIDTH/2
        y2 = self.y + SPACESHIP_WIDTH/2
        angle = 0
        area = 0
        A = abs(y2-y)
        B = abs(x2 - x)
        C = math.sqrt(A**2+B**2)
        rotation = degrees(acos((B/C)))
        if x <= x2 and y  <= y2:
            angle = -(90-rotation)
            area = 1
        elif x >= x2 and y  <= y2:
            angle = 90-rotation
            area = 2
        elif x <= x2 and y >= y2:
            angle = -90-rotation
            area = 3
        elif x >= x2 and y  >= y2:
            area = 4
            angle = -270+rotation  
        Enemyrotation = pygame.transform.rotate(ENEMY, -angle)
        new_rect = Enemyrotation.get_rect(center = ENEMY.get_rect(center = (self.x + SPACESHIP_WIDTH/2, self.y+ SPACESHIP_WIDTH/2)).center)
        return [Enemyrotation, new_rect, angle, area]

    def calculatemovement(self, max_speed, borderx, bordery):
        if self.velocityx < max_speed and self.velocityx > -max_speed:
            self.velocityx += self.accelerationx
        elif(self.velocityx > max_speed):
            self.velocityx =max_speed 
        elif(self.velocityx < -max_speed):
            self.velocityx = -max_speed 
        if self.velocityy < max_speed and self.velocityy > -max_speed:
            self.velocityy += self.accelerationy
        elif(self.velocityy > max_speed):
            self.velocityy =max_speed 
        elif(self.velocityy < -max_speed):
            self.velocityy = -max_speed
        if(-max_speed/100 < self.velocityx < max_speed/100):
            self.accelerationx = 0
        if(-max_speed/100 < self.velocityy < max_speed/100):
            self.accelerationy = 0  
        self.move(borderx, bordery)  
# Define the Rocket class to represent the player's spaceship
class Rocket():
    def __init__(self, x, y, jetforce, mass, Rect, health):
        self.x = x
        self.y = y
        self.jetforce = jetforce
        self.mass = mass
        self.velocityx = 0
        self.velocityy = 0
        self.accelerationx = 0
        self.accelerationy = 0
        self.Rect = Rect
        self.health = 10
    def slowingforce(self, slowpower = 0.05, gravityforce = 9.81):
        if(self.velocityx > 0):
            self.accelerationx -= (self.mass * gravityforce * slowpower)/self.mass
        if(self.velocityy > 0):
            self.accelerationy -= (self.mass * gravityforce * slowpower)/self.mass
        if(self.velocityx < 0):
            self.accelerationx += (self.mass * gravityforce * slowpower)/self.mass
        if(self.velocityy < 0):
            self.accelerationy += (self.mass * gravityforce * slowpower)/self.mass
            
        return (self.mass * gravityforce * slowpower)/self.mass

    def movejetforce(self, keys_pressed):
        if keys_pressed[pygame.K_a]:#LEFT
           self.accelerationx = self.jetforce/self.mass
        if keys_pressed[pygame.K_d] :#RIGHT
           self.accelerationx = -self.jetforce/self.mass
        if keys_pressed[pygame.K_w]:#UP
           self.accelerationy = self.jetforce/self.mass 
        if keys_pressed[pygame.K_s]:#DOWN
           self.accelerationy = -self.jetforce/self.mass 
    def move(self, borderx, bordery):
        if((self.x < 0 or self.x > borderx) == True):       
            self.accelerationx = -self.accelerationx/2
            self.velocityx = -self.velocityx/2
            self.x += self.velocityx
            self.y += self.velocityy
        if((self.y < 0 or self.y > bordery) == True):       
            self.accelerationy = -self.accelerationy/2
            self.velocityy = -self.velocityy/2
            self.x += self.velocityx
            self.y += self.velocityy*4
        else:
            self.x += self.velocityx
            self.y += self.velocityy
        self.Rect.update((self.x, self.y), (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))

    def calculatemovement(self, max_speed, borderx, bordery):
        if self.velocityx < max_speed and self.velocityx > -max_speed:
            self.velocityx += self.accelerationx
        elif(self.velocityx > max_speed):
            self.velocityx =max_speed 
        elif(self.velocityx < -max_speed):
            self.velocityx = -max_speed 
        if self.velocityy < max_speed and self.velocityy > -max_speed:
            self.velocityy += self.accelerationy
        elif(self.velocityy > max_speed):
            self.velocityy =max_speed 
        elif(self.velocityy < -max_speed):
            self.velocityy = -max_speed
        if(-max_speed/100 < self.velocityx < max_speed/100):
            self.accelerationx = 0
        if(-max_speed/100 < self.velocityy < max_speed/100):
            self.accelerationy = 0
                 
        self.move(borderx, bordery) 


play_button = Button(108*2, 44*2, PLAY, 1)
leadboard_button = Button(108*2, 89*2, LEADBOARD, 1)
leave_button = Button(108*2, 135*2, EXIT, 1)
menu_button_end = Button(150*2, 90*2, MENU, 1)
menu_button_leadboard = Button(220*2, 8*2, MENU, 1)
reset_button = Button(100*2, 90*2, RESET, 1)
# GAME FUNCTIONS
# Function to draw text on the screen
def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font('Adore64.ttf', size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surf.blit(text_surface,text_rect)
# Function to manage game stages based on the current time
def stage(currenttime):
    if currenttime < 10:
        spawnspeed = 5
        mass = 1.2
        inteligence = 1
    if currenttime > 10 and currenttime < 20:
        spawnspeed = 4
        mass = 1
        inteligence = 0.8
    if currenttime > 20 and currenttime < 40:
        spawnspeed = 3
        mass = 0.8
        inteligence = 0.6
    if currenttime > 40 and currenttime < 50:
        spawnspeed = 2
        mass = 0.6
        inteligence = 0.5
    if currenttime > 50 and currenttime < 100:
        spawnspeed = 1
        mass = 0.5
        inteligence = 0.4
    if currenttime > 100:
        spawnspeed = 0.1
        mass = 0.3
        inteligence = 0.2
    return [spawnspeed, mass, inteligence]
# Function to draw the main window and all game elements
def draw_window(rocket, enemygroup, bullet_group, bonus_h, bonus_b):

    WIN.blit(bg, (0, 0))

    WIN.blit(ROCKET, (rocket.x, rocket.y))
    for i in enemygroup:
        WIN.blit(i.rotatetowardplayer()[0], i.rotatetowardplayer()[1].topleft)
    for i in bullet_group:
        WIN.blit(pygame.transform.rotate(BULLETSHOOT, -i.angle), (i.x, i.y))
    for i in bonus_b:
        WIN.blit(i.update()[0], i.update()[1].topleft)
    for i in bonus_h:
        WIN.blit(i.update()[0], i.update()[1].topleft)
    WIN.blit(rotate_riffle(rocket)[0], rotate_riffle(rocket)[1].topleft)
    WIN.blit(HEALTH, (20*2 ,11*2))
    WIN.blit(BULLET, (60*2 ,11*2))

            
        
# Function to rotate the player's rifle based on the mouse position
def rotate_riffle(rocket):
    x, y = pygame.mouse.get_pos()
    x2 = rocket.x + SPACESHIP_WIDTH/2
    y2 = rocket.y + SPACESHIP_WIDTH/2
    angle = 0

    A = abs(y2-y)
    B = abs(x2 - x)
    C = math.sqrt(A**2+B**2)
    rotation = degrees(acos((B/C)))
    if x <= x2 and y  <= y2:
        angle = -(90-rotation)
        area = 1
    elif x >= x2 and y  <= y2:
        angle = 90-rotation
        area = 2
    elif x <= x2 and y >= y2:
        angle = -90-rotation
        area = 3
    elif x >= x2 and y  >= y2:
        angle = -270+rotation  
        area = 4
    RIFFLEroation = pygame.transform.rotate(RIFFLE, -angle)
    new_rect = RIFFLEroation.get_rect(center = RIFFLE.get_rect(center = (rocket.x + SPACESHIP_WIDTH/2, rocket.y + SPACESHIP_WIDTH/2)).center)
    return [RIFFLEroation, new_rect, angle, area]

def mouseclicked():
    if pygame.mouse.get_pressed()[0]:
        return True
    else:
        return False
# MAIN GAME LOOP
def main():
    spaceship = pygame.Rect(x, y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    enemyspaceship = pygame.Rect(100, 200, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    bulletrect = pygame.Rect(1,1, 6, 10)
    bonusbulletrect = pygame.Rect(1,1, 14, 22)
    bonushealthrect = pygame.Rect(1,1, 14, 24)
    rocket = Rocket(x,y,Jetpower, mass, spaceship, 10)
    enemylist = []
    bullet_list = []
    bonus_bullet_list = []
    bonus_health_list = []
    generated = False
    clock = pygame.time.Clock()
    run = True
    menu = True
    game = False
    dead = False
    leadboard = False
    pressed = True
    clock.tick(FPS)
    spawntime = 0
    bulletcartidge = 10
    score = 0
    new_record = False
    timestart = 0
    f = open("Rekord.txt", "r")
    high_score = f.read()
    f.close()
    while run:
        print(str(dead) + "    " + str(menu)) 
        for event in pygame.event.get():
                if  event.type == pygame.QUIT:
                    run = False
        if game:    
            spawnspeed, massmult, inteligence = stage(score)

            score = time.time() - timestart
            if  time.time() - spawntime > spawnspeed:
                generated = False
                spawntime = time.time()
            if generated == False:             
                spawn = random.randint(1, 4)
                if spawn == 1:
                    enemylist.append(Enemy(40,40,Jetpower*100, mass*massmult, enemyspaceship, 10, rocket))
                if spawn == 2:
                    enemylist.append(Enemy(WIDTH-45,HEIGHT-45,Jetpower*100, mass*massmult, pygame.Rect(100, 200, SPACESHIP_WIDTH, SPACESHIP_HEIGHT), 10, rocket))
                if spawn == 3:
                    enemylist.append(Enemy(WIDTH-45,45,Jetpower*100, mass*massmult,  pygame.Rect(100, 200, SPACESHIP_WIDTH, SPACESHIP_HEIGHT), 10, rocket))
                if spawn == 4:
                    enemylist.append(Enemy(45,HEIGHT-45,Jetpower*100, mass*massmult,  pygame.Rect(100, 200, SPACESHIP_WIDTH, SPACESHIP_HEIGHT), 10, rocket))
                generated = True
            for i in bonus_health_list:
                i.update()    
                if i.rect.colliderect(spaceship):
                    bonus_health_list.remove(i)
                    heal_sound.play()
                    rocket.health += 1
            for i in bonus_bullet_list:
                i.update()    
                if i.rect.colliderect(spaceship):
                    bonus_bullet_list.remove(i)
                    pickup_sound.play()
                    bulletcartidge += 2
                    

            for i in enemylist:
                if time.time() - i.inteligence > inteligence:
                    i.movejetforce()
                    i.inteligence = time.time()
                i.calculatemovement(1000, WIDTH-SPACESHIP_WIDTH, HEIGHT-SPACESHIP_HEIGHT)
                if i.Rect.colliderect(spaceship):
                    enemylist.remove(i)
                    hit_hurt_sound.play()
                    rocket.health -= 1
            for i in bullet_list:
                i.update()
                if i.x > WIDTH or i.x < 0 or i.y > HEIGHT or i.y < 0:
                    bullet_list.remove(i)
                for z in enemylist:
                    if i.Rect.colliderect(z.Rect):
                        chose = random.random()
                        explosion_bullet_sound.play()
                        if chose < 0.20:
                            bonus_health_list.append(Bonushealth(z.x, z.y, bonushealthrect))
                        if chose > 0.20 and chose < 0.80:
                            bonus_bullet_list.append(Bonusbullet(z.x, z.y, bonusbulletrect))
                        enemylist.remove(z)
                
            keys_pressed = pygame.key.get_pressed()
            rocket.movejetforce(keys_pressed)

            if pygame.mouse.get_pressed()[0] == 1 and pressed == False and bulletcartidge > 0: 
                lasershoot_sound.play()
                bulletcartidge -= 1
                bullet_list.append(Bullet(bulletrect, rocket))
                pressed = True
            if pygame.mouse.get_pressed()[0] == False: 
                pressed = False
            if(rocket.velocityx != 0 or rocket.velocityy != 0):
                rocket.slowingforce(0.000001, 9.81)
            # print(rocket.accelerationx, rocket.velocityx)
            rocket.calculatemovement(maxspeed, WIDTH-SPACESHIP_WIDTH, HEIGHT-SPACESHIP_HEIGHT)
            draw_window(rocket, enemylist, bullet_list, bonus_health_list, bonus_bullet_list)
            rotate_riffle(rocket)
            draw_text(WIN, str(bulletcartidge), 20, 170, 30, (255,200,37))
            draw_text(WIN, str(rocket.health), 20, 90, 30, (12, 241, 255))
            draw_text(WIN, str(int(score)), 20, 250, 30, (255,255,255))
            pygame.display.update()
            
            if rocket.health <= 0:
                dead = True
                explosion_sound.play()
                game = False

 
        elif menu:
            WIN.blit(bg, (0, 0))
            if play_button.draw():
                new_record = False
                rocket.accelerationx = 0
                rocket.accelerationy = 0
                rocket.velocityx = 0
                rocket.velocityy = 0
                rocket.x = WIDTH/2
                rocket.y = WIDTH/2
                rocket.health = 5
                bulletcartidge = 10
                enemylist = []
                bullet_list = []
                bonus_bullet_list = []
                bonus_health_list = []
                game = True
                timestart = time.time()
                pressed = True
                menu = False
            if leave_button.draw():
                run = False
            if leadboard_button.draw():
                menu = False 
                leadboard = True
            play_button.draw()
            leadboard_button.draw()
            leave_button.draw()
            pygame.display.update()
        elif dead:
            WIN.blit(bg, (0, 0))
            if int(score) > int(high_score):
                new_record= True
                high_score = int(score)
                f = open("Rekord.txt", "w")
                f.write(str(high_score)) 
                f.close
            if new_record:
                draw_text(WIN, "NEW HIGH SCORE!", 30, WIDTH/2, 100, (255, 209, 56))
            draw_text(WIN, "YOUR SCORE:  " + str(int(score)), 20, WIDTH/2, HEIGHT/2-50, (254, 230, 255))
            if reset_button.draw():
                dead = False
                game = True
                new_record = False
                rocket.accelerationx = 0
                rocket.accelerationy = 0
                rocket.velocityx = 0
                rocket.velocityy = 0
                rocket.x = WIDTH/2
                rocket.y = WIDTH/2
                rocket.health = 5
                pressed = True
                bulletcartidge = 10
                enemylist = []
                bullet_list = []
                bonus_bullet_list = []
                bonus_health_list = []
                timestart = time.time()
            if menu_button_end.draw():
                menu = True
                dead = False
            menu_button_end.draw()    
            reset_button.draw()    

            
            pygame.display.update()
        elif leadboard:
            WIN.blit(bg, (0, 0))
            if menu_button_leadboard.draw():
                menu = True
                leadboard = False
            menu_button_leadboard.draw()
            draw_text(WIN, "YOUR BEST SCORE:" + str(int(high_score)), 20, WIDTH/2, HEIGHT/2-50, (254, 230, 255))    
            pygame.display.update()
        else:
            run = False
    pygame.mixer.music.stop()
    pygame.mixer.quit() 
    pygame.quit()

# Check if this is the main module being run
if __name__ == "__main__":
    main()
    