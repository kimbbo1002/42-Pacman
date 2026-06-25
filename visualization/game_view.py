from parsing import Config
from mazegenerator import MazeGenerator
import arcade
from objects import Maze, Cell, Player


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8

WALL_COLOR = arcade.color.BLUE
PACGUM_COLOR = arcade.color.YELLOW
SUPER_PACGUM_COLOR = arcade.color.WHITE

WALL_WIDTH = 3
MARGIN = 50


class GameView(arcade.View):
    """View that draws the maze."""

    def __init__(self, config: Config, level_index: int, score: int):
        """Store the maze size and the positions of the pacgums."""
        super().__init__()
        self.config = config
        self.cols = config.width
        self.rows = config.height
        self.level_index = level_index
        self.score = score

    def on_show_view(self):
        self.window.background_color = arcade.csscolor.BLACK

    def setup(self, generator: MazeGenerator):
        """Build the maze and place a pacgum in every cell."""
        maze = generator.maze
        self.maze = Maze(maze, self.config)
        self.maze.place_objects()
        self.player = self.maze.player

    def _grid_geometry(self):
        """Return the cell size and where to start drawing the maze."""
        w = self.window.width
        h = self.window.height
        cell_size = min(
            (w - 2 * MARGIN) // self.cols,
            (h - 2 * MARGIN) // self.rows,
        )
        maze_w = self.cols * cell_size
        maze_h = self.rows * cell_size
        offset_x = (w - maze_w) / 2
        offset_y = (h - maze_h) / 2
        maze_top = offset_y + maze_h
        return cell_size, offset_x, maze_top

    def cell_center(self, row: int, col: int, cell_size: int,
                    offset_x: float, maze_top: float):
        """Return the screen point at the middle of a cell."""
        cx = offset_x + col * cell_size + cell_size / 2
        cy = maze_top - row * cell_size - cell_size / 2
        return cx, cy

    def on_draw(self):
        """Draw the walls and the pacgums on the screen."""
        self.clear()

        cell_size, offset_x, maze_top = self._grid_geometry()
        radius = max(2, cell_size // 10)
        s_radius = max(5, cell_size // 4)

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.maze.maze[r][c]

                left = offset_x + c * cell_size
                right = left + cell_size
                top = maze_top - r * cell_size
                bottom = top - cell_size

                cx, cy = self.cell_center(r, c, cell_size, offset_x, maze_top)

                # display walls
                if cell.cell_wall & WALL_TOP:
                    arcade.draw_line(left, top, right, top,
                                     WALL_COLOR, WALL_WIDTH)
                if cell.cell_wall & WALL_BOTTOM:
                    arcade.draw_line(left, bottom, right, bottom,
                                     WALL_COLOR, WALL_WIDTH)
                if cell.cell_wall & WALL_LEFT:
                    arcade.draw_line(left, bottom, left, top,
                                     WALL_COLOR, WALL_WIDTH)
                if cell.cell_wall & WALL_RIGHT:
                    arcade.draw_line(right, bottom, right, top,
                                     WALL_COLOR, WALL_WIDTH)

                # display pacgums & super_pacgums
                if cell.pacgum is True:
                    arcade.draw_circle_filled(cx, cy, radius, PACGUM_COLOR)
                if cell.super_pacgum is True:
                    arcade.draw_circle_filled(cx, cy, s_radius, SUPER_PACGUM_COLOR)

                # display player
                if cell.player is True:
                    arcade.draw_circle_filled(cx, cy, s_radius, arcade.color.VIOLET)
                if cell.ghost is True:
                    arcade.draw_circle_filled(cx, cy, s_radius, arcade.color.CARMINE_RED)

    def on_key_press(self, key: int, modifiers):
        """Toggle fullscreen with F, go back to menu with Escape."""
        from .menu_view import MenuView
        if key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView(Config(
                width=self.cols,
                height=self.rows,
                seed=42,
            )))
        # controls of the player
        elif key == arcade.key.UP:
            self.player.move_player(0, -1)
        elif key == arcade.key.DOWN:
            self.player.move_player(0, 1)
        elif key == arcade.key.LEFT:
            self.player.move_player(-1, 0)
        elif key == arcade.key.RIGHT:
            self.player.move_player(1, 0)

