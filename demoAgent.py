from env import *

player_img = pygame.image.load(os.path.join("img", "player.png")).convert()

class demoPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image = pygame.transform.scale(player_img, (WALLSIZE, WALLSIZE))
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, rand_color(random.randint(0,N)), self.image.get_rect(), 3)
        self.rect = self.image.get_rect() # get image position
        self.rect.x = random.randint(0, N-1) * WALLSIZE
        self.rect.y = random.randint(0, N-1) * WALLSIZE
        self.speedx = SPEED
        self.speedy = SPEED
        self.score = 0
        self.steps = 0

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

    def update(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.move('r')
        if key_pressed[pygame.K_LEFT]:
            self.move('l')
        if key_pressed[pygame.K_UP]:
            self.move('u')
        if key_pressed[pygame.K_DOWN]:
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

    def is_player_collide_wall(self):
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False
