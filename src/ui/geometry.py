import arcade
from typing import TYPE_CHECKING
from src.visualization import ui_scale

if TYPE_CHECKING:
    from src.visualization import GameView


LEFT_PANEL_WIDTH = 600
RIGHT_PANEL_WIDTH = 650
MARGIN = 50


class Geometry:
    def __init__(self, view: "GameView") -> None:
        self.view = view

    def grid_geometry(self) -> tuple[int, float, float]:
        """Return the cell size and where to start drawing the maze."""
        w = self.view.window.width
        h = self.view.window.height
        scale = ui_scale(self.view.window)

        # reserve space for the side panels, fit the maze in what remains
        left_reserved = LEFT_PANEL_WIDTH * scale
        right_reserved = RIGHT_PANEL_WIDTH * scale
        avail_w = w - left_reserved - right_reserved
        avail_h = h - 2 * MARGIN

        cell_size = max(1, int(min(
            avail_w // self.view.cols,
            avail_h // self.view.rows,
        )))
        maze_w = self.view.cols * cell_size
        maze_h = self.view.rows * cell_size
        # center the maze within the central band, between the two panels
        offset_x = left_reserved + (avail_w - maze_w) / 2
        offset_y = (h - maze_h) / 2
        maze_top = offset_y + maze_h
        return cell_size, offset_x, maze_top

    def cell_center(self, row: int, col: int, cell_size: int,
                    offset_x: float, maze_top: float) -> tuple[float, float]:
        """Return the screen point at the middle of a cell."""
        cx = offset_x + col * cell_size + cell_size / 2
        cy = maze_top - row * cell_size - cell_size / 2
        return cx, cy

    @staticmethod
    def fit_to_cell(sprite: arcade.BasicSprite, cell_size: int,
                    fraction: float) -> None:
        """Scale a sprite so its largest side spans `fraction` of a cell,
        keeping the texture aspect ratio (independent of its native size)."""
        native = max(sprite.texture.width, sprite.texture.height)
        sprite.scale = (cell_size * fraction) / native
