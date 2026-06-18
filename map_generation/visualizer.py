from mazegenerator import MazeGenerator
from parsing import Config
import arcade


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Pac-Man"

WALL_COLOR = arcade.color.DARK_BLUE
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
    """
    Main application class
    """

    def __init__(self, maze_cols, maze_rows):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
                         WINDOW_TITLE, fullscreen=True)
        self.maze_cols = maze_cols
        self.maze_rows = maze_rows
        self.background_color = arcade.csscolor.BLACK

    def setup(self, generator):
        """Set up the game here. Call this function to restart the game"""
        generator.generate()
        self.maze = generator.maze

    def on_draw(self):
        self.clear()

        cell_size = min(
            (self.width - 2 * MARGIN) // self.maze_cols,
            (self.height - 2 * MARGIN) // self.maze_rows,
        )

        maze_w = self.maze_cols * cell_size
        maze_h = self.maze_rows * cell_size
        offset_x = (self.width - maze_w) / 2
        offset_y = (self.height - maze_h) / 2
        maze_top = offset_y + maze_h

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

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F:
            self.set_fullscreen(not self.fullscreen)
        elif key == arcade.key.ESCAPE:
            self.close()


def setup_vizualisation(config: Config):
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
