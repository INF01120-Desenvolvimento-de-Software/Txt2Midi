import os
from midiutil import MIDIFile

class File:
    allowed_extension = ""

    def __init__(self, path=None):
        self.path = path
        file = 

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        if new_path is not None:
            if self.allowed_extension and not new_path.lower().endswith(self.allowed_extension):
                raise ValueError(f"Invalid extension. Expected: '{self.allowed_extension}'")
        self._path = new_path


class txtFile(File):
    allowed_extension = ".txt"

    def __init__(self, path):
        super().__init__(path)
        self.text = self.read_file()

    def read_file(self) -> str:
        if not self.path:
            raise ValueError("Path is not defined.")
        
        try:
            # O with garante que o arquivo vai ser fechado quando o bloco terminar
            with open(self.path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at '{self.path}' was not found.")
            
    


class MidiFile(File):
    allowed_extension = ".mid"

    def __init__(self, path):
         super().__init__(path)
         self.midi = MIDIFile(1)

    def save_file(self, new_path=None) -> str:
        if new_path:
            self.path = new_path

        if not self.path:
            raise ValueError("Path is not defined.")
        
        # O with garante que o arquivo vai ser fechado quando o bloco terminar
        with open(self.path, "wb") as output_file:
            self.midi.writeFile(output_file)
            
        return self.path