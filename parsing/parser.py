import json
import sys
from pydantic import BaseModel, model_validator
from typing import Dict, Any
from enum import Enum


class Colors(Enum):
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[0;32m"
    RESET = "\033[0m"

    def __str__(self):
        return self.value


class Config(BaseModel):
    highscore_filename: str = "highscore.json"
    level: int = 10
    width: int = 15
    height: int = 15
    lives: int = 3
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90

    @model_validator(mode='before')
    @classmethod
    def check_config_types(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """This function verifies all field's types before initializing."""
        # verify highscore_filename
        if 'highscore_filename' in data.keys():
            try:
                val = data.get('highscore_filename')
                if not isinstance(val, str):
                    raise ValueError(
                        "'highscore_filename' must be a valid string"
                    )
            except ValueError as e:
                default = cls.model_fields['highscore_filename'].default
                print(
                    f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                    f"Error parsing 'highscore_filename': {e}\n"
                    f"Setting to default value {default}"
                )
        else:
            default = cls.model_fields['highscore_filename'].default
            print(
                f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                f"'highscore_filename' not found, "
                f"setting to default value {default}"
            )

        # verify integer fields
        int_configs = [
            "level", "width", "height", "lives",
            "points_per_pacgum", "points_per_super_pacgum",
            "points_per_ghost", "seed", "level_max_time"
        ]
        for c in int_configs:
            if c in data.keys():
                val = data.get(c)

                try:
                    if val:
                        v = int(val)

                        if v < 0:
                            raise ValueError(
                                f"'{c}' needs to be a positive integer"
                            )
                        data[c] = v

                except ValueError as e:
                    default = cls.model_fields[c].default
                    print(
                        f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                        f"Error parsing '{c}': {e}\n"
                        f"Setting to default value {default}"
                    )
                    data[c] = default
            else:
                default = cls.model_fields[c].default
                print(
                    f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                    f"'{c}' not found, setting to default value {default}"
                )

        return data

    @model_validator(mode='after')
    def check_config_values(self) -> "Config":
        """This function verifies all field's values after initializing."""

        # verify highscore_filename
        if not self.highscore_filename.endswith('.json'):
            default = Config.model_fields['highscore_filename'].default
            print(
                f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                "Error parsing 'highscore_filename': "
                "'highscore_filename' must be a valid JSON file name\n"
                f"Setting to default value {default}"
            )

        # verify minimum map area
        for c in ['width', 'height']:
            val = getattr(self, c)
            if val < 10 or val > 30:
                default = Config.model_fields[c].default
                print(
                    f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                    f"Error parsing '{c}': "
                    f"minimum map size is 10x10, "
                    "maximum map size is 30x30\n"
                    f"Setting to default value {default}"
                )
                setattr(self, c, default)

        # verify level_max_time
        if self.level_max_time > 150:
            default = Config.model_fields['level_max_time'].default
            print(
                f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                f"Error parsing '{c}': "
                f"maximum time per level is 150 seconds"
                f"Setting to default value {default}"
            )
            self.level_max_time = default

        return self


def load_config() -> Config:
    try:
        config_filename = sys.argv[1]
        try:
            with open(config_filename, "r") as file:
                raw_config = json.load(file)
            config = Config(**raw_config)
        except FileNotFoundError:
            print(
                f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
                f"File '{config_filename}' was not found\n"
                "Setting configuration to default values"
            )
            config = Config()
    except Exception:
        print(
            f"\n{Colors.RED}ERROR(CONFIG):\n{Colors.RESET}"
            "Unexpected error occured during configuration parsing\n"
            "Setting configuration to default values"
        )
        config = Config()
    return config


def test_parsing(config: Config) -> None:
    print(f"\n{Colors.GREEN}==TESTING=={Colors.RESET}")

    for attr in Config.model_fields:
        print(f"{attr} = {getattr(config, attr)}")


if __name__ == "__main__":
    test_parsing(load_config())
