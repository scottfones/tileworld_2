"""Self-contained code for player B."""

import heapq
from enum import Enum, unique

from env import *

Location = tuple[int, int]

sonic_img = pygame.image.load(os.path.join("img", "sonic_art.png")).convert_alpha()


@unique
class Movement(Enum):
    """Movement enum to represent the direction of the agent."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Partition:
    """Partition class to represent a partition of the map."""

    def __init__(self, name: str, x_bounds: tuple[int, int], y_bounds: tuple[int, int]):
        """Set the partition boundaries."""
        self.name = name
        self.x_min, self.x_max = x_bounds
        self.y_min, self.y_max = y_bounds

    def __contains__(self, loc: Location) -> bool:
        """Check if `loc` is in the partition."""
        return self.x_min <= loc[0] <= self.x_max and self.y_min <= loc[1] <= self.y_max

    def __repr__(self) -> str:
        """Return the partition name and bounds."""
        return f"{self.name}: x=[{self.x_min}, {self.x_max}], y=[{self.y_min}, {self.y_max}]"


class PlayerB(pygame.sprite.Sprite):
    """Defines a Hybrid, Partitioned, Pathfinding agent.

    The agent is hybrid in pursuing the best coin.
    The agent is partitioned in its responsibilities (3x3 partition of map).
    The agent uses a pathfinding algorithm to move to the closest coin.
    """

    # pylint: disable=too-many-instance-attributes

    # calculate scaling constants
    SCALED_N = HEIGHT // WALLSIZE
    THIRD_N = HEIGHT // (WALLSIZE * 3)

    # scale wall locations
    WALL_POS = [(wall[0] // WALLSIZE, wall[1] // WALLSIZE) for wall in get_wall_data()]

    # define partitions
    PART_TL = Partition("TL", (0, THIRD_N), (0, THIRD_N))
    PART_TM = Partition("TM", (THIRD_N, 2 * THIRD_N), (0, THIRD_N))
    PART_TR = Partition("TR", (2 * THIRD_N, SCALED_N), (0, THIRD_N))

    PART_ML = Partition("ML", (0, THIRD_N), (THIRD_N, 2 * THIRD_N))
    PART_MM = Partition("MM", (THIRD_N, 2 * THIRD_N), (THIRD_N, 2 * THIRD_N))
    PART_MR = Partition("MR", (2 * THIRD_N, SCALED_N), (THIRD_N, 2 * THIRD_N))

    PART_BL = Partition("BL", (0, THIRD_N), (2 * THIRD_N, SCALED_N))
    PART_BM = Partition("BM", (THIRD_N, 2 * THIRD_N), (2 * THIRD_N, SCALED_N))
    PART_BR = Partition("BR", (2 * THIRD_N, SCALED_N), (2 * THIRD_N, SCALED_N))

    PART_LIST = [
        PART_BL,
        PART_BM,
        PART_BR,
        PART_TL,
        PART_TM,
        PART_TR,
        PART_ML,
        PART_MM,
        PART_MR,
    ]

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

        # view partition boundaries
        # for part in self.PART_LIST:
        #    print(part)

    def _is_move_blocked(self, mov_dir: Movement, my_pos: Location) -> bool:
        """Determine if a movement would be blocked."""
        next_pos = (
            my_pos[0] + mov_dir.value[0],
            my_pos[1] + mov_dir.value[1],
        )
        if next_pos in self.WALL_POS:  # type: ignore
            return True
        return False

    def _loc_identity_check(self, pos: Location) -> bool:
        """Check if the position is the same as the player's position."""
        return (pos[0] * WALLSIZE, pos[1] * WALLSIZE) == (self.rect.x, self.rect.y)

    def _translate_coins(self, their_parts: list[Partition]) -> list[Location]:
        """Convert coin data into a dictionary, location -> value."""
        target_coins: list[Location] = []
        _, coin_locs = get_coin_data()

        for c_loc in coin_locs:
            c_pos = (c_loc[0] // self.speedx, c_loc[1] // self.speedy)

            if any((c_pos in part for part in their_parts)):
                continue

            target_coins.append(c_pos)
        return target_coins

    def _update_players_pos(self) -> tuple[Location, Location]:
        """Translate and verify both player's locations."""
        # list comprehension as Group isn't subscriptable
        my_pos, their_pos = [
            (plr.rect.x // self.speedx, plr.rect.y // self.speedy)
            for plr in players
            if plr.rect
        ]

        # swap postions if they're reversed
        if not self._loc_identity_check(my_pos):
            their_pos, my_pos = my_pos, their_pos
        return my_pos, their_pos

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
        my_pos, their_pos = self._update_players_pos()
        their_parts = [part for part in self.PART_LIST if their_pos in part]

        # print excluded partitions
        # print(their_parts)

        target_coins = self._translate_coins(their_parts)

        if not target_coins:
            return

        goal, visited, next_pos = self.find_path(target_coins, my_pos)

        # backtrace to construct path
        path = [next_pos]
        while next_pos != my_pos:
            next_pos = visited[next_pos]
            path.append(next_pos)

        while path and goal in target_coins:
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

            # update to make sure target coin still exists
            target_coins = self._translate_coins(their_parts)

    def find_path(
        self, target_coins: list[Location], my_pos: Location
    ) -> tuple[Location, dict[Location, Location], Location]:
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
                if next_pos in target_coins:
                    visited[next_pos] = current[1]
                    return next_pos, visited, next_pos
                if current[0] == 10:
                    visited[next_pos] = current[1]
                    return next_pos, visited, next_pos

                heapq.heappush(
                    frontier,
                    (
                        current[0] + 1,
                        next_pos,
                        current[1],
                    ),
                )
                visited[next_pos] = current[1]

        return my_pos, visited, my_pos
