from ui.MidiConstants import MIDI_EXTENSION
from midi_engine.Rule import Rules

class MidiWriter:

    def __init__(self):
        self.parser = Rules()
        self.midi = None

    def process_text(self, text: str):
        self.midi = self.parser.parse_text(text)

    def save_midi(self, file_name: str):
        if not file_name.endswith(MIDI_EXTENSION):
            file_name = file_name + MIDI_EXTENSION

        self.midi.save(file_name)