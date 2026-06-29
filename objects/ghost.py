import random
import math
import numpy as np
from collections import deque
from .player import Player
from .maze import Cell
from typing import List
import time
import arcade


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8

RESPAWN_DELAY = 5.0  # seconds before an eaten ghost reappears at its spawn

GHOST_CREEPER = "resources/ghosts/ghost_creeper.png"
GHOST_ENDERMAN = "resources/ghosts/ghost_enderman.png"
GHOST_SKELETON = "resources/ghosts/ghost_skeleton.png"
GHOST_ZOMBIE = "resources/ghosts/ghost_zombie.png"


class Ghost:
    """An enemy that moves through the maze to catch the player."""

    def __init__(self, id: int, x: int, y: int, maze: List[List[Cell]]
                 ) -> None:
        """Create a ghost at (x, y) and remember it as its spawn."""
        self.id = id
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y
        self.history = deque(maxlen=3)
        self.point = 0
        self.is_closest = False
        self.dead = False
        self.dead_since = 0.0
        self.maze = maze

        # initialize textures
        textures = [
            GHOST_CREEPER,
            GHOST_ENDERMAN,
            GHOST_SKELETON,
            GHOST_ZOMBIE,
        ]

        texture = arcade.load_texture(textures[self.id])
        self.sprite = arcade.BasicSprite(texture, scale=0.6)
        self.maze.sprites.append(self.sprite)

    def die(self) -> None:
        """Despawn the ghost: clear its cell and start the respawn timer."""
        self.dead = True
        self.dead_since = time.time()
        self.is_closest = False
        self.maze.maze[self.y][self.x].ghost = False

    def respawn(self) -> None:
        """Bring the ghost back to its starting position."""
        self.dead = False
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.history.clear()
        self.maze.maze[self.y][self.x].ghost = True

    def is_available(self, x2: int, y2: int) -> bool:
        """Tell if the ghost can step to (x2, y2): no wall, no edge,
        no other ghost."""
        if x2 < 0 or x2 >= len(self.maze.maze) or y2 < 0 or y2 >= len(self.maze.maze[0]):
            return False
        next_cell = self.maze.maze[y2][x2]
        if next_cell.ghost is True:
            return False

        dx = x2 - self.x
        dy = y2 - self.y

        cell = self.maze.maze[self.y][self.x]
        # top
        if dy == -1 and dx == 0:
            if cell.cell_wall & WALL_TOP:
                return False

        # bottom
        elif dy == 1 and dx == 0:
            if cell.cell_wall & WALL_BOTTOM:
                return False

        # left
        elif dx == -1 and dy == 0:
            if cell.cell_wall & WALL_LEFT:
                return False

        # right
        elif dx == 1 and dy == 0:
            if cell.cell_wall & WALL_RIGHT:
                return False

        return True

    def random_move(self) -> None:
        """Move to a random free neighbour, avoiding the last cells."""
        directions = [
            (self.x, self.y + 1),
            (self.x, self.y - 1),
            (self.x + 1, self.y),
            (self.x - 1, self.y)
        ]
        available_neighbors: List[Cell] = []
        for next_x, next_y in directions:
            if self.is_available(next_x, next_y):
                if (next_x, next_y) in self.history:
                    continue
                available_neighbors.append(self.maze.maze[next_y][next_x])

        if not available_neighbors:
            for dx, dy in directions:
                if self.is_available(dx, dy):
                    available_neighbors.append(self.maze.maze[dy][dx])
        if not available_neighbors:
            available_neighbors.append(self.maze.maze[self.y][self.x])

        next_cell = random.choice(available_neighbors)
        if next_cell:
            self.history.append((self.x, self.y))
            self.maze.maze[self.y][self.x].ghost = False
            self.x = next_cell.x
            self.y = next_cell.y
            next_cell.ghost = True

    def find_shortest_move(self, player: Player) -> Cell:
        """Return the next cell on the shortest path to the player (BFS)."""
        start_x, start_y = self.x, self.y
        target = (player.x, player.y)

        start_cell = self.maze.maze[start_y][start_x]
        target_cell = self.maze.maze[player.y][player.x]

        # Already on the player's cell: nothing to path-find.
        if (start_x, start_y) == target:
            return start_cell

        queue = deque([(start_x, start_y)])
        path = {start_cell: None}

        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        found = False

        while queue:
            curr_x, curr_y = queue.popleft()
            curr_cell = self.maze.maze[curr_y][curr_x]

            if (curr_x, curr_y) == target:
                found = True
                break

            for dx, dy in directions:
                next_x, next_y = curr_x + dx, curr_y + dy

                if 0 <= next_x < len(self.maze.maze[0]) and 0 <= next_y < len(
                        self.maze.maze):
                    neighbor_cell = self.maze.maze[next_y][next_x]

                    if neighbor_cell not in path:
                        self.x, self.y = curr_x, curr_y

                        if self.is_available(next_x, next_y):
                            path[neighbor_cell] = curr_cell
                            queue.append((next_x, next_y))

        self.x, self.y = start_x, start_y

        if not found or target_cell not in path:
            return start_cell
        curr = target_cell
        while path[curr] != start_cell:
            curr = path[curr]

        return curr

    def chase_move(self, player: Player) -> None:
        """Take one step toward the player."""
        next_cell = self.find_shortest_move(player)
        self.maze.maze[self.y][self.x].ghost = False
        self.x = next_cell.x
        self.y = next_cell.y
        next_cell.ghost = True

    @staticmethod
    def calculate_closest(player: Player, ghosts: List["Ghost"]) -> None:
        """Flag the living ghost nearest to the player as is_closest."""
        for g in ghosts:
            g.is_closest = False

        alive = [g for g in ghosts if not g.dead]
        if not alive:
            return

        dists = []
        for g in alive:
            dist = math.sqrt(math.pow(g.x - player.x, 2) + math.pow(
                    g.y - player.y, 2))
            dists.append(dist)
        closest = alive[int(np.argmin(dists))]
        closest.is_closest = True

    def get_farthest_cell_from_player(self, player: Player) -> Cell:
        """Return the free neighbour cell that is farthest from the player."""
        available_neighbors = []
        directions = [(0, -1), (-1, 0), (1, 0), (0, 1)]
        distances = {}

        for dx, dy in directions:
            next_x = self.x + dx
            next_y = self.y + dy
            if self.is_available(next_x, next_y):
                if (next_x, next_y) in self.history:
                    continue
                available_neighbors.append(self.maze.maze[next_y][next_x])

        if not available_neighbors:
            for dx, dy in directions:
                if self.is_available(self.x + dx, self.y + dy):
                    return self.maze.maze[self.y + dy][self.x + dx]
            return self.maze.maze[self.y][self.x]

        for cell in available_neighbors:
            distance = abs(cell.x - player.x) + abs(cell.y - player.y)
            distances[cell] = distance

        return max(distances, key=distances.get)

    def escape_move(self, player: Player) -> None:
        """Take one step away from the player (used in super_mode)."""
        next_cell = self.get_farthest_cell_from_player(player)
        self.history.append((self.x, self.y))
        self.maze.maze[self.y][self.x].ghost = False
        self.x = next_cell.x
        self.y = next_cell.y
        next_cell.ghost = True


def move_ghosts(player: Player, ghosts: List[Ghost]) -> None:
    """Move every ghost once: respawn the dead ones, then chase, flee or
    wander depending on the player's state, and check for a collision."""
    now = time.time()
    if player.maze.ghost_freeze is False:
        for g in ghosts:
            if g.dead and now - g.dead_since >= RESPAWN_DELAY:
                g.respawn()

        if not player.dead:
            Ghost.calculate_closest(player, ghosts)
        for g in ghosts:
            if g.dead:
                continue
            if player.super_mode:
                g.escape_move(player)
            elif g.is_closest is False or player.dead:
                g.random_move()
            else:
                g.chase_move(player)

    player.check_ghost_collision()
