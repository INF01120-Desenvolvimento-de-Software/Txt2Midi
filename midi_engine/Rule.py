from abc import ABC, abstractmethod
from mido import Message


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
            "A": 69,
            "B": 71,
            "C": 60,
            "D": 62,
            "E": 64,
            "F": 65,
            "G": 67,
            "a": None,
            "c": None,
            "d": None,
            "e": None,
            "f": None,
            "g": None,
            "h": None,
        }

    def match(self, char: str) -> bool:
        return char in self.notes

    def apply(self, char: str, state):
        musical_note = self.notes[char]

        if musical_note is None:
            state.track.append(Message("note_on", note=60, velocity=0, time=0))
            state.track.append(Message("note_off", note=60, velocity=0, time=480))
        else:
            state.track.append(
                Message("note_on", note=musical_note, velocity=80, time=0)
            )
            state.track.append(
                Message("note_off", note=musical_note, velocity=80, time=480)
            )


class InstrumentRule(Rule):
    def __init__(self):
        self.instruments = {
            "!": 24,
            "O": 110,
            "o": 110,
            "I": 110,
            "i": 110,
            "U": 110,
            "u": 110,
            ";": 15,
            ",": 114,
        }

    def match(self, char: str) -> bool:
        return char in self.instruments

    def apply(self, char: str, state):
        instrument = self.instruments[char]
        state.track.append(Message("program_change", program=instrument, time=0))
