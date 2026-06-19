from mazegenerator import MazeGenerator
from parsing import Config
import arcade


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Pac-Man"

WALL_COLOR = arcade.color.BLUE
WALL_WIDTH = 3

ROWS = 30
COLS = 30
CELL_SIZE = 40
MARGIN = 50

WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8


class GameView(arcade.Window):
    """Window that draws the maze."""

    def __init__(self, maze_cols, maze_rows):
        """Create the window and store the maze size."""
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
                         WINDOW_TITLE, fullscreen=True)
        self.maze_cols = maze_cols
        self.maze_rows = maze_rows
        self.background_color = arcade.csscolor.BLACK
        self.pacgums = set()
        self.super_pacgums = set()

    def setup(self, generator: MazeGenerator):
        """Build the maze and place a dot in every cell."""
        self.maze = generator.maze

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
        }

    def _grid_geometry(self):
        """Return the cell size and where to start drawing the maze."""
        cell_size = min(
            (self.width - 2 * MARGIN) // self.maze_cols,
            (self.height - 2 * MARGIN) // self.maze_rows,
        )
        maze_w = self.maze_cols * cell_size
        maze_h = self.maze_rows * cell_size
        offset_x = (self.width - maze_w) / 2
        offset_y = (self.height - maze_h) / 2
        maze_top = offset_y + maze_h
        return cell_size, offset_x, maze_top

    def cell_center(self, row, col, cell_size, offset_x, maze_top):
        """Return the screen point at the middle of a cell."""
        cx = offset_x + col * cell_size + cell_size / 2
        cy = maze_top - row * cell_size - cell_size / 2
        return cx, cy

    def on_draw(self):
        """Draw the walls and the dots on the screen."""
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

        PACGUM_COLOR = arcade.color.YELLOW
        radius = max(2, cell_size // 10)
        for (row, col) in self.pacgums:
            cx, cy = self.cell_center(row, col, cell_size, offset_x, maze_top)
            arcade.draw_circle_filled(cx, cy, radius, PACGUM_COLOR)

        SUPER_PACGUM_COLOR = arcade.color.WHITE
        power_radius = max(5, cell_size // 4)
        for (row, col) in self.super_pacgums:
            cx, cy = self.cell_center(row, col, cell_size, offset_x, maze_top)
            arcade.draw_circle_filled(cx, cy, power_radius, SUPER_PACGUM_COLOR)

    def on_key_press(self, key, modifiers):
        """Toggle fullscreen with F and quit with Escape."""
        if key == arcade.key.F:
            self.set_fullscreen(not self.fullscreen)
        elif key == arcade.key.ESCAPE:
            self.close()


def setup_vizualisation(config: Config):
    """Build a maze from the config and open the game window."""
    generator = MazeGenerator(
        size=(config.width, config.height),
        perfect=False,
        seed=config.seed
        )
    window = GameView(config.width, config.height)
    window.setup(generator)
    arcade.run()


if __name__ == "__main__":
    config = Config(
                    width=15,
                    height=15,
                    seed=42,
                    )
    setup_vizualisation(config)
