from mazegenerator import MazeGenerator
from .game_view import GameView
import arcade


class MenuView(arcade.View):
    """Menu of the game, press SPACE to start to play."""

    def __init__(self, config):
        super().__init__()
        self.config = config

    def on_show_view(self):
        "Setup the window with a black background."
        self.window.background_color = arcade.color.BLACK

    def on_draw(self):
        "Write the menu."
        self.clear()
        cx = self.window.width / 2
        cy = self.window.height / 2

        arcade.draw_text("PAC-MAN", cx, cy + 60,
                         arcade.color.YELLOW, 64, anchor_x="center", bold=True)
        arcade.draw_text("Push SPACE to play",
                         cx, cy - 20,
                         arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        """Start to play with SPACE, leave fullscreen with F,
            and close the window with ESCAPE."""
        if key == arcade.key.SPACE:
            generator = MazeGenerator(
                size=(self.config.width, self.config.height),
                perfect=False,
                seed=self.config.seed,
            )
            game = GameView(self.config,
                            level_index=0,
                            score=0)
            game.setup(generator)
            self.window.show_view(game)
        elif key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ESCAPE:
            self.window.close()
