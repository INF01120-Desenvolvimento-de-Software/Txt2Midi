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
        return self.voices[voice_number % self.voice_count]

    def volume_for_voice(self, voice_number: int) -> int:
        volume = self._get_voice(voice_number).volume
        return max(1, min(MAX_MIDI_NOTE, volume))

    def instrument_for_voice(self, voice_number: int) -> int:
        return self._get_voice(voice_number).instrument

    def octave_for_voice(self, voice_number: int) -> int:
        return self.base_octave - (voice_number % self.voice_count)

    def faster_bpm(self, bpm: int) -> int:
        return min(self.max_bpm, bpm + self.bpm_step)

    def slower_bpm(self, bpm: int) -> int:
        return max(self.min_bpm, bpm - self.bpm_step)

    @staticmethod
    def _check_range(name: str, value: int, minimum: int, maximum: int):
        if not minimum <= value <= maximum:
            raise ValueError(f"{name} deve estar entre {minimum} e {maximum}.")
