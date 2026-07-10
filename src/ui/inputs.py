import arcade
import time
from src.visualization import GameView


class Inputs:
    def __init__(self, view: "GameView") -> None:
        self.view = view

    def on_key_press(self, key: int, _: int) -> None:
        """Toggle fullscreen with F, go back to menu with Escape."""
        from src.visualization import MenuView
        if key == arcade.key.ESCAPE:
            self.view.window.show_view(MenuView(self.view.config))

        elif key == arcade.key.C:
            if self.view.player.cheat_mode is False:
                self.view.player.cheat_mode = True
            else:
                self.view.player.cheat_mode = False
        elif key == arcade.key.G and self.view.player.cheat_mode is True:
            if self.view.maze.ghost_freeze is True:
                self.view.maze.ghost_freeze = False
            else:
                self.view.maze.ghost_freeze = True

        # pass the level (Only in cheat mode)
        elif key == arcade.key.N and self.view.player.cheat_mode:
            if self.view.level == self.view.config.level:
                from src.visualization import WinView
                win = WinView(self.view.config, self.view.player.score)
                self.view.window.show_view(win)
            else:
                from src.visualization import TransitionView
                transition = TransitionView(self.view.config,
                                            self.view.player.score,
                                            self.view.player.lives,
                                            self.view.level + 1,
                                            self.view.player.cheat_mode)
                self.view.window.show_view(transition)

        # pause the game: freeze time and show the pause menu
        elif key == arcade.key.P:
            from src.visualization.pause_view import PauseView
            self.view.pause = True
            self.view.pause_start = time.time()
            self.view.window.show_view(PauseView(self.view))

        # controls of the player
        if not self.view.pause:
            if key == arcade.key.UP:
                self.view.player.move_up = True
            elif key == arcade.key.DOWN:
                self.view.player.move_down = True
            elif key == arcade.key.LEFT:
                self.view.player.move_left = True
            elif key == arcade.key.RIGHT:
                self.view.player.move_right = True

    def on_key_release(self, key: int, _: int) -> None:
        if not self.view.pause:
            if key == arcade.key.UP:
                self.view.player.move_up = False
            elif key == arcade.key.DOWN:
                self.view.player.move_down = False
            elif key == arcade.key.LEFT:
                self.view.player.move_left = False
            elif key == arcade.key.RIGHT:
                self.view.player.move_right = False
