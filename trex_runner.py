import os
import pygame
from spritesheet import Spritesheet
import random

pygame.init()

WIN_WIDTH, WIN_HEIGHT = 1200, 250
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("T-Rex Runner")
WIN.fill("white")

main_sprite = Spritesheet('main_sprite.png')
TREX_IMGS = {
    'idle': pygame.transform.scale2x(main_sprite.parse_sprite('trex_idle')),
    'walk': [pygame.transform.scale2x(main_sprite.parse_sprite(f'trex_walk{i}')) for i in range(1, 4+1)],
    'crouch': [pygame.transform.scale2x(main_sprite.parse_sprite('trex_crouch1')), pygame.transform.scale2x(main_sprite.parse_sprite('trex_crouch2'))],
    'death': pygame.transform.scale2x(main_sprite.parse_sprite('trex_death'))
}
BASE_IMG = pygame.transform.scale2x(main_sprite.parse_sprite('base'))
CACTUSES = []
for i in range(1, 6+1): CACTUSES.append(pygame.transform.scale2x(main_sprite.parse_sprite(f'cactus{i}')))

VELOCITY = 5

class trex():

    def __init__(self):
        pass

class obstacle():
    VEL = VELOCITY

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.IMG = None
    
    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.bilt(self.IMG, (self.x, self.y))

    def collide(self, trex):
        trex_mask = trex.get_mask()
        mask = pygame.mask.from_surface(self.IMG)
        offset = (self.x - trex.x, self.y - self.IMG.get_height() - round(trex.y))

        point = trex_mask.overlap(mask, offset)

        if point:
            return True

        return False

class cactus(obstacle):
    IMGS = CACTUSES

    def __init__(self, x, y):
        super().__init__(x, y)
        rand = random.randint(1, len(self.IMGS))
        self.IMG = self.IMGS[rand]


class base():
    VEL = VELOCITY
    WIDTH = BASE_IMG.get_width()
    HEIGHT = BASE_IMG.get_height()
    IMG = BASE_IMG

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
        win.bilt(self.IMG, (self.x1, self.y))
        win.bilt(self.IMG, (self.x2, self.y))


def main():
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()
                break
            
        pygame.display.update()

main()