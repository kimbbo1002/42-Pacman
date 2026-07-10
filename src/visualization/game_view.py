from mazegenerator import MazeGenerator
from src.parsing import Config
from src.objects import Maze, Ghost
import arcade
import time


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8

WALL_WIDTH = 3

PLAYER_CELL_FRACTION = 0.8
GHOST_CELL_FRACTION = 0.8
PACGUM_CELL_FRACTION = 0.6
SUPER_PACGUM_CELL_FRACTION = 1.0

RESPAWN_PLAYER_DELAY = 3.0
RESPAWN_PLAYER_DURATION = 3.0
SUPER_MODE_DELAY = 8.0


class GameView(arcade.View):
    """View that draws the maze."""

    def __init__(self, config: Config, level: int, score: int, lives: int,
                 cheat_mode: bool = False):
        """Store the maze size and the positions of the pacgums."""
        from src.ui import GameHUD, Geometry, Inputs
        super().__init__()
        self.config = config
        self.cols = config.width
        self.rows = config.height
        self.level = level
        self.score = score
        self.cheat_mode = cheat_mode
        self.time_passed = 0.0
        self.ghost_speed = Ghost.scale_speed(self.level, self.config.level)
        self.lives = lives
        self.remaining_time = config.level_max_time
        self.remaining_time_stock = 0.0
        self.time_before_respawn = 0.0
        self.pause = False
        self.pause_start = 0.0
        self.time_out = False
        arcade.resources.load_kenney_fonts()
        self.hud = GameHUD(self)
        self.geometry = Geometry(self)
        self.inputs = Inputs(self)

    def setup(self, generator: MazeGenerator) -> None:
        """Build the maze and place a pacgum in every cell."""
        maze = generator.maze
        self.maze = Maze(maze, self.config, self.score, self.lives)
        self.maze.place_objects()
        self.player = self.maze.player
        self.player.cheat_mode = self.cheat_mode

    def on_draw(self) -> None:
        """Draw the walls and the pacgums on the screen."""
        self.clear()

        cell_size, offset_x, maze_top = self.geometry.grid_geometry()

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.maze.maze[r][c]

                left = offset_x + c * cell_size
                right = left + cell_size
                top = maze_top - r * cell_size
                bottom = top - cell_size

                cx, cy = self.geometry.cell_center(r, c, cell_size, offset_x,
                                                   maze_top)

                # fully-walled "42" cells are filled with the wall color
                if cell.pattern_42:
                    arcade.draw_lrbt_rectangle_filled(
                        left, right, bottom, top, self.maze.assets.wall)

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

                # display pacgums & super_pacgums (sized to the cell)
                self.geometry.fit_to_cell(cell.sprite_pacgum, cell_size,
                                          PACGUM_CELL_FRACTION)
                self.geometry.fit_to_cell(cell.sprite_super_pacgum,
                                          cell_size,
                                          SUPER_PACGUM_CELL_FRACTION)
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
        self.hud.draw()

    def resume(self) -> None:
        """Resume the game after a pause.

        Shift every wall-clock timer by the paused duration so nothing
        (respawn, super mode, invincibility) expires while the game was
        frozen behind the pause menu."""
        paused_duration = time.time() - self.pause_start
        self.player.dead_since += paused_duration
        self.player.super_mode_start += paused_duration
        self.player.respawning_start += paused_duration
        self.pause = False
        self.window.show_view(self)

    def on_update(self, delta_time: float) -> None:
        """Run one game step: end super_mode when it times out, respawn the
            player after its delay, set the background, and move the ghosts
            at their own speed."""
        from src.objects import move_ghosts
        if not self.pause:
            now = time.time()

            if self.player.move_time > 0.06:
                if self.player.move_up:
                    self.player.move_player(0, -1)
                elif self.player.move_down:
                    self.player.move_player(0, 1)
                elif self.player.move_left:
                    self.player.move_player(-1, 0)
                elif self.player.move_right:
                    self.player.move_player(1, 0)
                self.player.move_time = 0.0
            else:
                self.player.move_time += delta_time

            if self.player.dead:
                self.time_before_respawn = (RESPAWN_PLAYER_DELAY -
                                            (now - self.player.dead_since)) + 1
            if not self.player.cheat_mode:
                self.remaining_time_stock += delta_time
                if self.remaining_time_stock >= 1:
                    self.remaining_time -= 1
                    self.remaining_time_stock -= 1.0

            if self.remaining_time < 0:
                self.time_out = True

            if now - self.player.super_mode_start > SUPER_MODE_DELAY:
                self.player.super_mode = False

            # out of lives: end the game now, do not respawn
            if self.player.is_dead() or self.time_out:
                from src.visualization import LoseView
                self.window.show_view(LoseView(self.config,
                                               self.player.score,
                                               self.time_out))
                return

            if (self.player.dead and now - self.player.dead_since
                    > RESPAWN_PLAYER_DELAY):
                self.player.respawn()

            if self.player.super_mode:
                arcade.set_background_color(
                    (*self.maze.assets.super_background, 255))
            else:
                arcade.set_background_color(
                    (*self.maze.assets.background, 255))

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
            cell_size, offset_x, maze_top = self.geometry.grid_geometry()
            for g in self.maze.ghosts:
                if g.dead is True:
                    g.sprite.visible = False
                    continue
                else:
                    g.sprite.visible = True
                cx, cy = self.geometry.cell_center(
                    g.y, g.x,
                    cell_size,
                    offset_x,
                    maze_top,
                )
                self.geometry.fit_to_cell(g.sprite, cell_size,
                                          GHOST_CELL_FRACTION)
                g.sprite.center_x = cx
                g.sprite.center_y = cy

            # update coordinates for player
            cx, cy = self.geometry.cell_center(
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

            # While dead (waiting to respawn), keep the player hidden
            if self.player.dead:
                return

            # Show the selected one (sized to the cell)
            self.geometry.fit_to_cell(active_sprite, cell_size,
                                      PLAYER_CELL_FRACTION)
            active_sprite.center_x = cx
            active_sprite.center_y = cy

            # While respawning (invincible)
            if self.player.respawning:
                active_sprite.visible = int(now / 0.2) % 2 == 0
            else:
                active_sprite.visible = True

            if self.maze.is_level_win():
                if self.level == self.config.level:
                    from src.visualization import WinView
                    win = WinView(self.config, self.player.score)
                    self.window.show_view(win)
                else:
                    from src.visualization import TransitionView
                    transition = TransitionView(self.config,
                                                self.player.score,
                                                self.player.lives,
                                                self.level + 1,
                                                self.player.cheat_mode)
                    self.window.show_view(transition)

    def on_key_press(self, key: int, modifiers: int) -> None:
        self.inputs.on_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int) -> None:
        self.inputs.on_key_release(key, modifiers)
