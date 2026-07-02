import arcade
import arcade.gui
from parsing import Config


class LoseView(arcade.View):
    """Screen of lose."""

    def __init__(self, config: Config, score: int):
        """Store the config and the final score to display."""
        super().__init__()
        self.config = config
        self.score = score
        self.manager = arcade.gui.UIManager()

        # 2. On crée le champ de texte (UIInputText)
        # On lui donne une position, une taille et un texte par défaut
        self.input_field = arcade.gui.UIInputText(
            x=200, y=300, width=400, height=40, text="Write your name here..."
        )
        self.manager.add(self.input_field)

        # On peut personnaliser un peu son style visuel en l'entourant d'un widget décoratif
        # (Optionnel, mais plus joli pour voir où l'on clique)
        # self.input_box = self.input_field.with_background(
        #     texture=arcade.texture.Texture.create_empty(
        #         "box", color=arcade.color.DARK_BLUE_GRAY
        #     )
        # )

    def on_show_view(self):
        "Setup the window with a black background."
        self.manager.enable()
        self.window.background_color = arcade.color.BLACK

    def on_draw(self):
        "Write the lose message and the score."
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
        self.manager.draw()
        print(f"name: {self.input_field.text}")
        arcade.draw_text("Push SPACE to return to menu",
                         cx, cy - 500,
                         arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        """Return to menu with SPACE, leave fullscreen with F,
            and close the window with ESCAPE."""
        if key == arcade.key.SPACE:
            from .menu_view import MenuView
            # sauvegarder le score (rajouter un encadré pour entrer
            # le score et pouvoir le sauvegarder)
            menu = MenuView(self.config)
            self.window.show_view(menu)

        elif key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ESCAPE:
            self.window.close()
