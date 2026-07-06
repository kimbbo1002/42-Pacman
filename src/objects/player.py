from .maze import Maze
import time
import arcade
from src.parsing import Config


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8


class Player:
    """The character moved by the user: eats pacgums and ghosts."""

    def __init__(self, config: Config, x: int, y: int, lives: int,
                 maze: Maze, score: int) -> None:
        """Create the player at (x, y) with a number of lives."""
        self.config = config
        self.maze = maze
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y
        self.lives = lives
        self.score = score
        self.dead = False
        self.dead_since = 0.0
        self.respawning = False
        self.respawning_start = 0.0
        self.super_mode = False
        self.super_mode_start = 0.0
        self.cheat_mode = False
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        self.move_time = 0.0

        # initialize sprites for player, themed from the config
        assets = self.maze.assets
        normal_texture = arcade.load_texture(
            assets.texture("player", "normal"))
        super_texture = arcade.load_texture(
            assets.texture("player", "super"))
        cheat_texture = arcade.load_texture(
            assets.texture("player", "cheat"))
        self.sprite_normal = arcade.BasicSprite(normal_texture, scale=0.6)
        self.sprite_super = arcade.BasicSprite(super_texture, scale=0.6)
        self.sprite_cheat = arcade.BasicSprite(cheat_texture, scale=0.6)

        # append sprites to the character layer (drawn on top of pacgums)
        self.maze.character_sprites.append(self.sprite_normal)
        self.maze.character_sprites.append(self.sprite_super)
        self.maze.character_sprites.append(self.sprite_cheat)

    def die(self) -> None:
        """Kill the player: lose one life and clear its cell."""
        self.dead = True
        self.dead_since = time.time()
        self.lives -= 1
        self.maze.maze[self.y][self.x].player = False

    def respawn(self) -> None:
        """Put the player back on its starting cell."""
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.maze.maze[self.y][self.x].player = True
        self.dead = False
        self.respawning_start = time.time()
        self.respawning = True

    def is_available(self, dx: int, dy: int) -> bool:
        """Tell if the player can move by (dx, dy): no wall, no edge."""
        x2, y2 = self.x + dx, self.y + dy
        if x2 < 0 or x2 >= len(
                self.maze.maze[0]) or y2 < 0 or y2 >= len(self.maze.maze):
            return False
        if self.cheat_mode:
            return True

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
        """Eat the pacgum on the current cell and add its points.
            A super pacgum also turns on super_mode."""
        cell = self.maze.maze[self.y][self.x]

        if cell.super_pacgum is True:
            self.score += cell.point
            cell.super_pacgum = False
            self.maze.super_pacgums -= 1

            # Start super mode
            self.super_mode_start = time.time()
            self.super_mode = True

        elif cell.pacgum is True:
            self.score += cell.point
            cell.pacgum = False
            self.maze.pacgums -= 1

    def check_ghost_collision(self) -> None:
        """Eat in super_mode, else die. Called after every movement
            (player and ghosts) so a contact is never missed between
            two ghost ticks or on a swap of cells."""
        if self.dead:
            return
        for g in self.maze.ghosts:
            if g.dead or g.x != self.x or g.y != self.y:
                continue
            if self.super_mode:
                self.score += g.point
                g.die()
            else:
                if self.respawning is False and self.cheat_mode is False:
                    self.die()
                    break

    def is_dead(self) -> bool:
        """ Return True if the player no longer has lives.
            False if he is still alive."""
        if self.lives <= 0:
            return True
        return False

    def move_player(self, dx: int, dy: int) -> None:
        """Move the player by (dx, dy), then check pacgums and ghosts."""
        if self.dead:
            return
        if self.is_available(dx, dy):
            self.maze.maze[self.y][self.x].player = False
            self.x += dx
            self.y += dy
            self.maze.maze[self.y][self.x].player = True
        else:
            pass

        self.monitor_score()
        self.check_ghost_collision()
