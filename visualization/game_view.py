from parsing import Config
from mazegenerator import MazeGenerator
import arcade
from objects import Maze
import time


WALL_TOP = 1      # bit 1
WALL_RIGHT = 2    # bit 2
WALL_BOTTOM = 4   # bit 4
WALL_LEFT = 8     # bit 8

WALL_WIDTH = 3
MARGIN = 50

PLAYER_CELL_FRACTION = 0.8
GHOST_CELL_FRACTION = 0.8
PACGUM_CELL_FRACTION = 0.22
SUPER_PACGUM_CELL_FRACTION = 0.5

RESPAWN_PLAYER_DELAY = 3.0
RESPAWN_PLAYER_DURATION = 3.0
SUPER_MODE_DELAY = 8.0


class GameView(arcade.View):
    """View that draws the maze."""

    def __init__(self, config: Config, level: int, score: int, lives: int,
                 cheat_mode: bool = False):
        """Store the maze size and the positions of the pacgums."""
        super().__init__()
        self.config = config
        self.cols = config.width
        self.rows = config.height
        self.level = level
        self.score = score
        self.cheat_mode = cheat_mode
        self.time_passed = 0
        self.ghost_speed = 0.5
        self.lives = lives
        self.remaining_time = config.level_max_time
        self.remaining_time_stock = 0.0
        self.time_before_respawn = 0
        self.pause = False
        self.pause_start = 0.0
        arcade.resources.load_kenney_fonts()

    def setup(self, generator: MazeGenerator):
        """Build the maze and place a pacgum in every cell."""
        maze = generator.maze
        self.maze = Maze(maze, self.config, self.score, self.lives)
        self.maze.place_objects()
        self.player = self.maze.player
        self.player.cheat_mode = self.cheat_mode

    def grid_geometry(self):
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

    @staticmethod
    def fit_to_cell(sprite: arcade.BasicSprite, cell_size: int,
                    fraction: float) -> None:
        """Scale a sprite so its largest side spans `fraction` of a cell,
        keeping the texture aspect ratio (independent of its native size)."""
        native = max(sprite.texture.width, sprite.texture.height)
        sprite.scale = (cell_size * fraction) / native

    def draw_lives(self, info_x: int, info_y: int) -> None:
        if self.config.theme == "pacman":
            scale = 0.5
        elif self.config.theme == "minecraft":
            scale = 0.3
        elif self.config.theme == "stardew_valley":
            scale = 0.8
        lives_list = arcade.SpriteList()
        life_x = info_x + 50
        life_y = info_y - 80
        if self.config.lives <= 5:
            for i in range(self.player.lives):
                texture_path = self.maze.assets.texture("player", "normal")
                texture = arcade.load_texture(texture_path)
                sprite = arcade.BasicSprite(
                    texture, center_x=life_x, center_y=life_y, scale=scale
                )
                lives_list.append(sprite)
                life_x += 100
        else:
            for i in range(5):
                if self.player.lives > i:
                    texture_path = self.maze.assets.texture("player", "normal")
                    texture = arcade.load_texture(texture_path)
                    sprite = arcade.BasicSprite(
                        texture, center_x=life_x, center_y=life_y, scale=scale
                    )
                    lives_list.append(sprite)
                    life_x += 100
            life_x = info_x + 50
            for i in range(self.player.lives - 5):
                texture_path = self.maze.assets.texture("player", "normal")
                texture = arcade.load_texture(texture_path)
                sprite = arcade.BasicSprite(
                    texture, center_x=life_x, center_y=life_y - 120,
                    scale=scale
                )
                lives_list.append(sprite)
                life_x += 100
        lives_list.draw()

    def display_info_right(self) -> None:
        """Draw the level, score, remaining lives, remaining time
            and remaining time before respawn when the player is dead
            on the right side of the maze."""
        cell_size, offset_x, maze_top = self.grid_geometry()

        maze_w = self.cols * cell_size
        maze_right_edge = offset_x + maze_w

        info_x = maze_right_edge + 50
        info_y_level = maze_top - 100
        info_y_score = info_y_level - 100
        info_y_lives = info_y_score - 100
        if self.config.lives <= 5:
            info_y_time = info_y_lives - 200
        else:
            info_y_time = info_y_lives - 320
        info_y_time_respawn = info_y_time - 200
        info_y_pause = info_y_time_respawn - 200

        # display level
        arcade.draw_text(
            f"Level {self.level}",
            info_x,
            info_y_level,
            arcade.color.YELLOW,
            30,
            font_name="Kenney Rocket"
        )

        # display score
        arcade.draw_text(
            f"Score : {self.player.score}",
            info_x, info_y_score,
            arcade.color.YELLOW,
            30,
            font_name="Kenney Rocket"
        )

        # display lives
        if self.player.lives > 1:
            color_lives = arcade.color.YELLOW
        else:
            color_lives = arcade.color.RED
        arcade.draw_text(
            "Lives : ",
            info_x, info_y_lives,
            color_lives,
            30,
            font_name="Kenney Rocket"
        )
        self.draw_lives(info_x, info_y_lives)

        # display time
        if self.remaining_time > 5:
            color_time = arcade.color.YELLOW
        else:
            color_time = arcade.color.RED
        arcade.draw_text(
            f"Time : {max(0, self.remaining_time)}",
            info_x,
            info_y_time,
            color_time,
            30,
            font_name="Kenney Rocket"
        )

        # remaining time before respawn
        if self.player.dead:
            arcade.draw_text(
                f"Respawn in : {int(self.time_before_respawn)}",
                info_x,
                info_y_time_respawn,
                arcade.color.YELLOW,
                30,
                font_name="Kenney Rocket"
            )
        # pause game
        if self.pause:
            arcade.draw_text(
                "PAUSE",
                info_x,
                info_y_pause,
                arcade.color.YELLOW,
                50,
                font_name="Kenney Rocket"
            )
            arcade.draw_text(
                "Press P to resume",
                info_x,
                info_y_pause - 100,
                arcade.color.YELLOW,
                25,
                font_name="Kenney Rocket"
            )

    def display_info_left(self) -> None:
        """Display controls on the left side of the maze."""
        cell_size, offset_x, maze_top = self.grid_geometry()

        info_x = offset_x - 550
        y_title = maze_top - 100

        arcade.draw_text(
            "[Commands]",
            info_x,
            y_title,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "> Normal Mode :",
            info_x,
            y_title - 100,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Move : (Key Arrows)",
            info_x,
            y_title - 150,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Pause : P",
            info_x,
            y_title - 200,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "> Cheat Mode :",
            info_x,
            y_title - 300,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Activate : C",
            info_x,
            y_title - 350,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Freeze Ghosts : G",
            info_x,
            y_title - 400,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Skip Level : N",
            info_x,
            y_title - 450,
            arcade.color.YELLOW,
            20,
            font_name="Kenney Rocket Square"
        )

    def on_draw(self):
        """Draw the walls and the pacgums on the screen."""
        self.clear()

        cell_size, offset_x, maze_top = self.grid_geometry()

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.maze.maze[r][c]

                left = offset_x + c * cell_size
                right = left + cell_size
                top = maze_top - r * cell_size
                bottom = top - cell_size

                cx, cy = self.cell_center(r, c, cell_size, offset_x, maze_top)

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
                self.fit_to_cell(cell.sprite_pacgum, cell_size,
                                 PACGUM_CELL_FRACTION)
                self.fit_to_cell(cell.sprite_super_pacgum, cell_size,
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
        self.display_info_right()
        self.display_info_left()

    def on_key_press(self, key: int, modifiers):
        """Toggle fullscreen with F, go back to menu with Escape."""
        from .menu_view import MenuView
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView(Config(
                width=self.cols,
                height=self.rows,
                seed=42,
            )))

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

        # pass the level (Only in cheat mode)
        elif key == arcade.key.N and self.player.cheat_mode:
            if self.level == self.config.level:
                from visualization import WinView
                win = WinView(self.config, self.player.score)
                self.window.show_view(win)
            else:
                from visualization import TransitionView
                transition = TransitionView(self.config,
                                            self.player.score,
                                            self.player.lives,
                                            self.level + 1,
                                            self.player.cheat_mode)
                self.window.show_view(transition)

        # pause the game
        elif key == arcade.key.P:
            if self.pause:
                paused_duration = time.time() - self.pause_start
                self.player.dead_since += paused_duration
                self.player.super_mode_start += paused_duration
                self.player.respawning_start += paused_duration
                self.pause = False
            else:
                self.pause_start = time.time()
                self.pause = True

        # controls of the player
        if not self.pause:
            if key == arcade.key.UP:
                self.player.move_up = True
            elif key == arcade.key.DOWN:
                self.player.move_down = True
            elif key == arcade.key.LEFT:
                self.player.move_left = True
            elif key == arcade.key.RIGHT:
                self.player.move_right = True

    def on_key_release(self, key: int, modifiers):
        if not self.pause:
            if key == arcade.key.UP:
                self.player.move_up = False
            elif key == arcade.key.DOWN:
                self.player.move_down = False
            elif key == arcade.key.LEFT:
                self.player.move_left = False
            elif key == arcade.key.RIGHT:
                self.player.move_right = False

    def on_update(self, delta_time: float):
        """Run one game step: end super_mode when it times out, respawn the
            player after its delay, set the background, and move the ghosts
            at their own speed."""
        from objects import move_ghosts
        if not self.pause:
            now = time.time()

            if self.player.move_time > 0.08:
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
                self.player.lives = -1

            if now - self.player.super_mode_start > SUPER_MODE_DELAY:
                self.player.super_mode = False

            # out of lives: end the game now, do not respawn
            if self.player.is_dead():
                from visualization import LoseView
                self.window.show_view(LoseView(self.config, self.player.score))
                return

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
            cell_size, offset_x, maze_top = self.grid_geometry()
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
                self.fit_to_cell(g.sprite, cell_size, GHOST_CELL_FRACTION)
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

            # While dead (waiting to respawn), keep the player hidden
            if self.player.dead:
                return

            # Show the selected one (sized to the cell)
            self.fit_to_cell(active_sprite, cell_size, PLAYER_CELL_FRACTION)
            active_sprite.center_x = cx
            active_sprite.center_y = cy

            # While respawning (invincible)
            if self.player.respawning:
                active_sprite.visible = int(now / 0.2) % 2 == 0
            else:
                active_sprite.visible = True

            if self.maze.is_level_win():
                if self.level == self.config.level:
                    from visualization import WinView
                    win = WinView(self.config, self.player.score)
                    self.window.show_view(win)
                else:
                    from visualization import TransitionView
                    transition = TransitionView(self.config,
                                                self.player.score,
                                                self.player.lives,
                                                self.level + 1,
                                                self.player.cheat_mode)
                    self.window.show_view(transition)
