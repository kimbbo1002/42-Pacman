from .maze import Maze


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8


class Player:
    def __init__(self, x: int, y: int, life: int, maze: Maze) -> None:
        self.maze = maze
        self.x = x
        self.y = y
        self.life = life
        self.score = 0
        self.dead = False
        self.respawning = False
        self.super_mode = False
        self.super_mode_start = 0
        self.cheat_mode = False

    def is_available(self, dx: int, dy: int) -> bool:
        x2, y2 = self.x + dx, self.y + dy
        if x2 < 0 or x2 >= len(self.maze.maze[0]) or y2 < 0 or y2 >= len(self.maze.maze):
            return False

        # top
        if dx == 0 and dy == -1:
            if self.maze.maze[self.y][self.x].cell_wall & WALL_TOP:
                return False

        # bottom
        elif dx == 0 and dy == 1:
            if self.maze.maze[self.y][self.x].cell_wall & WALL_BOTTOM:
                return False

        # left
        elif dx == -1 and dy == 0:
            if self.maze.maze[self.y][self.x].cell_wall & WALL_LEFT:
                return False

        # right
        elif dx == 1 and dy == 0:
            if self.maze.maze[self.y][self.x].cell_wall & WALL_RIGHT:
                return False

        return True

    def monitor_score(self) -> None:
        cell = self.maze.maze[self.y][self.x]
        if  cell.super_pacgum is True:
            self.score += cell.point
            cell.super_pacgum = False
        elif cell.pacgum is True:
            self.score += cell.point
            cell.pacgum = False
        
        # add to count ghosts (depending on mode)

    def move_player(self, dx: int, dy: int) -> None:
        if self.is_available(dx, dy):
            self.maze.maze[self.y][self.x].player = False
            self.x += dx
            self.y += dy
            self.maze.maze[self.y][self.x].player = True
        else:
            pass

        self.monitor_score()
