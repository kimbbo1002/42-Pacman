import arcade
from src.visualization import GameView
from .scaler import ui_scale


class PauseView(arcade.View):
    """Pause menu shown over a running game.

    Press SPACE to resume the game exactly where it was left, or ESCAPE
    to go back to the main menu.
    """

    def __init__(self, game_view: GameView):
        """Store the paused game view so it can be resumed later."""
        super().__init__()
        self.game_view = game_view

    def on_show_view(self):
        "Setup the window with a black background."
        self.window.background_color = arcade.color.BLACK
        self.cx = self.window.width / 2
        self.cy = self.window.height / 2

    def on_draw(self):
        "Write the menu."
        self.clear()
        scale = ui_scale(self.window)

        arcade.draw_text("PAUSE", self.cx, self.cy + 60 * scale,
                         arcade.color.YELLOW, int(64 * scale), anchor_x="center", bold=True)
        arcade.draw_text(f"Level {self.game_view.level}",
                         self.cx, self.cy - 20 * scale,
                         arcade.color.YELLOW, int(30 * scale), anchor_x="center")
        arcade.draw_text(f"Your score : {self.game_view.player.score}",
                         self.cx, self.cy - 60 * scale,
                         arcade.color.YELLOW, int(30 * scale), anchor_x="center")
        arcade.draw_text("Push SPACE to resume the game",
                         self.cx, self.cy - 200 * scale,
                         arcade.color.WHITE, int(20 * scale), anchor_x="center")
        arcade.draw_text("Push ESCAPE to exit the game and return to menu",
                         self.cx, self.cy - 400 * scale,
                         arcade.color.BLUE_GRAY, int(20 * scale), anchor_x="center",
                         bold=True)

    def on_key_press(self, key, modifiers):
        """Resume the game with SPACE, go back to the menu with ESCAPE."""
        if key == arcade.key.SPACE:
            self.game_view.resume()
        elif key == arcade.key.ESCAPE:
            from .menu_view import MenuView
            self.window.show_view(MenuView(self.game_view.config))
