import pygame
import random
import numpy as np
import os

SEED = 0
SEC = 12  # Total game time in seconds. You may change it to a larger value to make the game runs longer
FPS = 10  # You may accelerate the game by changing it to a larger number, and decelerate it to debug
total_time = SEC * 1000  # Pygame runs in millisecond
global_time = 0

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def rand_color(seed):
    np.random.seed(seed)
    color = list(np.random.choice(range(256), size=3))
    return color


# Tileworld size
N = 11
WALLSIZE = 50  # Walls = random obstacles
WIDTH = HEIGHT = WALLSIZE * N

# Number of walls
WALLNUM = N
np.random.seed(SEED)
wall_pos = np.random.randint(1, N - 1, size=(WALLNUM, 2))

# Total number of coins
COINNUM = 10000

# Each agent can move at most one square at each step
SPEED = WALLSIZE

# The game stops when both of the agents reach "STEPNUM" steps
STEPNUM = N * N * 2

##############################
## DO NOT CHANGE BELOW THIS ##
##############################
# random agent path : DONOT CHANGE THIS
np.random.seed(SEED)
randAgentPath = np.random.randint(4, size=STEPNUM * 10)
np.random.seed(SEED + 200)
randAgentPath1 = np.random.randint(4, size=STEPNUM * 10)


# Initialize game and create window : DONOT CHANGE THIS
pygame.init()
pygame.mixer.init()  # initialize sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multi-Agent Simulator")

# Load images
wall_img = pygame.image.load(os.path.join("img", "wall.png")).convert()
coin_imgs = []
for i in range(1, 10):
    coin_imgs.append(pygame.image.load(os.path.join("img", f"coin{i}.png")).convert())

# Game objects
class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = wall_img
        self.image = pygame.transform.scale(wall_img, (WALLSIZE, WALLSIZE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()  # get image position
        self.rect.x = pos_x * WALLSIZE  # random.randrange(1, N-1) * WALLSIZE
        self.rect.y = pos_y * WALLSIZE  # random.randrange(1, N-1) * WALLSIZE
        # if self.rect.x == 0 and self.rect.y == 0:
        #     self.rect.x = random.randrange(0, N) * WALLSIZE
        #     self.rect.y = random.randrange(0, N) * WALLSIZE


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, val, coin_life):
        pygame.sprite.Sprite.__init__(self)
        self.value = val  # random.randrange(1, 10)
        self.image = coin_imgs[self.value - 1]
        self.image = pygame.transform.scale(self.image, (WALLSIZE, WALLSIZE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()  # get image position
        self.rect.x = pos_x * WALLSIZE  # random.randrange(1, N-1) * WALLSIZE
        self.rect.y = pos_y * WALLSIZE  # random.randrange(1, N-1) * WALLSIZE
        self.coin_start = pygame.time.get_ticks()
        self.coin_lifespan = coin_life * 1000

    def update(self):
        if pygame.time.get_ticks() > self.coin_start + self.coin_lifespan:
            self.kill()


np.random.seed(SEED)
coin_pos = np.random.randint(0, N, size=(COINNUM, 2))
coin_val = np.random.randint(1, 10, size=(COINNUM, 1))
coin_life = np.random.randint(1, 5, size=(COINNUM, 1))
coin_arr = np.concatenate((coin_pos, coin_val, coin_life), axis=1)
coin_arr = coin_arr.tolist()

all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
walls = pygame.sprite.Group()
coins = pygame.sprite.Group()
running = True

for i in range(WALLNUM):
    wall = Wall(wall_pos[i][0], wall_pos[i][1])
    if wall not in walls:
        all_sprites.add(wall)
        walls.add(wall)


def get_coin_data():
    cur_coin_vals = []
    cur_coin_poss = []
    for coin in coins:
        cur_coin_vals.append(coin.value)
        cur_coin_poss.append([coin.rect.x, coin.rect.y])
    return cur_coin_vals, cur_coin_poss


def get_wall_data():
    cur_wall_poss = []
    for wall in walls:
        cur_wall_poss.append([wall.rect.x, wall.rect.y])
    return cur_wall_poss
