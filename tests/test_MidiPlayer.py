import unittest
from unittest.mock import patch
from midi_engine.MidiPlayer import MidiPlayer


class TestMidiPlayer(unittest.TestCase):
    def setUp(self):
        MidiPlayer.paused = False

    @patch("pygame.mixer.music.load")
    def test_load_midi_success(self, mock_load):
        # Teste de carregamento do caminho do arquivo
        MidiPlayer.load_midi("teste.mid")
        mock_load.assert_called_once_with("teste.mid")

    @patch("pygame.mixer.music.play")
    def test_play_from_start(self, mock_play):
        # Teste de reprodução inicial de áudio
        MidiPlayer.play_audio()
        mock_play.assert_called_once()
        self.assertFalse(MidiPlayer.paused)

    @patch("pygame.mixer.music.unpause")
    @patch("pygame.mixer.music.play")
    def test_play_from_paused_state(self, mock_play, mock_unpause):
        # Teste de retomada de reprodução de áudio pausado
        MidiPlayer.paused = True
        MidiPlayer.play_audio()
        mock_unpause.assert_called_once()
        mock_play.assert_not_called()
        self.assertFalse(MidiPlayer.paused)

    @patch("pygame.mixer.music.pause")
    def test_pause_audio(self, mock_pause):
        # Teste de pausa de áudio
        MidiPlayer.pause_audio()
        mock_pause.assert_called_once()
        self.assertTrue(MidiPlayer.paused)

    @patch("pygame.mixer.music.stop")
    @patch("pygame.mixer.music.play")
    def test_reset_audio(self, mock_play, mock_stop):
        # Teste de reinicialização de áudio
        MidiPlayer.reset_audio()
        mock_stop.assert_called_once()
        mock_play.assert_called_once()
        self.assertFalse(MidiPlayer.paused)

    @patch("pygame.mixer.music.load")
    def test_load_missing_file_handled(self, mock_load):
        # Teste de caminho não reconhecido
        mock_load.side_effect = FileNotFoundError("Arquivo MIDI não encontrado")
        with self.assertRaises(FileNotFoundError):
            MidiPlayer.load_midi("inexistente.mid")


if __name__ == "__main__":
    unittest.main()
