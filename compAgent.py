"""User defined player classes."""

from enum import Enum, unique

from env import *

import heapq
import math

# Design your own agent(s) in this file.
# You can use your own favorite icon or as simple as a colored square (with different colors) to represent your agent(s).
playerA_img = pygame.image.load(os.path.join("img", "playerA.png")).convert()
playerB_img = pygame.image.load(os.path.join("img", "playerB.png")).convert()

@unique
class Movement(Enum):
    """Movement enum to represent the direction of the agent."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


def get_distance(a: tuple[int, int], b: tuple[int, int], m_type: str) -> float:
    """Return the distance between a and b Distance.

    m_type:
        "e": Euclidean Distance
        "m": Manhattan Distance
    """
    match m_type:
        case "e":
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
        case "m":
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
    return -1


class PlayerA(pygame.sprite.Sprite):
    """Defines a Hybrid, Partitioned, Pathfinding agent.

    The agent is hybrid in pursuing the best coin.
    The agent is partitioned in its responsibilities (top/bottom of map).
    The agent uses a pathfinding algorithm to move to the closest coin.
    """

    def __init__(self):
        """Initialize the agent."""
        pygame.sprite.Sprite.__init__(self)
        self.image = playerA_img
        self.image = pygame.transform.scale(playerA_img, (WALLSIZE, WALLSIZE))
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(
            self.image, rand_color(random.randint(0, N)), self.image.get_rect(), 1
        )
        self.rect: pygame.rect.Rect = self.image.get_rect()  # get image position
        self.rect.x = 0
        self.rect.y = 0
        self.speedx = SPEED
        self.speedy = SPEED
        self.score = 0
        self.steps = 0

        self.my_pos: tuple[int, int] = (0, 0)
        self.their_pos: tuple[int, int] = (0, 0)
        self.path: list[tuple[int, int]] = []


        self.HALF_HEIGHT = (HEIGHT // self.speedy) // 2
        self.HALF_WIDTH = (WIDTH // self.speedx) // 2

        self.coin_dict: dict[tuple[int, int], int]
        self.wall_pos = [
            (wall[0] // self.speedx, wall[1] // self.speedy)
            for wall in get_wall_data()
        ]

    def _is_move_blocked(self, mov_dir: Movement) -> bool:
        """Determine if a movement would be blocked."""
        next_pos = (
            self.my_pos[0] + mov_dir.value[0],
            self.my_pos[1] + mov_dir.value[1],
        )
        if next_pos in self.wall_pos:
            return True
        return False

    def _translate_coins(self) -> dict[tuple[int, int], int]:
        """Convert coin data into a dictionary, location -> value."""
        coins: dict[tuple[int, int], int] = {}
        coin_values, coin_locs = get_coin_data()
        for c_val, c_loc in zip(coin_values, coin_locs):
            pos = (c_loc[0] // self.speedx, c_loc[1] // self.speedy)
            coins[pos] = c_val
        return coins

    def move(self, direction):
        """Translate movement intention into a change in position."""
        self.steps += 1
        match direction:
            case Movement.RIGHT:
                self.rect.x += self.speedx
                if self.is_player_collide_wall():
                    self.rect.x -= self.speedx
            case Movement.LEFT:
                self.rect.x -= self.speedx
                if self.is_player_collide_wall():
                    self.rect.x += self.speedx
            case Movement.UP:
                self.rect.y -= self.speedy
                if self.is_player_collide_wall():
                    self.rect.y += self.speedy
            case Movement.DOWN:
                self.rect.y += self.speedy
                if self.is_player_collide_wall():
                    self.rect.y -= self.speedy

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
        """Determine wall collision state."""
        for wall in walls:
            if self.rect.colliderect(wall):  # type: ignore
                return True
        return False

    def update(self):
        """Implement agent's hybrid logic."""
        # print("Current Time in milliseconds:", pygame.time.get_ticks())  ## get current time
        # print("Coin Data:", get_coin_data())                             ## get current information of the coins
        # print("Wall Positions:", get_wall_data())                        ## get current information of the walls

        # update my_pos
        self.my_pos = (self.rect.x // self.speedx, self.rect.y // self.speedy)

        # update coin_dict
        self.coin_dict = self._translate_coins()

        # calculate agent's coin queue
        self.coin_queue: list[tuple[float, int, tuple[int, int]]] = []
        for c_loc, c_val in self.coin_dict.items():
            if pygame.time.get_ticks() < 1000 and c_loc[0] < self.HALF_WIDTH:
                continue
            c_dist = get_distance(self.my_pos, c_loc, "m")

            heapq.heappush(self.coin_queue, (c_dist, 9 - c_val, c_loc))

        if not self.coin_queue:
            return

        goal = heapq.heappop(self.coin_queue)
        visited, next_pos = self.find_path(goal[0], goal[2])

        self.path = [next_pos]
        while next_pos != self.my_pos:
            next_pos = visited[next_pos]
            self.path.append(next_pos)

        while self.path and self.coin_dict[goal[2]]:
            cmp_pos = self.path.pop()
            rel_x = cmp_pos[0] - self.my_pos[0]
            rel_y = cmp_pos[1] - self.my_pos[1]
            match (rel_x, rel_y):
                case (1, 0):
                    self.move(Movement.RIGHT)
                case (-1, 0):
                    self.move(Movement.LEFT)
                case (0, 1):
                    self.move(Movement.DOWN)
                case (0, -1):
                    self.move(Movement.UP)

    def find_path(
        self, dist: float, goal: tuple[int, int]
    ) -> tuple[dict[tuple[int, int], tuple[int, int]], tuple[int, int]]:
        """Return path via modified Astar."""
        # frontier: (priority, current_pos, prev_pos)
        frontier: list[tuple[int, tuple[int, int], tuple[int, int]]] = []
        visited: dict[tuple[int, int], tuple[int, int]] = {}

        heapq.heappush(frontier, (0, self.my_pos, self.my_pos))
        # Get the path to the coin
        while frontier:
            current = heapq.heappop(frontier)

            for mov_dir in Movement:
                next_pos = (
                    current[1][0] + mov_dir.value[0],
                    current[1][1] + mov_dir.value[1],
                )
                if get_distance(next_pos, goal, "m") > dist + 3:
                    continue

                if (
                    -1 in next_pos
                    or next_pos[0] > WIDTH // self.speedx
                    or next_pos[1] > HEIGHT // self.speedy
                ):
                    continue

                if next_pos in visited.values():
                    continue
                if next_pos in self.wall_pos:
                    continue
                if next_pos == goal:
                    visited[next_pos] = current[1]
                    return visited, next_pos
                if current[0] == 10:
                    visited[next_pos] = current[1]
                    return visited, next_pos

                heapq.heappush(
                    frontier,
                    (
                        current[0] + 1,
                        next_pos,
                        current[1],
                    ),
                )
                visited[next_pos] = current[1]

        return visited, self.my_pos

# You can design another player class to represent the other player if they work in different ways.
class PlayerB(PlayerA):
    """Placeholder for Player B."""

    def update(self):
        """Implement agent's hybrid logic."""
        # update my_pos
        self.my_pos = (self.rect.x // self.speedx, self.rect.y // self.speedy)

        # update their_pos
        both_players = [p for p in players]
        for p in both_players:
            if p.rect and p.rect.x != self.rect.x and p.rect.y != self.rect.y:
                self.their_pos = (p.rect.x // self.speedx, p.rect.y // self.speedy)

        # update coin_dict
        self.coin_dict = self._translate_coins()

        # calculate agent's coin queue
        self.coin_queue: list[tuple[float, int, tuple[int, int]]] = []
        for c_loc, c_val in self.coin_dict.items():
            c_dist = get_distance(self.my_pos, c_loc, "m")
            if self.their_pos:
                o_dist = get_distance(self.their_pos, c_loc, "m")
                if o_dist < c_dist:
                    continue

            heapq.heappush(self.coin_queue, (c_dist, 9 - c_val, c_loc))

        if not self.coin_queue:
            return

        goal = heapq.heappop(self.coin_queue)
        visited, next_pos = self.find_path(goal[0], goal[2])

        self.path = [next_pos]
        while next_pos != self.my_pos:
            next_pos = visited[next_pos]
            self.path.append(next_pos)

        while self.path and self.coin_dict[goal[2]]:
            #if get_distance(self.their_pos, self.my_pos, "m") < 4:
            #    break
            cmp_pos = self.path.pop()
            rel_x = cmp_pos[0] - self.my_pos[0]
            rel_y = cmp_pos[1] - self.my_pos[1]
            match (rel_x, rel_y):
                case (1, 0):
                    self.move(Movement.RIGHT)
                case (-1, 0):
                    self.move(Movement.LEFT)
                case (0, 1):
                    self.move(Movement.DOWN)
                case (0, -1):
                    self.move(Movement.UP)




# Hint: To cooperate, it's better if your agents explore different areas of the map, so you can write a
# communication function to broadcast their locations in order that they can keep a reasonable distance from each other.
# The bottom line is at least they shouldn't collide with each other.
# You may try different strategies (e.g. reactive, heuristic, learning, etc).
