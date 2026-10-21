class StorageError(Exception):
    """Base de todas as exceções do pacote storage."""


class PathNotDefinedError(StorageError):
    def __init__(self):
        super().__init__("O caminho do arquivo não foi definido.")


class InvalidExtensionError(StorageError):
    def __init__(self, expected_extension: str):
        self.expected_extension = expected_extension
        super().__init__(f"Extensão inválida. Esperado: '{expected_extension}'")


class FileReadError(StorageError):
    message = "Não foi possível ler o arquivo '{path}'."

    def __init__(self, path: str):
        self.path = path
        super().__init__(self.message.format(path=path))


class MissingFileError(FileReadError):
    message = "O arquivo '{path}' não foi encontrado."


class FileWriteError(StorageError):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Não foi possível escrever no arquivo '{path}'.")