import arcade
from .game_view import GameView
from src.parsing import Config
from mazegenerator import MazeGenerator
import random
from .scaler import ui_scale


class TransitionView(arcade.View):
    """Screen of transition between two levels."""

    def __init__(
            self, config: Config, score: int,
            lives: int, next_level: int,
            cheat_mode: bool = False
    ) -> None:
        """Store the score, remaining lives and the level to play next."""
        super().__init__()
        self.config = config
        self.score = score
        self.remaining_lives = lives
        self.next_level = next_level
        self.cheat_mode = cheat_mode

    def on_show_view(self) -> None:
        "Setup the window with a black background."
        self.window.background_color = arcade.color.BLACK

    def on_draw(self) -> None:
        "Write the next level, the score, and the remaining lives."
        self.clear()
        scale = ui_scale(self.window)
        cx = self.window.width / 2
        cy = self.window.height / 2

        arcade.draw_text(
            "You win!", cx, cy + 180 * scale,
            arcade.color.GREEN, int(50 * scale),
            anchor_x="center", bold=True
        )

        arcade.draw_text(
            f"LEVEL {self.next_level} / {self.config.level}",
            cx, cy + 60 * scale,
            arcade.color.YELLOW, int(64 * scale), anchor_x="center", bold=True
        )
        arcade.draw_text(
            "Push SPACE to continue",
            cx, cy - 20 * scale,
            arcade.color.WHITE, int(20 * scale), anchor_x="center"
        )
        arcade.draw_text(
            f"Your score : {self.score}", cx, cy - 200 * scale,
            arcade.color.BLUE_VIOLET, int(50 * scale), anchor_x="center"
        )
        arcade.draw_text(
            f"Remaining lives : {self.remaining_lives}",
            cx, cy - 300 * scale,
            arcade.color.BLUE_VIOLET, int(50 * scale), anchor_x="center"
        )

    def on_key_press(self, key: int, _: int) -> None:
        """Start the next level with SPACE, leave fullscreen with F,
            and close the window with ESCAPE."""
        if key == arcade.key.SPACE:
            try:
                generator = MazeGenerator(
                    size=(self.config.width, self.config.height),
                    perfect=False,
                    seed=random.random(),
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate maze "
                    f"(size={self.config.width}x{self.config.height}, "
                    f"seed={self.config.seed})"
                ) from e
            game = GameView(self.config,
                            level=self.next_level,
                            score=self.score,
                            lives=self.remaining_lives,
                            cheat_mode=self.cheat_mode)
            game.setup(generator)
            self.window.show_view(game)
        elif key == arcade.key.ESCAPE:
            self.window.close()
