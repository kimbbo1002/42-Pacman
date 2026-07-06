import arcade
import arcade.gui
from src.parsing import Config
from src.objects import Score, InputName
from .scaler import ui_scale


class LoseView(arcade.View):
    """Screen of lose."""

    def __init__(self, config: Config, score: int) -> None:
        """Store the config and the final score to display."""
        super().__init__()
        self.config = config
        self.score = score
        self.manager = arcade.gui.UIManager()
        scale = ui_scale(self.window)
        box_width = int(400 * scale)

        self.v_box = arcade.gui.UIBoxLayout(space_between=10 * scale)

        self.label = arcade.gui.UITextArea(
            text="Enter your name :",
            width=box_width,
            height=int(30 * scale),
            text_color=arcade.color.WHITE,
            font_size=int(20 * scale),
            font_name="Kenney Rocket"
        )
        self.v_box.add(self.label)

        self.input_field = InputName(
            width=box_width, height=int(50 * scale),
            text="", text_color=arcade.color.BLACK,
            font_size=int(25 * scale)
        )

        input_bg = self.input_field.with_background(
            texture=arcade.texture.Texture.create_empty(
                name="input_bg", size=(box_width, int(50 * scale)),
                color=arcade.color.WHITE
            )
        )
        self.v_box.add(input_bg)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            child=self.v_box,
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-120 * scale
        )

        self.manager.add(anchor_layout)

    def on_show_view(self) -> None:
        "Setup the window with a black background."
        self.manager.enable()
        self.window.background_color = arcade.color.BLACK

        self.cx = self.window.width / 2
        self.cy = self.window.height / 2

    def on_draw(self) -> None:
        "Write the lose message and the score."
        self.clear()
        scale = ui_scale(self.window)

        arcade.draw_text(
            "The ghosts have gotten the better of you",
            self.cx, self.cy + 190 * scale,
            arcade.color.RED_DEVIL, int(40 * scale),
            anchor_x="center"
        )
        arcade.draw_text(
            "YOU LOST", self.cx, self.cy + 100 * scale,
            arcade.color.RED_DEVIL, int(60 * scale),
            anchor_x="center", bold=True
        )
        arcade.draw_text(
            f"Your score : {self.score}", self.cx, self.cy + 20 * scale,
            arcade.color.BLUE_VIOLET, int(50 * scale), anchor_x="center"
        )
        self.manager.draw()
        arcade.draw_text(
            "Push ENTER to save and return to menu",
            self.cx, self.cy - 500 * scale,
            arcade.color.WHITE, int(20 * scale), anchor_x="center"
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
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
