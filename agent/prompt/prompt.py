from typing import List, Dict, Any
import os
import json

abs_path = os.path.dirname(os.path.realpath(__file__))

class Prompt:
    def __init__(self, part: str) -> None:
        self.text = ""
        self.part = part
        self.load_text()

    def cover(self, text: str) -> None:
        self.text = text

    def to_string(self, params: Dict[str, Any]) -> str:
        text = self.text
        for key, value in params.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            if isinstance(value, (int, float)):
                value = str(value)
            text = text.replace(key, value)
        return text

    def load_text(self) -> None:
        with open(os.path.join(abs_path, f"{self.part}.txt"), "r", encoding="utf-8") as text_file:
            self.text = text_file.read()
