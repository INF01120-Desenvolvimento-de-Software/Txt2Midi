from abc import ABC, abstractmethod
from mido import Message

from ui.MidiConstants import (
    ACOUSTIC_GUITAR_NYLON,
    DULCIMER,
    FIDDLE,
    NO_DELAY,
    NOTE_A,
    NOTE_B,
    NOTE_C,
    NOTE_D,
    NOTE_DURATION_TICKS,
    NOTE_E,
    NOTE_F,
    NOTE_G,
    NOTE_VELOCITY,
    REST_PLACEHOLDER_NOTE,
    SILENT_VELOCITY,
    STEEL_DRUMS,
)

REST = None


class Rule(ABC):
    @abstractmethod
    def apply(self, char: str, midi_state) -> str:
        pass

    @abstractmethod
    def match(self, char: str) -> bool:
        pass


class NoteRule(Rule):
    def __init__(self):
        self.notes = {
            "A": NOTE_A,
            "B": NOTE_B,
            "C": NOTE_C,
            "D": NOTE_D,
            "E": NOTE_E,
            "F": NOTE_F,
            "G": NOTE_G,
            "a": REST,
            "c": REST,
            "d": REST,
            "e": REST,
            "f": REST,
            "g": REST,
            "h": REST,
        }

    def match(self, char: str) -> bool:
        return char in self.notes

    def apply(self, char: str, state):
        musical_note = self.notes[char]

        if musical_note is REST:
            state.track.append(
                Message(
                    "note_on",
                    note=REST_PLACEHOLDER_NOTE,
                    velocity=SILENT_VELOCITY,
                    time=NO_DELAY,
                )
            )
            state.track.append(
                Message(
                    "note_off",
                    note=REST_PLACEHOLDER_NOTE,
                    velocity=SILENT_VELOCITY,
                    time=NOTE_DURATION_TICKS,
                )
            )
        else:
            state.track.append(
                Message(
                    "note_on",
                    note=musical_note,
                    velocity=NOTE_VELOCITY,
                    time=NO_DELAY,
                )
            )
            state.track.append(
                Message(
                    "note_off",
                    note=musical_note,
                    velocity=NOTE_VELOCITY,
                    time=NOTE_DURATION_TICKS,
                )
            )


class InstrumentRule(Rule):
    def __init__(self):
        self.instruments = {
            "!": ACOUSTIC_GUITAR_NYLON,
            "O": FIDDLE,
            "o": FIDDLE,
            "I": FIDDLE,
            "i": FIDDLE,
            "U": FIDDLE,
            "u": FIDDLE,
            ";": DULCIMER,
            ",": STEEL_DRUMS,
        }

    def match(self, char: str) -> bool:
        return char in self.instruments

    def apply(self, char: str, state):
        instrument = self.instruments[char]
        state.track.append(
            Message("program_change", program=instrument, time=NO_DELAY)
        )