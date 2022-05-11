from demoAgent import demoPlayer
from randomAgent import randPlayer
from compAgent import *
random.seed(1)

case = 3
if case == 0:  # Play with this case to get an idea of the environment
    player1 = demoPlayer()
    player2 = randPlayer(randAgentPath, BLUE)
elif case == 1: # Base Case
    player1 = randPlayer(randAgentPath, BLUE)
    player2 = randPlayer(randAgentPath1, YELLOW)
elif case == 2: # Test if your agent is rational
    player1 = randPlayer(randAgentPath, BLUE)
    player2 = PlayerA()
elif case == 3: # Test if your agents cooperate with each other
    player1 = PlayerA()
    player2 = PlayerB()

all_sprites.add(player1)
all_sprites.add(player2)
players.add(player1)
players.add(player2)

def gen_new_coin():
    new_coin = coin_arr.pop(0)
    coin = Coin(*new_coin)
    if coin not in coins:
        all_sprites.add(coin)
        coins.add(coin)

# Game loop
clock = pygame.time.Clock()
while running:
    dt = clock.tick(FPS)
    global_time += dt
    if global_time > 1000 * SEC:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game update
    if len(coins) < N :
        gen_new_coin()

    all_sprites.update() ## update all objects in all_sprites Group

    # When player 1 hits/collects a coin:
    hits1 = pygame.sprite.spritecollide(player1, coins, True)
    for hit in hits1:
        player1.score += hit.value
    # When player 2 hits/collects a coin:
    hits2 = pygame.sprite.spritecollide(player2, coins, True)
    for hit in hits2:
        player2.score += hit.value

    hits = pygame.sprite.groupcollide(walls, coins, False, True)
    for hit in hits:
        gen_new_coin()

    # !! Note: collision between agents may result in negative utility, so your agents should cooperate well
    if player1.rect.colliderect(player2) or player2.rect.colliderect(player1):
        if (player1.rect.x != 0 and player1.rect.y != 0) and (player2.rect.x != 0 and player2.rect.y != 0):
            player1.score -= 100
            player2.score -= 100

    # Game Render
    screen.fill(WHITE)
    all_sprites.draw(screen) ## draw all objects in all_sprites Group to the screen
    pygame.display.update()

pygame.quit()

print("Score of Player 1:", player1.score)
print("Score of Player 2:", player2.score)
# print("Total Score:", player1.score + player2.score)
