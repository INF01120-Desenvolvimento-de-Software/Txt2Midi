from mido import MidiFile, MidiTrack, Message
from midi_engine.Exceptions import MidiSaveError
from midi_engine.Rule import NoteRule, InstrumentRule
from ui.MidiConstants import MIDI_EXTENSION 


class MidiState:
    def __init__(self):
        self.track = MidiTrack()


class MidiWriter:
    def __init__(self):
        self.midi = MidiFile()
        self.state = MidiState()
        self.midi.tracks.append(self.state.track)

        self.rules = [NoteRule(), InstrumentRule()]

    def process_text(self, text: str):
        for caractere in text:
            for rule in self.rules:
                if rule.match(caractere):
                    rule.apply(caractere, self.state)
                    break

    def save_midi(self, file_name: str):
        if not file_name.endswith(MIDI_EXTENSION):
            file_name += MIDI_EXTENSION

        try:
            self.midi.save(file_name)
        except OSError as error:
            raise MidiSaveError(file_name) from error

        print(f"Arquivo {file_name} salvo com sucesso")