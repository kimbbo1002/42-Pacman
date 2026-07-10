import arcade
from typing import TYPE_CHECKING
from src.visualization import ui_scale

if TYPE_CHECKING:
    from src.visualization import GameView


class GameHUD:
    """ Class that get the view informations and display the commands
        and game informations on the sides of the window."""
    def __init__(self, view: "GameView") -> None:
        """ Store the view in an attribut."""
        self.view = view

    def draw(self) -> None:
        """ Draw the two panel of informations on the two sides
            of the window."""
        scale = ui_scale(self.view.window)
        self._draw_left_panel(scale)
        self._draw_right_panel(scale)

    def draw_lives(self, info_x: float, info_y: float) -> None:
        """ Draw the lives depending on the theme and the
            number of lives."""
        scale_ui = ui_scale(self.view.window)
        if self.view.config.theme == "pacman":
            theme_scale = 0.5
        elif self.view.config.theme == "minecraft":
            theme_scale = 0.3
        elif self.view.config.theme == "stardew_valley":
            theme_scale = 0.8
        scale = theme_scale * scale_ui
        spacing = 100 * scale_ui
        lives_list: arcade.SpriteList[arcade.BasicSprite] = \
            arcade.SpriteList()
        life_x = info_x + 50 * scale_ui
        life_y = info_y - 80 * scale_ui
        if self.view.config.lives <= 5:
            for i in range(self.view.player.lives):
                texture_path = self.view.maze.assets.texture("player",
                                                             "normal")
                texture = arcade.load_texture(texture_path)
                sprite = arcade.BasicSprite(
                    texture, center_x=life_x, center_y=life_y, scale=scale
                )
                lives_list.append(sprite)
                life_x += spacing
        else:
            for i in range(5):
                if self.view.player.lives > i:
                    texture_path = self.view.maze.assets.texture("player",
                                                                 "normal")
                    texture = arcade.load_texture(texture_path)
                    sprite = arcade.BasicSprite(
                        texture, center_x=life_x, center_y=life_y, scale=scale
                    )
                    lives_list.append(sprite)
                    life_x += spacing
            life_x = info_x + 50 * scale_ui
            for i in range(self.view.player.lives - 5):
                texture_path = self.view.maze.assets.texture("player",
                                                             "normal")
                texture = arcade.load_texture(texture_path)
                sprite = arcade.BasicSprite(
                    texture, center_x=life_x, center_y=life_y - 120 * scale_ui,
                    scale=scale
                )
                lives_list.append(sprite)
                life_x += spacing
        lives_list.draw()

    def _draw_left_panel(self, scale: float) -> None:
        """Display controls on the left side of the maze."""
        _, offset_x, maze_top = self.view.geometry.grid_geometry()
        font_size = int(20 * scale)

        info_x = offset_x - 550 * scale
        y_title = maze_top - 100 * scale

        arcade.draw_text(
            "[Commands]",
            info_x,
            y_title,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "> Normal Mode :",
            info_x,
            y_title - 100 * scale,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Move : (Key Arrows)",
            info_x,
            y_title - 150 * scale,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Pause : P",
            info_x,
            y_title - 200 * scale,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "> Cheat Mode :",
            info_x,
            y_title - 300 * scale,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Activate : C",
            info_x,
            y_title - 350 * scale,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Freeze Ghosts : G",
            info_x,
            y_title - 400 * scale,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )
        arcade.draw_text(
            "- Skip Level : N",
            info_x,
            y_title - 450 * scale,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket Square"
        )

    def _draw_right_panel(self, scale: float) -> None:
        """Draw the level, score, remaining lives, remaining time
            and remaining time before respawn when the player is dead
            on the right side of the maze."""
        cell_size, offset_x, maze_top = self.view.geometry.grid_geometry()
        font_size = int(30 * scale)

        maze_w = self.view.cols * cell_size
        maze_right_edge = offset_x + maze_w

        info_x = maze_right_edge + 50 * scale
        info_y_level = maze_top - 100 * scale
        info_y_score = info_y_level - 100 * scale
        info_y_lives = info_y_score - 100 * scale
        if self.view.config.lives <= 5:
            info_y_time = info_y_lives - 200 * scale
        else:
            info_y_time = info_y_lives - 320 * scale
        info_y_time_respawn = info_y_time - 200 * scale
        info_y_cheat_mode = info_y_time_respawn - 200 * scale

        # display level
        arcade.draw_text(
            f"Level {self.view.level} / {self.view.config.level}",
            info_x,
            info_y_level,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket"
        )

        # display score
        arcade.draw_text(
            f"Score : {self.view.player.score}",
            info_x, info_y_score,
            arcade.color.YELLOW,
            font_size,
            font_name="Kenney Rocket"
        )

        # display lives
        if self.view.player.lives > 1:
            color_lives = arcade.color.YELLOW
        else:
            color_lives = arcade.color.RED
        arcade.draw_text(
            "Lives : ",
            info_x, info_y_lives,
            color_lives,
            font_size,
            font_name="Kenney Rocket"
        )
        self.draw_lives(info_x, info_y_lives)

        # display time
        if self.view.remaining_time > 5:
            color_time = arcade.color.YELLOW
        else:
            color_time = arcade.color.RED
        arcade.draw_text(
            f"Time : {max(0, self.view.remaining_time)}",
            info_x,
            info_y_time,
            color_time,
            font_size,
            font_name="Kenney Rocket"
        )

        # remaining time before respawn
        if self.view.player.dead:
            arcade.draw_text(
                f"Respawn in : {int(self.view.time_before_respawn)}",
                info_x,
                info_y_time_respawn,
                arcade.color.YELLOW,
                font_size,
                font_name="Kenney Rocket"
            )
        # cheatmode
        if self.view.player.cheat_mode:
            arcade.draw_text(
                "CHEAT MODE",
                info_x,
                info_y_cheat_mode,
                arcade.color.YELLOW,
                font_size,
                font_name="Kenney Rocket"
            )
