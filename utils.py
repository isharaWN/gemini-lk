from pathlib import Path


class Utils:
    def __init__(self):
        self.instructions_file: str = "instructions.txt"

    def read_instructions(self) -> str:
        return Path(self.instructions_file).read_text(encoding="utf-8").strip()
