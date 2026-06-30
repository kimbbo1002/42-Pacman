from typing import List
from parsing import Config
from .assets import Assets
import arcade


def load_pacgum_textures(assets: Assets) -> List[arcade.BasicSprite]:
    pacgum_texture = arcade.load_texture(
        assets.texture("pacgums", "pacgum"))
    super_pacgum_texture = arcade.load_texture(
        assets.texture("pacgums", "super_pacgum"))
    sprite_pacgum = arcade.BasicSprite(pacgum_texture, scale=0.2)
    sprite_super_pacgum = arcade.BasicSprite(super_pacgum_texture, scale=0.6)

    return [sprite_pacgum, sprite_super_pacgum]


class Cell:
    """One square of the maze: its walls and what sits on it."""

    def __init__(
            self,
            x: int,
            y: int,
            cell_wall: int,
            assets: Assets
    ) -> None:
        """Initialize each cell of maze."""
        self.x = x
        self.y = y
        self.cell_wall = cell_wall
        self.super_pacgum = False
        self.player = False
        self.ghost = False
        self.pattern_42 = True if cell_wall == 15 else False
        self.pacgum = False
        self.point = 0
        self.sprite_pacgum, self.sprite_super_pacgum = load_pacgum_textures(
            assets)


class Maze:
    """The grid of cells and everything placed on it."""

    def __init__(self, maze: List[List[int]], config: Config,
                 score: int) -> None:
        """Initialize the maze, place pacgums & super_pacgums & player."""
        self.maze: List[List[Cell]] = []
        self.config = config
        self.assets = Assets(config.theme)
        self.cols = config.width
        self.rows = config.height
        self.pacgums = 0
        self.end_of_game = False
        self.cheat_mode = False
        self.ghost_freeze = False
        self.score = score
        # pacgums in the back layer, characters (ghosts + player) on top
        self.sprites = arcade.SpriteList()
        self.character_sprites = arcade.SpriteList()

        # initialize maze
        for y, line in enumerate(maze):
            line_list = []
            for x, col in enumerate(line):
                cell = Cell(x, y, col, self.assets)
                line_list.append(cell)
            self.maze.append(line_list)

    def place_objects(self) -> None:
        """Fill the maze: super pacgums in the corners, ghosts near them,
        the player in the middle, and a normal pacgum in every other cell."""
        from .ghost import Ghost
        from .player import Player

        # place super_pacgums & ghosts
        super_pacgum_coordinates = [
            (0, 0),
            (0, self.cols - 1),
            (self.rows - 1, 0),
            (self.rows - 1, self.cols - 1)
        ]
        ghost_coordinates = [
            (1, 0),
            (0, self.rows - 2),
            (self.cols - 1, 1),
            (self.cols - 2, self.rows - 1)
        ]

        for x, y in super_pacgum_coordinates:
            cell = self.maze[y][x]
            cell.super_pacgum = True
            cell.point = self.config.points_per_super_pacgum
            self.pacgums += 1
            self.sprites.append(cell.sprite_super_pacgum)

        self.ghosts: List[Ghost] = []
        for i, (x, y) in enumerate(ghost_coordinates):
            ghost = Ghost(i, x, y, self)
            ghost.point = self.config.points_per_ghost
            self.ghosts.append(ghost)
            self.maze[y][x].ghost = True

        # place player
        self.player = Player(self.config, self.cols // 2,
                             self.rows // 2, self.config.lives,
                             self, self.score)
        self.maze[self.rows // 2][self.cols // 2].player = True

        # place pacgums
        for y in range(len(self.maze[0])):
            for x in range(len(self.maze)):
                cell = self.maze[y][x]
                if (not cell.super_pacgum and not cell.player
                        and not cell.pattern_42):
                    cell.pacgum = True
                    cell.point = self.config.points_per_pacgum
                    self.pacgums += 1
                    self.sprites.append(cell.sprite_pacgum)

    def is_level_win(self) -> bool:
        if self.pacgums == 0:
            return True
        return False
