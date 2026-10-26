import unittest
from unittest.mock import patch
from midi_engine.MidiSettings import MidiSettings, VoiceConfig
from midi_engine.MidiConstants import HARPSICHORD


class TestMidiSettings(unittest.TestCase):
    def test_default_initialization(self):
        # Teste para checagem de inicialização padrão
        settings = MidiSettings()

        self.assertEqual(settings.initial_bpm, 120)
        self.assertEqual(settings.base_octave, 6)
        self.assertEqual(len(settings.voices), 4)
        self.assertEqual(settings.voice_count, 4)
        self.assertEqual(settings.default_duration, 480)

    def test_invert_bpm_range(self):
        # Teste para min_bpm > max_bpm
        with self.assertRaises(ValueError):
            MidiSettings(min_bpm=200, max_bpm=100)

    def test_empty_voices(self):
        # Teste para passagem de paramêtros sem as vozes
        with self.assertRaises(ValueError):
            MidiSettings(voices=())

    def test_bpm_out_of_range(self):
        # Teste para bpm fora do intervalo
        with self.assertRaises(ValueError):
            MidiSettings(initial_bpm=10)

    def test_base_octave_out_of_range(self):
        # Teste para oitava padrão fora do intervalo
        with self.assertRaises(ValueError):
            MidiSettings(base_octave=0)

    def test_volume_out_of_range(self):
        # Teste para volume fora do intervalo
        with self.assertRaises(ValueError):
            MidiSettings(voices=(VoiceConfig(instrument=0, volume=200),))

    def test_instrument_out_of_range(self):
        # Teste para instrumento fora do intervalo
        with self.assertRaises(ValueError):
            MidiSettings(voices=(VoiceConfig(instrument=-1, volume=100),))

    def test_normal_faster_bpm(self):
        # Teste de checagem da função que aumenta o valor de bpm
        settings = MidiSettings()
        self.assertEqual(
            settings.faster_bpm(MidiSettings.initial_bpm),
            MidiSettings.initial_bpm + MidiSettings.bpm_step,
        )

    def test_normal_slower_bpm(self):
        # Teste de checagem da função que diminui o valor de bpm
        settings = MidiSettings()
        self.assertEqual(
            settings.slower_bpm(MidiSettings.initial_bpm),
            MidiSettings.initial_bpm - MidiSettings.bpm_step,
        )

    def test_volume_for_voice(self):
        # Teste que verifica a ciclagem da função de volume pelas vozes
        settings = MidiSettings()
        self.assertEqual(settings.volume_for_voice(5), 80)
        self.assertEqual(settings.volume_for_voice(5), settings.volume_for_voice(1))

    def test_instrument_for_voice(self):
        # Teste que verifica a ciclagem da função de instrumento pelas vozes
        settings = MidiSettings()
        self.assertEqual(settings.instrument_for_voice(4), HARPSICHORD)
        self.assertEqual(
            settings.instrument_for_voice(4), settings.instrument_for_voice(0)
        )

    def test_octave_for_voice(self):
        # Teste que verifica a ciclagem da função de oitava pelas vozes
        settings = MidiSettings()
        self.assertEqual(settings.octave_for_voice(4), 6)
        self.assertEqual(settings.octave_for_voice(4), settings.octave_for_voice(0))


if __name__ == "__main__":
    unittest.main()
