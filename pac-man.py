from parsing import load_config
from visualization import MenuView
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Pac-Man"


def main() -> None:
    try:
        config = load_config()
        window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT,
                               WINDOW_TITLE, fullscreen=True)
        window.show_view(MenuView(config))
        arcade.run()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
