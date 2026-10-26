import unittest
from unittest.mock import MagicMock, patch
from midi_engine.MidiWriter import MidiWriter


class TestMidiWriter(unittest.TestCase):
    def setUp(self):
        self.writer = MidiWriter()

    @patch("midi_engine.Rule.Rules.parse_text")
    def test_process_text_success(self, mock_parse):
        # Teste de processamento de texto com sucesso
        fake_midi = MagicMock()
        mock_parse.return_value = fake_midi

        self.writer.process_text("A:3 B:2")
        mock_parse.assert_called_once_with("A:3 B:2")
        self.assertEqual(self.writer.midi, fake_midi)

    def test_save_midi_with_implicit_extension(self):
        # Teste de salvamento de MIDI com extensão implícita
        self.writer.midi = MagicMock()
        self.writer.save_midi("minha_composicao")
        self.writer.midi.save.assert_called_once_with("minha_composicao.mid")

    def test_save_midi_with_explicit_extension(self):
        # Teste de salvamento de MIDI com extensão explícita
        self.writer.midi = MagicMock()
        self.writer.save_midi("minha_composicao.mid")
        self.writer.midi.save.assert_called_once_with("minha_composicao.mid")

    def test_save_midi_without_processing(self):
        # Teste de erro ao salvar sem processamento prévio
        with self.assertRaises(AttributeError):
            self.writer.save_midi("falha.mid")


if __name__ == "__main__":
    unittest.main()
