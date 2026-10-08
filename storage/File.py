import os

# Remova a importação do midiutil


class File:
    allowed_extension = ""

    def __init__(self, path=None):
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        if new_path is not None:
            if self.allowed_extension and not new_path.lower().endswith(
                self.allowed_extension
            ):
                raise ValueError(
                    f"Invalid extension. Expected: '{self.allowed_extension}'"
                )
        self._path = new_path


class TxtFile(File):
    allowed_extension = ".txt"

    def __init__(self, path, text=""):
        super().__init__(path)
        self.text = text

    @classmethod
    def load(cls, path) -> "TxtFile":
        file = cls(path)
        file.text = file.read_file()
        return file


    def read_file(self) -> str:
        if not self.path:
            raise ValueError("Path is not defined.")

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at '{self.path}' was not found.")

    def write_file(self) -> None:
        if not self.path:
            raise ValueError("Path is not defined.")
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(self.text)

class MidiFile(File):
    allowed_extension = ".mid"

    def __init__(self, path):
        super().__init__(path)
