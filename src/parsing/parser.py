import json
import sys
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any
from enum import Enum


class Colors(Enum):
    """Colors codes used to print warnings in the terminal."""

    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[0;32m"
    RESET = "\033[0m"

    def __str__(self) -> str:
        """Return the raw code so the enum prints as its color."""
        return self.value


def log_warning(field_name: str, message: str, default: Any) -> None:
    """Helper function to handle all repetitive warning logs."""
    print(
        f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
        f"Error parsing '{field_name}': {message}\n"
        f"Setting to default value {default}"
    )


class Config(BaseModel):
    """Game settings read from the config file, with safe defaults."""
    highscore_filename: str = Field(default="highscore.json")
    level: int = Field(default=10)
    width: int = Field(default=15)
    height: int = Field(default=15)
    lives: int = Field(default=3)
    points_per_pacgum: int = Field(default=10)
    points_per_super_pacgum: int = Field(default=50)
    points_per_ghost: int = Field(default=200)
    seed: int = Field(default=42)
    level_max_time: int = Field(default=90)
    theme: str = Field(default="pacman")

    @model_validator(mode='before')
    @classmethod
    def pre_validate_and_fallback(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Pydantic validates fields,
        and falling back to default in case of error."""
        if not isinstance(data, dict):
            return data

        for f_name in data.keys():
            if f_name not in cls.model_fields:
                print(
                    f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                    f"Unknown field '{f_name}' in config file, ignoring it"
                )

        clean_data = {}
        themes = ["pacman", "stardew_valley", "minecraft"]
        for field_name, field_info in cls.model_fields.items():
            default_value = field_info.default

            if field_name not in data:
                clean_data[field_name] = default_value
                continue

            raw_value = data[field_name]

            try:
                if field_info.annotation is int:
                    if isinstance(raw_value, float):
                        print(
                            f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                            f"Field '{field_name}' is a float, converting to int"
                        )
                    validated_val = int(raw_value)
                    if validated_val <= 0:
                        raise ValueError("needs to be greater than 0")
                else:
                    validated_val_str = str(raw_value)

                # Specific range validations
                if (
                    field_name in ['width', 'height']
                    and not (10 <= validated_val <= 30)
                ):
                    raise ValueError(
                        "minimum map size is 10x10, maximum map size is 30x30"
                    )
                if (
                    field_name == 'level_max_time'
                    and not 10 <= validated_val <= 180
                ):
                    raise ValueError("time per level must be between 10 and "
                                     "180 seconds")
                if (
                    field_name == 'highscore_filename'
                    and not validated_val_str.endswith('.json')
                ):
                    raise ValueError("must be a valid JSON file name")
                if (
                    field_name == 'level'
                    and validated_val > 20
                ):
                    raise ValueError("maximum level of game is 20")
                if (
                    field_name == 'lives'
                    and validated_val > 10
                ):
                    raise ValueError("maximum lives of player is 10")
                if (
                    field_name == 'theme'
                    and validated_val_str not in themes
                ):
                    raise ValueError(f"must be {', '.join(themes)}")

                if field_info.annotation is int:
                    clean_data[field_name] = validated_val
                else:
                    clean_data[field_name] = validated_val_str

            except Exception as e:
                # Custom clean error parsing messages
                err_msg = str(e).replace(
                    "invalid literal for int() with base 10: ", "")
                log_warning(field_name, err_msg, default_value)
                clean_data[field_name] = default_value

        return clean_data

    @model_validator(mode='after')
    def validate_points(self) -> "Config":
        """Check point values and hierarchy, reset to defaults if invalid."""
        # check if points are in range
        if (
            not 0 < self.points_per_pacgum <= 250
            or not 0 < self.points_per_super_pacgum <= 500
            or not 0 < self.points_per_ghost <= 1000
        ):
            print(
                f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                "Error parsing [points_per_pacgum, points_per_super_pacgum, "
                "points_per_ghost]\n"
                "\nAll points must respect ranges:\n"
                "points_per_pacgum: 1-250\n"
                "points_per_super_pacgum: 1-500\n"
                "points_per_ghost: 1-1000"
                "\n\n Returning to default values:"
                "points_per_pacgum: 10\n"
                "points_per_super_pacgum: 20\n"
                "points_per_ghost: 200"
            )
            self.points_per_pacgum = 10
            self.points_per_super_pacgum = 50
            self.points_per_ghost = 200
            return self

        # check if point hierarchy is correct
        if (
            not self.points_per_pacgum * 2 <= self.points_per_super_pacgum
            or not self.points_per_super_pacgum * 2 <= self.points_per_ghost
        ):
            print(
                f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                "Error parsing [points_per_pacgum, points_per_super_pacgum, "
                "points_per_ghost]\n"
                "\nAll points must respect hierarchy\n"
                "points_per_pacgum * 2 <= points_per_super_pacgum * 2"
                " <= points_per_ghost"
            )
            self.points_per_pacgum = 10
            self.points_per_super_pacgum = 50
            self.points_per_ghost = 200
            return self

        return self


def load_config() -> Config:
    """Read the config file given on the command line, or fall back
    to default values on any error."""
    if len(sys.argv) != 2:
        print(
            f"\n{Colors.RED}ERROR(CONFIG):\n{Colors.RESET}"
            "This program takes exactly one argument: a configuration file\n"
            "Example use: python3 pac-man.py config.json"
        )
        sys.exit(1)

    config_filename = sys.argv[1]
    try:
        with open(config_filename, "r") as file:
            raw_config = json.load(file)
            return Config(**raw_config)
    except FileNotFoundError:
        print(
            f"\n{Colors.RED}ERROR(CONFIG):\n{Colors.RESET}"
            f"File '{config_filename}' was not found"
        )
    except json.JSONDecodeError:
        print(
            f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
            "Configuration file is empty or corrupted"
        )
    except Exception:
        print(
            f"\n{Colors.RED}ERROR(CONFIG):\n{Colors.RESET}"
            "Unexpected error occurred during configuration parsing")

    print("Setting configuration to default values")
    return Config()


def test_parsing(config: Config) -> None:
    """Print every config field and its value (debug helper)."""
    print(f"\n{Colors.GREEN}==TESTING=={Colors.RESET}")
    for attr in Config.model_fields:
        print(f"{attr} = {getattr(config, attr)}")


if __name__ == "__main__":
    test_parsing(load_config())
