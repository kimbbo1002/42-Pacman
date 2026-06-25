import random
import math
import numpy as np
from collections import deque
from .player import Player
from .maze import Maze, Cell
from typing import List, Any, Dict


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8


class Ghost:
    def __init__(self, id: int, x: int, y: int, maze: List[List[Cell]]) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.point = 0
        self.is_closest = False
        self.dead = False
        self.maze = maze

    def is_available(self, x2: int, y2: int) -> bool:
        if x2 < 0 or x2 >= len(self.maze) or y2 < 0 or y2 >= len(self.maze[0]):
            return False
        next_cell = self.maze[y2][x2]
        if next_cell.ghost is True:
            return False

        dx = x2 - self.x
        dy = y2 - self.y

        cell = self.maze[self.y][self.x]
        # top
        if dy == 1 and dx == 0:
            if cell.cell_wall & WALL_TOP:
                return False

        # bottom
        elif dy == -1 and dx == 0:
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
        directions = [
            (self.x, self.y + 1),
            (self.x, self.y - 1),
            (self.x + 1, self.y),
            (self.x - 1, self.y)
        ]
        available_neighbors: set[Cell] = set()
        for x, y in directions:
            if self.is_available(x, y):
                available_neighbors.add(self.maze[y][x])

        next_cell = random.choice(available_neighbors)
        if next_cell:
            self.maze[self.y][self.x].ghost = False
            self.x = next_cell.x
            self.y = next_cell.y
            next_cell.ghost = True

    def find_shortest_move(self, player: Player) -> Cell:
        start_x, start_y = self.x, self.y
        target = (player.x, player.y)

        queue = deque([(start_x, start_y)])
        path = {self.maze[self.y][self.x]: None}

        start_cell = self.maze[start_x][start_y]
        target_cell = self.maze[player.x][player.y]

        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        found = False

        while queue:
            curr_x, curr_y = queue.popleft()
            curr_cell = self.maze[curr_x][curr_y]

            if (curr_x, curr_y) == target:
                found = True
                break

            for dx, dy in directions:
                next_x, next_y = curr_x + dx, curr_y + dy

                if 0 <= next_x < len(self.maze) and 0 <= next_y < len(self.maze[0]):
                    neighbor_cell = self.maze[next_x][next_y]

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
        next_cell = self.find_shortest_move(player)
        self.maze[self.y][self.x].ghost = False
        self.x = next_cell.x
        self.y = next_cell.y
        next_cell.ghost = True

    @staticmethod
    def calculate_closest(player: Player, ghosts: List["Ghost"]) -> None:
        dists = []
        for g in ghosts:
            dist = math.sqrt(math.pow(g.x - player.x, 2) + math.pow(g.y - player.y, 2))
            dists.append(dist)
        min = np.argmin(dists)
        for g in ghosts:
            if g.id == min:
                g.is_closest = True


def move_ghosts(player: Player, ghosts: List[Ghost]) -> None:
    Ghost.calculate_closest(player, ghosts)
    for g in ghosts:
        if g.is_closest is False:
            g.random_move()
        else:
            g.chase_move(player)
