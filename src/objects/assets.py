
class Assets:
    """Resolve textures and colors for the chosen theme."""

    RESOURCES = "src/resources"

    PALETTES = {
        "pacman": {
            "wall": (0, 0, 255),                # blue
            "background": (0, 0, 0),            # black
            "super_background": (86, 3, 25),    # dark scarlet
        },
        "minecraft": {
            "wall": (140, 105, 66),             # light dirt brown
            "background": (24, 28, 33),         # dark stone
            "super_background": (60, 20, 20),   # dark red glow
        },
        "stardew_valley": {
            "wall": (122, 79, 46),              # wood brown
            "background": (40, 58, 38),         # dark grass green
            "super_background": (66, 22, 16),   # dark red
        },
    }

    def __init__(self, theme: str) -> None:
        """Bind to the chosen theme."""
        self.theme = theme
        self.palette = self.PALETTES.get(theme, self.PALETTES["pacman"])

    def texture(self, category: str, name: str) -> str:
        """Build the path to a texture in the current theme."""
        return f"{self.RESOURCES}/{self.theme}/{category}/{name}.png"

    @property
    def wall(self) -> tuple[int, int, int]:
        """Maze wall color."""
        return self.palette["wall"]

    @property
    def background(self) -> tuple[int, int, int]:
        """Normal background color."""
        return self.palette["background"]

    @property
    def super_background(self) -> tuple[int, int, int]:
        """Background color during super mode."""
        return self.palette["super_background"]
