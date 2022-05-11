"""User defined player classes."""

import heapq

from enum import Enum, unique

from env import *

Location = tuple[int, int]

# You can use your own favorite icon or as simple as a colored square
# (with different colors) to represent your agent(s).
playerA_img = pygame.image.load(os.path.join("img", "playerA.png")).convert()
playerB_img = pygame.image.load(os.path.join("img", "playerB.png")).convert()
sonic_img = pygame.image.load(os.path.join("img", "sonic_art.png")).convert()


@unique
class Movement(Enum):
    """Movement enum to represent the direction of the agent."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


def get_distance(loc_a: Location, loc_b: Location) -> int:
    """Return the Manhattan distance between `loc_a` and `loc_b` Distance."""
    return abs(loc_a[0] - loc_b[0]) + abs(loc_a[1] - loc_b[1])


class Partition:
    """Partition class to represent a partition of the map."""

    def __init__(self, x_min: int, x_max: int, y_min: int, y_max: int):
        """Set the partition boundaries."""
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def __contains__(self, loc: Location) -> bool:
        """Check if `loc` is in the partition."""
        return self.x_min <= loc[0] <= self.x_max and self.y_min <= loc[1] <= self.y_max


class PlayerA(pygame.sprite.Sprite):
    """Defines a Hybrid, Partitioned, Pathfinding agent.

    The agent is hybrid in pursuing the best coin.
    The agent is partitioned in its responsibilities (top/bottom of map).
    The agent uses a pathfinding algorithm to move to the closest coin.
    """

    # pylint: disable=too-many-instance-attributes

    HALF_HEIGHT = (HEIGHT // WALLSIZE) // 2
    HALF_WIDTH = (WIDTH // WALLSIZE) // 2
    WALL_POS = [(wall[0] // WALLSIZE, wall[1] // WALLSIZE) for wall in get_wall_data()]

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

    def _is_move_blocked(self, mov_dir: Movement, my_pos: Location) -> bool:
        """Determine if a movement would be blocked."""
        next_pos = (
            my_pos[0] + mov_dir.value[0],
            my_pos[1] + mov_dir.value[1],
        )
        if next_pos in self.WALL_POS:  # type: ignore
            return True
        return False

    def _translate_coins(self) -> dict[Location, int]:
        """Convert coin data into a dictionary, location -> value."""
        coins_dict: dict[Location, int] = {}
        coin_values, coin_locs = get_coin_data()
        for c_val, c_loc in zip(coin_values, coin_locs):
            pos = (c_loc[0] // self.speedx, c_loc[1] // self.speedy)
            coins_dict[pos] = c_val
        return coins_dict

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
        self.rect.right = min(self.rect.right, WIDTH)
        self.rect.left = max(self.rect.left, 0)
        self.rect.bottom = min(self.rect.bottom, HEIGHT)
        self.rect.top = max(self.rect.top, 0)

    def is_player_collide_wall(self):
        """Determine wall collision state."""
        for wll in walls:
            if self.rect.colliderect(wll):  # type: ignore
                return True
        return False

    def update(self):
        """Implement agent's hybrid logic."""
        # update my_pos
        my_pos = (self.rect.x // self.speedx, self.rect.y // self.speedy)

        # update coin_dict
        coin_dict = self._translate_coins()

        # calculate agent's coin queue
        coin_queue: list[tuple[float, int, Location]] = []
        for c_loc, c_val in coin_dict.items():
            c_dist = get_distance(my_pos, c_loc)

            heapq.heappush(coin_queue, (c_dist, 9 - c_val, c_loc))

        if not coin_queue:
            return

        goal = heapq.heappop(coin_queue)
        visited, next_pos = self.find_path(goal[0], goal[2], my_pos)

        path = [next_pos]
        while next_pos != my_pos:
            next_pos = visited[next_pos]
            path.append(next_pos)

        while path and coin_dict[goal[2]]:
            cmp_pos = path.pop()
            rel_x = cmp_pos[0] - my_pos[0]
            rel_y = cmp_pos[1] - my_pos[1]
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
        self, dist: float, goal: Location, my_pos: Location
    ) -> tuple[dict[Location, Location], Location]:
        """Return path via modified Astar."""
        # frontier: (priority, current_pos, prev_pos)
        frontier: list[tuple[int, Location, Location]] = []
        visited: dict[Location, Location] = {}

        heapq.heappush(frontier, (0, my_pos, my_pos))
        # Get the path to the coin
        while frontier:
            current = heapq.heappop(frontier)

            for mov_dir in Movement:
                next_pos = (
                    current[1][0] + mov_dir.value[0],
                    current[1][1] + mov_dir.value[1],
                )
                if get_distance(next_pos, goal) > dist + 3:
                    continue

                if (
                    -1 in next_pos
                    or next_pos[0] > WIDTH // self.speedx
                    or next_pos[1] > HEIGHT // self.speedy
                ):
                    continue

                if next_pos in visited.values():
                    continue
                if next_pos in self.WALL_POS:
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

        return visited, my_pos


class PlayerB(pygame.sprite.Sprite):
    """Defines a Hybrid, Partitioned, Pathfinding agent.

    The agent is hybrid in pursuing the best coin.
    The agent is partitioned in its responsibilities (top/bottom of map).
    The agent uses a pathfinding algorithm to move to the closest coin.
    """

    # pylint: disable=too-many-instance-attributes

    SCALED_N = HEIGHT // WALLSIZE
    HALF_HEIGHT = HALF_WIDTH = SCALED_N // 2
    WALL_POS = [(wall[0] // WALLSIZE, wall[1] // WALLSIZE) for wall in get_wall_data()]

    PART_TL = Partition(0, HALF_WIDTH, 0, HALF_HEIGHT)
    PART_TR = Partition(HALF_WIDTH, SCALED_N, 0, HALF_HEIGHT)
    PART_BL = Partition(0, HALF_WIDTH, HALF_HEIGHT, SCALED_N)
    PART_BR = Partition(HALF_WIDTH, SCALED_N, HALF_HEIGHT, SCALED_N)
    PART_LIST = [PART_BL, PART_BR, PART_TL, PART_TR]

    def __init__(self):
        """Initialize player and set custom image."""
        pygame.sprite.Sprite.__init__(self)
        self.image = sonic_img
        self.image = pygame.transform.scale(sonic_img, (WALLSIZE, WALLSIZE))
        self.image.set_colorkey(BLUE)
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

    def _loc_identity_check(self, pos: Location) -> bool:
        """Check if the position is the same as the player's position."""
        return (pos[0] * WALLSIZE, pos[1] * WALLSIZE) == (self.rect.x, self.rect.y)

    def _is_move_blocked(self, mov_dir: Movement, my_pos: Location) -> bool:
        """Determine if a movement would be blocked."""
        next_pos = (
            my_pos[0] + mov_dir.value[0],
            my_pos[1] + mov_dir.value[1],
        )
        if next_pos in self.WALL_POS:  # type: ignore
            return True
        return False

    def _translate_coins(self) -> dict[Location, int]:
        """Convert coin data into a dictionary, location -> value."""
        coins_dict: dict[Location, int] = {}
        coin_values, coin_locs = get_coin_data()
        for c_val, c_loc in zip(coin_values, coin_locs):
            pos = (c_loc[0] // self.speedx, c_loc[1] // self.speedy)
            coins_dict[pos] = c_val
        return coins_dict

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
        self.rect.right = min(self.rect.right, WIDTH)
        self.rect.left = max(self.rect.left, 0)
        self.rect.bottom = min(self.rect.bottom, HEIGHT)
        self.rect.top = max(self.rect.top, 0)

    def is_player_collide_wall(self):
        """Determine wall collision state."""
        for wll in walls:
            if self.rect.colliderect(wll):  # type: ignore
                return True
        return False

    def update(self):
        """Implement agent's hybrid logic."""
        # update positions
        their_pos, my_pos = [
            (plr.rect.x // self.speedx, plr.rect.y // self.speedy)
            for plr in players
            if plr.rect
        ]

        # check pos assignments
        if not self._loc_identity_check(my_pos):
            my_pos, their_pos = their_pos, my_pos

        their_parts = [part for part in PlayerB.PART_LIST if their_pos in part]

        # update coin_dict
        coin_dict = self._translate_coins()

        # calculate agent's coin queue
        coin_queue: list[tuple[float, int, Location]] = []
        for c_loc, c_val in coin_dict.items():
            if any((c_loc in part for part in their_parts)):
                continue

            c_dist = get_distance(my_pos, c_loc)
            heapq.heappush(coin_queue, (c_dist, 9 - c_val, c_loc))

        if not coin_queue:
            return

        goal = heapq.heappop(coin_queue)
        visited, next_pos = self.find_path(goal[0], goal[2], my_pos)

        path = [next_pos]
        while next_pos != my_pos:
            next_pos = visited[next_pos]
            path.append(next_pos)

        while path and coin_dict[goal[2]]:
            cmp_pos = path.pop()
            rel_x = cmp_pos[0] - my_pos[0]
            rel_y = cmp_pos[1] - my_pos[1]
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
        self, dist: float, goal: Location, my_pos: Location
    ) -> tuple[dict[Location, Location], Location]:
        """Return path via modified Astar."""
        # frontier: (priority, current_pos, prev_pos)
        frontier: list[tuple[int, Location, Location]] = []
        visited: dict[Location, Location] = {}

        heapq.heappush(frontier, (0, my_pos, my_pos))
        # Get the path to the coin
        while frontier:
            current = heapq.heappop(frontier)

            for mov_dir in Movement:
                next_pos = (
                    current[1][0] + mov_dir.value[0],
                    current[1][1] + mov_dir.value[1],
                )
                if get_distance(next_pos, goal) > dist + 3:
                    continue

                if (
                    -1 in next_pos
                    or next_pos[0] > WIDTH // self.speedx
                    or next_pos[1] > HEIGHT // self.speedy
                ):
                    continue

                if next_pos in visited.values():
                    continue
                if next_pos in self.WALL_POS:
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

        return visited, my_pos
