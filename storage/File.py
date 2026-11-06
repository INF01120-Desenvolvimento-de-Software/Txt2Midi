"""Classes de arquivo com validação de extensão e leitura/escrita de texto."""

import os

from .Exceptions import (
    FileReadError,
    FileWriteError,
    InvalidExtensionError,
    MissingFileError,
    PathNotDefinedError,
)


class File:
    """Arquivo genérico com um caminho validado pela extensão permitida.

    Attributes:
        allowed_extension: Extensão aceita (ex.: ".txt"). Vazia aceita qualquer uma.
        path: Caminho do arquivo, validado a cada atribuição.
    """

    allowed_extension = ""

    def __init__(self, path=None):
        """Cria o arquivo.

        Args:
            path: Caminho do arquivo, ou None se ainda não definido.

        Raises:
            InvalidExtensionError: Se a extensão do caminho não for a permitida.
        """
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        """Define o caminho, validando a extensão.

        Args:
            new_path: Novo caminho, ou None.

        Raises:
            InvalidExtensionError: Se a extensão não for a permitida.
        """
        if new_path is not None:
            if self.allowed_extension and not new_path.lower().endswith(
                self.allowed_extension
            ):
                raise InvalidExtensionError(self.allowed_extension)
        self._path = new_path


class TxtFile(File):
    """Arquivo de texto (.txt) codificado em UTF-8.

    Attributes:
        text: Conteúdo do arquivo.
    """

    allowed_extension = ".txt"

    def __init__(self, path, text=""):
        """Cria o arquivo de texto.

        Args:
            path: Caminho do arquivo (deve terminar em .txt).
            text: Conteúdo inicial.
        """
        super().__init__(path)
        self.text = text

    @classmethod
    def load(cls, path) -> "TxtFile":
        """Cria um TxtFile já com o conteúdo lido do disco.

        Args:
            path: Caminho do arquivo a ler.

        Returns:
            TxtFile com o texto carregado.

        Raises:
            StorageError: Se o caminho for inválido ou a leitura falhar.
        """
        file = cls(path)
        file.text = file.read_file()
        return file

    def read_file(self) -> str:
        """Lê o conteúdo do arquivo.

        Returns:
            Texto lido.

        Raises:
            PathNotDefinedError: Se o caminho não foi definido.
            MissingFileError: Se o arquivo não existe.
            FileReadError: Se houver erro de leitura ou de decodificação.
        """
        if not self.path:
            raise PathNotDefinedError()

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError as error:
            raise MissingFileError(self.path) from error
        except (OSError, UnicodeDecodeError) as error:
            raise FileReadError(self.path) from error

    def write_file(self) -> None:
        """Grava o texto no arquivo, sobrescrevendo o conteúdo anterior.

        Raises:
            PathNotDefinedError: Se o caminho não foi definido.
            FileWriteError: Se houver erro de escrita ou de codificação.
        """
        if not self.path:
            raise PathNotDefinedError()

        try:
            with open(self.path, "w", encoding="utf-8") as file:
                file.write(self.text)
        except (OSError, UnicodeEncodeError) as error:
            raise FileWriteError(self.path) from error
