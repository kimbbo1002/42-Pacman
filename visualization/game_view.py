from parsing import Config
from mazegenerator import MazeGenerator
import arcade


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8   si bin = 15 : 42

WALL_COLOR = arcade.color.BLUE
PACGUM_COLOR = arcade.color.YELLOW
SUPER_PACGUM_COLOR = arcade.color.WHITE

WALL_WIDTH = 3
MARGIN = 50


class GameView(arcade.View):
    """View that draws the maze."""

    def __init__(self, maze_cols: int, maze_rows: int, level_index: int):
        """Store the maze size and the positions of the pacgums."""
        super().__init__()
        self.maze_cols = maze_cols
        self.maze_rows = maze_rows
        self.pacgums = set()
        self.super_pacgums = set()
        self.level_index = level_index
        self.pattern_42 = []

    def on_show_view(self):
        self.window.background_color = arcade.csscolor.BLACK

    def setup(self, generator: MazeGenerator):
        """Build the maze and place a pacgum in every cell."""
        self.maze = generator.maze
        # check for the 42 cells patern
        for x, line in enumerate(self.maze):
            for y, col in enumerate(line):
                if col == 15:
                    self.pattern_42.append((x, y))

        self.super_pacgums = {
            (0, 0),
            (0, self.maze_cols - 1),
            (self.maze_rows - 1, 0),
            (self.maze_rows - 1, self.maze_cols - 1),
        }
        self.pacgums = {
            (row, col)
            for row in range(self.maze_rows)
            for col in range(self.maze_cols)
            if (row, col) not in self.super_pacgums
            and (row, col) not in self.pattern_42
        }

    def _grid_geometry(self):
        """Return the cell size and where to start drawing the maze."""
        w = self.window.width
        h = self.window.height
        cell_size = min(
            (w - 2 * MARGIN) // self.maze_cols,
            (h - 2 * MARGIN) // self.maze_rows,
        )
        maze_w = self.maze_cols * cell_size
        maze_h = self.maze_rows * cell_size
        offset_x = (w - maze_w) / 2
        offset_y = (h - maze_h) / 2
        maze_top = offset_y + maze_h
        return cell_size, offset_x, maze_top

    def cell_center(self, row: int, col: int, cell_size: int,
                    offset_x: int, maze_top: int):
        """Return the screen point at the middle of a cell."""
        cx = offset_x + col * cell_size + cell_size / 2
        cy = maze_top - row * cell_size - cell_size / 2
        return cx, cy

    def on_draw(self):
        """Draw the walls and the pacgums on the screen."""
        self.clear()

        cell_size, offset_x, maze_top = self._grid_geometry()

        for row in range(self.maze_rows):
            for col in range(self.maze_cols):
                cell = self.maze[row][col]
                left = offset_x + col * cell_size
                right = left + cell_size
                top = maze_top - row * cell_size
                bottom = top - cell_size

                if cell & WALL_TOP:
                    arcade.draw_line(left, top, right, top,
                                     WALL_COLOR, WALL_WIDTH)
                if cell & WALL_BOTTOM:
                    arcade.draw_line(left, bottom, right, bottom,
                                     WALL_COLOR, WALL_WIDTH)
                if cell & WALL_LEFT:
                    arcade.draw_line(left, bottom, left, top,
                                     WALL_COLOR, WALL_WIDTH)
                if cell & WALL_RIGHT:
                    arcade.draw_line(right, bottom, right, top,
                                     WALL_COLOR, WALL_WIDTH)

        radius = max(2, cell_size // 10)
        for (row, col) in self.pacgums:
            cx, cy = self.cell_center(row, col, cell_size, offset_x, maze_top)
            arcade.draw_circle_filled(cx, cy, radius, PACGUM_COLOR)

        power_radius = max(5, cell_size // 4)
        for (row, col) in self.super_pacgums:
            cx, cy = self.cell_center(row, col, cell_size, offset_x, maze_top)
            arcade.draw_circle_filled(cx, cy, power_radius, SUPER_PACGUM_COLOR)

    def on_key_press(self, key: arcade.key, modifiers):
        """Toggle fullscreen with F, go back to menu with Escape."""
        from .menu_view import MenuView
        if key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView(Config(
                width=self.maze_cols,
                height=self.maze_rows,
                seed=42,
            )))
