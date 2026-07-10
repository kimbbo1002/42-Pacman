import json
import arcade.gui
from typing import Dict, Any

from ..paths import writable_path


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
    def load_scores(filename: str) -> list[Dict[str, Any]]:
        """Read the JSON file and return the list of valid scores.
        Invalid entries (not an object, missing or empty player_name,
        name too long, missing or negative score) are skipped. A missing
        file or an unreadable file returns an empty list."""
        filename = writable_path(filename)
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"{filename} is not valid JSON, ignoring highscores")
            return []

        if not isinstance(data, list):
            print(f"{filename} must contain a list of scores, "
                  "ignoring highscores")
            return []

        valid_scores: list[Dict[str, Any]] = []
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                print(f"Entry {i + 1} is not an object, skipped: {entry!r}")
                continue

            name = entry.get("player_name")
            if not isinstance(name, str) or name == "":
                print(f"Entry {i + 1} has an invalid or empty "
                      f"player_name, skipped: {entry!r}")
                continue
            if len(name) > 10:
                print(f"Entry {i + 1} has a player_name too long "
                      f"(max 10 characters), skipped: {entry!r}")
                continue

            score = entry.get("score")
            if not isinstance(score, int) or score < 0:
                print(f"Entry {i + 1} has an invalid or negative "
                      f"score, skipped: {entry!r}")
                continue

            valid_scores.append(entry)

        return valid_scores

    def save(self, filename: str) -> None:
        """Save the score in a sorted order in the JSON file with
            the top 10 highscores."""
        filename = writable_path(filename)
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

        handled: bool | None = super().on_event(event)
        text: str = getattr(self, "text")
        if len(text) > self.MAX_LENGTH:
            truncated = text[:self.MAX_LENGTH]
            self.text = truncated
            self.caret.position = len(truncated)
        return handled
