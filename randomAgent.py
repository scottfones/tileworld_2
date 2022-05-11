from env import *

class randPlayer(pygame.sprite.Sprite):
    def __init__(self, randAgentPath, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((WALLSIZE, WALLSIZE))
        self.image.fill(color)
        pygame.draw.rect(self.image, rand_color(random.randint(0,N)), self.image.get_rect(), 3)
        self.rect = self.image.get_rect() # get image position
        self.rect.x = random.randint(0, N-1) * WALLSIZE
        self.rect.y = random.randint(0, N-1) * WALLSIZE
        self.speedx = SPEED
        self.speedy = SPEED
        self.score = 0
        self.steps = 0
        self.randAgentPath = randAgentPath

    def move(self, direction):
        if direction == 'r':
            self.steps += 1
            self.rect.x += self.speedx
            if self.is_player_collide_wall():
                self.rect.x -= self.speedx
        if direction == 'l':
            self.steps += 1
            self.rect.x -= self.speedx
            if self.is_player_collide_wall():
                self.rect.x += self.speedx
        if direction == 'u':
            self.steps += 1
            self.rect.y -= self.speedy
            if self.is_player_collide_wall():
                self.rect.y += self.speedy
        if direction == 'd':
            self.steps += 1
            self.rect.y += self.speedy
            if self.is_player_collide_wall():
                self.rect.y -= self.speedy

    def is_player_collide_wall(self):
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False

    def update(self):
        direction = self.randAgentPath[self.steps] #random.choice(directions)
        # print(direction)
        if direction == 0: ## left
            self.move('l')
        if direction == 1: ## right
            self.move('r')
        if direction == 2: ## up
            self.move('u')
        if direction == 3: ## down
            self.move('d')

        # Avoid colliding with wall and go out of edges
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
