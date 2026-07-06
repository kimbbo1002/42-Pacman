import json
import arcade.gui
from typing import Dict, Any


class Score:

    def __init__(self, player_name: str, score: int):
        self.player_name = player_name
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        """Convert the objet Score to dictionnary with JSON compatibility."""
        if self.player_name == "":
            self.player_name = "Anonymous"
        return {"player_name": self.player_name, "score": self.score}

    @staticmethod
    def load_scores(filename: str = "highscores.json") -> list[Dict[str, Any]]:
        """Read the JSON file and return the list of scores.

        Raise a ValueError if the file content is not a list or if any
        entry is not a dict holding a string player_name and an int score.
        """

        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as error:
            raise ValueError(f"{filename} is not valid JSON") from error

        if not isinstance(data, list):
            raise ValueError(f"{filename} must contain a list of scores")

        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                raise ValueError(f"Entry {i + 1} is not an object: {entry!r}")

            name = entry.get("player_name")
            if not isinstance(name, str) or name == "":
                raise ValueError(
                    f"Entry {i + 1} has a missing or "
                    f"empty player_name: {entry!r}"
                )
            elif len(name) > 10:
                raise ValueError(
                    f"Entry {i + 1} has a player_name too long "
                    f"(max 10 characters): {entry!r}"
                )

            score = entry.get("score")
            if not isinstance(score, int) or score < 0:
                raise ValueError(
                    f"Entry {i + 1} has a missing or negative score: {entry!r}"
                )

        return data

    def save(self, filename: str = "highscores.json") -> None:
        """Save the score in a sorted order in the JSON file with
            the top 10 highscores."""

        scores_list = self.load_scores(filename)
        scores_list.append(self.to_dict())

        scores_list = sorted(
            scores_list, key=lambda x: x["score"], reverse=True
        )
        scores_list = scores_list[:10]

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(scores_list, file, indent=4, ensure_ascii=False)


class InputName(arcade.gui.UIInputText):

    MAX_LENGTH = 10

    def on_event(self, event: arcade.gui.UIEvent) -> bool | None:
        """Only allow alphanumeric characters and spaces, and never let
        the text exceed MAX_LENGTH characters."""
        if isinstance(event, arcade.gui.UITextInputEvent):
            event.text = "".join(
                c for c in event.text if c.isalnum() or c == " "
            )
            if not event.text:
                return True

        handled = super().on_event(event)
        if len(self.text) > self.MAX_LENGTH:
            self.text = self.text[:self.MAX_LENGTH]
            self.caret.position = len(self.text)
        return handled
