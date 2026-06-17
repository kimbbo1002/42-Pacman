import json
import sys
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any
from enum import Enum


class Colors(Enum):
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[0;32m"
    RESET = "\033[0m"

    def __str__(self):
        return self.value


def log_warning(field_name: str, message: str, default: Any):
    """Helper function to handle all repetitive warning logs."""
    print(
        f"\n{Colors.YELLOW}WARNING(CONFIG):\n{Colors.RESET}"
        f"Error parsing '{field_name}': {message}\n"
        f"Setting to default value {default}"
    )


class Config(BaseModel):
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

    @model_validator(mode='before')
    @classmethod
    def pre_validate_and_fallback(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Pydantic validates fields,
        and falling back to default in case of error."""
        if not isinstance(data, dict):
            return data

        clean_data = {}
        for field_name, field_info in cls.model_fields.items():
            default_value = field_info.default

            if field_name not in data:
                clean_data[field_name] = default_value
                continue

            raw_value = data[field_name]

            try:
                if field_info.annotation is int:
                    validated_val = int(raw_value)
                    if validated_val < 0:
                        raise ValueError("needs to be a positive integer")
                else:
                    validated_val = str(raw_value)

                # 2. Specific range validations
                if (
                    field_name in ['width', 'height']
                    and not (10 <= validated_val <= 30)
                ):
                    raise ValueError(
                        "minimum map size is 10x10, maximum map size is 30x30"
                    )
                if (
                    field_name == 'level_max_time'
                    and validated_val > 150
                ):
                    raise ValueError("maximum time per level is 150 seconds")
                if (
                    field_name == 'highscore_filename'
                    and not validated_val.endswith('.json')
                ):
                    raise ValueError("must be a valid JSON file name")

                clean_data[field_name] = validated_val

            except Exception as e:
                # Custom clean error parsing messages
                err_msg = str(e).replace(
                    "invalid literal for int() with base 10: ", "")
                log_warning(field_name, err_msg, default_value)
                clean_data[field_name] = default_value

        return clean_data


def load_config() -> Config:
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
    print(f"\n{Colors.GREEN}==TESTING=={Colors.RESET}")
    for attr in Config.model_fields:
        print(f"{attr} = {getattr(config, attr)}")


if __name__ == "__main__":
    test_parsing(load_config())
