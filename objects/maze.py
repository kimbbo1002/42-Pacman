from typing import List
from parsing import Config


class Cell:
    """One square of the maze: its walls and what sits on it."""

    def __init__(self, x: int, y: int, cell_wall: int) -> None:
        """Initialize each cell of maze."""
        self.x = x
        self.y = y
        self.cell_wall = cell_wall
        self.super_pacgum = False
        self.player = False
        self.ghost = False
        self.pattern_42 = True if cell_wall == 15 else False
        self.pacgum = False
        self.point = 0


class Maze:
    """The grid of cells and everything placed on it."""

    def __init__(self, maze: List[List[int]], config: Config) -> None:
        """Initialize the maze, place pacgums & super_pacgums & player."""
        self.maze: List[List[Cell]] = []
        self.config = config
        self.cols = config.width
        self.rows = config.height
        self.pacgums = 0
        self.end_of_game = False

        # initialize maze
        for y, line in enumerate(maze):
            line_list = []
            for x, col in enumerate(line):
                cell = Cell(x, y, col)
                line_list.append(cell)
            self.maze.append(line_list)

    def place_objects(self) -> None:
        """Fill the maze: super pacgums in the corners, ghosts near them,
        the player in the middle, and a normal pacgum in every other cell."""
        from .ghost import Ghost
        from .player import Player

        # place super_pacgums & ghosts
        super_pacgum_coordinates = [
            (0, 0),
            (0, self.cols - 1),
            (self.rows - 1, 0),
            (self.rows - 1, self.cols - 1)
        ]
        ghost_coordinates = [
            (1, 0),
            (0, self.rows - 2),
            (self.cols - 1, 1),
            (self.cols - 2, self.rows - 1)
        ]

        for x, y in super_pacgum_coordinates:
            cell = self.maze[y][x]
            cell.super_pacgum = True
            cell.point = self.config.points_per_super_pacgum
            self.pacgums += 1

        self.ghosts: List[Ghost] = []
        for i, (x, y) in enumerate(ghost_coordinates):
            ghost = Ghost(i, x, y, self.maze)
            ghost.point = self.config.points_per_ghost
            self.ghosts.append(ghost)
            self.maze[y][x].ghost = True

        # place player
        self.player = Player(self.cols // 2, self.rows // 2,
                             self.config.lives, self)
        self.maze[self.rows // 2][self.cols // 2].player = True

        # place pacgums
        for y in range(len(self.maze[0])):
            for x in range(len(self.maze)):
                cell = self.maze[y][x]
                if (not cell.super_pacgum and not cell.player
                        and not cell.pattern_42):
                    cell.pacgum = True
                    cell.point = self.config.points_per_pacgum
                    self.pacgums += 1

    def check_pacgums_left(self) -> None:
        if self.pacgums == 0:
            self.end_of_game = True
