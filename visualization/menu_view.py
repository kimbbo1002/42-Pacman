from mazegenerator import MazeGenerator
from .game_view import GameView
from parsing import Config
import arcade
from objects import Score


class MenuView(arcade.View):
    """Menu of the game, press SPACE to start to play."""

    def __init__(self, config: Config):
        """Store the game config used to start a new game."""
        super().__init__()
        self.config = config

    def on_show_view(self):
        "Setup the window with a black background."
        self.window.background_color = arcade.color.BLACK

    def on_draw(self):
        "Write the menu."
        self.clear()
        cx = self.window.width / 2
        cx_scores = cx - 500
        cx_rules = cx + 500
        cy = self.window.height / 2

        arcade.draw_text("PAC-MAN", cx, cy + 60,
                         arcade.color.YELLOW, 64, anchor_x="center", bold=True)
        arcade.draw_text("Push SPACE to play",
                         cx, cy - 20,
                         arcade.color.WHITE, 20, anchor_x="center")

        # Highscores display
        arcade.draw_text("HIGHSCORES :",
                         cx_scores, cy - 200,
                         arcade.color.BLUE_GRAY, 20, anchor_x="center",
                         bold=True)

        highscores = Score.load_scores(self.config.highscore_filename)

        cy_score = cy - 250
        if highscores == []:
            arcade.draw_text("No scores saved",
                             cx_scores, cy_score,
                             arcade.color.WHITE, 20, anchor_x="center")
        else:
            for i, entry in enumerate(highscores):

                arcade.draw_text(f"{i+1}. {entry['player_name']} :"
                                 f" {entry['score']} pts",
                                 cx_scores, cy_score,
                                 arcade.color.WHITE, 20, anchor_x="center")
                cy_score -= 40

        # Commands display
        arcade.draw_text("COMMANDS AND RULES :",
                         cx_rules, cy - 200,
                         arcade.color.BLUE_GRAY, 20, anchor_x="center",
                         bold=True, width=800)
        arcade.draw_text("** You will spawn in the middle of a maze **\n"
                         "-> Use the arrows to move through the corridors\n"
                         "-> Hold an arrow key to move continuously "
                         "in that direction\n"
                         "-> Eat all the Pacgums to win the level\n"
                         "-> If a ghost catches you, you lose a life\n"
                         "-> Game Over when you run out of lives or time",
                         cx_rules + 170, cy - 250,
                         arcade.color.WHITE, 20, anchor_x="center",
                         multiline=True,
                         width=1000)

    def on_key_press(self, key, modifiers):
        """Start to play with SPACE, leave fullscreen with F,
            and close the window with ESCAPE."""
        if key == arcade.key.SPACE:
            try:
                generator = MazeGenerator(
                    size=(self.config.width, self.config.height),
                    perfect=False,
                    seed=self.config.seed,
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate maze "
                    f"(size={self.config.width}x{self.config.height}, "
                    f"seed={self.config.seed})"
                ) from e
            game = GameView(self.config,
                            level=1,
                            score=0,
                            lives=self.config.lives)
            game.setup(generator)
            self.window.show_view(game)
        elif key == arcade.key.ESCAPE:
            self.window.close()
