from parsing import Config
from mazegenerator import MazeGenerator
import arcade


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
        self.points_per_pacgum = config.points_per_pacgum
        self.points_per_super_pacgum = config.points_per_super_pacgum
        self.points_per_ghost = config.points_per_ghost
        self.cols = config.width
        self.rows = config.height
        self.pacgums = set()
        self.super_pacgums = set()
        self.level_index = level_index
        self.pattern_42 = []
        self.pacman_pos = [self.cols // 2, self.rows // 2]
        self.score = score

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
            (0, self.cols - 1),
            (self.rows - 1, 0),
            (self.rows - 1, self.cols - 1),
        }
        self.pacgums = {
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if (row, col) not in self.super_pacgums
            and (row, col) not in self.pattern_42
            and (row, col) != self.pacman_pos
        }

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
                    offset_x: int, maze_top: int):
        """Return the screen point at the middle of a cell."""
        cx = offset_x + col * cell_size + cell_size / 2
        cy = maze_top - row * cell_size - cell_size / 2
        return cx, cy

    def on_draw(self):
        """Draw the walls and the pacgums on the screen."""
        # mettre a jour l'affichage des pacgums
        self.clear()

        cell_size, offset_x, maze_top = self._grid_geometry()

        for row in range(self.rows):
            for col in range(self.cols):
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

        # player
        cx, cy = self.cell_center(self.pacman_pos[0], self.pacman_pos[1],
                                  cell_size, offset_x, maze_top)
        arcade.draw_circle_filled(cx, cy, power_radius, arcade.color.VIOLET)

    def on_key_press(self, key: arcade.key, modifiers):
        """Toggle fullscreen with F, go back to menu with Escape."""
        from .menu_view import MenuView
        x_pacman, y_pacman = self.pacman_pos[0], self.pacman_pos[1]
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
            if not (self.maze[x_pacman][y_pacman] & WALL_TOP):
                self.pacman_pos[0] -= 1
        elif key == arcade.key.DOWN:
            if not (self.maze[x_pacman][y_pacman] & WALL_BOTTOM):
                self.pacman_pos[0] += 1
        elif key == arcade.key.LEFT:
            if not (self.maze[x_pacman][y_pacman] & WALL_LEFT):
                self.pacman_pos[1] -= 1
        elif key == arcade.key.RIGHT:
            if not (self.maze[x_pacman][y_pacman] & WALL_RIGHT):
                self.pacman_pos[1] += 1

        # After each movement, the score is recalculate
        self.actualize_score()

    def actualize_score(self):
        """ Check if the player is on a cell with a pacgum or a super_pacgum,
            remove it and increase the score."""
        pos = tuple(self.pacman_pos)
        if pos in self.pacgums:
            self.score += self.points_per_pacgum
            self.pacgums.remove(pos)

        elif pos in self.super_pacgums:
            self.score += self.points_per_super_pacgum
            self.super_pacgums.remove(pos)
            # AJOUTER LE FAIT DE POUVOIR MANGER LES GHOSTS
