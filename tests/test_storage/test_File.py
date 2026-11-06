import unittest
from unittest.mock import patch, mock_open

from storage.File import File, TxtFile
from storage.Exceptions import (
    InvalidExtensionError,
    PathNotDefinedError,
    MissingFileError,
)


class TestFile(unittest.TestCase):

    def test_file_init_and_property(self):
        # Testa a inicialização básica e o getter (@property) do path
        arquivo = File("caminho/teste.ext")
        self.assertEqual(arquivo.path, "caminho/teste.ext")

    def test_file_path_setter_validation(self):
        # Testa a validação de extensão no setter usando a subclasse TxtFile
        with self.assertRaises(InvalidExtensionError):
            TxtFile("documento.pdf")

    def test_file_path_setter_none(self):
        # Testa se a classe aceita None sem acionar a validação de extensão
        arquivo = TxtFile(None)
        self.assertIsNone(arquivo.path)


class TestTxtFile(unittest.TestCase):

    def test_txtfile_init(self):
        # Testa o construtor com os valores padrão e valores preenchidos
        arquivo_vazio = TxtFile("teste.txt")
        self.assertEqual(arquivo_vazio.text, "")

        arquivo_cheio = TxtFile("teste.txt", "Olá Mundo")
        self.assertEqual(arquivo_cheio.text, "Olá Mundo")

    @patch("builtins.open", new_callable=mock_open, read_data="Conteudo simulado")
    def test_txtfile_read_file_success(self, mock_arquivo):
        # Testa a leitura interceptando o 'open' nativo para ler da memória
        arquivo = TxtFile("teste.txt")
        conteudo = arquivo.read_file()

        self.assertEqual(conteudo, "Conteudo simulado")
        mock_arquivo.assert_called_once_with("teste.txt", "r", encoding="utf-8")

    def test_txtfile_read_file_no_path(self):
        # Testa a proteção de leitura quando o caminho é nulo
        arquivo = TxtFile(None)
        with self.assertRaises(PathNotDefinedError):
            arquivo.read_file()

    @patch("builtins.open")
    def test_txtfile_read_file_not_found(self, mock_arquivo):
        # Força um erro de disco para garantir que o método repassa o MissingFileError
        mock_arquivo.side_effect = FileNotFoundError
        arquivo = TxtFile("inexistente.txt")

        with self.assertRaises(MissingFileError):
            arquivo.read_file()

    @patch("builtins.open", new_callable=mock_open)
    def test_txtfile_write_file_success(self, mock_arquivo):
        # Testa a escrita interceptando o 'open' para gravar na memória
        arquivo = TxtFile("teste.txt", "Gravando isso")
        arquivo.write_file()

        # Verifica se o arquivo foi aberto no modo certo e se o texto exato foi escrito
        mock_arquivo.assert_called_once_with("teste.txt", "w", encoding="utf-8")
        mock_arquivo().write.assert_called_once_with("Gravando isso")

    def test_txtfile_write_file_no_path(self):
        # Testa a proteção de escrita quando o caminho é nulo
        arquivo = TxtFile(None, "Texto")
        with self.assertRaises(PathNotDefinedError):
            arquivo.write_file()

    @patch.object(TxtFile, "read_file", return_value="Texto do load")
    def test_txtfile_load_classmethod(self, mock_read):
        # Testa o @classmethod interceptando o read_file da própria classe
        arquivo_carregado = TxtFile.load("teste.txt")

        self.assertIsInstance(arquivo_carregado, TxtFile)
        self.assertEqual(arquivo_carregado.path, "teste.txt")
        self.assertEqual(arquivo_carregado.text, "Texto do load")
        mock_read.assert_called_once()


if __name__ == "__main__":
    unittest.main()
