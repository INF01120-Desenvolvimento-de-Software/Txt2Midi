import unittest
from unittest.mock import patch, MagicMock
from storage.OSInterface import OSInterface


class TestOSInterface(unittest.TestCase):

    @patch("tkinter.Tk")
    def test_hidden_root_management(self, mock_tk):
        # Testa se a janela oculta do Tkinter é criada, escondida e destruída corretamente
        mock_root_instance = MagicMock()
        mock_tk.return_value = mock_root_instance

        with OSInterface._hidden_root() as root:
            self.assertEqual(root, mock_root_instance)
            # Verifica se .withdraw() foi chamado para esconder a janela fantasma
            mock_root_instance.withdraw.assert_called_once()

        # Verifica se, ao sair do bloco 'with', a janela é destruída para libertar memória
        mock_root_instance.destroy.assert_called_once()

    @patch("tkinter.filedialog.askopenfilename")
    @patch("storage.OSInterface.TxtFile.load")
    def test_get_txt_content_success(self, mock_txt_load, mock_askopen):
        # Cenário ideal: Utilizador seleciona um ficheiro válido
        mock_askopen.return_value = "caminho/teste.txt"

        mock_txt_instance = MagicMock()
        mock_txt_instance.text = "Conteúdo simulado"
        mock_txt_load.return_value = mock_txt_instance

        resultado = OSInterface.get_txt_content()

        self.assertEqual(resultado, "Conteúdo simulado")
        mock_askopen.assert_called_once()
        mock_txt_load.assert_called_once_with("caminho/teste.txt")

    @patch("tkinter.filedialog.askopenfilename")
    def test_get_txt_content_user_cancelled(self, mock_askopen):
        # Cenário alternativo: Utilizador clica em "Cancelar" na janela (retorna string vazia)
        mock_askopen.return_value = ""

        resultado = OSInterface.get_txt_content()

        self.assertIsNone(resultado)

    @patch("tkinter.filedialog.askopenfilename")
    @patch("storage.OSInterface.TxtFile.load")
    def test_get_txt_content_handles_exception(self, mock_txt_load, mock_askopen):
        # Cenário de falha: Proteção do bloco try/except se o disco falhar
        mock_askopen.return_value = "caminho/corrompido.txt"
        mock_txt_load.side_effect = Exception("Erro simulado de leitura")

        resultado = OSInterface.get_txt_content()

        self.assertIsNone(resultado)

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("storage.OSInterface.TxtFile")
    def test_save_txt_content_success(self, mock_txt_class, mock_asksave):
        # Cenário ideal: Utilizador escolhe onde guardar e a escrita funciona
        mock_asksave.return_value = "caminho/salvar.txt"

        mock_txt_instance = MagicMock()
        mock_txt_class.return_value = mock_txt_instance

        resultado = OSInterface.save_txt_content("Texto para guardar")

        self.assertTrue(resultado)
        mock_txt_class.assert_called_once_with(
            "caminho/salvar.txt", "Texto para guardar"
        )
        mock_txt_instance.write_file.assert_called_once()

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_save_txt_content_user_cancelled(self, mock_asksave):
        # Cenário alternativo: Utilizador cancela a gravação
        mock_asksave.return_value = ""

        resultado = OSInterface.save_txt_content("Texto")

        self.assertFalse(resultado)

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("storage.OSInterface.TxtFile")
    def test_save_txt_content_handles_exception(self, mock_txt_class, mock_asksave):
        # Cenário de falha: Disco sem espaço ou permissão negada
        mock_asksave.return_value = "caminho/bloqueado.txt"

        mock_txt_instance = MagicMock()
        mock_txt_instance.write_file.side_effect = PermissionError("Acesso negado")
        mock_txt_class.return_value = mock_txt_instance

        resultado = OSInterface.save_txt_content("Texto")

        self.assertFalse(resultado)

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_save_midi_content_success(self, mock_asksave):
        # Cenário ideal: Guarda o ficheiro MIDI gerado pelo mido
        mock_asksave.return_value = "musica_final.mid"

        # Cria um objeto MIDI falso para simular o retorno da classe Rule
        mock_midi_object = MagicMock()

        resultado = OSInterface.save_midi_content(mock_midi_object)

        self.assertTrue(resultado)
        mock_midi_object.save.assert_called_once_with("musica_final.mid")

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_save_midi_content_user_cancelled(self, mock_asksave):
        # Cenário alternativo: Utilizador cancela a gravação do MIDI
        mock_asksave.return_value = ""
        mock_midi_object = MagicMock()

        resultado = OSInterface.save_midi_content(mock_midi_object)

        self.assertFalse(resultado)
        mock_midi_object.save.assert_not_called()

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_save_midi_content_handles_exception(self, mock_asksave):
        # Cenário de falha: Erro interno da biblioteca mido ao tentar guardar
        mock_asksave.return_value = "musica.mid"
        mock_midi_object = MagicMock()
        mock_midi_object.save.side_effect = IOError("Erro no sistema de ficheiros")

        resultado = OSInterface.save_midi_content(mock_midi_object)

        self.assertFalse(resultado)


if __name__ == "__main__":
    unittest.main()
