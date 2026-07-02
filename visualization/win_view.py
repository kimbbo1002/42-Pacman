import arcade
import arcade.gui
from parsing import Config
from objects import Score, InputName


class WinView(arcade.View):
    """Screen of win."""

    def __init__(self, config: Config, score: int):
        """Store the config and the final score to display."""
        super().__init__()
        self.config = config
        self.score = score
        self.manager = arcade.gui.UIManager()

        self.v_box = arcade.gui.UIBoxLayout(space_between=10)

        self.label = arcade.gui.UITextArea(
            text="Enter your name :",
            width=400,
            height=30,
            text_color=arcade.color.WHITE,
            font_size=20,

        )
        self.v_box.add(self.label)

        self.input_field = InputName(
            width=400, height=50, text="", text_color=arcade.color.BLACK,
            font_size=25
        )

        input_bg = self.input_field.with_background(
            texture=arcade.texture.Texture.create_empty(
                name="input_bg", size=(400, 40), color=arcade.color.WHITE
            )
        )
        self.v_box.add(input_bg)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            child=self.v_box,
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-120
        )

        self.manager.add(anchor_layout)

    def on_show_view(self):
        "Setup the window with a black background."
        self.manager.enable()
        self.window.background_color = arcade.color.BLACK

        self.cx = self.window.width / 2
        self.cy = self.window.height / 2

    def on_draw(self):
        "Write the win message and the score."
        self.clear()

        arcade.draw_text("CONGRATULATIONS, YOU WIN !", self.cx, self.cy + 80,
                         arcade.color.GREEN, 50, anchor_x="center")
        arcade.draw_text(f"Your score : {self.score}", self.cx, self.cy - 20,
                         arcade.color.BLUE_VIOLET, 50, anchor_x="center")
        self.manager.draw()
        arcade.draw_text("Push ENTER to save and return to menu",
                         self.cx, self.cy - 500,
                         arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        """Return to menu with SPACE, leave fullscreen with F,
            and close the window with ESCAPE."""
        if key == arcade.key.ENTER:
            from .menu_view import MenuView

            score = Score(self.input_field.text.strip(), self.score)
            score.save()

            menu = MenuView(self.config)
            self.window.show_view(menu)

        elif key == arcade.key.ESCAPE:
            self.window.close()
