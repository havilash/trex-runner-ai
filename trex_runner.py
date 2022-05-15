from email.mime import base
from math import fabs
import os
import pygame
from sqlalchemy import true
from spritesheet import Spritesheet
import random

pygame.init()

WIN_WIDTH, WIN_HEIGHT = 1200, 330
FLOOR = 260
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("T-Rex Runner")

main_sprite = Spritesheet('main_sprite.png')
TREX_IMGS = {
    'idle': pygame.transform.scale2x(main_sprite.parse_sprite('trex_idle')),
    'walk': [pygame.transform.scale2x(main_sprite.parse_sprite(f'trex_walk{i}')) for i in range(1, 4+1)],
    'crouch': [pygame.transform.scale2x(main_sprite.parse_sprite('trex_crouch1')), pygame.transform.scale2x(main_sprite.parse_sprite('trex_crouch2'))],
    'death': pygame.transform.scale2x(main_sprite.parse_sprite('trex_death'))
}
BASE_IMG = pygame.transform.scale2x(main_sprite.parse_sprite('base'))
CACTUSES = []
for i in range(1, 12+1): CACTUSES.append(pygame.transform.scale2x(main_sprite.parse_sprite(f'cactus{i}')))

FPS = 30
VELOCITY = 5

class Trex():
    IMGS = TREX_IMGS

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tick_count = 0
        self.vel = 0
        self.img = self.IMGS['idle']

    def jump(self):
        self.vel = -13
        self.tick_count = 0

    def move(self):
        self.tick_count += 1

        self.displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2

        # terminal velocity
        if self.displacement >= 16:
            self.displacement = (self.displacement/abs(self.displacement)) * 16

        if self.displacement < 0:
            self.displacement -= 2

        self.y += self.displacement

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

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

    def collide(self, trex):
        trex_mask = trex.get_mask()
        mask = pygame.mask.from_surface(self.img)
        offset = (self.x - trex.x, self.y - self.img.get_height() - round(trex.y))

        point = trex_mask.overlap(mask, offset)

        if point:
            return True

        return False

class Cactus(Obstacle):
    IMGS = CACTUSES

    def __init__(self, x, y):
        super().__init__(x, y)
        rand = random.randint(1, len(self.IMGS))
        self.img = self.IMGS[rand]


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
    if y > FLOOR + (BASE_IMG.get_height()/1.5): return True
    else: return False

def draw_window(win, trex, base):
    win.fill("white")

    trex.draw(win)
    base.draw(win)
    

def main():
    is_running = True
    is_jumping = False

    base = Base(FLOOR)
    trex = Trex(100, FLOOR-TREX_IMGS['idle'].get_height())

    clock = pygame.time.Clock()
    while is_running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if is_grounded(trex.y+trex.img.get_height()):
                        trex.jump()
        
        if is_grounded(trex.y+trex.img.get_height()):
            trex.y -= trex.displacement
        trex.move()
        base.move()

        draw_window(WIN, trex, base)
            
        pygame.display.update()
    
    pygame.quit()


main()