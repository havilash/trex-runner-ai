import os
import pygame
from spritesheet import Spritesheet
import random
import neat

pygame.init()

WIN_WIDTH, WIN_HEIGHT = 1200, 330
FLOOR = 260
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("T-Rex Runner")
STAT_FONT = pygame.font.SysFont("comicsans", 20)

main_sprite = Spritesheet('main_sprite.png')
TREX_IMGS = {
    'jump': pygame.transform.scale2x(main_sprite.parse_sprite('trex_jump')),
    'walk': [pygame.transform.scale2x(main_sprite.parse_sprite(f'trex_walk{i}')) for i in range(1, 3+1)],
    'crouch': [pygame.transform.scale2x(main_sprite.parse_sprite('trex_crouch1')), pygame.transform.scale2x(main_sprite.parse_sprite('trex_crouch2'))],
    'death': pygame.transform.scale2x(main_sprite.parse_sprite('trex_death'))
}
BASE_IMG = pygame.transform.scale2x(main_sprite.parse_sprite('base'))
CACTUS_IMGS = []
for i in range(1, 6+1): CACTUS_IMGS.append(pygame.transform.scale2x(main_sprite.parse_sprite(f'cactus{i}')))
BIRD_IMGS = [pygame.transform.scale2x(main_sprite.parse_sprite('bird1')), pygame.transform.scale2x(main_sprite.parse_sprite('bird2'))]

FPS = 30
VELOCITY = 20

class Trex():
    IMGS = TREX_IMGS
    ANIM_TIME = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tick_count = 0
        self.vel = 0
        self.img = self.IMGS['jump']
        self.img_count = 0
        self.anim_status = 'walk'

    def jump(self):
        self.vel = -13
        self.tick_count = 0

        self.anim_status = 'jump'

    def crouch(self):
        self.anim_status = 'crouch'

    def death(self):
        self.anim_status = 'death'

    def move(self):
        self.tick_count += 1

        self.displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2

        # terminal velocity
        if self.displacement >= 16:
            self.displacement = (self.displacement/abs(self.displacement)) * 16

        if self.displacement < 0:
            self.displacement -= 2

        self.y += self.displacement

        if is_grounded(self.y+self.img.get_height()) and self.anim_status != 'crouch' and self.anim_status != 'death':
            self.anim_status = 'walk'


    def draw(self, win):
        self.img_count += 1


        if self.anim_status == 'jump':
            self.img = self.IMGS['jump']

        if self.anim_status == 'walk':
            if self.img_count <= self.ANIM_TIME:
                self.img = self.IMGS['walk'][0]
            elif self.img_count <= self.ANIM_TIME*2:
                self.img = self.IMGS['walk'][1]
            elif self.img_count <= self.ANIM_TIME*3:
                self.img = self.IMGS['walk'][0]
            elif self.img_count <= self.ANIM_TIME*4:
                self.img = self.IMGS['walk'][2]
            elif self.img_count >= self.ANIM_TIME*4:
                self.img_count = 0

        if self.anim_status == 'crouch':
            if self.img_count <= self.ANIM_TIME:
                self.img = self.IMGS['crouch'][0]
            elif self.img_count <= self.ANIM_TIME*2:
                self.img = self.IMGS['crouch'][1]
            elif self.img_count >= self.ANIM_TIME*3:
                self.img_count = 0
        
        if self.anim_status == 'death':
            self.img = self.IMGS['death']

        win.blit(self.img, (self.x, self.y))

    def collide(self, obstacle):
        trex_mask = pygame.mask.from_surface(self.img)
        mask = obstacle.get_mask()
        offset = (obstacle.x - self.x, obstacle.y - round(self.y))
        point = trex_mask.overlap(mask, offset) # point of intercept

        if point: return True
        return False

class Obstacle():
    VEL = VELOCITY

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = None
    
    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Cactus(Obstacle):
    IMGS = CACTUS_IMGS

    def __init__(self, x, y, cactus_num):
        super().__init__(x, y)
        self.img = self.IMGS[cactus_num]

class Bird(Obstacle):
    IMGS = BIRD_IMGS
    ANIM_TIME = 5
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img_count = 0

    def draw(self, win):
        self.img_count += 1

        if self.img_count <= self.ANIM_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIM_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count >= self.ANIM_TIME*3:
            self.img_count = 0

        win.blit(self.img, (self.x, self.y))


class Base():
    VEL = VELOCITY
    WIDTH = BASE_IMG.get_width()
    HEIGHT = BASE_IMG.get_height()
    img = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH <= 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH <= 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))

def is_grounded(y):
    if y > FLOOR: return True
    else: return False

def draw(win, trex, base, obstacles, score):
    win.fill("white")

    base.draw(win)
    for obstacle in obstacles:
        obstacle.draw(win)
    trex.draw(win)


    score_label = STAT_FONT.render("Score: " + str(score), 1, (0,0,0))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()

def main():
    is_running = True
    frame_count = 0
    OBSTACLE_COUNT = 60
    score = 0

    base = Base(FLOOR-(BASE_IMG.get_height()/2))
    trex = Trex(100, FLOOR-TREX_IMGS['jump'].get_height())
    obstacles = []

    clock = pygame.time.Clock()
    while is_running:
        clock.tick(FPS)
        frame_count += 1
        score += 1
        trex.move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if is_grounded(trex.y+trex.img.get_height()):
                        trex.jump()

                if event.key == pygame.K_DOWN:
                    trex.crouch()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    trex.anim_status = 'jump'

        # Spawn Obstacles
        if frame_count > OBSTACLE_COUNT:
            frame_count = 0
            rand = random.randint(1, 10)
            if rand == 10:
                obstacles.append(Bird(WIN_WIDTH, 140))
            if rand <= 9:
                cactus_num = random.randint(0, len(CACTUS_IMGS)-1)
                obstacles.append(Cactus(WIN_WIDTH, 10+FLOOR-CACTUS_IMGS[cactus_num].get_height(), cactus_num))

        # Check Collisions
        for obstacle in obstacles:
            if obstacle:
                if trex.collide(obstacle):
                    print("death")
                    trex.death()
                # pygame.time.delay(3000)

        # Stop if is Grounded
        if is_grounded(trex.y+trex.img.get_height()):
            trex.y = FLOOR - trex.img.get_height()

        base.move()
        for obstacle in obstacles:
            obstacle.move()

        draw(WIN, trex, base, obstacles, score)    
    pygame.quit()


main()