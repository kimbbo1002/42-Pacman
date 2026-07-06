from mazegenerator import MazeGenerator
from .game_view import GameView
from src.parsing import Config
import arcade
from src.objects import Score
from src.objects.assets import Assets
from .scaler import ui_scale

# Classic Pac-Man palette, reused for menu accents
PACMAN_YELLOW = (255, 255, 0)
BLINKY_RED = (255, 0, 0)
PINKY_PINK = (255, 184, 255)
INKY_CYAN = (0, 255, 255)
CLYDE_ORANGE = (255, 184, 82)

GHOST_DOTS = [PACMAN_YELLOW, BLINKY_RED, PINKY_PINK, INKY_CYAN, CLYDE_ORANGE]

# Medals for the top-3 scores, then white for the rest
MEDALS = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]

# Each rule line with its own color
RULES_LINES = [
    ("** You will spawn in the middle of a maze **", PACMAN_YELLOW),
    ("-> Use the arrows to move through the corridors", INKY_CYAN),
    ("-> Hold an arrow key to move continuously", PINKY_PINK),
    ("   in that direction", PINKY_PINK),
    ("-> Eat all the Pacgums to win the level", CLYDE_ORANGE),
    ("-> If a ghost catches you, you lose a life", BLINKY_RED),
    ("-> Game Over when you run out of lives or time", (144, 238, 144)),
]


class MenuView(arcade.View):
    """Menu of the game"""

    def __init__(self, config: Config) -> None:
        """Store the game config and resolve the theme palette."""
        super().__init__()
        self.config = config
        palette = Assets(config.theme).palette
        self.background = palette["background"]
        self.panel_fill = tuple(c // 5 for c in palette["wall"]) + (220,)

    def on_show_view(self) -> None:
        "Setup the window with the theme background."
        self.window.background_color = self.background

    def _draw_panel(self, left: float, right: float,
                    bottom: float, top: float, border: tuple) -> None:
        """Draw a filled panel with a colored border."""
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top, self.panel_fill)
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top, border, 2)

    def on_draw(self) -> None:
        """Write the menu title, a panel to display the highscores on the left"
            and a panel to displays the rules on the right."""
        self.clear()
        scale = ui_scale(self.window)
        cx = self.window.width / 2
        cy = self.window.height / 2
        font_size = int(20 * scale)

        # Title and call to action
        arcade.draw_text(
            "PAC-MAN", cx, cy + 260 * scale,
            arcade.color.YELLOW, int(64 * scale),
            anchor_x="center", bold=True
        )
        arcade.draw_text(
            "Push SPACE to play",
            cx, cy + 170 * scale,
            arcade.color.WHITE, font_size, anchor_x="center", bold=True
        )

        # Colorful row of Pac-Man / dots under the title
        dot_r = 12 * scale
        dot_gap = 50 * scale
        dots_y = cy + 130 * scale
        start_x = cx - dot_gap * (len(GHOST_DOTS) - 1) / 2
        for i, color in enumerate(GHOST_DOTS):
            arcade.draw_circle_filled(start_x + i * dot_gap, dots_y,
                                      dot_r, color)

        # Two symmetric panels around the center
        panel_w = 760 * scale
        gap = 60 * scale
        pad = 30 * scale
        panel_top = cy + 90 * scale
        panel_bottom = cy - 340 * scale
        header_y = panel_top - pad - font_size

        # Highscores panel (left)
        hs_left = cx - gap / 2 - panel_w
        hs_right = cx - gap / 2
        self._draw_panel(hs_left, hs_right, panel_bottom, panel_top, MEDALS[0])
        arcade.draw_text("HIGHSCORES", hs_left + pad, header_y,
                         MEDALS[0], font_size, anchor_x="left", bold=True)

        highscores = Score.load_scores(self.config.highscore_filename)
        cy_score = header_y - 50 * scale
        if highscores == []:
            arcade.draw_text("No scores saved", hs_left + pad, cy_score,
                             arcade.color.WHITE, font_size, anchor_x="left")
        else:
            for i, entry in enumerate(highscores):
                color = MEDALS[i] if i < len(MEDALS) else arcade.color.WHITE
                arcade.draw_text(
                    f"{i+1}. {entry['player_name']} : {entry['score']} pts",
                    hs_left + pad, cy_score,
                    color, font_size, anchor_x="left"
                )
                cy_score -= 40 * scale

        # Commands and rules panel (right)
        rules_left = cx + gap / 2
        rules_right = cx + gap / 2 + panel_w
        self._draw_panel(rules_left, rules_right,
                         panel_bottom, panel_top, INKY_CYAN)
        arcade.draw_text("COMMANDS AND RULES", rules_left + pad, header_y,
                         INKY_CYAN, font_size, anchor_x="left", bold=True)
        cy_rule = header_y - 50 * scale
        for line, color in RULES_LINES:
            arcade.draw_text(line, rules_left + pad, cy_rule,
                             color, font_size, anchor_x="left")
            cy_rule -= 36 * scale

        cy_exit = cy_rule - 200 * scale
        arcade.draw_text("Press ESCAPE to exit", cx, cy_exit,
                         arcade.color.WHITE, font_size, anchor_x="center")

    def on_key_press(self, key: int, _: int) -> None:
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
