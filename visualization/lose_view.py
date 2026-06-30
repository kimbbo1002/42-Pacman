import arcade
from parsing import Config


class LoseView(arcade.View):
    """Screen of transition between two levels."""

    def __init__(self, config: Config, score: int):
        super().__init__()
        self.config = config
        self.score = score

    def on_show_view(self):
        "Setup the window with a black background."
        self.window.background_color = arcade.color.BLACK

    def on_draw(self):
        "Write the menu."
        self.clear()
        cx = self.window.width / 2
        cy = self.window.height / 2

        arcade.draw_text("The ghosts have gotten "
                         "the better of you", cx, cy + 190,
                         arcade.color.RED_DEVIL, 40, anchor_x="center")
        arcade.draw_text("YOU LOST", cx, cy + 100,
                         arcade.color.RED_DEVIL, 60,
                         anchor_x="center", bold=True)
        arcade.draw_text(f"Your score : {self.score}", cx, cy - 40,
                         arcade.color.BLUE_VIOLET, 50, anchor_x="center")
        arcade.draw_text("Push SPACE to return to menu",
                         cx, cy - 500,
                         arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        """Start to play with SPACE, leave fullscreen with F,
            and close the window with ESCAPE."""
        if key == arcade.key.SPACE:
            from .menu_view import MenuView
            menu = MenuView(self.config)
            self.window.show_view(menu)

        elif key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ESCAPE:
            self.window.close()
