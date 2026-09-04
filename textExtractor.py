class textExtractor:
    
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_file(self) -> str:
        try:
            # O with garente que o arquivo vai ser fechado quando o bloco terminar
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: The file at '{self.file_path}' was not found."