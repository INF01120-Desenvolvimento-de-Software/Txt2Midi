import os

class File:
    def __init__(self, path):
        self.path = path


class txtFile(File):
    def __init__(self, path, text):
        super().__init__(path)
        self.text = self.read_file()

    def read_file(self) -> str:
            
            if not self.path.lower().endswith('.txt'):
                return f"Error: The file at '{self.path}' is not (.txt)."
            
            try:
                # O with garente que o arquivo vai ser fechado quando o bloco terminar
                with open(self.path, 'r', encoding='utf-8') as file:
                    return file.read()
            except FileNotFoundError:
                return f"Error: The file at '{self.path}' was not found."
            
    def sequence_extract(self):
            char_sequence = list(self.text)
            return char_sequence

    