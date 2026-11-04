from dataclasses import dataclass
from typing import Tuple

from midi_engine.MidiConstants import (
    MIN_BASE_OCTAVE,
    MAX_BASE_OCTAVE,
    MAX_MIDI_NOTE,
    HARPSICHORD,
    PIPE_ORGAN,
    PIANO0,
    BASSOON,
)


@dataclass(frozen=True)
class VoiceConfig:
    instrument: int
    volume: int


@dataclass(frozen=True)
class MidiSettings:
    """Parâmetros do arquivo MIDI a ser gerado. Para alterar um valor é necessário usar dataclasses.replace.

    Attributes:
        initial_bpm: BPM inicial da música.
        min_bpm: Menor BPM permitido.
        max_bpm: Maior BPM permitido.
        bpm_step: Quanto o BPM muda a cada ">" ou "<".
        base_octave: Oitava base da primeira voz.
        voices: Configuração de cada voz.
        default_duration: Duração padrão das notas, em ticks.
    """

    initial_bpm: int = 120
    min_bpm: int = 20
    max_bpm: int = 300
    bpm_step: int = 10

    base_octave: int = 6

    voices: Tuple[VoiceConfig, ...] = (
        VoiceConfig(instrument=HARPSICHORD, volume=100),
        VoiceConfig(instrument=PIPE_ORGAN, volume=80),
        VoiceConfig(instrument=PIANO0, volume=60),
        VoiceConfig(instrument=BASSOON, volume=40),
    )

    default_duration: int = 480

    def __post_init__(self):
        """Valida os valores da classe logo após a criação, impedindo a abertura do software caso algum parâmetro esteja fora do esperado.

        Raises:
            ValueError: Se algum valor estiver fora do intervalo permitido.
        """
        if self.min_bpm >= self.max_bpm:
            raise ValueError("min_bpm deve ser menor que max_bpm.")
        if not self.voices:
            raise ValueError("É necessário ao menos uma voz configurada.")

        self._check_range("BPM", self.initial_bpm, self.min_bpm, self.max_bpm)
        self._check_range("Oitava", self.base_octave, MIN_BASE_OCTAVE, MAX_BASE_OCTAVE)

        for i, voice in enumerate(self.voices):
            self._check_range(f"Volume da voz {i}", voice.volume, 1, MAX_MIDI_NOTE)
            self._check_range(
                f"Instrumento da voz {i}", voice.instrument, 0, MAX_MIDI_NOTE
            )

    @property
    def voice_count(self) -> int:
        return len(self.voices)

    def _get_voice(self, voice_number: int) -> VoiceConfig:
        """Retorna a configuração da voz, repetindo o ciclo se o número passar do total"""
        return self.voices[voice_number % self.voice_count]

    def volume_for_voice(self, voice_number: int) -> int:
        volume = self._get_voice(voice_number).volume
        return max(1, min(MAX_MIDI_NOTE, volume))

    def instrument_for_voice(self, voice_number: int) -> int:
        return self._get_voice(voice_number).instrument

    def octave_for_voice(self, voice_number: int) -> int:
        """Calcula a oitava base de cada voz

        Args:
            voice_number: Número da voz (0 em diante)
        """
        return self.base_octave - (voice_number % self.voice_count)

    def faster_bpm(self, bpm: int) -> int:
        """Calcula o aumento de bpm em bpm_step

        Args:
            bpm: BPM atual.
        """
        return min(self.max_bpm, bpm + self.bpm_step)

    def slower_bpm(self, bpm: int) -> int:
        """Calcula a diminuição de bpm em bpm_step

        Args:
            bpm: BPM atual.
        """
        return max(self.min_bpm, bpm - self.bpm_step)

    @staticmethod
    def _check_range(name: str, value: int, minimum: int, maximum: int):
        """Valida se um valor está dentro do intervalo fechado.

        Args:
            name: Nome do campo, usado na mensagem de erro.
            value: Valor a ser validado.
            minimum: Limite inferior.
            maximum: Limite superior.

        Raises:
            ValueError: Se o valor estiver fora do intervalo.
        """
        if not minimum <= value <= maximum:
            raise ValueError(f"{name} deve estar entre {minimum} e {maximum}.")
