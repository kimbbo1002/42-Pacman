from parsing import Config
from mazegenerator import MazeGenerator
import arcade
from objects import Maze, move_ghosts
import time


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8

WALL_WIDTH = 3
MARGIN = 50

RESPAWN_PLAYER_DELAY = 0.0
RESPAWN_PLAYER_DURATION = 3.0
SUPER_MODE_DELAY = 8.0


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
        self.time_passed = 0
        self.ghost_speed = 0.5

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
                                     self.maze.assets.wall, WALL_WIDTH)
                if cell.cell_wall & WALL_BOTTOM:
                    arcade.draw_line(left, bottom, right, bottom,
                                     self.maze.assets.wall, WALL_WIDTH)
                if cell.cell_wall & WALL_LEFT:
                    arcade.draw_line(left, bottom, left, top,
                                     self.maze.assets.wall, WALL_WIDTH)
                if cell.cell_wall & WALL_RIGHT:
                    arcade.draw_line(right, bottom, right, top,
                                     self.maze.assets.wall, WALL_WIDTH)

                # display pacgums & super_pacgums
                cell.sprite_pacgum.center_x = cx
                cell.sprite_pacgum.center_y = cy
                cell.sprite_super_pacgum.center_x = cx
                cell.sprite_super_pacgum.center_y = cy
                if cell.super_pacgum is True:
                    cell.sprite_super_pacgum.visible = True
                else:
                    cell.sprite_super_pacgum.visible = False
                if cell.pacgum is True:
                    cell.sprite_pacgum.visible = True
                else:
                    cell.sprite_pacgum.visible = False
        self.maze.sprites.draw()
        self.maze.character_sprites.draw()

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
        
        elif key == arcade.key.C:
            if self.player.cheat_mode is False:
                self.player.cheat_mode = True
            else:
                self.player.cheat_mode = False
        elif key == arcade.key.G and self.player.cheat_mode is True:
            if self.maze.ghost_freeze is True:
                self.maze.ghost_freeze = False
            else:
                self.maze.ghost_freeze = True

    def on_update(self, delta_time: float):
        """Run one game step: end super_mode when it times out, respawn the
            player after its delay, set the background, and move the ghosts
            at their own speed."""
        now = time.time()

        if now - self.player.super_mode_start > SUPER_MODE_DELAY:
            self.player.super_mode = False

        if (self.player.dead and now - self.player.dead_since
                > RESPAWN_PLAYER_DELAY):
            self.player.respawn()

        if self.player.super_mode:
            arcade.set_background_color(self.maze.assets.super_background)
        else:
            arcade.set_background_color(self.maze.assets.background)

        if self.time_passed < self.ghost_speed:
            self.time_passed += delta_time
        else:
            move_ghosts(self.player, self.maze.ghosts)
            self.time_passed = 0

        if now - self.player.respawning_start > RESPAWN_PLAYER_DURATION:
            self.player.respawning = False
        
        if self.maze.end_of_game is True:
            self.window.close()
        
        # update coordinates for ghosts
        cell_size, offset_x, maze_top = self._grid_geometry()
        for g in self.maze.ghosts:
            if g.dead is True:
                g.sprite.visible = False
                continue
            else:
                g.sprite.visible = True
            cx, cy = self.cell_center(
                g.y, g.x,
                cell_size,
                offset_x,
                maze_top,
            )
            g.sprite.center_x = cx
            g.sprite.center_y = cy

        
        # update coordinates for player
        cx, cy = self.cell_center(
            self.player.y, self.player.x,
            cell_size, offset_x, maze_top
        )
        if self.player.super_mode:
            active_sprite = self.player.sprite_super
        elif self.player.cheat_mode:
            active_sprite = self.player.sprite_cheat
        else:
            active_sprite = self.player.sprite_normal

        # Hide every sprite
        self.player.sprite_normal.visible = False
        self.player.sprite_super.visible = False
        self.player.sprite_cheat.visible = False

        # Show the selected one
        active_sprite.center_x = cx
        active_sprite.center_y = cy
        active_sprite.visible = True