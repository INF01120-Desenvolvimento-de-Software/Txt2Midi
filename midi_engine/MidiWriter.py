from midi_engine.MidiConstants import MIDI_EXTENSION
from midi_engine.Rule import Rules
from midi_engine.MidiSettings import MidiSettings


class MidiWriter:

    def __init__(self, settings: MidiSettings = None):
        self.parser = Rules(settings or MidiSettings())
        self.midi = None

    def process_text(self, text: str):
        self.midi = self.parser.parse_text(text)

    def save_midi(self, file_name: str):
        if not file_name.endswith(MIDI_EXTENSION):
            file_name = file_name + MIDI_EXTENSION

        self.midi.save(file_name)
