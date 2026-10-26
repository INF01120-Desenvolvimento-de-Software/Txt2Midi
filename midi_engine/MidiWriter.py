from mido import MidiFile
from midi_engine.Exceptions import MidiSaveError
from midi_engine.MidiConstants import MIDI_EXTENSION
from midi_engine.MidiSettings import MidiSettings
from midi_engine.Rule import Rules


class MidiWriter:

    def __init__(self, settings: MidiSettings = None):
        self.parser = Rules(settings or MidiSettings())
        self.midi: MidiFile = None

    def process_text(self, text: str):
        self.midi = self.parser.parse_text(text)

    def save_midi(self, file_name: str):
        if not file_name.endswith(MIDI_EXTENSION):
            file_name = file_name + MIDI_EXTENSION

        try:
            self.midi.save(file_name)
        except OSError as error:
            raise MidiSaveError(file_name) from error

        print(f"Arquivo {file_name} salvo com sucesso")
